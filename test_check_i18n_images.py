import datetime as dt
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from check_i18n_images import (
    DEFAULT_THUMBNAIL_ISSUES,
    Finding,
    ImageFile,
    _filter_whitelisted_files,
    _load_config_pairs,
    apply_max_file_sample,
    compare_category,
    enrich_findings_with_translation,
    ocr_text_detector_factory,
    write_html_report,
    write_xlsx,
)

UTC = dt.timezone.utc


def img(rel, when, full=None):
    return ImageFile(
        rel,
        full or rel,
        dt.datetime.fromisoformat(when).replace(tzinfo=UTC),
        "cat",
    )


class CheckI18nImagesTest(unittest.TestCase):
    def test_existing_i18n_reports_when_mainland_is_newer(self):
        findings, _stats = compare_category(
            "ui",
            {"a.dds": img("a.dds", "2026-01-01T00:00:00")},
            {"a.dds": img("a.dds", "2026-01-02T00:00:00")},
            None,
            lambda _: False,
        )

        self.assertEqual([f.issue for f in findings], ["mainland_changed"])

    def test_existing_i18n_matches_paths_case_insensitively(self):
        findings, _stats = compare_category(
            "ui",
            {"active/nomalbp_1.tga": img("Active/NomalBP_1.tga", "2026-01-02T00:00:00")},
            {"active/nomalbp_1.tga": img("Active/NomalBP_1.Tga", "2026-01-01T00:00:00")},
            None,
            lambda _: False,
        )

        self.assertEqual(findings, [])

    def test_existing_i18n_preserves_original_relative_path_in_findings(self):
        findings, _stats = compare_category(
            "ui",
            {"active/nomalbp_1.tga": img("Active/NomalBP_1.tga", "2026-01-01T00:00:00")},
            {"active/nomalbp_1.tga": img("Active/NomalBP_1.Tga", "2026-01-02T00:00:00")},
            None,
            lambda _: False,
        )

        self.assertEqual(findings[0].relative_path, "Active/NomalBP_1.tga")

    def test_existing_i18n_ignores_when_i18n_is_same_or_newer(self):
        findings, _stats = compare_category(
            "ui",
            {"a.dds": img("a.dds", "2026-01-02T00:00:00")},
            {"a.dds": img("a.dds", "2026-01-02T00:00:00")},
            None,
            lambda _: False,
        )

        self.assertEqual(findings, [])

    def test_existing_i18n_reports_when_mainland_missing(self):
        findings, _stats = compare_category(
            "ui",
            {"a.tga": img("a.tga", "2026-01-01T00:00:00")},
            {},
            None,
            lambda _: False,
        )

        self.assertEqual(findings[0].issue, "mainland_missing")

    def test_new_mainland_reports_only_after_last_check_and_with_text(self):
        mainland = {
            "old.dds": img("old.dds", "2026-01-01T00:00:00"),
            "plain.dds": img("plain.dds", "2026-01-03T00:00:00"),
            "text.dds": img("text.dds", "2026-01-03T00:00:00"),
        }

        findings, _stats = compare_category(
            "ui",
            {},
            mainland,
            dt.datetime(2026, 1, 2, tzinfo=UTC),
            lambda f: f.relative_path == "text.dds",
        )

        self.assertEqual(
            [(f.issue, f.relative_path) for f in findings],
            [
                ("mainland_new_no_text", "plain.dds"),
                ("mainland_new_with_text", "text.dds"),
            ],
        )

    def test_new_mainland_ocr_progress_is_printed(self):
        mainland = {
            "plain.dds": img("plain.dds", "2026-01-03T00:00:00"),
            "text.dds": img("text.dds", "2026-01-03T00:00:00"),
        }

        stderr = io.StringIO()
        with patch("sys.stderr", stderr):
            compare_category(
                "ui",
                {},
                mainland,
                dt.datetime(2026, 1, 2, tzinfo=UTC),
                lambda f: f.relative_path == "text.dds",
            )

        self.assertIn("当前分析进度：1/2", stderr.getvalue())
        self.assertIn("当前分析进度：2/2", stderr.getvalue())

    def test_max_file_sample_uses_shared_keys_for_both_sides(self):
        i18n = {
            "a.tga": img("a.tga", "2026-01-01T00:00:00"),
            "b.tga": img("b.tga", "2026-01-01T00:00:00"),
        }
        mainland = {
            "a.tga": img("a.tga", "2026-01-01T00:00:00"),
            "aa_extra.tga": img("aa_extra.tga", "2026-01-01T00:00:00"),
            "b.tga": img("b.tga", "2026-01-01T00:00:00"),
        }

        sampled_i18n, sampled_mainland = apply_max_file_sample(i18n, mainland, 2)

        self.assertEqual(list(sampled_i18n), ["a.tga"])
        self.assertEqual(list(sampled_mainland), ["a.tga", "aa_extra.tga"])

    def test_config_root_expands_relative_pairs_and_whitelist(self):
        with tempfile.TemporaryDirectory() as td:
            config = Path(td) / "check_config.json"
            config.write_text(
                """
{
  "root": "f:/project/client",
  "whitelist": [
    "ui\\\\Image\\\\ExteriorPic",
    "ui/Image/UItimate/OperationCenter/NewChargeGiftMonthly"
  ],
  "pairs": [
    {
      "name": "ui",
      "i18n": "i18n/zh_TW/ui",
      "mainland": "ui"
    }
  ]
}
""",
                encoding="utf-8",
            )

            pairs = _load_config_pairs(str(config))

        self.assertEqual(pairs[0]["i18n"], "f:/project/client/i18n/zh_TW/ui")
        self.assertEqual(pairs[0]["mainland"], "f:/project/client/ui")
        self.assertEqual(
            pairs[0]["whitelist"],
            [
                "ui/Image/ExteriorPic",
                "ui/Image/UItimate/OperationCenter/NewChargeGiftMonthly",
            ],
        )

    def test_filter_whitelisted_files_uses_pair_relative_prefix(self):
        pair = {
            "i18n_relative": "i18n/zh_TW/ui",
            "mainland_relative": "ui",
            "whitelist": ["ui/Image/ExteriorPic"],
        }
        files = {
            "image/exteriorpic/a.tga": img("Image/ExteriorPic/a.tga", "2026-01-01T00:00:00"),
            "image/keep/b.tga": img("Image/Keep/b.tga", "2026-01-01T00:00:00"),
        }

        filtered = _filter_whitelisted_files(files, pair)

        self.assertEqual(list(filtered), ["image/keep/b.tga"])

    def test_write_xlsx_creates_excel_package(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out.xlsx"
            write_xlsx(out, [])
            self.assertTrue(out.exists())
            self.assertGreater(out.stat().st_size, 100)

    def test_write_xlsx_embeds_local_error_thumbnail_when_available(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow is not installed")

        with tempfile.TemporaryDirectory() as td:
            img_path = Path(td) / "source.tga"
            Image.new("RGB", (16, 16), (255, 0, 0)).save(img_path)
            out = Path(td) / "out.xlsx"
            write_xlsx(
                out,
                [
                    Finding(
                        "ui",
                        "mainland_changed",
                        "source.tga",
                        str(img_path),
                        str(img_path),
                        dt.datetime(2026, 1, 1, tzinfo=UTC),
                        dt.datetime(2026, 1, 2, tzinfo=UTC),
                        "陆版文件修改时间晚于国际版",
                    )
                ],
                thumbnail_issues={"mainland_changed"},
            )

            import zipfile

            with zipfile.ZipFile(out) as zf:
                media = [name for name in zf.namelist() if name.startswith("xl/media/")]
            self.assertTrue(media)

    def test_default_thumbnail_issues_uses_detail_column(self):
        self.assertEqual(DEFAULT_THUMBNAIL_ISSUES, {"__has_detail__"})

    def test_ocr_cache_records_detected_text(self):
        with tempfile.TemporaryDirectory() as td:
            cache_path = Path(td) / "ocr_cache.json"
            image_path = Path(td) / "source.tga"
            image_path.write_bytes(b"fake image")
            image = ImageFile(
                "NewTest/source.tga",
                str(image_path),
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                "ui",
            )

            with patch("check_i18n_images.run_ocr", return_value="文字内容"):
                detector = ocr_text_detector_factory(cache_path)
                self.assertTrue(detector(image))

            data = __import__("json").loads(cache_path.read_text(encoding="utf-8"))
            self.assertNotIn("has_test", data["NewTest/source.tga"])
            self.assertEqual(data["NewTest/source.tga"]["test_str"], "文字内容")

    def test_ocr_cache_refreshes_entries_without_detected_text(self):
        with tempfile.TemporaryDirectory() as td:
            cache_path = Path(td) / "ocr_cache.json"
            image_path = Path(td) / "source.tga"
            image_path.write_bytes(b"fake image")
            image = ImageFile(
                "NewTest/source.tga",
                str(image_path),
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                "ui",
            )
            md5 = __import__("hashlib").md5(b"fake image").hexdigest()
            cache_path.write_text(
                __import__("json").dumps(
                    {"NewTest/source.tga": {"md5": md5, "has_text": False}},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with patch("check_i18n_images.run_ocr", return_value="文字内容"):
                detector = ocr_text_detector_factory(cache_path)
                self.assertTrue(detector(image))

            data = __import__("json").loads(cache_path.read_text(encoding="utf-8"))
            self.assertNotIn("has_test", data["NewTest/source.tga"])
            self.assertEqual(data["NewTest/source.tga"]["test_str"], "文字内容")

    def test_ocr_cache_removes_legacy_has_test_on_cache_hit(self):
        with tempfile.TemporaryDirectory() as td:
            cache_path = Path(td) / "ocr_cache.json"
            image_path = Path(td) / "source.tga"
            image_path.write_bytes(b"fake image")
            image = ImageFile(
                "NewTest/source.tga",
                str(image_path),
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                "ui",
            )
            md5 = __import__("hashlib").md5(b"fake image").hexdigest()
            cache_path.write_text(
                __import__("json").dumps(
                    {
                        "NewTest/source.tga": {
                            "md5": md5,
                            "has_text": True,
                            "has_test": True,
                            "test_str": "文字内容",
                        }
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            detector = ocr_text_detector_factory(cache_path)
            self.assertTrue(detector(image))

            data = __import__("json").loads(cache_path.read_text(encoding="utf-8"))
            self.assertNotIn("has_test", data["NewTest/source.tga"])
            self.assertEqual(data["NewTest/source.tga"]["test_str"], "文字内容")

    def test_write_xlsx_embeds_thumbnail_when_detail_is_present_by_default(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow is not installed")

        with tempfile.TemporaryDirectory() as td:
            img_path = Path(td) / "source.tga"
            Image.new("RGB", (16, 16), (255, 0, 0)).save(img_path)
            out = Path(td) / "out.xlsx"
            write_xlsx(
                out,
                [
                    Finding(
                        "ui",
                        "mainland_changed",
                        "source.tga",
                        str(img_path),
                        str(img_path),
                        dt.datetime(2026, 1, 1, tzinfo=UTC),
                        dt.datetime(2026, 1, 2, tzinfo=UTC),
                        "has detail",
                    )
                ],
            )

            import zipfile

            with zipfile.ZipFile(out) as zf:
                media = [name for name in zf.namelist() if name.startswith("xl/media/")]
            self.assertTrue(media)


    def test_enrich_skips_mainland_missing(self):
        """mainland_missing findings are not enriched (no mainland file to OCR)."""
        findings = [
            Finding("ui", "mainland_missing", "a.dds", "/i18n/a.dds", "", None, None, "废弃")
        ]
        checker = lambda m, i: ("ok", "")
        result = enrich_findings_with_translation(findings, checker)
        self.assertEqual(result[0].translation_status, None)

    def test_enrich_sets_no_cn_text_when_mainland_has_no_chinese(self):
        """If mainland OCR text has no Chinese characters, status is no_cn_text."""
        findings = [
            Finding(
                "ui", "mainland_changed", "a.dds", "/i18n/a.dds", "/ml/a.dds",
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                dt.datetime(2026, 1, 2, tzinfo=UTC),
                "陆版更新",
            )
        ]
        checker = lambda m, i: ("ok", "")
        with patch("check_i18n_images.run_ocr_from_path", return_value="hello world"):
            result = enrich_findings_with_translation(findings, checker)
        self.assertEqual(result[0].translation_status, "no_cn_text")

    def test_enrich_calls_checker_when_mainland_has_chinese(self):
        """If mainland has Chinese text, translation_checker is called and result stored."""
        findings = [
            Finding(
                "ui", "mainland_changed", "a.dds", "/i18n/a.dds", "/ml/a.dds",
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                dt.datetime(2026, 1, 2, tzinfo=UTC),
                "陆版更新",
            )
        ]
        ocr_returns = {"/ml/a.dds": "简体文字", "/i18n/a.dds": "繁體文字"}
        checker = lambda m, i: ("ok", "")
        with patch(
            "check_i18n_images.run_ocr_from_path",
            side_effect=lambda path, cat="": ocr_returns.get(path),
        ):
            result = enrich_findings_with_translation(findings, checker)
        self.assertEqual(result[0].translation_status, "ok")
        self.assertEqual(result[0].mainland_ocr_text, "简体文字")
        self.assertEqual(result[0].i18n_ocr_text, "繁體文字")

    def test_enrich_new_with_text_has_no_i18n_ocr(self):
        """For mainland_new_with_text, i18n_path is empty so i18n_text is None -> missing."""
        findings = [
            Finding(
                "ui", "mainland_new_with_text", "b.dds", "", "/ml/b.dds",
                None,
                dt.datetime(2026, 1, 2, tzinfo=UTC),
                "新增",
            )
        ]
        checker = lambda m, i: ("missing", "无繁体") if i is None else ("ok", "")
        with patch("check_i18n_images.run_ocr_from_path", return_value="新增中文"):
            result = enrich_findings_with_translation(findings, checker)
        self.assertEqual(result[0].translation_status, "missing")
        self.assertEqual(result[0].translation_note, "无繁体")

    def test_write_xlsx_includes_translation_columns(self):
        """Excel output contains translation columns even when values are None."""
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out.xlsx"
            write_xlsx(
                out,
                [
                    Finding(
                        "ui",
                        "mainland_changed",
                        "a.dds",
                        "/i18n/a.dds",
                        "/ml/a.dds",
                        dt.datetime(2026, 1, 1, tzinfo=UTC),
                        dt.datetime(2026, 1, 2, tzinfo=UTC),
                        "陆版更新",
                        mainland_ocr_text="简体",
                        i18n_ocr_text="繁體",
                        translation_status="ok",
                        translation_note="",
                    )
                ],
            )
            import zipfile

            import html

            with zipfile.ZipFile(out) as zf:
                sheet = html.unescape(zf.read("xl/worksheets/sheet1.xml").decode("utf-8"))
            # 14 columns: header row should contain translation column headers
            self.assertIn("翻译状态", sheet)
            self.assertIn("翻译问题说明", sheet)

    def test_write_html_report_contains_summary_and_clickable_images(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow is not installed")

        with tempfile.TemporaryDirectory() as td:
            img_path = Path(td) / "source.tga"
            Image.new("RGB", (16, 16), (255, 0, 0)).save(img_path)
            out = Path(td) / "report.html"
            write_html_report(
                out,
                [
                    Finding(
                        "ui",
                        "mainland_missing",
                        "source.tga",
                        str(img_path),
                        "",
                        dt.datetime(2026, 1, 1, tzinfo=UTC),
                        None,
                        "missing detail",
                    ),
                    Finding(
                        "ui",
                        "mainland_changed",
                        "changed.tga",
                        str(img_path),
                        str(img_path),
                        dt.datetime(2026, 1, 1, tzinfo=UTC),
                        dt.datetime(2026, 1, 2, tzinfo=UTC),
                        "changed detail",
                    ),
                ],
            )

            content = out.read_text(encoding="utf-8")
            self.assertIn("多语言图片检查汇总", content)
            self.assertIn("报告详情", content)
            self.assertIn("疑似废除文件", content)
            self.assertIn("summary-table", content)
            self.assertIn("sortTable", content)
            self.assertIn("filterTable", content)
            self.assertNotIn("陆版创建时间", content)
            self.assertIn("修改时间异常", content)
            self.assertIn("报告详情", content)
            self.assertIn("<table", content)
            self.assertIn("<img", content)
            self.assertIn("data-full-src=", content)
            self.assertIn("openPreview", content)
            assets_dir = out.parent / "report_assets"
            asset_files = sorted(assets_dir.glob("*.png"))
            self.assertGreaterEqual(len(asset_files), 2)
            for asset in asset_files:
                self.assertGreater(asset.stat().st_size, 0)
                self.assertEqual(asset.suffix.lower(), ".png")
                self.assertIn(f'report_assets/{asset.name}', content)
            self.assertIn("report_assets/img_1_i18n.tga.png", content)
            self.assertNotIn('src="report_assets/img_1_i18n.tga"', content)
            self.assertNotIn('src="report_assets/img_1_i18n.dds"', content)
            self.assertNotIn("data:image/png;base64,", content)
            self.assertNotIn(str(img_path), content)
            self.assertNotIn(img_path.resolve().as_uri(), content)

    def test_write_html_report_includes_new_no_text_review_rows_and_ocr_text(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow is not installed")

        with tempfile.TemporaryDirectory() as td:
            img_path = Path(td) / "source.tga"
            Image.new("RGB", (16, 16), (255, 0, 0)).save(img_path)
            out = Path(td) / "report.html"
            write_html_report(
                out,
                [
                    Finding(
                        "ui",
                        "mainland_new_with_text",
                        "NewTest/text.tga",
                        "",
                        str(img_path),
                        None,
                        dt.datetime(2026, 1, 2, tzinfo=UTC),
                        "text detail",
                        mainland_ocr_text="大剑网三",
                    ),
                    Finding(
                        "ui",
                        "mainland_new_no_text",
                        "NewTest/plain.tga",
                        "",
                        str(img_path),
                        None,
                        dt.datetime(2026, 1, 2, tzinfo=UTC),
                        "review detail",
                    ),
                ],
                new_no_text=1,
            )

            content = out.read_text(encoding="utf-8")
            cn = lambda value: value.encode("ascii").decode("unicode_escape")
            self.assertIn("NewTest/plain.tga", content)
            self.assertIn(cn(r"\u65b0\u589e\u65e0\u6587\u5b57\u56fe\u7247"), content)
            self.assertIn(cn(r"\u8bc6\u522b\u6587\u5b57\uff1a"), content)
            self.assertIn(cn(r"\u5927\u5251\u7f51\u4e09"), content)
            self.assertIn("report-shell", content)
            self.assertIn("exportFilteredRows", content)
            self.assertIn(cn(r"\u5bfc\u51fa\u7b5b\u9009\u7ed3\u679c"), content)
            self.assertIn("buildExportImageCell", content)
            self.assertIn("imageSrcToDataUri", content)
            self.assertIn("FileReader", content)
            self.assertIn("data:image", content)
            self.assertIn("application/vnd.ms-excel", content)
            self.assertIn("ui_image_check_filtered.xls", content)
            self.assertIn('<select data-filter="category" onchange="filterTable()">', content)
            self.assertIn('<select data-filter="issue" onchange="filterTable()">', content)
            self.assertIn('<option>ui</option>', content)
            self.assertIn("<colgroup>", content)
            self.assertIn(cn(r"\u4e8c\u3001\u6b63\u5e38\u56fe\u7247\uff1a\u5171"), content)
            self.assertIn(cn(r"\u4e09\u3001\u5f02\u5e38\u56fe\u7247\uff1a\u5171"), content)
            self.assertNotIn("metric-grid", content)
            self.assertNotIn('class="summary-card', content)
            header_row_start = content.index(cn(r"\u5e8f\u53f7") + "<span")
            header_row_end = content.index("</tr>", header_row_start)
            header_row = content[header_row_start:header_row_end]
            expected_order = [
                cn(r"\u5e8f\u53f7"),
                cn(r"\u7c7b\u522b"),
                cn(r"\u95ee\u9898\u7c7b\u578b"),
                cn(r"\u76f8\u5bf9\u8def\u5f84"),
                cn(r"\u9646\u7248\u56fe\u7247"),
                cn(r"\u56fd\u9645\u7248\u56fe\u7247"),
                cn(r"\u9646\u7248\u4fee\u6539\u65f6\u95f4"),
                cn(r"\u56fd\u9645\u7248\u4fee\u6539\u65f6\u95f4"),
                cn(r"\u8bf4\u660e"),
            ]
            positions = [header_row.index(label) for label in expected_order]
            self.assertEqual(positions, sorted(positions))
            self.assertNotIn(f"<th onclick=\"sortTable(9)\">{cn(r'\u8bc6\u522b\u6587\u5b57')}", header_row)
            self.assertNotIn(cn(r"\u9646\u7248\u521b\u5efa\u65f6\u95f4"), header_row)
            self.assertIn(f'class="mainland-new-with-text" title="{cn(r"\u8bc6\u522b\u6587\u5b57\uff1a\u5927\u5251\u7f51\u4e09")}" data-ocr="{cn(r"\u5927\u5251\u7f51\u4e09")}"', content)
            self.assertIn('class="mainland-new-no-text"><td class="row-index"', content)
            self.assertIn('tr.mainland-new-with-text[title] { cursor:help; }', content)
            self.assertNotIn('tr.mainland-new-no-text[title] { cursor:help; }', content)
            self.assertIn("min-width:1280px", content)
            self.assertIn("border-collapse:separate", content)
            self.assertIn("border-spacing:0", content)
            self.assertIn(".filter-row th { top:40px", content)
            self.assertIn("height:40px", content)


if __name__ == "__main__":
    unittest.main()
