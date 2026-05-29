#!/usr/bin/env python3
"""Check i18n image differences between zh_TW and mainland client trees."""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import html
import json
import shutil
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable, Sequence
from xml.etree import ElementTree as ET

BEIJING_TZ = dt.timezone(dt.timedelta(hours=8))

IMAGE_EXTENSIONS = {".dds", ".tga"}
STATE_FILE = ".check_i18n_images_state"
OCR_CACHE_FILE = ".ocr_cache.json"
DEFAULT_THUMBNAIL_ISSUES = {
    "__has_detail__",
}
TEXT_REPORT_TITLE = "\u591a\u8bed\u8a00\u56fe\u7247\u68c0\u67e5\u6c47\u603b"
TEXT_RUN_RESULT = "\u672c\u8f6e\u6267\u884c\u7ed3\u679c"
TEXT_MISSING_ISSUE = "\u6587\u4ef6\u4e0d\u5b58\u5728\u95ee\u9898"
TEXT_CHANGED_ISSUE = "\u65f6\u95f4\u4e0d\u5bf9\u95ee\u9898"
TEXT_NEW_TEXT_ISSUE = "\u9646\u7248\u65b0\u589e\u542b\u6587\u5b57\u95ee\u9898"
TEXT_REPORT_DETAIL = "\u62a5\u544a\u8be6\u60c5"
TEXT_OTHER_ISSUE = "\u5176\u4ed6\u95ee\u9898"
TEXT_CATEGORY = "\u7c7b\u522b"
TEXT_ISSUE_TYPE = "\u95ee\u9898\u7c7b\u578b"
TEXT_RELATIVE_PATH = "\u76f8\u5bf9\u8def\u5f84"
TEXT_I18N_IMAGE = "\u56fd\u9645\u7248\u56fe\u7247"
TEXT_MAINLAND_IMAGE = "\u9646\u7248\u56fe\u7247"
TEXT_I18N_MODIFIED = "\u56fd\u9645\u7248\u4fee\u6539\u65f6\u95f4"
TEXT_MAINLAND_MODIFIED = "\u9646\u7248\u4fee\u6539\u65f6\u95f4"
TEXT_DETAIL = "\u8bf4\u660e"
TEXT_I18N = "\u56fd\u9645\u7248"
TEXT_MAINLAND = "\u9646\u7248"
TEXT_NONE = "\u65e0"
TEXT_ITEM = "\u9879"

@dataclass(frozen=True)
class ImageFile:
    relative_path: str
    full_path: str
    modified_at: dt.datetime
    category: str
    created_at: dt.datetime | None = None


@dataclass(frozen=True)
class Finding:
    category: str
    issue: str
    relative_path: str
    i18n_path: str
    mainland_path: str
    i18n_modified_at: dt.datetime | None
    mainland_modified_at: dt.datetime | None
    detail: str
    mainland_created_at: dt.datetime | None = None
    mainland_ocr_text: str | None = None
    i18n_ocr_text: str | None = None
    # ok / error / missing / no_cn_text
    translation_status: str | None = None
    translation_note: str | None = None


def normalize_rel(path: str) -> str:
    return str(PurePosixPath(path.replace("\\", "/"))).lstrip("/")


def compare_key(relative_path: str) -> str:
    return normalize_rel(relative_path).casefold()


def is_image(path: str) -> bool:
    return PurePosixPath(path).suffix.lower() in IMAGE_EXTENSIONS


def to_aware_utc(value: dt.datetime) -> dt.datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=dt.timezone.utc)
    return value.astimezone(dt.timezone.utc)


def compare_category(
    category: str,
    i18n_files: dict[str, ImageFile],
    mainland_files: dict[str, ImageFile],
    last_check_at: dt.datetime | None,
    text_detector: Callable[[ImageFile], bool],
) -> list[Finding]:
    findings: list[Finding] = []

    for rel, i18n_file in sorted(i18n_files.items()):
        mainland_file = mainland_files.get(rel)
        if mainland_file is None:
            findings.append(
                Finding(
                    category,
                    "mainland_missing",
                    i18n_file.relative_path,
                    i18n_file.full_path,
                    "",
                    i18n_file.modified_at,
                    None,
                    "陆版无对应文件，国际版文件可能已废弃",
                )
            )
            continue
        if to_aware_utc(i18n_file.modified_at) < to_aware_utc(mainland_file.modified_at):
            findings.append(
                Finding(
                    category,
                    "mainland_changed",
                    i18n_file.relative_path,
                    i18n_file.full_path,
                    mainland_file.full_path,
                    i18n_file.modified_at,
                    mainland_file.modified_at,
                    "陆版文件修改时间晚于国际版",
                )
            )

    since = to_aware_utc(last_check_at) if last_check_at else None
    for rel, mainland_file in sorted(mainland_files.items()):
        if rel in i18n_files:
            continue
        if since is not None and to_aware_utc(mainland_file.modified_at) <= since:
            continue
        if text_detector(mainland_file):
            findings.append(
                Finding(
                    category,
                    "mainland_new_with_text",
                    mainland_file.relative_path,
                    "",
                    mainland_file.full_path,
                    None,
                    mainland_file.modified_at,
                    "陆版新增图片且检测到文字",
                    mainland_created_at=mainland_file.created_at,
                )
            )
    return findings


def apply_max_file_sample(
    i18n_files: dict[str, ImageFile],
    mainland_files: dict[str, ImageFile],
    max_files: int | None,
) -> tuple[dict[str, ImageFile], dict[str, ImageFile]]:
    if max_files is None or max_files < 0:
        return i18n_files, mainland_files
    sampled_keys = set(sorted(set(i18n_files) | set(mainland_files))[:max_files])
    return (
        {key: value for key, value in sorted(i18n_files.items()) if key in sampled_keys},
        {key: value for key, value in sorted(mainland_files.items()) if key in sampled_keys},
    )


