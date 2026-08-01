#!/usr/bin/env python3
"""Rà toàn bộ link nội bộ trong public/ đã build — dò href/src trỏ tới file không
tồn tại, href rỗng, hoặc thiếu tiền tố baseURL (docs/plan.md §11 M9). Script tạm
thời cho việc rà soát cuối, không phải một phần pipeline build/CI thường xuyên.
"""
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
BASE_PATH = "/toeic-vocab/"

#  minify bỏ dấu nháy khi giá trị không cần (HTML5 hợp lệ), nên phải chấp nhận
#  cả 3 dạng: href="x", href='x', href=x (không nháy, dừng ở khoảng trắng/> ).
HREF_RE = re.compile(r'''(?:href|src)=(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))''')


def all_html_files():
    return sorted(PUBLIC.rglob("*.html"))


def public_path_exists(url_path):
    """url_path bắt đầu bằng '/', vd '/toeic-vocab/words/offices/memo/'."""
    rel = url_path[len(BASE_PATH):] if url_path.startswith(BASE_PATH) else url_path.lstrip("/")
    candidate = PUBLIC / rel
    if candidate.is_dir():
        candidate = candidate / "index.html"
    elif not candidate.suffix:
        candidate = candidate.with_suffix("") / "index.html" if False else candidate
    return candidate.exists() or (PUBLIC / rel).with_name((PUBLIC / rel).name).exists()


def main():
    errors = []
    checked = 0
    empty_href = 0
    missing_prefix = 0

    for html_file in all_html_files():
        text = html_file.read_text(encoding="utf-8")
        page_url = "/" + str(html_file.relative_to(PUBLIC).parent) + "/"
        for m in HREF_RE.finditer(text):
            href = m.group(1) if m.group(1) is not None else (m.group(2) if m.group(2) is not None else m.group(3))
            if href.startswith(("http://", "https://", "mailto:", "tel:", "data:", "#")):
                continue
            checked += 1
            if href == "":
                empty_href += 1
                errors.append(f"{html_file.relative_to(PUBLIC)}: href/src RỖNG")
                continue
            if href.startswith("/") and not href.startswith(BASE_PATH):
                missing_prefix += 1
                errors.append(f"{html_file.relative_to(PUBLIC)}: thiếu tiền tố {BASE_PATH} -> {href!r}")
                continue

            abs_url = urljoin("https://example.com" + page_url, href)
            path = urlsplit(abs_url).path
            rel = path[len(BASE_PATH):] if path.startswith(BASE_PATH) else path.lstrip("/")
            candidate = PUBLIC / rel
            if candidate.is_dir():
                candidate = candidate / "index.html"
            if not candidate.exists():
                errors.append(f"{html_file.relative_to(PUBLIC)}: link hỏng -> {href!r} (tìm {candidate.relative_to(PUBLIC)})")

    print(f"Đã kiểm {checked} link nội bộ trong {len(all_html_files())} file HTML.")
    print(f"  href/src rỗng: {empty_href}")
    print(f"  thiếu tiền tố {BASE_PATH}: {missing_prefix}")

    if errors:
        print(f"\n{len(errors)} lỗi:")
        for e in errors[:100]:
            print(f"  - {e}")
        sys.exit(1)

    print("\nOK — không có link nội bộ nào hỏng.")


if __name__ == "__main__":
    main()
