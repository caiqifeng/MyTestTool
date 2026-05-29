import datetime as dt
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from check_i18n_images import (
    DEFAULT_THUMBNAIL_ISSUES,
    Finding,
    ImageFile,
    apply_max_file_sample,
    compare_category,
    enrich_findings_with_translation,
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
        findings = compare_category(
            "ui",
            {"a.dds": img("a.dds", "2026-01-01T00:00:00")},
            {"a.dds": img("a.dds", "2026-01-02T00:00:00")},
            None,
            lambda _: False,
        )

        self.assertEqual([f.issue for f in findings], ["mainland_changed"])

    def test_existing_i18n_matches_paths_case_insensitively(self):
        findings = compare_category(
            "ui",
            {"active/nomalbp_1.tga": img("Active/NomalBP_1.tga", "2026-01-02T00:00:00")},
            {"active/nomalbp_1.tga": img("Active/NomalBP_1.Tga", "2026-01-01T00:00:00")},
            None,
            lambda _: False,
        )

        self.assertEqual(findings, [])

    def test_existing_i18n_preserves_original_relative_path_in_findings(self):
        findings = compare_category(
            "ui",
            {"active/nomalbp_1.tga": img("Active/NomalBP_1.tga", "2026-01-01T00:00:00")},
            {"active/nomalbp_1.tga": img("Active/NomalBP_1.Tga", "2026-01-02T00:00:00")},
            None,
            lambda _: False,
        )

        self.assertEqual(findings[0].relative_path, "Active/NomalBP_1.tga")

    def test_existing_i18n_ignores_when_i18n_is_same_or_newer(self):
        findings = compare_category(
            "ui",
            {"a.dds": img("a.dds", "2026-01-02T00:00:00")},
            {"a.dds": img("a.dds", "2026-01-02T00:00:00")},
            None,
            lambda _: False,
        )

        self.assertEqual(findings, [])

    def test_existing_i18n_reports_when_mainland_missing(self):
        findings = compare_category(
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

        findings = compare_category(
            "ui",
            {},
            mainland,
            dt.datetime(2026, 1, 2, tzinfo=UTC),
            lambda f: f.relative_path == "text.dds",
        )

        self.assertEqual(
            [(f.issue, f.relative_path) for f in findings],
            [("mainland_new_with_text", "text.dds")],
        )

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
            self.assertIn("文件不存在问题", content)
            self.assertIn("summary-table", content)
            self.assertIn("sortTable", content)
            self.assertIn("filterTable", content)
            self.assertIn("陆版创建时间", content)
            self.assertIn("时间不对问题", content)
            self.assertIn("报告详情", content)
            self.assertIn("<table", content)
            self.assertIn("<img", content)
            self.assertIn("data-full-src=", content)
            self.assertIn("openPreview", content)
            self.assertIn("report_assets/", content)


if __name__ == "__main__":
    unittest.main()
