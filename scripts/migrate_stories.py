#!/usr/bin/env python3
"""Sinh content/lessons/lesson-NN/_index.md (front matter) từ data/story/ + data/slugs/.

Script một lần (docs/plan.md §6.1, M1). Chạy sau scripts/build_taxonomy.py (cần
data/taxonomy.yaml đã có để tra `act`).

Nội dung truyện thật (tokenize thành chip bấm được) là việc của
scripts/tokenize_stories.py (M2, ghi ra tokens.json) — script này CHỈ sinh front
matter. Trang /lessons/lesson-NN/ chưa có thân bài cho tới khi M2 chạy.

Thuật toán (§6.1):
  - topic của một lesson lấy từ data/slugs/story-slug.md (ánh xạ 1:1, đã verify ở §2.5
    cho exercises và đúng tương tự cho lesson) — KHÔNG suy từ union topic của
    data/words, vì một số từ trùng tên (§2.3 điểm 4, vd `streamline`, `supplies`)
    có bản sao ở topic khác nhưng CÙNG lesson, sẽ làm lẫn topic nếu suy ngây thơ.
  - subtopics/level: lọc data/words theo ĐÚNG (lesson, topic) rồi mới gom, tránh
    lẫn dữ liệu của bản sao từ trùng tên nói trên.
  - summary (§12.3 Q6): lấy phần "preview" trong teaser của CHƯƠNG TRƯỚC (câu
    "*Hết Chương N. Chương sau (lesson-NN): …*" có ở 27/28 file VI, không có ở
    chương 28 vì đó là chương cuối). Chương 1 không có chương trước → viết tay.
"""
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
STORY_VI_DIR = ROOT / "data/story/story-vi"
STORY_SLUG_MD = ROOT / "data/slugs/story-slug.md"
TAXONOMY_YAML = ROOT / "data/taxonomy.yaml"
WORDS_DIR = ROOT / "data/words"
OUT_DIR = ROOT / "content/lessons"

LESSON1_SUMMARY = (
    "cuộc họp hội đồng quản trị định đoạt số phận của Project Aria, ngay trước khi "
    "Priya vướng vào rắc rối điện thoại đầu tiên trong ngày."
)

ROW_RE = re.compile(
    r"^\|\s*\d+\s*\|\s*[^|]+?\s*\|\s*`lesson-(\d+)\.md`\s*\|\s*`([a-z0-9-]+)`\s*\|"
    r"\s*([^|]+?)\s*\|\s*`([a-z0-9-]+)`\s*\|\s*$",
    re.M,
)
TEASER_RE = re.compile(r"^\*(Hết Chương.+)\*\s*$", re.M)
NEXT_PREVIEW_RE = re.compile(r"Chương sau \(lesson-\d+[^)]*\):\s*(.+)$")
CHAR_PAIR_RE = re.compile(r"\*\*([^*]+)\*\*\s*\(([^)]+)\)")


def parse_story_slug_table():
    """-> dict lesson_id -> {topic, title_en, story_slug}"""
    text = STORY_SLUG_MD.read_text(encoding="utf-8")
    rows = {}
    for ln, topic, title, slug in ROW_RE.findall(text):
        rows[f"lesson-{ln}"] = {"topic": topic, "title_en": title.strip(), "story_slug": slug}
    if len(rows) != 28:
        sys.exit(f"Kỳ vọng 28 dòng trong bảng story-slug.md, tìm thấy {len(rows)}")
    return rows


def load_act_by_lesson():
    """-> dict lesson_id -> {label, slug}. `slug` nạp vào front matter dạng list
    (`acts: [slug]`) để Hugo tự nhận làm taxonomy "acts" (đã verify thực nghiệm:
    front matter phải là field số nhiều khớp giá trị bên phải trong hugo.toml
    `[taxonomies] act = "acts"`, không phải field "act" số ít)."""
    taxonomy = yaml.safe_load(TAXONOMY_YAML.read_text(encoding="utf-8"))
    act_by_lesson = {}
    for act in taxonomy["acts"]:
        for lesson_id in act["lessons"]:
            act_by_lesson[lesson_id] = {"label": act["label"], "slug": act["slug"]}
    return act_by_lesson