def scan_local(directory: str) -> dict[str, ImageFile]:
    base_path = Path(directory)
    result: dict[str, ImageFile] = {}
    if not base_path.exists():
        return result

    for file in base_path.rglob("*"):
        if not file.is_file():
            continue
        rel = normalize_rel(file.relative_to(base_path).as_posix())
        if not is_image(rel):
            continue
        stat = file.stat()
        modified_at = dt.datetime.fromtimestamp(stat.st_mtime, dt.timezone.utc)
        created_at = dt.datetime.fromtimestamp(stat.st_ctime, dt.timezone.utc)
        result[compare_key(rel)] = ImageFile(rel, str(file), modified_at, "", created_at)
    return result


def run_svn(args: Sequence[str]) -> bytes:
    proc = subprocess.run(
        ["svn", *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(stderr or f"svn {' '.join(args)} failed")
    return proc.stdout


def scan_svn(url: str) -> dict[str, ImageFile]:
    try:
        xml = run_svn(["list", "--xml", "-R", url])
    except RuntimeError as exc:
        print(f"WARN: 跳过无法读取的 SVN 路径: {url}: {exc}", file=sys.stderr)
        return {}

    doc = ET.fromstring(xml)
    result: dict[str, ImageFile] = {}
    for entry in doc.findall(".//entry"):
        if entry.get("kind") != "file":
            continue
        rel = normalize_rel(entry.findtext("name") or "")
        if not is_image(rel):
            continue
        date_text = entry.findtext("commit/date")
        if not date_text:
            continue
        modified_at = dt.datetime.fromisoformat(date_text.replace("Z", "+00:00"))
        result[compare_key(rel)] = ImageFile(rel, url.rstrip("/") + "/" + rel.strip("/"), modified_at, "")
    return result


def default_text_detector(image: ImageFile) -> bool:
    return False


def assume_text_detector(image: ImageFile) -> bool:
    return True


def _tesseract_exe() -> str:
    import shutil as _shutil
    found = _shutil.which("tesseract")
    if found:
        return found
    candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return "tesseract"


def _tesseract_env() -> dict[str, str]:
    env = os.environ.copy()
    # ensure TESSDATA_PREFIX points to a writable location with chi_sim/chi_tra
    if "TESSDATA_PREFIX" not in env:
        user_tessdata = str(Path.home() / "tessdata")
        if os.path.isdir(user_tessdata):
            env["TESSDATA_PREFIX"] = str(Path.home())
    return env


def _is_tesseract_available() -> bool:
    try:
        subprocess.run(
            [_tesseract_exe(), "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            env=_tesseract_env(),
        )
        return True
    except FileNotFoundError:
        return False


def run_ocr(image: ImageFile) -> str | None:
    """Run tesseract OCR on an image; return extracted text or None on failure."""
    source = image.full_path
    local_temp: str | None = None
    try:
        if source.lower().startswith(("http://", "https://")):
            suffix = PurePosixPath(source).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as fp:
                fp.write(run_svn(["cat", source]))
                local_temp = fp.name
                source = fp.name
        proc = subprocess.run(
            [_tesseract_exe(), source, "stdout", "-l", "chi_sim+chi_tra+eng"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
            env=_tesseract_env(),
        )
        text = proc.stdout.decode("utf-8", errors="ignore").strip()
        return text if text else None
    except Exception as exc:
        print(f"WARN: OCR 失败: {image.full_path}: {exc}", file=sys.stderr)
        return None
    finally:
        if local_temp:
            try:
                os.unlink(local_temp)
            except OSError:
                pass


def run_ocr_from_path(path: str, category: str = "") -> str | None:
    """Run OCR on a local path or SVN URL; return extracted text."""
    if not path:
        return None
    dummy = ImageFile(
        relative_path="",
        full_path=path,
        modified_at=dt.datetime.now(dt.timezone.utc),
        category=category,
    )
    return run_ocr(dummy)


def _file_md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_ocr_cache(cache_path: Path) -> dict[str, dict[str, object]]:
    if not cache_path.exists():
        return {}
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_ocr_cache(cache_path: Path, cache: dict[str, dict[str, object]]) -> None:
    cache_path.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


def ocr_text_detector_factory(
    cache_path: Path | None = None,
) -> Callable[[ImageFile], bool]:
    if not _is_tesseract_available():
        print(
            "WARN: 未找到 tesseract，新增图片文字检测将返回否；"
            "可使用 --assume-new-has-text 或安装 OCR 工具",
            file=sys.stderr,
        )
        return default_text_detector

    cache: dict[str, dict[str, object]] = {}
    if cache_path is not None:
        cache = load_ocr_cache(cache_path)

    def detect(image: ImageFile) -> bool:
        file_key = image.relative_path
        file_md5 = _file_md5(image.full_path)
        if file_key in cache:
            entry = cache[file_key]
            if isinstance(entry, dict) and entry.get("md5") == file_md5:
                return bool(entry.get("has_text", False))

        text = run_ocr(image)
        has_text = bool(re.search(r"[\w一-鿿]", text or ""))
        cache[file_key] = {"md5": file_md5, "has_text": has_text}
        if cache_path is not None:
            save_ocr_cache(cache_path, cache)
        return has_text

    return detect


_TRANSLATION_SYSTEM_PROMPT = (
    "你是游戏本地化翻译质量检查专家，"
    "专注于中文游戏《剑厑3》的简体→繁体转换。\n"
    "你需要判断：国际版（繁体中文）图片中的文字，"
    "是否是对应陆版（简体中文）文字的准确繁体翻译。\n\n"
    "判断标准：\n"
    "1. 繁体字形是否正确（不得残留简体字）\n"
    "2. 内容是否完整（无漏译）\n"
    "3. 语义是否准确（无错译、无语法错误）\n\n"
    "若图片为 UI 元素（按鈕、标签、提示），以游戏术语习惯为准。\n\n"
    "请严格按以下格式回复（不要有多余内容）：\n"
    "状态：OK\n"
    "或\n"
    "状态：ERROR\n"
    "说明：<具体问题，一句话>"
)


def make_translation_checker(
    api_key: str,
) -> Callable[[str, str | None], tuple[str, str]]:
    """
    Return a translation check function: check(mainland_text, i18n_text) -> (status, note).
    status values: "ok" | "error" | "missing"
    """
    try:
        import anthropic
    except ImportError:
        raise SystemExit(
            "ERROR: 翻译检查需要 anthropic 库，请先执行：pip install anthropic"
        )

    client = anthropic.Anthropic(api_key=api_key)

    def check(mainland_text: str, i18n_text: str | None) -> tuple[str, str]:
        if not i18n_text or not i18n_text.strip():
            return "missing", "国际版图片未识别到文字，可能缺少翻译"

        try:
            response = client.messages.create(
                model="claude-opus-4-7",
                max_tokens=300,
                system=[
                    {
                        "type": "text",
                        "text": _TRANSLATION_SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"陆版文字：\n{mainland_text}\n\n"
                            f"国际版文字：\n{i18n_text}"
                        ),
                    }
                ],
            )
            reply = response.content[0].text.strip()
        except Exception as exc:
            print(f"WARN: Claude API 调用失败: {exc}", file=sys.stderr)
            return "error", f"API 调用失败: {exc}"

        if "状态：OK" in reply or "状态:OK" in reply:
            return "ok", ""
        note = ""
        for line in reply.splitlines():
            stripped = line.strip()
            if stripped.startswith("说明：") or stripped.startswith("说明:"):
                note = stripped.split("：", 1)[-1].split(":", 1)[-1].strip()
                break
        return "error", note or reply

    return check


def enrich_findings_with_translation(
    findings: list[Finding],
    translation_checker: Callable[[str, str | None], tuple[str, str]],
) -> list[Finding]:
    """
    For mainland_changed / mainland_new_with_text findings, run OCR on both images
    and call translation_checker to assess translation quality.
    Returns a new list; original findings are not mutated.
    """
    NEEDS_CHECK = {"mainland_changed", "mainland_new_with_text"}
    result: list[Finding] = []
    for f in findings:
        if f.issue not in NEEDS_CHECK:
            result.append(f)
            continue

        mainland_text = run_ocr_from_path(f.mainland_path, f.category)
        if not mainland_text or not re.search(r"[一-鿿]", mainland_text):
            result.append(dataclasses.replace(f, translation_status="no_cn_text"))
            continue

        i18n_text = run_ocr_from_path(f.i18n_path, f.category) if f.i18n_path else None
        status, note = translation_checker(mainland_text, i18n_text)
        result.append(
            dataclasses.replace(
                f,
                mainland_ocr_text=mainland_text,
                i18n_ocr_text=i18n_text,
                translation_status=status,
                translation_note=note,
            )
        )
    return result


def load_last_check(path: Path) -> dt.datetime | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return None
    return dt.datetime.fromisoformat(text.replace("Z", "+00:00"))


def save_last_check(path: Path, value: dt.datetime) -> None:
    path.write_text(value.astimezone(dt.timezone.utc).isoformat(), encoding="utf-8")


def xlsx_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, dt.datetime):
        value = value.astimezone(BEIJING_TZ).strftime("%Y-%m-%d %H:%M:%S")
    return html.escape(str(value), quote=True)


def cell_name(col_index: int, row_index: int) -> str:
    col = ""
    n = col_index
    while n:
        n, rem = divmod(n - 1, 26)
        col = chr(65 + rem) + col
    return f"{col}{row_index}"


def write_xlsx(
    path: Path,
    findings: Sequence[Finding],
    thumbnail_limit: int | None = None,
    thumbnail_issues: set[str] | None = None,
    no_thumbnail_resize: bool = False,
    max_image_px: int | None = None,
) -> None:
    if thumbnail_issues is None:
        thumbnail_issues = DEFAULT_THUMBNAIL_ISSUES
    try:
        write_xlsx_with_openpyxl(
            path,
            findings,
            thumbnail_limit,
            thumbnail_issues,
            no_thumbnail_resize,
            max_image_px,
        )
        return
    except ImportError:
        pass
    except Exception as exc:
        print(f"WARN: 带缩略图 Excel 输出失败，降级为纯文本 xlsx: {exc}", file=sys.stderr)

    rows: list[list[object]] = [
        [
            "类别",
            "问题类型",
            "相对路径",
            "国际版路径",
            "陆版路径",
            "国际版缩略图",
            "陆版缩略图",
            "国际版修改时间",
            "陆版修改时间",
            "说明",
            "陆版识别文字",
            "国际版识别文字",
            "翻译状态",
            "翻译问题说明",
        ]
    ]
    for finding in findings:
        rows.append(
            [
                finding.category,
                finding.issue,
                finding.relative_path,
                finding.i18n_path,
                finding.mainland_path,
                "",
                "",
                finding.i18n_modified_at,
                finding.mainland_modified_at,
                finding.detail,
                finding.mainland_ocr_text,
                finding.i18n_ocr_text,
                finding.translation_status,
                finding.translation_note,
            ]
        )

    sheet_rows: list[str] = []
    for row_index, row in enumerate(rows, 1):
        cells = []
        for col_index, value in enumerate(row, 1):
            ref = cell_name(col_index, row_index)
            cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{xlsx_text(value)}</t></is></c>')
        sheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(sheet_rows)}</sheetData></worksheet>'
    )
    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="检查结果" sheetId="1" r:id="rId1"/></sheets></workbook>'
    )
    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/></Relationships>'
    )
    wb_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/></Relationships>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        "</Types>"
    )

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels_xml)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", wb_rels_xml)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def write_xlsx_with_openpyxl(
    path: Path,
    findings: Sequence[Finding],
    thumbnail_limit: int | None = None,
    thumbnail_issues: set[str] | None = None,
    no_thumbnail_resize: bool = False,
    max_image_px: int | None = None,
) -> None:
    if thumbnail_issues is None:
        thumbnail_issues = DEFAULT_THUMBNAIL_ISSUES
    if no_thumbnail_resize:
        box: tuple[int, int] | None = None
    elif max_image_px is not None and max_image_px > 0:
        box = (max_image_px, max_image_px)
    else:
        box = (96, 72)
    dynamic_row_height = no_thumbnail_resize or (
        max_image_px is not None and max_image_px > 0
    )
    from openpyxl import Workbook
    from openpyxl.drawing.image import Image as XlsxImage
    from openpyxl.styles import Alignment, Font
    from openpyxl.utils import get_column_letter
    from PIL import Image as PILImage

    wb = Workbook()
    ws = wb.active
    ws.title = "检查结果"
    headers = [
        "类别",
        "问题类型",
        "相对路径",
        "国际版路径",
        "陆版路径",
        "国际版缩略图",
        "陆版缩略图",
        "国际版修改时间",
        "陆版修改时间",
        "说明",
        "陆版识别文字",
        "国际版识别文字",
        "翻译状态",
        "翻译问题说明",
    ]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")

    thumb_dir = path.parent / f".{path.stem}_thumbs"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    temp_files: list[Path] = []

    inserted_thumbnails = 0
    max_col_px = {"F": 0, "G": 0}
    try:
        for row_index, finding in enumerate(findings, 2):
            ws.append(
                [
                    finding.category,
                    finding.issue,
                    finding.relative_path,
                    finding.i18n_path,
                    finding.mainland_path,
                    "",
                    "",
                    format_dt(finding.i18n_modified_at),
                    format_dt(finding.mainland_modified_at),
                    finding.detail,
                    finding.mainland_ocr_text or "",
                    finding.i18n_ocr_text or "",
                    finding.translation_status or "",
                    finding.translation_note or "",
                ]
            )
            ws.row_dimensions[row_index].height = 72
            thumbnail_keys = {finding.issue}
            if finding.detail:
                thumbnail_keys.add("__has_detail__")
            if finding.translation_status:
                thumbnail_keys.add(f"translation_{finding.translation_status}")
            should_embed = bool(thumbnail_keys & thumbnail_issues)
            under_limit = thumbnail_limit is None or inserted_thumbnails < thumbnail_limit
            max_px_h = 0
            if should_embed and under_limit:
                inserted, px_w, px_h = add_thumbnail(
                    ws,
                    PILImage,
                    XlsxImage,
                    finding.i18n_path,
                    f"F{row_index}",
                    thumb_dir,
                    temp_files,
                    no_resize=no_thumbnail_resize,
                    max_box=box,
                )
                inserted_thumbnails += inserted
                max_px_h = max(max_px_h, px_h)
                max_col_px["F"] = max(max_col_px["F"], px_w)
                if thumbnail_limit is None or inserted_thumbnails < thumbnail_limit:
                    inserted, px_w, px_h = add_thumbnail(
                        ws,
                        PILImage,
                        XlsxImage,
                        finding.mainland_path,
                        f"G{row_index}",
                        thumb_dir,
                        temp_files,
                        no_resize=no_thumbnail_resize,
                        max_box=box,
                    )
                    inserted_thumbnails += inserted
                    max_px_h = max(max_px_h, px_h)
                    max_col_px["G"] = max(max_col_px["G"], px_w)
            if dynamic_row_height and max_px_h > 0:
                ws.row_dimensions[row_index].height = max(72, max_px_h * 0.75)

        widths = [14, 22, 48, 70, 70, 14, 14, 24, 24, 36, 40, 40, 14, 50]
        if dynamic_row_height:
            for col_letter, idx in (("F", 5), ("G", 6)):
                if max_col_px[col_letter] > 0:
                    widths[idx] = max(widths[idx], max_col_px[col_letter] / 7 + 2)
        for idx, width in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(idx)].width = width
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for row in ws.iter_rows():
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=True)
        wb.save(path)
    finally:
        for file in temp_files:
            try:
                file.unlink()
            except OSError:
                pass
        try:
            thumb_dir.rmdir()
        except OSError:
            pass


