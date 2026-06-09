import datetime as dt
import io
import os
import tempfile
import time
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
    default_config_path,
    default_ocr_cache_db_path,
    default_output_path,
    enrich_findings_with_translation,
    format_progress_line,
    migrate_ocr_json_to_sqlite,
    ocr_text_detector_factory,
    main,
    sqlite_ocr_text_detector_factory,
    serve_report,
    update_ocr_cache_operation_sqlite,
    update_ocr_cache_operation,
    scan_local,
    write_html_report,
    write_xlsx,
    _require_pillow_for_report,
)

UTC = dt.timezone.utc
cn = lambda value: value.encode("ascii").decode("unicode_escape")


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

    def test_existing_i18n_matches_same_stem_with_different_image_extension(self):
        calls = []

        def detector(image):
            calls.append(image.relative_path)
            return True

        findings, stats = compare_category(
            "ui",
            {"active/nomalbp_1": img("Active/NomalBP_1.tga", "2026-01-02T00:00:00")},
            {"active/nomalbp_1": img("Active/NomalBP_1.dds", "2026-01-01T00:00:00")},
            None,
            detector,
        )

        self.assertEqual(findings, [])
        self.assertEqual(stats["normal_synced"], 1)
        self.assertEqual(calls, [])

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

    def test_existing_mainland_file_does_not_run_ocr(self):
        calls = []

        def detector(image):
            calls.append(image.relative_path)
            return True

        findings, stats = compare_category(
            "ui",
            {"a.dds": img("a.dds", "2026-01-02T00:00:00")},
            {"a.dds": img("a.dds", "2026-01-01T00:00:00")},
            None,
            detector,
        )

        self.assertEqual(findings, [])
        self.assertEqual(stats["normal_synced"], 1)
        self.assertEqual(calls, [])

    def test_existing_i18n_reports_when_mainland_missing(self):
        findings, _stats = compare_category(
            "ui",
            {"a.tga": img("a.tga", "2026-01-01T00:00:00")},
            {},
            None,
            lambda _: False,
        )

        self.assertEqual(findings[0].issue, "mainland_missing")

    def test_new_mainland_reports_all_mainland_only_images_and_classifies_text(self):
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
                ("mainland_new_no_text", "old.dds"),
                ("mainland_new_no_text", "plain.dds"),
                ("mainland_new_with_text", "text.dds"),
            ],
        )

    def test_ocr_text_detector_treats_only_chinese_text_as_text(self):
        detector = ocr_text_detector_factory()
        with tempfile.TemporaryDirectory() as td:
            english_path = Path(td) / "english.dds"
            chinese_path = Path(td) / "chinese.dds"
            english_path.write_bytes(b"english")
            chinese_path.write_bytes(b"chinese")
            english_image = img("english.dds", "2026-01-03T00:00:00", full=str(english_path))
            chinese_image = img("chinese.dds", "2026-01-03T00:00:00", full=str(chinese_path))

            with patch("check_i18n_images.run_ocr") as run_ocr:
                run_ocr.side_effect = lambda image: {
                    "english.dds": "Season 2026_01",
                    "chinese.dds": cn(r"\u8d5b\u5b63\u5f00\u542f"),
                }[image.relative_path]

                self.assertFalse(detector(english_image))
                self.assertTrue(detector(chinese_image))

    def test_new_mainland_ignores_last_check_time_for_mainland_only_images(self):
        old_candidate = img("SampleOnly/text.tga", "2026-01-01T00:00:00")

        findings, _stats = compare_category(
            "ui",
            {},
            {"SampleOnly/text.tga": old_candidate},
            dt.datetime(2026, 1, 2, tzinfo=UTC),
            lambda _: True,
        )

        self.assertEqual([(f.issue, f.relative_path) for f in findings], [("mainland_new_with_text", "SampleOnly/text.tga")])

    def test_new_mainland_ocr_progress_is_printed(self):
        mainland = {
            "plain.dds": img("plain.dds", "2026-01-03T00:00:00", full="/tmp/plain.dds"),
            "text.dds": img("text.dds", "2026-01-03T00:00:00", full="/tmp/text.dds"),
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

        output = stderr.getvalue()
        self.assertIn("1/2", output)
        self.assertIn("2/2", output)
        self.assertIn("/tmp/plain.dds", output)
        self.assertIn("/tmp/text.dds", output)
        self.assertTrue(output.endswith("\n"))

    def test_new_mainland_ocr_can_run_with_multiple_workers(self):
        mainland = {
            f"{i}.dds": img(f"{i}.dds", "2026-01-03T00:00:00")
            for i in range(4)
        }
        calls = []

        def detector(image):
            time.sleep(0.05)
            calls.append(image.relative_path)
            return image.relative_path in {"1.dds", "3.dds"}

        started = time.monotonic()
        findings, stats = compare_category(
            "ui",
            {},
            mainland,
            None,
            detector,
            ocr_workers=4,
        )
        elapsed = time.monotonic() - started

        self.assertLess(elapsed, 1.0)
        self.assertEqual(set(calls), {"0.dds", "1.dds", "2.dds", "3.dds"})
        self.assertEqual(stats["new_no_text"], 2)
        self.assertEqual(
            [(f.issue, f.relative_path) for f in findings],
            [
                ("mainland_new_no_text", "0.dds"),
                ("mainland_new_with_text", "1.dds"),
                ("mainland_new_no_text", "2.dds"),
                ("mainland_new_with_text", "3.dds"),
            ],
        )

    def test_parallel_ocr_progress_includes_worker_thread_name(self):
        mainland = {
            f"{i}.dds": img(f"{i}.dds", "2026-01-03T00:00:00")
            for i in range(2)
        }

        def detector(_image):
            time.sleep(0.01)
            return False

        stderr = io.StringIO()
        with patch("sys.stderr", stderr):
            compare_category(
                "ui",
                {},
                mainland,
                None,
                detector,
                ocr_workers=2,
            )

        self.assertIn("OCR线程", stderr.getvalue())

    def test_scan_local_keys_images_by_directory_and_stem(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            image = root / "Image" / "Active" / "NomalBP_1.dds"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"image")

            files = scan_local(str(root))

        self.assertIn("image/active/nomalbp_1", files)
        self.assertNotIn("image/active/nomalbp_1.dds", files)

    def test_format_progress_line_includes_current_full_path(self):
        line = format_progress_line(3, 10, 1, 5, r"E:\trunk\client\ui\a.tga")

        self.assertIn("3/10", line)
        self.assertIn("01", line)
        self.assertIn("05", line)
        self.assertIn(r"E:\trunk\client\ui\a.tga", line)

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
    "ui/Image/UItimate/OperationCenter/NewChargeGiftMonthly",
    "data/source/maps/*minimap*/^[0-9_-]+$.*"
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
                "data/source/maps/*minimap*/^[0-9_-]+$.*",
            ],
        )

    def test_config_preserves_pair_category_and_type_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            config = Path(td) / "check_config.json"
            config.write_text(
                """
{
  "root": "f:/project/client",
  "pairs": [
    {
      "name": "ui",
      "category": "界面",
      "type": "UI资源",
      "i18n": "i18n/zh_TW/ui",
      "mainland": "ui"
    }
  ]
}
""",
                encoding="utf-8",
            )

            pairs = _load_config_pairs(str(config))

        self.assertEqual(pairs[0]["category"], "界面")
        self.assertEqual(pairs[0]["type"], "UI资源")

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

    def test_filter_whitelisted_files_supports_minimap_filename_rule(self):
        pair = {
            "i18n_relative": "i18n/zh_TW/data/source",
            "mainland_relative": "data/source",
            "whitelist": ["data/source/maps/*minimap*/^[0-9_-]+$.*"],
        }
        files = {
            "maps/worldminimap/001_002.tga": img("maps/worldminimap/001_002.tga", "2026-01-01T00:00:00"),
            "maps/worldminimap/001_002-1.tga": img("maps/worldminimap/001_002-1.tga", "2026-01-01T00:00:00"),
            "maps/world_minimap_hd/9.dds": img("maps/world_minimap_hd/9.dds", "2026-01-01T00:00:00"),
            "maps/worldminimap/title_001.tga": img("maps/worldminimap/title_001.tga", "2026-01-01T00:00:00"),
            "maps/worldminimap/001_a-1.tga": img("maps/worldminimap/001_a-1.tga", "2026-01-01T00:00:00"),
            "maps/world/001_002.tga": img("maps/world/001_002.tga", "2026-01-01T00:00:00"),
        }

        filtered = _filter_whitelisted_files(files, pair)

        self.assertEqual(
            list(filtered),
            ["maps/worldminimap/title_001.tga", "maps/worldminimap/001_a-1.tga", "maps/world/001_002.tga"],
        )

    def test_scan_local_skips_whitelisted_directories_before_descending(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            skipped_dir = root / "Image" / "ExteriorPic"
            kept_dir = root / "Image" / "Keep"
            skipped_dir.mkdir(parents=True)
            kept_dir.mkdir(parents=True)
            (skipped_dir / "ignored.tga").write_bytes(b"ignored")
            (kept_dir / "kept.tga").write_bytes(b"kept")

            result = scan_local(
                str(root),
                {
                    "i18n_relative": "i18n/zh_TW/ui",
                    "mainland_relative": "ui",
                    "whitelist": ["ui/Image/ExteriorPic"],
                },
            )

            self.assertEqual(list(result), ["image/keep/kept"])

    def test_main_rejects_non_html_output(self):
        with tempfile.TemporaryDirectory() as td:
            config = Path(td) / "check_config.json"
            config.write_text(
                '{"pairs":[{"name":"ui","i18n":"i18n","mainland":"ui"}]}',
                encoding="utf-8",
            )

            with self.assertRaises(SystemExit) as cm:
                main(["--config", str(config), "--output", str(Path(td) / "out.xlsx"), "--no-ocr"])

        self.assertNotEqual(cm.exception.code, 0)

    def test_main_writes_red_error_report_when_config_directory_is_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = root / "check_config.json"
            output = root / "out.html"
            missing_i18n = root / "missing_i18n"
            missing_mainland = root / "missing_mainland"
            config.write_text(
                __import__("json").dumps(
                    {
                        "pairs": [
                            {
                                "name": "ui",
                                "i18n": str(missing_i18n),
                                "mainland": str(missing_mainland),
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            result = main(["--config", str(config), "--output", str(output), "--no-ocr"])

            content = output.read_text(encoding="utf-8")
            self.assertEqual(result, 1)
            self.assertIn("ERROR", content)
            self.assertIn("color:#b42318", content)
            self.assertIn("missing_i18n", content)
            self.assertIn("missing_mainland", content)

    def test_main_does_not_accept_removed_product_options(self):
        removed_options = [
            ["--state-file", "state.txt"],
            ["--no-save-state"],
            ["--enable-translation-check"],
            ["--anthropic-api-key", "key"],
            ["--thumbnail-limit", "10"],
            ["--no-thumbnail-resize"],
            ["--thumbnail-issue", "mainland_changed"],
        ]

        for option_args in removed_options:
            with self.subTest(option=option_args[0]):
                args = [
                    *option_args,
                    "--i18n",
                    "missing-i18n",
                    "--mainland",
                    "missing-mainland",
                    "--no-ocr",
                ]
                with patch(
                    "check_i18n_images.collect_findings",
                    return_value=([], {"i18n_count": 0, "mainland_count": 0, "normal_synced": 0, "new_no_text": 0}),
                ), patch("check_i18n_images._require_pillow_for_report"), patch("check_i18n_images.write_html_report"):
                    with self.assertRaises(SystemExit) as cm:
                        main(args)

                self.assertEqual(cm.exception.code, 2)

    def test_main_defaults_ocr_workers_to_one(self):
        captured = {}

        def fake_collect(args, report_callback=None):
            captured["ocr_workers"] = args.ocr_workers
            return [], {"i18n_count": 0, "mainland_count": 0, "normal_synced": 0, "new_no_text": 0}

        with patch("check_i18n_images.os.cpu_count", return_value=12), patch(
            "check_i18n_images.collect_findings", side_effect=fake_collect
        ), patch(
            "check_i18n_images._require_pillow_for_report"
        ), patch("check_i18n_images.write_html_report"):
            main([
                "--i18n",
                "missing-i18n",
                "--mainland",
                "missing-mainland",
                "--output",
                "out.html",
                "--no-ocr",
            ])

        self.assertEqual(captured["ocr_workers"], 1)

    def test_real_cli_starts_report_service_once_after_first_report(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "i18n").mkdir()
            (root / "ui").mkdir()
            config = root / "check_config.json"
            output = root / "ui_image_check_report.html"
            db_path = root / ".ocr_cache.db"
            config.write_text(
                __import__("json").dumps(
                    {
                        "pairs": [
                            {
                                "name": "ui",
                                "i18n": str(root / "i18n"),
                                "mainland": str(root / "ui"),
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            counts = {"i18n_count": 0, "mainland_count": 0, "normal_synced": 0, "new_no_text": 0}

            def fake_collect(_args, report_callback=None):
                report_callback([], counts)
                report_callback([], counts)
                return [], counts

            with patch("sys.argv", ["check_i18n_images.py"]), patch(
                "check_i18n_images.default_config_path", return_value=config
            ), patch("check_i18n_images.default_output_path", return_value=output), patch(
                "check_i18n_images.default_ocr_cache_db_path", return_value=db_path
            ), patch("check_i18n_images.collect_findings", side_effect=fake_collect), patch(
                "check_i18n_images._require_pillow_for_report"
            ), patch("check_i18n_images.write_html_report"), patch(
                "check_i18n_images.start_report_service_once", return_value=True
            ) as start_service:
                result = main(None)

            self.assertEqual(result, 0)
            start_service.assert_called_once()
            self.assertEqual(start_service.call_args.args[0], output)
            self.assertEqual(start_service.call_args.kwargs["cache_db_path"], db_path)

    def test_main_logs_version_and_current_time_before_running(self):
        fixed_now = dt.datetime(2026, 6, 4, 16, 1, 28, tzinfo=dt.timezone(dt.timedelta(hours=8)))
        stderr = io.StringIO()

        with patch(
            "check_i18n_images.collect_findings",
            return_value=([], {"i18n_count": 0, "mainland_count": 0, "normal_synced": 0, "new_no_text": 0}),
        ), patch("check_i18n_images._require_pillow_for_report"), patch(
            "check_i18n_images.write_html_report"
        ), patch("check_i18n_images.dt.datetime") as mock_datetime, patch("sys.stderr", stderr):
            mock_datetime.now.return_value = fixed_now
            mock_datetime.fromtimestamp.side_effect = dt.datetime.fromtimestamp
            mock_datetime.fromisoformat.side_effect = dt.datetime.fromisoformat
            main([
                "--i18n",
                "missing-i18n",
                "--mainland",
                "missing-mainland",
                "--output",
                "out.html",
                "--no-ocr",
            ])

        self.assertIn("version = 1.0.2，time = 2026-06-04 16:01:28 +08:00", stderr.getvalue())

    def test_main_writes_version_line_to_run_log(self):
        fixed_now = dt.datetime(2026, 6, 4, 16, 1, 28, tzinfo=dt.timezone(dt.timedelta(hours=8)))

        with tempfile.TemporaryDirectory() as td:
            previous_cwd = os.getcwd()
            os.chdir(td)
            try:
                with patch(
                    "check_i18n_images.collect_findings",
                    return_value=([], {"i18n_count": 0, "mainland_count": 0, "normal_synced": 0, "new_no_text": 0}),
                ), patch("check_i18n_images._require_pillow_for_report"), patch(
                    "check_i18n_images.write_html_report"
                ), patch("check_i18n_images.dt.datetime") as mock_datetime:
                    mock_datetime.now.return_value = fixed_now
                    mock_datetime.fromtimestamp.side_effect = dt.datetime.fromtimestamp
                    mock_datetime.fromisoformat.side_effect = dt.datetime.fromisoformat
                    main([
                        "--i18n",
                        "missing-i18n",
                        "--mainland",
                        "missing-mainland",
                        "--output",
                        "out.html",
                        "--no-ocr",
                    ])

                log_text = Path("Log/20260604_160128.log").read_text(encoding="utf-8")
            finally:
                os.chdir(previous_cwd)

        self.assertIn("version = 1.0.2，time = 2026-06-04 16:01:28 +08:00", log_text)

    def test_main_defaults_ocr_workers_to_at_least_one(self):
        captured = {}

        def fake_collect(args, report_callback=None):
            captured["ocr_workers"] = args.ocr_workers
            return [], {"i18n_count": 0, "mainland_count": 0, "normal_synced": 0, "new_no_text": 0}

        with patch("check_i18n_images.os.cpu_count", return_value=1), patch(
            "check_i18n_images.collect_findings", side_effect=fake_collect
        ), patch(
            "check_i18n_images._require_pillow_for_report"
        ), patch("check_i18n_images.write_html_report"):
            main([
                "--i18n",
                "missing-i18n",
                "--mainland",
                "missing-mainland",
                "--output",
                "out.html",
                "--no-ocr",
            ])

        self.assertEqual(captured["ocr_workers"], 1)

    def test_main_writes_run_log_and_ocr_candidate_list(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            i18n_dir = root / "i18n"
            mainland_dir = root / "ui"
            new_image = mainland_dir / "Image" / "new.tga"
            i18n_dir.mkdir()
            new_image.parent.mkdir(parents=True)
            new_image.write_bytes(b"fake image")
            config = root / "check_config.json"
            config.write_text(
                __import__("json").dumps(
                    {
                        "pairs": [
                            {
                                "name": "ui",
                                "i18n": str(i18n_dir),
                                "mainland": str(mainland_dir),
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            old_cwd = os.getcwd()
            os.chdir(root)
            try:
                with patch("check_i18n_images._require_pillow_for_report"), patch(
                    "check_i18n_images.write_html_report"
                ):
                    main(["--config", str(config), "--output", str(root / "out.html"), "--no-ocr"])
            finally:
                os.chdir(old_cwd)

            log_files = list((root / "Log").glob("*.log"))
            ocr_lists = list((root / "Log").glob("*_ocr_images.txt"))
            log_text = log_files[0].read_text(encoding="utf-8") if log_files else ""
            ocr_list_text = ocr_lists[0].read_text(encoding="utf-8") if ocr_lists else ""

        self.assertEqual(len(log_files), 1)
        self.assertEqual(len(ocr_lists), 1)
        self.assertIn("开始检查", log_text)
        self.assertIn("Image/new.tga", ocr_list_text)

    def test_main_without_args_uses_default_config_output_and_logs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            i18n_dir = root / "i18n"
            mainland_dir = root / "ui"
            i18n_dir.mkdir()
            mainland_dir.mkdir()
            config = root / "check_config.json"
            output = root / "ui_image_check_report.html"
            cache_db = root / ".ocr_cache.db"
            config.write_text(
                __import__("json").dumps(
                    {
                        "pairs": [
                            {
                                "name": "ui",
                                "i18n": str(i18n_dir),
                                "mainland": str(mainland_dir),
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with patch("check_i18n_images.default_config_path", return_value=config), patch(
                "check_i18n_images.default_output_path", return_value=output
            ), patch("check_i18n_images.default_ocr_cache_db_path", return_value=cache_db), patch(
                "check_i18n_images._require_pillow_for_report"
            ), patch("check_i18n_images.write_html_report") as write_report:
                main([])

        self.assertEqual(write_report.call_args.args[0], output)
        self.assertEqual(write_report.call_args.kwargs["ocr_cache_name"], ".ocr_cache.db")

    def test_script_sibling_defaults_are_used_for_config_output_and_sqlite_cache(self):
        script_path = Path("C:/work/tools/check_i18n_images.py")

        self.assertEqual(default_config_path(script_path), Path("C:/work/tools/check_config.json"))
        self.assertEqual(default_output_path(script_path), Path("C:/work/tools/ui_image_check_report.html"))
        self.assertEqual(default_ocr_cache_db_path(script_path), Path("C:/work/tools/.ocr_cache.db"))

    def test_help_no_longer_exposes_ocr_cache_arguments(self):
        stdout = io.StringIO()
        with patch("sys.stdout", stdout), self.assertRaises(SystemExit):
            main(["--help"])

        help_text = stdout.getvalue()
        self.assertNotIn("--ocr-cache-db", help_text)
        self.assertNotIn("--ocr-cache-file", help_text)

    def test_main_writes_new_no_text_list_to_run_log(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            i18n_dir = root / "i18n"
            mainland_dir = root / "ui"
            image = mainland_dir / "Image" / "plain.tga"
            i18n_dir.mkdir()
            image.parent.mkdir(parents=True)
            image.write_bytes(b"fake image")
            config = root / "check_config.json"
            output = root / "ui_image_check_report.html"
            cache_db = root / ".ocr_cache.db"
            config.write_text(
                __import__("json").dumps(
                    {
                        "pairs": [
                            {
                                "name": "ui",
                                "i18n": str(i18n_dir),
                                "mainland": str(mainland_dir),
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            old_cwd = os.getcwd()
            os.chdir(root)
            try:
                with patch("check_i18n_images.default_config_path", return_value=config), patch(
                    "check_i18n_images.default_output_path", return_value=output
                ), patch("check_i18n_images.default_ocr_cache_db_path", return_value=cache_db), patch(
                    "check_i18n_images._require_pillow_for_report"
                ), patch("check_i18n_images.write_html_report"):
                    main(["--no-ocr"])
                log_file = next((root / "Log").glob("*.log"))
                log_text = log_file.read_text(encoding="utf-8")
            finally:
                os.chdir(old_cwd)

        self.assertIn("count=1", log_text)
        self.assertIn("Image/plain.tga", log_text)

    def test_main_writes_cumulative_html_report_after_each_pair(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = root / "check_config.json"
            config.write_text(
                __import__("json").dumps(
                    {
                        "root": str(root),
                        "pairs": [
                            {
                                "name": "ui",
                                "type": "UI",
                                "i18n": "i18n_ui",
                                "mainland": "mainland_ui",
                            },
                            {
                                "name": "map",
                                "type": "地图",
                                "i18n": "i18n_map",
                                "mainland": "mainland_map",
                            },
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            first_finding = Finding(
                "UI",
                "mainland_missing",
                "a.tga",
                "a-i18n.tga",
                "",
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                None,
                "missing",
            )
            second_finding = Finding(
                "地图",
                "mainland_changed",
                "b.tga",
                "b-i18n.tga",
                "b-mainland.tga",
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                dt.datetime(2026, 1, 2, tzinfo=UTC),
                "changed",
            )
            for directory in ("i18n_ui", "mainland_ui", "i18n_map", "mainland_map"):
                (root / directory).mkdir()

            def fake_scan(path, pair):
                return {"one": img("one.tga", "2026-01-01T00:00:00", full=str(root / "one.tga"))}

            with patch("check_i18n_images.scan_local", side_effect=fake_scan), patch(
                "check_i18n_images.compare_category",
                side_effect=[
                    ([first_finding], {"normal_synced": 2, "new_no_text": 1}),
                    ([second_finding], {"normal_synced": 3, "new_no_text": 0}),
                ],
            ) as compare, patch("check_i18n_images._require_pillow_for_report"), patch(
                "check_i18n_images.write_html_report"
            ) as write_report:
                main(["--config", str(config), "--output", str(root / "out.html"), "--no-ocr"])

        self.assertEqual(write_report.call_count, 2)
        self.assertEqual(compare.call_args_list[0].args[0], "UI")
        self.assertEqual(compare.call_args_list[1].args[0], "地图")
        self.assertEqual(write_report.call_args_list[0].args[1], [first_finding])
        self.assertEqual(write_report.call_args_list[0].kwargs["i18n_count"], 1)
        self.assertEqual(write_report.call_args_list[0].kwargs["mainland_count"], 1)
        self.assertEqual(write_report.call_args_list[0].kwargs["normal_synced"], 2)
        self.assertEqual(write_report.call_args_list[0].kwargs["new_no_text"], 1)
        self.assertEqual(write_report.call_args_list[1].args[1], [first_finding, second_finding])
        self.assertEqual(write_report.call_args_list[1].kwargs["i18n_count"], 2)
        self.assertEqual(write_report.call_args_list[1].kwargs["mainland_count"], 2)
        self.assertEqual(write_report.call_args_list[1].kwargs["normal_synced"], 5)
        self.assertEqual(write_report.call_args_list[1].kwargs["new_no_text"], 1)

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
                        "changed detail",
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

    def test_module_does_not_expose_tesseract_fallback(self):
        module = __import__("check_i18n_images")

        self.assertFalse(hasattr(module, "run_tesseract_ocr"))
        self.assertFalse(hasattr(module, "_is_tesseract_available"))
        self.assertFalse(hasattr(module, "_tesseract_exe"))

    def test_run_ocr_uses_rapidocr_without_tesseract_fallback(self):
        image = ImageFile(
            "source.tga",
            "source.tga",
            dt.datetime(2026, 1, 1, tzinfo=UTC),
            "ui",
        )

        with patch("check_i18n_images.run_rapidocr", return_value="越海珠贝"):
            self.assertEqual(__import__("check_i18n_images").run_ocr(image), "越海珠贝")

        with patch("check_i18n_images.run_rapidocr", return_value=None):
            self.assertEqual(__import__("check_i18n_images").run_ocr(image), None)

    def test_ocr_text_detector_uses_rapidocr_when_tesseract_is_missing(self):
        with tempfile.TemporaryDirectory() as td:
            cache_path = Path(td) / "ocr_cache.json"
            image_path = Path(td) / "source.tga"
            image_path.write_bytes(b"fake image")
            image = ImageFile(
                "SampleOnly/source.tga",
                str(image_path),
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                "ui",
            )

            with patch("check_i18n_images.run_ocr", return_value="测试文字") as rapidocr:
                detector = ocr_text_detector_factory(cache_path)
                self.assertTrue(detector(image))
                rapidocr.assert_called_once_with(image)

    def test_rapidocr_ignores_low_confidence_preprocessed_false_positive(self):
        image = ImageFile(
            "source.tga",
            "source.tga",
            dt.datetime(2026, 1, 1, tzinfo=UTC),
            "ui",
        )
        ocr_results = [
            (None, None),
            ([[[[0, 0], [10, 0], [10, 10], [0, 10]], "战场", "0.65"]], None),
            (None, None),
            (None, None),
        ]

        class FakeRapidOCR:
            def __call__(self, _path):
                return ocr_results.pop(0)

        with patch("check_i18n_images._prepare_ocr_sources", return_value=(["original.tga", "enhanced.png"], [])), patch(
            "rapidocr_onnxruntime.RapidOCR",
            FakeRapidOCR,
        ):
            import check_i18n_images

            check_i18n_images._RAPIDOCR_ENGINE = None
            try:
                self.assertIsNone(check_i18n_images.run_rapidocr(image))
            finally:
                check_i18n_images._RAPIDOCR_ENGINE = None

    def test_rapidocr_uses_lower_preprocessed_threshold_when_original_has_text(self):
        image = ImageFile(
            "source.tga",
            "source.tga",
            dt.datetime(2026, 1, 1, tzinfo=UTC),
            "ui",
        )
        ocr_results = [
            ([[[[0, 0], [10, 0], [10, 10], [0, 10]], "加入", "0.66"]], None),
            ([[[[0, 0], [10, 0], [10, 10], [0, 10]], "加入丐帮", "0.743"]], None),
        ]

        class FakeRapidOCR:
            def __call__(self, _path):
                return ocr_results.pop(0)

        with patch("check_i18n_images._prepare_ocr_sources", return_value=(["original.tga", "enhanced.png"], [])), patch(
            "rapidocr_onnxruntime.RapidOCR",
            FakeRapidOCR,
        ):
            import check_i18n_images

            check_i18n_images._RAPIDOCR_ENGINE = None
            try:
                self.assertEqual(check_i18n_images.run_rapidocr(image), "加入丐帮")
            finally:
                check_i18n_images._RAPIDOCR_ENGINE = None

    def test_rapidocr_normalizes_common_game_ui_ocr_confusions(self):
        image = ImageFile(
            "source.tga",
            "source.tga",
            dt.datetime(2026, 1, 1, tzinfo=UTC),
            "ui",
        )
        ocr_results = [
            ([[[[0, 0], [10, 0], [10, 10], [0, 10]], "加入", "0.66"]], None),
            ([[[[0, 0], [10, 0], [10, 10], [0, 10]], "加入巧帮", "0.743"]], None),
        ]

        class FakeRapidOCR:
            def __call__(self, _path):
                return ocr_results.pop(0)

        with patch("check_i18n_images._prepare_ocr_sources", return_value=(["original.tga", "enhanced.png"], [])), patch(
            "rapidocr_onnxruntime.RapidOCR",
            FakeRapidOCR,
        ):
            import check_i18n_images

            check_i18n_images._RAPIDOCR_ENGINE = None
            try:
                self.assertEqual(check_i18n_images.run_rapidocr(image), "加入丐帮")
            finally:
                check_i18n_images._RAPIDOCR_ENGINE = None

    def test_rapidocr_engine_is_reused_between_calls(self):
        import check_i18n_images

        check_i18n_images._RAPIDOCR_ENGINE = None

        class FakeRapidOCR:
            created = 0

            def __init__(self):
                FakeRapidOCR.created += 1

            def __call__(self, _path):
                return [[[[0, 0], [10, 0], [10, 10], [0, 10]], "加入段氏", "0.80"]], None

        image = ImageFile(
            "source.tga",
            "source.tga",
            dt.datetime(2026, 1, 1, tzinfo=UTC),
            "ui",
        )

        with patch("check_i18n_images._prepare_ocr_sources", return_value=(["original.tga"], [])), patch(
            "rapidocr_onnxruntime.RapidOCR",
            FakeRapidOCR,
        ):
            try:
                self.assertEqual(check_i18n_images.run_rapidocr(image), "加入段氏")
                self.assertEqual(check_i18n_images.run_rapidocr(image), "加入段氏")
            finally:
                check_i18n_images._RAPIDOCR_ENGINE = None

        self.assertEqual(FakeRapidOCR.created, 1)

    def test_rapidocr_skips_preprocessing_when_original_result_is_strong(self):
        image = ImageFile(
            "source.tga",
            "source.tga",
            dt.datetime(2026, 1, 1, tzinfo=UTC),
            "ui",
        )
        calls = []

        class FakeRapidOCR:
            def __call__(self, path):
                calls.append(path)
                return [[[[0, 0], [10, 0], [10, 10], [0, 10]], "加入凌雪阁", "0.82"]], None

        with patch("check_i18n_images._prepare_ocr_sources", return_value=(["original.tga", "enhanced.png"], [])), patch(
            "rapidocr_onnxruntime.RapidOCR",
            FakeRapidOCR,
        ):
            import check_i18n_images

            check_i18n_images._RAPIDOCR_ENGINE = None
            try:
                self.assertEqual(check_i18n_images.run_rapidocr(image), "加入凌雪阁")
            finally:
                check_i18n_images._RAPIDOCR_ENGINE = None

        self.assertEqual(calls, ["original.tga"])

    def test_run_ocr_uses_filename_hint_for_chapter_titles(self):
        image = ImageFile(
            "Image/ChaptersTga/教主·陆危楼.tga",
            r"F:\client\ui\Image\ChaptersTga\教主·陆危楼.tga",
            dt.datetime(2026, 1, 1, tzinfo=UTC),
            "ui",
        )

        with patch("check_i18n_images.run_rapidocr", return_value="陆危楼"):
            self.assertEqual(__import__("check_i18n_images").run_ocr(image), "教主\n陆危楼")

    def test_run_ocr_does_not_use_filename_hint_for_non_text_chapter_assets(self):
        image = ImageFile(
            "Image/ChaptersTga/箭头-1.tga",
            r"F:\client\ui\Image\ChaptersTga\箭头-1.tga",
            dt.datetime(2026, 1, 1, tzinfo=UTC),
            "ui",
        )

        with patch("check_i18n_images.run_rapidocr", return_value=None):
            self.assertIsNone(__import__("check_i18n_images").run_ocr(image))

    def test_ocr_cache_records_detected_text(self):
        with tempfile.TemporaryDirectory() as td:
            cache_path = Path(td) / "ocr_cache.json"
            image_path = Path(td) / "source.tga"
            image_path.write_bytes(b"fake image")
            image = ImageFile(
                "SampleOnly/source.tga",
                str(image_path),
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                "ui",
            )

            with patch("check_i18n_images.run_ocr", return_value="閺傚洤鐡ч崘鍛啇"):
                detector = ocr_text_detector_factory(cache_path)
                self.assertTrue(detector(image))

            data = __import__("json").loads(cache_path.read_text(encoding="utf-8"))
            self.assertNotIn("has_test", data["SampleOnly/source.tga"])
            self.assertEqual(data["SampleOnly/source.tga"]["test_str"], "閺傚洤鐡ч崘鍛啇")

    def test_ocr_cache_refreshes_entries_when_file_content_changed(self):
        with tempfile.TemporaryDirectory() as td:
            cache_path = Path(td) / "ocr_cache.json"
            image_path = Path(td) / "source.tga"
            image_path.write_bytes(b"fake image")
            image = ImageFile(
                "SampleOnly/source.tga",
                str(image_path),
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                "ui",
            )
            cache_path.write_text(
                __import__("json").dumps(
                    {"SampleOnly/source.tga": {"md5": "stale-md5", "has_text": False}},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with patch("check_i18n_images.run_ocr", return_value="閺傚洤鐡ч崘鍛啇"):
                detector = ocr_text_detector_factory(cache_path)
                self.assertTrue(detector(image))

            data = __import__("json").loads(cache_path.read_text(encoding="utf-8"))
            self.assertNotIn("has_test", data["SampleOnly/source.tga"])
            self.assertEqual(data["SampleOnly/source.tga"]["test_str"], "閺傚洤鐡ч崘鍛啇")

    def test_ocr_cache_hit_uses_cached_has_text_without_test_str(self):
        with tempfile.TemporaryDirectory() as td:
            cache_path = Path(td) / "ocr_cache.json"
            image_path = Path(td) / "source.tga"
            image_path.write_bytes(b"fake image")
            image = ImageFile(
                "SampleOnly/source.tga",
                str(image_path),
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                "ui",
            )
            md5 = __import__("hashlib").md5(b"fake image").hexdigest()
            cache_path.write_text(
                __import__("json").dumps(
                    {"SampleOnly/source.tga": {"md5": md5, "has_text": False}},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with patch("check_i18n_images.run_ocr", side_effect=AssertionError("OCR should not run")):
                detector = ocr_text_detector_factory(cache_path)
                self.assertFalse(detector(image))

            data = __import__("json").loads(cache_path.read_text(encoding="utf-8"))
            self.assertEqual(data["SampleOnly/source.tga"]["has_text"], False)

    def test_ocr_cache_removes_legacy_has_test_on_cache_hit(self):
        with tempfile.TemporaryDirectory() as td:
            cache_path = Path(td) / "ocr_cache.json"
            image_path = Path(td) / "source.tga"
            image_path.write_bytes(b"fake image")
            image = ImageFile(
                "SampleOnly/source.tga",
                str(image_path),
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                "ui",
            )
            md5 = __import__("hashlib").md5(b"fake image").hexdigest()
            cache_path.write_text(
                __import__("json").dumps(
                    {
                        "SampleOnly/source.tga": {
                            "md5": md5,
                            "has_text": True,
                            "has_test": True,
                            "test_str": "閺傚洤鐡ч崘鍛啇",
                        }
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            detector = ocr_text_detector_factory(cache_path)
            self.assertTrue(detector(image))

            data = __import__("json").loads(cache_path.read_text(encoding="utf-8"))
            self.assertNotIn("has_test", data["SampleOnly/source.tga"])
            self.assertEqual(data["SampleOnly/source.tga"]["test_str"], "閺傚洤鐡ч崘鍛啇")

    def test_ocr_cache_hit_exposes_ignore_operation_for_same_md5(self):
        with tempfile.TemporaryDirectory() as td:
            cache_path = Path(td) / "ocr_cache.json"
            image_path = Path(td) / "source.tga"
            image_path.write_bytes(b"fake image")
            image = ImageFile(
                "SampleOnly/source.tga",
                str(image_path),
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                "ui",
            )
            md5 = __import__("hashlib").md5(b"fake image").hexdigest()
            cache_path.write_text(
                __import__("json").dumps(
                    {
                        "SampleOnly/source.tga": {
                            "md5": md5,
                            "has_text": True,
                            "test_str": cn(r"\u8d5b\u5b63\u5f00\u542f"),
                            "operation": "ignore",
                        }
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            detector = ocr_text_detector_factory(cache_path)
            findings, _stats = compare_category("ui", {}, {"SampleOnly/source.tga": image}, None, detector)

            self.assertEqual(findings[0].issue, "mainland_new_with_text")
            self.assertEqual(findings[0].operation, "ignore")

    def test_ocr_cache_preserves_ignore_operation_when_refreshing_same_md5(self):
        with tempfile.TemporaryDirectory() as td:
            cache_path = Path(td) / "ocr_cache.json"
            image_path = Path(td) / "source.tga"
            image_path.write_bytes(b"fake image")
            image = ImageFile(
                "SampleOnly/source.tga",
                str(image_path),
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                "ui",
            )
            md5 = __import__("hashlib").md5(b"fake image").hexdigest()
            cache_path.write_text(
                __import__("json").dumps(
                    {"SampleOnly/source.tga": {"md5": md5, "operation": "ignore"}},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with patch("check_i18n_images.run_ocr", return_value=cn(r"\u8d5b\u5b63\u5f00\u542f")):
                detector = ocr_text_detector_factory(cache_path)
                self.assertTrue(detector(image))

            data = __import__("json").loads(cache_path.read_text(encoding="utf-8"))
            self.assertEqual(data["SampleOnly/source.tga"]["operation"], "ignore")
            self.assertEqual(data["SampleOnly/source.tga"]["md5"], md5)
            self.assertTrue(data["SampleOnly/source.tga"]["has_text"])

    def test_update_ocr_cache_operation_writes_ignore_marker(self):
        with tempfile.TemporaryDirectory() as td:
            cache_path = Path(td) / "ocr_cache.json"
            update_ocr_cache_operation(
                cache_path,
                "SampleOnly/source.tga",
                "abc123",
                "ignore",
            )

            data = __import__("json").loads(cache_path.read_text(encoding="utf-8"))
            self.assertEqual(data["SampleOnly/source.tga"]["md5"], "abc123")
            self.assertEqual(data["SampleOnly/source.tga"]["operation"], "ignore")

    def test_html_report_uses_sqlite_cache_name_when_configured(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "report.html"
            write_html_report(
                out,
                [],
                i18n_count=0,
                mainland_count=0,
                normal_synced=0,
                new_no_text=0,
                ocr_cache_name=".ocr_cache.db",
            )

            content = out.read_text(encoding="utf-8")
            self.assertIn("const OCR_CACHE_FILE_NAME = '.ocr_cache.db';", content)
            self.assertIn("file://", content)
            self.assertNotIn("readOcrCache", content)
            self.assertNotIn("writeOcrCache", content)

    def test_serve_report_defaults_to_port_9080(self):
        self.assertEqual(serve_report.__defaults__[-1], 9080)

    def test_migrate_ocr_json_to_sqlite_preserves_text_and_operation(self):
        with tempfile.TemporaryDirectory() as td:
            json_path = Path(td) / "ocr_cache.json"
            db_path = Path(td) / "ocr_cache.db"
            json_path.write_text(
                __import__("json").dumps(
                    {
                        "SampleOnly/source.tga": {
                            "md5": "abc123",
                            "has_text": True,
                            "test_str": cn(r"\u8d5b\u5b63\u5f00\u542f"),
                            "operation": "ignore",
                        }
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            count = migrate_ocr_json_to_sqlite(json_path, db_path)

            self.assertEqual(count, 1)
            import sqlite3

            conn = sqlite3.connect(db_path)
            try:
                row = conn.execute(
                    "SELECT md5, has_text, has_cn, test_str, operation FROM ocr_cache WHERE relative_path=?",
                    ("SampleOnly/source.tga",),
                ).fetchone()
            finally:
                conn.close()
            self.assertEqual(row, ("abc123", 1, 1, cn(r"\u8d5b\u5b63\u5f00\u542f"), "ignore"))

    def test_migrate_ocr_json_to_sqlite_sets_has_cn_from_test_str(self):
        with tempfile.TemporaryDirectory() as td:
            json_path = Path(td) / "ocr_cache.json"
            db_path = Path(td) / "ocr_cache.db"
            json_path.write_text(
                __import__("json").dumps(
                    {
                        "SampleOnly/chinese.tga": {
                            "md5": "cn-md5",
                            "has_text": True,
                            "test_str": cn(r"\u8d5b\u5b63\u5f00\u542f"),
                        },
                        "SampleOnly/ascii.tga": {
                            "md5": "ascii-md5",
                            "has_text": True,
                            "test_str": "Season_2026 123",
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            migrate_ocr_json_to_sqlite(json_path, db_path)

            import sqlite3

            conn = sqlite3.connect(db_path)
            try:
                columns = [row[1] for row in conn.execute("PRAGMA table_info(ocr_cache)").fetchall()]
                rows = {
                    row[0]: (row[1], row[2])
                    for row in conn.execute("SELECT relative_path, has_text, has_cn FROM ocr_cache").fetchall()
                }
            finally:
                conn.close()
            self.assertIn("has_cn", columns)
            self.assertEqual(rows["SampleOnly/chinese.tga"], (1, 1))
            self.assertEqual(rows["SampleOnly/ascii.tga"], (1, 0))

    def test_sqlite_ocr_cache_hit_exposes_ignore_operation_for_same_md5(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "ocr_cache.db"
            image_path = Path(td) / "source.tga"
            image_path.write_bytes(b"fake image")
            image = ImageFile(
                "SampleOnly/source.tga",
                str(image_path),
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                "ui",
            )
            md5 = __import__("hashlib").md5(b"fake image").hexdigest()
            update_ocr_cache_operation_sqlite(db_path, "SampleOnly/source.tga", md5, "ignore")

            with patch("check_i18n_images.run_ocr", return_value=cn(r"\u8d5b\u5b63\u5f00\u542f")):
                detector = sqlite_ocr_text_detector_factory(db_path)
                findings, _stats = compare_category("ui", {}, {"SampleOnly/source.tga": image}, None, detector)

            self.assertEqual(findings[0].issue, "mainland_new_with_text")
            self.assertEqual(findings[0].operation, "ignore")
            self.assertEqual(findings[0].mainland_md5, md5)

    def test_sqlite_ocr_cache_hit_with_only_ascii_text_is_no_text(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "ocr_cache.db"
            image_path = Path(td) / "source.tga"
            image_path.write_bytes(b"fake image")
            image = ImageFile(
                "SampleOnly/source.tga",
                str(image_path),
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                "ui",
            )
            md5 = __import__("hashlib").md5(b"fake image").hexdigest()
            json_path = Path(td) / "ocr_cache.json"
            json_path.write_text(
                __import__("json").dumps(
                    {
                        "SampleOnly/source.tga": {
                            "md5": md5,
                            "has_text": True,
                            "test_str": "Season_2026 123",
                        }
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            migrate_ocr_json_to_sqlite(json_path, db_path)

            with patch("check_i18n_images.run_ocr", side_effect=AssertionError("OCR should not run")):
                detector = sqlite_ocr_text_detector_factory(db_path)
                findings, stats = compare_category("ui", {}, {"SampleOnly/source.tga": image}, None, detector)

            self.assertEqual(findings[0].issue, "mainland_new_no_text")
            self.assertEqual(stats["new_no_text"], 1)

    def test_sqlite_ocr_cache_hit_progress_reports_unchanged_file(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "ocr_cache.db"
            image_path = Path(td) / "source.tga"
            image_path.write_bytes(b"fake image")
            image = ImageFile(
                "SampleOnly/source.tga",
                str(image_path),
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                "ui",
            )
            md5 = __import__("hashlib").md5(b"fake image").hexdigest()
            json_path = Path(td) / "ocr_cache.json"
            json_path.write_text(
                __import__("json").dumps(
                    {"SampleOnly/source.tga": {"md5": md5, "has_text": False}},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            migrate_ocr_json_to_sqlite(json_path, db_path)

            stderr = io.StringIO()
            with patch("sys.stderr", stderr), patch(
                "check_i18n_images.run_ocr",
                side_effect=AssertionError("OCR should not run"),
            ):
                detector = sqlite_ocr_text_detector_factory(db_path)
                compare_category("ui", {}, {"SampleOnly/source.tga": image}, None, detector)

            output = stderr.getvalue()
            self.assertIn("文件名：source.tga", output)
            self.assertIn(f"md5:{md5}", output)
            self.assertIn("【文件未修改】", output)
            self.assertIn(f"路径：{image_path}", output)

    def test_sqlite_ocr_cache_does_not_reuse_ignore_when_md5_changes(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "ocr_cache.db"
            image_path = Path(td) / "source.tga"
            image_path.write_bytes(b"old image")
            old_md5 = __import__("hashlib").md5(b"old image").hexdigest()
            update_ocr_cache_operation_sqlite(db_path, "SampleOnly/source.tga", old_md5, "ignore")

            image_path.write_bytes(b"new image")
            new_md5 = __import__("hashlib").md5(b"new image").hexdigest()
            image = ImageFile(
                "SampleOnly/source.tga",
                str(image_path),
                dt.datetime(2026, 1, 1, tzinfo=UTC),
                "ui",
            )

            with patch("check_i18n_images.run_ocr", return_value=cn(r"\u8d5b\u5b63\u5f00\u542f")):
                detector = sqlite_ocr_text_detector_factory(db_path)
                findings, _stats = compare_category("ui", {}, {"SampleOnly/source.tga": image}, None, detector)

            self.assertEqual(findings[0].issue, "mainland_new_with_text")
            self.assertIsNone(findings[0].operation)
            self.assertEqual(findings[0].mainland_md5, new_md5)

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
            Finding("ui", "mainland_missing", "a.dds", "/i18n/a.dds", "", None, None, "missing")
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
                "闂勫棛澧楅弴瀛樻煀",
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
                "闂勫棛澧楅弴瀛樻煀",
            )
        ]
        ocr_returns = {"/ml/a.dds": cn(r"\u7b80\u4f53\u6587\u5b57"), "/i18n/a.dds": cn(r"\u7e41\u9ad4\u6587\u5b57")}
        checker = lambda m, i: ("ok", "")
        with patch(
            "check_i18n_images.run_ocr_from_path",
            side_effect=lambda path, cat="": ocr_returns.get(path),
        ):
            result = enrich_findings_with_translation(findings, checker)
        self.assertEqual(result[0].translation_status, "ok")
        self.assertEqual(result[0].mainland_ocr_text, cn(r"\u7b80\u4f53\u6587\u5b57"))
        self.assertEqual(result[0].i18n_ocr_text, cn(r"\u7e41\u9ad4\u6587\u5b57"))

    def test_enrich_new_with_text_has_no_i18n_ocr(self):
        """For mainland_new_with_text, i18n_path is empty so i18n_text is None -> missing."""
        findings = [
            Finding(
                "ui", "mainland_new_with_text", "b.dds", "", "/ml/b.dds",
                None,
                dt.datetime(2026, 1, 2, tzinfo=UTC),
                "new detail",
            )
        ]
        checker = lambda m, i: ("missing", cn(r"\u65e0\u7e41\u4f53")) if i is None else ("ok", "")
        with patch("check_i18n_images.run_ocr_from_path", return_value=cn(r"\u65b0\u589e\u4e2d\u6587")):
            result = enrich_findings_with_translation(findings, checker)
        self.assertEqual(result[0].translation_status, "missing")
        self.assertEqual(result[0].translation_note, cn(r"\u65e0\u7e41\u4f53"))

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
                        "闂勫棛澧楅弴瀛樻煀",
                        mainland_ocr_text="mainland",
                        i18n_ocr_text="i18n",
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
            self.assertIn(cn(r"\u7ffb\u8bd1\u72b6\u6001"), sheet)
            self.assertIn(cn(r"\u7ffb\u8bd1\u95ee\u9898\u8bf4\u660e"), sheet)

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
            self.assertIn("summary-table", content)
            self.assertIn(cn(r"\u62a5\u544a\u8be6\u60c5"), content)
            self.assertIn(cn(r"\u7591\u4f3c\u5e9f\u9664\u6587\u4ef6"), content)
            self.assertIn("summary-table", content)
            self.assertIn("sortTable", content)
            self.assertIn("filterTable", content)
            self.assertNotIn(cn(r"\u9646\u7248\u521b\u5efa\u65f6\u95f4"), content)
            self.assertIn(cn(r"\u4fee\u6539\u65f6\u95f4\u5f02\u5e38"), content)
            self.assertIn(cn(r"\u62a5\u544a\u8be6\u60c5"), content)
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

    def test_write_html_report_title_includes_project_name_and_run_date(self):
        fixed_now = dt.datetime(2026, 6, 8, 9, 30, tzinfo=dt.timezone(dt.timedelta(hours=8)))

        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "report.html"
            with patch("check_i18n_images.dt.datetime") as mock_datetime:
                mock_datetime.now.return_value = fixed_now
                mock_datetime.fromtimestamp.side_effect = dt.datetime.fromtimestamp
                mock_datetime.fromisoformat.side_effect = dt.datetime.fromisoformat
                write_html_report(out, [])

            content = out.read_text(encoding="utf-8")

        expected_title = "《剑网三》多语言图片检查汇总（2026.06.08）"
        self.assertIn(f"<title>{expected_title}</title>", content)
        self.assertIn(f"<h1>{expected_title}</h1>", content)

    def test_write_html_report_creates_png_placeholder_when_source_preview_fails(self):
        with tempfile.TemporaryDirectory() as td:
            img_path = Path(td) / "source.tga"
            img_path.write_bytes(b"not a real tga")
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
                ],
            )

            content = out.read_text(encoding="utf-8")
            asset = out.parent / "report_assets" / "img_1_i18n.tga.png"
            self.assertTrue(asset.exists())
            self.assertGreater(asset.stat().st_size, 0)
            self.assertEqual(asset.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            self.assertIn("report_assets/img_1_i18n.tga.png", content)
            self.assertNotIn(str(img_path), content)
            self.assertNotIn(img_path.resolve().as_uri(), content)

    def test_write_html_report_respects_max_image_px(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow is not installed")

        with tempfile.TemporaryDirectory() as td:
            img_path = Path(td) / "source.tga"
            Image.new("RGB", (100, 80), (255, 255, 255)).save(img_path)
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
                ],
                max_image_px=20,
            )

            asset = out.parent / "report_assets" / "img_1_i18n.tga.png"
            with Image.open(asset) as img:
                self.assertLessEqual(max(img.size), 20)

    def test_report_generation_requires_pillow_before_writing_images(self):
        with patch("check_i18n_images._is_pillow_available", return_value=False):
            with self.assertRaises(SystemExit) as ctx:
                _require_pillow_for_report(Path("report.html"))

        message = str(ctx.exception)
        self.assertIn("Pillow", message)
        self.assertIn("pip install Pillow", message)
        self.assertIn("report.html", message)

    def test_write_html_report_excludes_new_no_text_detail_rows_but_keeps_summary(self):
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
                        "SampleOnly/text.tga",
                        "",
                        str(img_path),
                        None,
                        dt.datetime(2026, 1, 2, tzinfo=UTC),
                        "text detail",
                        mainland_ocr_text=cn(r"\u5927\u5251\u7f51\u4e09"),
                        operation="ignore",
                    ),
                    Finding(
                        "ui",
                        "mainland_new_no_text",
                        "SampleOnly/plain.tga",
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
            self.assertNotIn("SampleOnly/plain.tga", content)
            self.assertIn("新增含字符图片", content)
            self.assertIn("新增带中文图片", content)
            self.assertNotIn(cn(r"\u65b0\u589e\u65e0\u6587\u5b57\u56fe\u7247"), content)
            self.assertNotIn(cn(r"\u65b0\u589e\u5e26\u6587\u5b57\u56fe\u7247"), content)
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
            self.assertNotIn('data-filter="category"', content)
            self.assertIn('<select data-filter-col="1" data-filter="issue" onchange="filterTable()">', content)
            self.assertIn('class="detail-tabs"', content)
            self.assertIn('data-tab-type="ui"', content)
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
                cn(r"\u95ee\u9898\u7c7b\u578b"),
                cn(r"\u76f8\u5bf9\u8def\u5f84"),
                cn(r"\u9646\u7248\u56fe\u7247"),
                cn(r"\u56fd\u9645\u7248\u56fe\u7247"),
                cn(r"\u9646\u7248\u4fee\u6539\u65f6\u95f4"),
                cn(r"\u56fd\u9645\u7248\u4fee\u6539\u65f6\u95f4"),
                cn(r"\u8bf4\u660e"),
                cn(r"\u64cd\u4f5c"),
            ]
            positions = [header_row.index(label) for label in expected_order]
            self.assertEqual(positions, sorted(positions))
            self.assertNotIn(f"<th onclick=\"sortTable(9)\">{cn(r'\u8bc6\u522b\u6587\u5b57')}", header_row)
            self.assertIn(cn(r"\u5df2\u5ffd\u7565"), content)
            self.assertIn("operationStatus", content)
            self.assertIn("ignoreFinding", content)
            self.assertNotIn("entry.operation = OPERATION_IGNORE", content)
            self.assertNotIn("readOcrCache", content)
            self.assertNotIn("writeOcrCache", content)
            self.assertNotIn("showOpenFilePicker", content)
            self.assertIn('"operation": "ignore"', content)
            self.assertNotIn(cn(r"\u9646\u7248\u521b\u5efa\u65f6\u95f4"), header_row)
            self.assertIn('"className": "mainland-new-with-text"', content)
            self.assertNotIn('"className": "mainland-new-no-text"', content)
            self.assertNotIn(f"<option>{cn(r'\u65b0\u589e\u65e0\u6587\u5b57\u56fe\u7247')}</option>", content)
            self.assertIn("const PAGE_SIZE = 50", content)
            self.assertIn("function renderPage(page)", content)
            self.assertIn("function gotoPage(page)", content)
            self.assertIn("function switchTab(type)", content)
            self.assertIn("filteredRows = allRows.filter", content)
            self.assertIn("row.pairType !== activeTabType", content)
            self.assertIn("<tbody></tbody>", content)
            self.assertIn('tr.mainland-new-with-text[title] { cursor:help; }', content)
            self.assertNotIn('tr.mainland-new-no-text[title] { cursor:help; }', content)
            self.assertIn("min-width:1180px", content)
            self.assertIn("border-collapse:separate", content)
            self.assertIn("border-spacing:0", content)
            self.assertIn(".filter-row th { top:40px", content)
            self.assertIn("height:40px", content)
            self.assertIn('type="date" data-date-col="5" data-date-bound="start"', content)
            self.assertIn('type="date" data-date-col="5" data-date-bound="end"', content)
            self.assertIn('type="date" data-date-col="6" data-date-bound="start"', content)
            self.assertIn('type="date" data-date-col="6" data-date-bound="end"', content)
            self.assertIn(cn(r"\u81f3"), content)
            self.assertIn("const FILTER_COLUMNS = [0, 1, 2, 7, 8]", content)
            self.assertIn("function parseDateOnly(value)", content)
            self.assertIn("function dateInRange(value, start, end)", content)
            self.assertIn("collectDateRanges()", content)

    def test_write_html_report_does_not_show_ignore_button_for_missing_files(self):
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
                        "SampleOnly/missing.tga",
                        str(img_path),
                        "",
                        dt.datetime(2026, 1, 1, tzinfo=UTC),
                        None,
                        "missing detail",
                    ),
                ],
            )

            content = out.read_text(encoding="utf-8")
            self.assertIn(cn(r"\u64cd\u4f5c"), content)
            self.assertIn('"className": "mainland-missing"', content)
            self.assertIn('"canIgnore": false', content)
            self.assertIn('"missing detail", ""]', content)
            self.assertNotIn('onclick=\\"ignoreFinding(1)\\"', content)
            self.assertNotIn('>忽略</button>', content)

    def test_write_html_report_does_not_show_ignore_button_for_changed_files(self):
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
                        "mainland_changed",
                        "SampleOnly/changed.tga",
                        str(img_path),
                        str(img_path),
                        dt.datetime(2026, 1, 1, tzinfo=UTC),
                        dt.datetime(2026, 1, 2, tzinfo=UTC),
                        "changed detail",
                    ),
                ],
            )

            content = out.read_text(encoding="utf-8")
            self.assertIn('"className": "mainland-changed"', content)
            self.assertIn('"canIgnore": false', content)
            self.assertIn('"changed detail", ""]', content)
            self.assertNotIn('onclick=\\"ignoreFinding(1)\\"', content)

    def test_write_html_report_groups_details_by_pair_type_tabs_without_category_column(self):
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
                        "UI",
                        "mainland_missing",
                        "ui/a.tga",
                        str(img_path),
                        "",
                        dt.datetime(2026, 1, 1, tzinfo=UTC),
                        None,
                        "missing",
                    ),
                    Finding(
                        "地图",
                        "mainland_changed",
                        "map/b.tga",
                        str(img_path),
                        str(img_path),
                        dt.datetime(2026, 1, 1, tzinfo=UTC),
                        dt.datetime(2026, 1, 2, tzinfo=UTC),
                        "changed",
                    ),
                ],
            )

            content = out.read_text(encoding="utf-8")

        self.assertIn('class="detail-tabs"', content)
        self.assertIn('data-tab-type="UI"', content)
        self.assertIn('data-tab-type="地图"', content)
        self.assertIn('"pairType": "UI"', content)
        self.assertIn('"pairType": "地图"', content)
        header_row_start = content.index(cn(r"\u5e8f\u53f7") + "<span")
        header_row_end = content.index("</tr>", header_row_start)
        header_row = content[header_row_start:header_row_end]
        self.assertNotIn(cn(r"\u7c7b\u522b"), header_row)
        self.assertNotIn('data-filter="category"', content)
        self.assertIn("let activeTabType =", content)
        self.assertIn("function switchTab(type)", content)
        self.assertIn("row.pairType === activeTabType", content)


if __name__ == "__main__":
    unittest.main()