def load_words_by_lesson_topic():
    """-> dict (lesson_id, topic) -> list[word entry]"""
    index = defaultdict(list)
    for f in sorted(WORDS_DIR.glob("*.yaml")):
        for w in yaml.safe_load(f.read_text(encoding="utf-8")):
            for lesson_id in w["lesson"]:
                index[(lesson_id, w["topic"])].append(w)
    return index


def parse_vi_story(lesson_id):
    path = STORY_VI_DIR / f"story-{lesson_id.split('-')[1]}.md"
    lines = path.read_text(encoding="utf-8").splitlines()

    h1 = lines[0]
    heading_vi = re.sub(r"^#\s*LESSON\s*\d+\s*—\s*", "", h1).strip()

    char_line = lines[4]
    characters = [
        {"name": name.strip(), "role": role.strip()}
        for name, role in CHAR_PAIR_RE.findall(char_line)
    ]

    body_text = "\n".join(lines)
    teaser_m = TEASER_RE.search(body_text)
    if not teaser_m:
        sys.exit(f"{path}: không tìm thấy dòng teaser '*Hết Chương…*'")
    teaser = teaser_m.group(1).strip()

    preview_m = NEXT_PREVIEW_RE.search(teaser)
    next_preview = preview_m.group(1).strip() if preview_m else None

    if len(characters) < 2:
        print(f"  [review] {lesson_id}: chỉ tách được {len(characters)} nhân vật từ dòng: {char_line!r}")

    return {
        "heading_vi": heading_vi,
        "characters": characters,
        "teaser": teaser,
        "next_preview": next_preview,
    }


def main():
    table = parse_story_slug_table()
    act_by_lesson = load_act_by_lesson()
    words_index = load_words_by_lesson_topic()

    parsed = {}
    for n in range(1, 29):
        lesson_id = f"lesson-{n:02d}"
        parsed[lesson_id] = parse_vi_story(lesson_id)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    for n in range(1, 29):
        lesson_id = f"lesson-{n:02d}"
        row = table[lesson_id]
        info = parsed[lesson_id]

        words = words_index[(lesson_id, row["topic"])]
        if not words:
            sys.exit(f"{lesson_id}: không tìm thấy từ vựng nào cho topic '{row['topic']}'")
        subtopics = sorted({w["sub-topic"] for w in words if w.get("sub-topic")})
        level = statistics.median_low(sorted(w["level"] for w in words))

        if n == 1:
            summary = LESSON1_SUMMARY
        else:
            prev = parsed[f"lesson-{n - 1:02d}"]
            if not prev["next_preview"]:
                sys.exit(f"lesson-{n - 1:02d}: thiếu 'Chương sau (lesson-NN): …' để làm summary cho {lesson_id}")
            summary = prev["next_preview"]

        front_matter = {
            "title": f"Chương {n} — {row['title_en']}",
            "back": "/lessons/",
            "lesson_id": lesson_id,
            "chapter": n,
            "act": act_by_lesson[lesson_id]["label"],
            "acts": [act_by_lesson[lesson_id]["slug"]],
            "story_slug": row["story_slug"],
            "topics": [row["topic"]],
            "subtopics": subtopics,
            "heading_vi": info["heading_vi"],
            "summary": summary,
            "level": level,
            "characters": info["characters"],
            "teaser": info["teaser"],
            "weight": n,
        }

        lesson_dir = OUT_DIR / lesson_id
        lesson_dir.mkdir(parents=True, exist_ok=True)
        out_path = lesson_dir / "_index.md"
        with out_path.open("w", encoding="utf-8") as f:
            f.write("---\n")
            yaml.safe_dump(front_matter, f, allow_unicode=True, sort_keys=False, width=1000)
            f.write("---\n")
        written += 1

    print(f"\nĐã ghi {written} file content/lessons/lesson-NN/_index.md.")
    print("Lưu ý: chưa có thân truyện (tokens.json) — đó là việc của scripts/tokenize_stories.py (M2).")


if __name__ == "__main__":
    main()