def format_dt(value: dt.datetime | None) -> str:
    if value is None:
        return ""
    return value.astimezone(BEIJING_TZ).strftime("%Y-%m-%d %H:%M:%S")


def issue_title(issue: str) -> str:
    return {
        "mainland_missing": TEXT_MISSING_ISSUE,
        "mainland_changed": TEXT_CHANGED_ISSUE,
        "mainland_new_with_text": TEXT_NEW_TEXT_ISSUE,
    }.get(issue, issue)


def file_uri(path: str) -> str:
    if not path:
        return ""
    if path.lower().startswith(("http://", "https://")):
        return path
    return Path(path).resolve().as_uri()


def make_html_image_asset(source: str, assets_dir: Path, index: int, side: str) -> str:
    local = local_image_path(source)
    if local is None:
        return file_uri(source)
    assets_dir.mkdir(parents=True, exist_ok=True)
    out = assets_dir / f"img_{index}_{side}.png"
    try:
        from PIL import Image as PILImage

        with PILImage.open(local) as img:
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")
            img.save(out)
        return f"{assets_dir.name}/{out.name}"
    except Exception:
        try:
            copy_target = assets_dir / f"img_{index}_{side}{local.suffix.lower()}"
            shutil.copy2(local, copy_target)
            return f"{assets_dir.name}/{copy_target.name}"
        except Exception:
            return file_uri(source)


