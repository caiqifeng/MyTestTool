#!/usr/bin/env python3
"""Migrate .ocr_cache.json to the SQLite OCR cache database."""

from __future__ import annotations

import argparse
from pathlib import Path

from check_i18n_images import OCR_CACHE_FILE, migrate_ocr_json_to_sqlite


DEFAULT_DB_FILE = ".ocr_cache.db"


def main() -> int:
    parser = argparse.ArgumentParser(description="迁移 .ocr_cache.json 到 SQLite OCR 缓存库。")
    parser.add_argument(
        "--json",
        default=OCR_CACHE_FILE,
        help=f"源 OCR JSON 缓存路径，默认 {OCR_CACHE_FILE}",
    )
    parser.add_argument(
        "--db",
        default=DEFAULT_DB_FILE,
        help=f"目标 SQLite 数据库路径，默认 {DEFAULT_DB_FILE}",
    )
    args = parser.parse_args()

    json_path = Path(args.json)
    db_path = Path(args.db)
    if not json_path.exists():
        raise SystemExit(f"源文件不存在: {json_path}")

    count = migrate_ocr_json_to_sqlite(json_path, db_path)
    print(f"迁移完成: {count} 条 -> {db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
