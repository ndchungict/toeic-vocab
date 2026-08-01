#!/usr/bin/env python3
"""Sinh content/lessons/lesson-NN/exercise/index.md — leaf bundle bên trong branch
bundle lesson-NN (docs/plan.md §5.2, M7). Chỉ front matter tối thiểu: đề bài thật
đọc thẳng site.Data.exercises lúc render (layouts/lessons/single.html), không lưu
lại trong front matter (giống cách content/lessons/lesson-NN/_index.md không lưu
newWords — luôn suy từ nguồn, tránh lệch dữ liệu).

back trỏ về /exercises/ (danh sách 28 đề, §8) chứ không phải "home" như mockup
(§1.2) — mockup dùng "home" vì đó là mô hình điều hướng SPA cũ; kiến trúc thật
có trang /exercises/ riêng nên quay lại đó hợp lý hơn, giống cách /lessons/lesson-NN/
quay về /lessons/ và /words/offices/memo/ quay về /words/.
"""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "content/lessons"


def main():
    written = 0
    for n in range(1, 29):
        lesson_id = f"lesson-{n:02d}"
        front_matter = {
            "title": "Bài tập",
            "back": "/exercises/",
            "lesson_id": lesson_id,
            "weight": n,
        }
        out_dir = LESSONS_DIR / lesson_id / "exercise"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "index.md"
        with out_path.open("w", encoding="utf-8") as f:
            f.write("---\n")
            yaml.safe_dump(front_matter, f, allow_unicode=True, sort_keys=False, width=1000)
            f.write("---\n")
        written += 1

    print(f"Đã ghi {written} file content/lessons/lesson-NN/exercise/index.md.")


if __name__ == "__main__":
    main()