def html_img(asset: str, label: str) -> str:
    if not asset:
        return ""
    escaped_asset = html.escape(asset, quote=True)
    escaped_label = html.escape(label, quote=True)
    return (
        f'<button class="thumb-button" type="button" onclick="openPreview(this)" '
        f'data-full-src="{escaped_asset}" data-title="{escaped_label}">'
        f'<img src="{escaped_asset}" alt="{escaped_label}" loading="lazy"></button>'
    )


def write_html_report(
    path: Path,
    findings: Sequence[Finding],
    i18n_count: int = 0,
    mainland_count: int = 0,
) -> None:
    assets_dir = path.parent / f"{path.stem}_assets"
    if assets_dir.exists():
        shutil.rmtree(assets_dir)
    missing = [f for f in findings if f.issue == "mainland_missing"]
    changed = [f for f in findings if f.issue == "mainland_changed"]
    new_with_text = [f for f in findings if f.issue == "mainland_new_with_text"]
    others = [f for f in findings if f.issue not in {"mainland_missing", "mainland_changed", "mainland_new_with_text"}]

    issue_type_labels = {
        "mainland_missing": "国际版有、陆版无（可能已废弃）",
        "mainland_changed": "陆版修改时间晚于国际版（需更新翻译）",
        "mainland_new_with_text": "陆版新增含文字图片（缺少国际版对应翻译）",
    }

    def issue_summary_card(issue_key: str, items: list[Finding], index: int) -> str:
        label = issue_type_labels.get(issue_key, issue_key)
        return (
            f"<section><h3>{index}、{issue_title(issue_key)}：{len(items)} {TEXT_ITEM}</h3>"
            f"<p>{label}</p>"
            f"<ul>{_summary_items(items)}</ul></section>"
        )

    summary_cards: list[str] = []
    card_index = 0
    if missing:
        card_index += 1
        summary_cards.append(issue_summary_card("mainland_missing", missing, card_index))
    if changed:
        card_index += 1
        summary_cards.append(issue_summary_card("mainland_changed", changed, card_index))
    if new_with_text:
        card_index += 1
        summary_cards.append(issue_summary_card("mainland_new_with_text", new_with_text, card_index))
    if others:
        card_index += 1
        summary_cards.append(
            f"<section><h3>{card_index}、{TEXT_OTHER_ISSUE}：{len(others)} {TEXT_ITEM}</h3>"
            f"<ul>{_summary_items(others)}</ul></section>"
        )

    rows = []
    for index, finding in enumerate(findings, 1):
        i18n_asset = make_html_image_asset(finding.i18n_path, assets_dir, index, "i18n")
        mainland_asset = make_html_image_asset(finding.mainland_path, assets_dir, index, "mainland")
        rows.append(
            "<tr>"
            f"<td>{html.escape(finding.category)}</td>"
            f"<td>{html.escape(issue_title(finding.issue))}</td>"
            f"<td class=\"path\">{html.escape(finding.relative_path)}</td>"
            f"<td>{html_img(i18n_asset, TEXT_I18N + ' ' + finding.relative_path)}</td>"
            f"<td>{html_img(mainland_asset, TEXT_MAINLAND + ' ' + finding.relative_path)}</td>"
            f"<td>{html.escape(format_dt(finding.i18n_modified_at))}</td>"
            f"<td>{html.escape(format_dt(finding.mainland_modified_at))}</td>"
            f"<td>{html.escape(format_dt(finding.mainland_created_at))}</td>"
            f"<td>{html.escape(finding.detail)}</td>"
            "</tr>"
        )

    total_abnormal = len(findings)
    summary_table = _build_summary_table(i18n_count, mainland_count, total_abnormal, missing, changed, new_with_text, others)
    doc = _html_template(summary_table, summary_cards, rows)
    path.write_text(doc, encoding="utf-8")


def _summary_items(items: Sequence[Finding]) -> str:
    if not items:
        return f"<li>{TEXT_NONE}</li>"
    return "".join(
        f"<li>{html.escape(f.relative_path)} - {html.escape(f.detail)}</li>"
        for f in items
    )


def _build_summary_table(
    i18n_count: int,
    mainland_count: int,
    total_abnormal: int,
    missing: list[Finding],
    changed: list[Finding],
    new_with_text: list[Finding],
    others: list[Finding],
) -> str:
    rows = [
        ("国际版图片", f"{i18n_count} 张"),
        ("陆版图片", f"{mainland_count} 张"),
    ]
    tbody1 = "".join(
        f"<tr><td>{r[0]}</td><td>{r[1]}</td></tr>" for r in rows
    )
    table1 = (
        '<table class="summary-table"><thead><tr><th>指标</th><th>数量</th></tr></thead>'
        f"<tbody>{tbody1}</tbody></table>"
    )

    abnormal_rows: list[tuple[str, str, str]] = []
    if missing:
        abnormal_rows.append(("文件不存在问题", f"{len(missing)} 张", "国际版有、陆版无（可能已废弃）"))
    if changed:
        abnormal_rows.append(("时间不对问题", f"{len(changed)} 张", "陆版修改时间晚于国际版（需更新翻译）"))
    if new_with_text:
        abnormal_rows.append(("新增含文字图片", f"{len(new_with_text)} 张", "陆版新增含文字图片（缺少国际版对应翻译）"))
    for f in others:
        abnormal_rows.append((issue_title(f.issue), "—", f.detail))

    tbody2 = "".join(
        f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td></tr>" for r in abnormal_rows
    )
    table2 = (
        '<table class="summary-table"><thead><tr><th>问题类型</th><th>数量</th><th>说明</th></tr></thead>'
        f"<tbody>{tbody2}</tbody></table>"
    )

    return f"""
    <div class="overview">
    <p><strong>一、共检查图片</strong></p>
    {table1}
    <p style="margin-top:18px;"><strong>二、异常图片：共 <span class="abnormal">{total_abnormal}</span> 张</strong></p>
    {table2}
    </div>"""


def _html_template(summary_table: str, summary_cards: str, rows: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{TEXT_REPORT_TITLE}</title>
<style>
body {{ margin: 0; font-family: "Microsoft YaHei", Arial, sans-serif; color: #1f2933; background: #f7f8fa; }}
main {{ max-width: 1560px; margin: 0 auto; padding: 28px; }}
h1 {{ margin: 0 0 20px; font-size: 28px; }}
h2 {{ margin: 28px 0 12px; font-size: 20px; }}
.overview {{ background: #fff; border: 1px solid #d9dee7; border-radius: 6px; padding: 16px 20px; margin-bottom: 20px; }}
.overview p {{ margin: 6px 0; font-size: 15px; line-height: 1.8; }}
.overview .abnormal {{ font-weight: bold; color: #d93025; }}
.summary-table {{ width: 100%; border-collapse: collapse; margin: 8px 0; }}
.summary-table th, .summary-table td {{ border: 1px solid #d9dee7; padding: 8px 12px; font-size: 14px; text-align: left; }}
.summary-table th {{ background: #eef2f7; font-weight: bold; }}
.summary {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap: 16px; }}
.summary section {{ background: #fff; border: 1px solid #d9dee7; border-radius: 6px; padding: 16px; }}
.summary h3 {{ margin: 0 0 6px; font-size: 16px; }}
.summary p {{ margin: 0 0 8px; color: #5f6368; font-size: 13px; }}
.summary ul {{ margin: 0; padding-left: 20px; max-height: 260px; overflow: auto; font-size: 13px; }}
.filter-bar {{ display: flex; gap: 6px; margin-bottom: 8px; flex-wrap: wrap; }}
.filter-bar input {{ padding: 4px 8px; border: 1px solid #c8d0dc; border-radius: 3px; font-size: 12px; width: 100%; box-sizing: border-box; }}
.table-wrap {{ overflow: auto; background: #fff; border: 1px solid #d9dee7; border-radius: 6px; }}
table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
th, td {{ border-bottom: 1px solid #e5e9f0; padding: 10px; vertical-align: top; font-size: 13px; }}
th {{ position: sticky; top: 0; background: #eef2f7; text-align: left; z-index: 1; cursor: pointer; user-select: none; white-space: nowrap; }}
th:hover {{ background: #d9dee7; }}
th .sort-icon {{ margin-left: 4px; font-size: 11px; color: #999; }}
th.sorted-asc .sort-icon::after {{ content: " ▲"; color: #1a73e8; }}
th.sorted-desc .sort-icon::after {{ content: " ▼"; color: #1a73e8; }}
.path {{ word-break: break-all; }}
.thumb-button {{ width: 180px; height: 120px; padding: 0; border: 1px solid #c8d0dc; background: #f9fafb; cursor: zoom-in; display: inline-flex; align-items: center; justify-content: center; }}
.thumb-button img {{ max-width: 178px; max-height: 118px; object-fit: contain; }}
.overlay {{ position: fixed; inset: 0; background: rgba(15, 23, 42, .82); display: none; align-items: center; justify-content: center; padding: 32px; z-index: 20; }}
.overlay.open {{ display: flex; }}
.preview {{ max-width: 96vw; max-height: 92vh; background: #fff; border-radius: 6px; padding: 12px; }}
.preview img {{ max-width: 92vw; max-height: 82vh; object-fit: contain; display: block; }}
.preview-title {{ margin: 0 0 8px; font-size: 14px; color: #334155; word-break: break-all; }}
.no-results {{ text-align: center; padding: 40px; color: #999; font-size: 15px; }}
</style>
</head>
<body>
<main>
<h1>{TEXT_REPORT_TITLE}</h1>
{summary_table}
<h2>{TEXT_REPORT_DETAIL}</h2>
<div class="table-wrap">
<table id="detailTable">
<thead>
<tr>
<th onclick="sortTable(0)" class="sorted-asc">类别<span class="sort-icon"></span></th>
<th onclick="sortTable(1)">问题类型<span class="sort-icon"></span></th>
<th onclick="sortTable(2)">相对路径<span class="sort-icon"></span></th>
<th>国际版图片</th>
<th>陆版图片</th>
<th onclick="sortTable(5)">国际版修改时间<span class="sort-icon"></span></th>
<th onclick="sortTable(6)">陆版修改时间<span class="sort-icon"></span></th>
<th onclick="sortTable(7)">陆版创建时间<span class="sort-icon"></span></th>
<th onclick="sortTable(8)">说明<span class="sort-icon"></span></th>
</tr>
<tr class="filter-row">
<th><input type="text" oninput="filterTable()" placeholder="筛选..."></th>
<th><input type="text" oninput="filterTable()" placeholder="筛选..."></th>
<th><input type="text" oninput="filterTable()" placeholder="筛选..."></th>
<th></th>
<th></th>
<th><input type="text" oninput="filterTable()" placeholder="筛选..."></th>
<th><input type="text" oninput="filterTable()" placeholder="筛选..."></th>
<th><input type="text" oninput="filterTable()" placeholder="筛选..."></th>
<th><input type="text" oninput="filterTable()" placeholder="筛选..."></th>
</tr>
</thead>
<tbody>
{''.join(rows)}
</tbody>
</table>
<div class="no-results" id="noResults" style="display:none">没有匹配的结果</div>
</div>
</main>
<div id="overlay" class="overlay" onclick="closePreview()"><div class="preview" onclick="event.stopPropagation()"><p id="previewTitle" class="preview-title"></p><img id="previewImage" alt=""></div></div>
<script>
let sortCol = 0;
let sortAsc = false;

function sortTable(col) {{
  const table = document.getElementById('detailTable');
  const tbody = table.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const ths = table.querySelectorAll('thead tr:first-child th');
  ths.forEach((th, i) => {{ th.classList.remove('sorted-asc', 'sorted-desc'); if (i === col) th.classList.add(sortCol === col && sortAsc ? 'sorted-asc' : (sortCol === col ? 'sorted-desc' : 'sorted-asc')); }});
  if (sortCol === col) {{ sortAsc = !sortAsc; }} else {{ sortCol = col; sortAsc = true; }}
  rows.sort((a, b) => {{
    let va = (a.cells[col]?.textContent || '').trim().toLowerCase();
    let vb = (b.cells[col]?.textContent || '').trim().toLowerCase();
    let na = parseFloat(va), nb = parseFloat(vb);
    if (!isNaN(na) && !isNaN(nb)) {{ va = na; vb = nb; }}
    if (va < vb) return sortAsc ? -1 : 1;
    if (va > vb) return sortAsc ? 1 : -1;
    return 0;
  }});
  rows.forEach(r => tbody.appendChild(r));
  updateFilterState();
}}

function filterTable() {{
  const table = document.getElementById('detailTable');
  const tbody = table.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const inputs = table.querySelectorAll('.filter-row input');
  const filters = Array.from(inputs).map(inp => inp.value.trim().toLowerCase());
  let visibleCount = 0;
  rows.forEach(row => {{
    let show = true;
    for (let i = 0; i < filters.length; i++) {{
      if (filters[i] && !(row.cells[i]?.textContent || '').toLowerCase().includes(filters[i])) {{
        show = false; break;
      }}
    }}
    row.style.display = show ? '' : 'none';
    if (show) visibleCount++;
  }});
  document.getElementById('noResults').style.display = visibleCount === 0 ? '' : 'none';
}}

function updateFilterState() {{
  filterTable();
}}

function openPreview(button) {{
  const overlay = document.getElementById('overlay');
  document.getElementById('previewImage').src = button.dataset.fullSrc;
  document.getElementById('previewTitle').textContent = button.dataset.title || '';
  overlay.classList.add('open');
}}
function closePreview() {{
  document.getElementById('overlay').classList.remove('open');
  document.getElementById('previewImage').src = '';
}}
document.addEventListener('keydown', function(event) {{
  if (event.key === 'Escape') closePreview();
}});
</script>
</body>
</html>
"""


def add_thumbnail(
    ws,
    pil_image,
    xlsx_image,
    source: str,
    cell: str,
    thumb_dir: Path,
    temp_files: list[Path],
    no_resize: bool = False,
    max_box: tuple[int, int] | None = (96, 72),
) -> tuple[int, int, int]:
    local = local_image_path(source)
    if local is None:
        return 0, 0, 0
    try:
        with pil_image.open(local) as img:
            if not no_resize and max_box is not None:
                img.thumbnail(max_box)
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")
            thumb_path = thumb_dir / f"thumb_{cell}.png"
            img.save(thumb_path)
            out_w, out_h = img.size
        temp_files.append(thumb_path)
        drawing = xlsx_image(str(thumb_path))
        drawing.width = out_w
        drawing.height = out_h
        ws.add_image(drawing, cell)
        return 1, out_w, out_h
    except Exception as exc:
        if no_resize:
            label = "原图"
        elif max_box and max_box != (96, 72):
            label = f"{max(max_box)}px 限制图"
        else:
            label = "缩略图"
        print(f"WARN: 无法生成{label}，已保留路径文本: {source}: {exc}", file=sys.stderr)
        return 0, 0


def local_image_path(source: str) -> Path | None:
    if not source or source.lower().startswith(("http://", "https://")):
        return None
    path = Path(source)
    if path.exists() and path.is_file():
        return path
    return None


def parse_dt(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def _load_config_pairs(config_path: str) -> list[dict[str, str]]:
    data = json.loads(Path(config_path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        pairs = data
    elif isinstance(data, dict) and "pairs" in data:
        pairs = data["pairs"]
    else:
        raise SystemExit(f"ERROR: 配置文件格式错误，需要 [{{\"name\":..., \"i18n\":..., \"mainland\":...}}, ...]")
    for p in pairs:
        if "i18n" not in p or "mainland" not in p:
            raise SystemExit(f"ERROR: 配置项缺少 i18n 或 mainland 字段: {p}")
    return pairs


def collect_findings(args: argparse.Namespace) -> tuple[list[Finding], dict[str, int]]:
    last_check_at = args.since or load_last_check(Path(args.state_file))
    if args.assume_new_has_text:
        detector = assume_text_detector
    elif not args.no_ocr:
        detector = ocr_text_detector_factory(cache_path=Path(args.ocr_cache_file))
    else:
        detector = default_text_detector

    if args.config:
        pairs = _load_config_pairs(args.config)
    else:
        pairs = [{"name": "", "i18n": args.i18n, "mainland": args.mainland}]

    all_findings: list[Finding] = []
    total_i18n = 0
    total_mainland = 0

    for pair in pairs:
        is_remote = pair["i18n"].lower().startswith(("http://", "https://"))
        scanner = scan_svn if is_remote else scan_local
        i18n_files = scanner(pair["i18n"])
        mainland_files = scanner(pair["mainland"])
        total_i18n += len(i18n_files)
        total_mainland += len(mainland_files)
        i18n_files, mainland_files = apply_max_file_sample(
            i18n_files, mainland_files, args.max_files,
        )
        all_findings.extend(
            compare_category(pair.get("name", ""), i18n_files, mainland_files, last_check_at, detector)
        )

    if getattr(args, "enable_translation_check", False):
        api_key = os.environ.get("ANTHROPIC_API_KEY") or getattr(args, "anthropic_api_key", None)
        if not api_key:
            raise SystemExit(
                "ERROR: --enable-translation-check 需要 API Key，"
                "请设置环境变量 ANTHROPIC_API_KEY "
                "或使用 --anthropic-api-key 传入"
            )
        if not _is_tesseract_available():
            raise SystemExit(
                "ERROR: --enable-translation-check 需要 tesseract OCR，请先安装 tesseract"
            )
        checker = make_translation_checker(api_key)
        all_findings = enrich_findings_with_translation(all_findings, checker)

    return all_findings, {"i18n_count": total_i18n, "mainland_count": total_mainland}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="检查国际版/陆版图片差异，并输出 Excel/HTML。")
    parser.add_argument("--config", default=None, help="JSON 配置文件路径，定义多组检查目录对")
    parser.add_argument("--i18n", default=None, help="国际版图片目录路径（与 --mainland 配对，或使用 --config）")
    parser.add_argument("--mainland", default=None, help="陆版图片目录路径（与 --i18n 配对，或使用 --config）")
    parser.add_argument("--output", default="ui_image_check_report.html", help="输出文件路径，支持 .xlsx / .html")
    parser.add_argument("--state-file", default=STATE_FILE, help="增量检查时间点记录文件")
    parser.add_argument(
        "--since",
        type=parse_dt,
        help="只检查此时间后的陆版新增图片，例如 2026-05-27T00:00:00+08:00",
    )
    parser.add_argument("--no-ocr", action="store_true", help="禁用 OCR 文字检测（默认启用）")
    parser.add_argument(
        "--ocr-cache-file",
        default=OCR_CACHE_FILE,
        help=f"OCR 检测结果缓存文件（默认 {OCR_CACHE_FILE}），记录已检查文件避免重复 OCR",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        help="测试用：每个对比目录按相对路径排序后最多取多少张图片",
    )
    parser.add_argument(
        "--assume-new-has-text",
        action="store_true",
        help="将陆版新增图片全部按有文字报告，用于无 OCR 环境人工复核",
    )
    parser.add_argument(
        "--thumbnail-limit",
        type=int,
        default=500,
        help="最多插入多少张缩略图；传 -1 表示不限制",
    )
    parser.add_argument(
        "--no-thumbnail-resize",
        action="store_true",
        help="嵌入原图像素尺寸而非 96x72 缩略图；行高会随原图高度调整",
    )
    parser.add_argument(
        "--max-image-px",
        type=int,
        default=None,
        help="嵌入图最长边像素上限（保持纵横比）；默认 96x72 缩略图；与 --no-thumbnail-resize 互斥",
    )
    parser.add_argument(
        "--thumbnail-issue",
        action="append",
        choices=["mainland_changed", "mainland_missing", "mainland_new_with_text"],
        help="指定哪些问题类型插入缩略图；可重复传入。默认只给 changed/missing 插图",
    )
    parser.add_argument("--no-save-state", action="store_true", help="不更新增量检查时间点")
    parser.add_argument(
        "--enable-translation-check",
        action="store_true",
        help="对 mainland_changed/mainland_new_with_text 图片进行 OCR+Claude 翻译质量检查",
    )
    parser.add_argument(
        "--anthropic-api-key",
        default=None,
        help="Anthropic API Key（优先使用环境变量 ANTHROPIC_API_KEY）",
    )
    args = parser.parse_args(argv)

    if not args.config and (not args.i18n or not args.mainland):
        parser.error("需要同时指定 --i18n 和 --mainland，或使用 --config 指定配置文件")

    check_started_at = dt.datetime.now(dt.timezone.utc)
    findings, counts = collect_findings(args)
    thumbnail_limit = None if args.thumbnail_limit < 0 else args.thumbnail_limit
    thumbnail_issues = (
        set(args.thumbnail_issue)
        if args.thumbnail_issue
        else DEFAULT_THUMBNAIL_ISSUES
    )
    if args.no_thumbnail_resize and args.max_image_px is not None:
        raise SystemExit("ERROR: --no-thumbnail-resize 与 --max-image-px 不能同时使用")
    output_path = Path(args.output)
    if output_path.suffix.lower() in {".html", ".htm"}:
        write_html_report(
            output_path,
            findings,
            i18n_count=counts["i18n_count"],
            mainland_count=counts["mainland_count"],
        )
    else:
        write_xlsx(
            output_path,
            findings,
            thumbnail_limit,
            thumbnail_issues,
            no_thumbnail_resize=args.no_thumbnail_resize,
            max_image_px=args.max_image_px,
        )
    if not args.no_save_state:
        save_last_check(Path(args.state_file), check_started_at)
    print(f"检查完成: {len(findings)} 项，输出: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
