#!/usr/bin/env python3
"""Kiểm tra tính nhất quán của dữ liệu (docs/plan.md §9).

Chạy trong CI (.github/workflows/validate.yml) và cục bộ trước khi commit dữ liệu
mới do 2 skill sinh ra. Không kiểm tra token {w:…} trong truyện nếu tokens.json
(M2) chưa tồn tại — script này chạy được ngay từ M1, trước khi
tokenize_stories.py sinh tokens.json, và tiếp tục hữu ích ở mọi milestone sau.
"""
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WORDS_DIR = ROOT / "data/words"
EXERCISES_DIR = ROOT / "data/exercises"
LESSONS_DIR = ROOT / "content/lessons"
TAXONOMY_YAML = ROOT / "data/taxonomy.yaml"

BLANK_RE = re.compile(r"\*\*\((\d+)\)_+\*\*")

errors = []


def err(msg):
    errors.append(msg)


def load_words():
    words = []
    for f in sorted(WORDS_DIR.glob("*.yaml")):
        words.extend(yaml.safe_load(f.read_text(encoding="utf-8")) or [])
    return words


def load_exercises():
    by_file = {}
    for f in sorted(EXERCISES_DIR.glob("*.yaml")):
        by_file[f.stem] = yaml.safe_load(f.read_text(encoding="utf-8")) or []
    return by_file


def check_taxonomy_consistency(words, taxonomy):
    valid_topics = set(taxonomy["topics"])
    valid_subtopics = {
        (topic, s["slug"]) for topic, t in taxonomy["topics"].items() for s in t["subtopics"]
    }
    for w in words:
        if w["topic"] not in valid_topics:
            err(f"words: topic lạ '{w['topic']}' (word={w['word']!r})")
        st = w.get("sub-topic")
        if st and (w["topic"], st) not in valid_subtopics:
            err(f"words: sub-topic lạ ({w['topic']}, {st}) (word={w['word']!r})")


def check_duplicate_keys(words):
    seen = set()
    for w in words:
        key = (w["topic"], w["word"])
        if key in seen:
            err(f"words: khóa (topic, word) trùng: {key}")
        seen.add(key)


def check_example_markers(words):
    for w in words:
        en = w["example"]["en"]
        if "{" not in en or "}" not in en:
            err(f"words: example.en thiếu marker {{…}}: {w['topic']}:{w['word']!r}")


def check_lessons_complete(words, exercises_by_file):
    words_lessons = set()
    for w in words:
        words_lessons.update(w["lesson"])

    for n in range(1, 29):
        lesson_id = f"lesson-{n:02d}"
        if lesson_id not in words_lessons:
            err(f"lessons: {lesson_id} không có từ vựng nào trong data/words")
        if not (LESSONS_DIR / lesson_id / "_index.md").exists():
            err(f"lessons: thiếu content/lessons/{lesson_id}/_index.md")
        if not (LESSONS_DIR / lesson_id / "exercise" / "index.md").exists():
            err(f"lessons: thiếu content/lessons/{lesson_id}/exercise/index.md")
        ex_key = f"exercise-{n:02d}"
        if ex_key not in exercises_by_file:
            err(f"lessons: thiếu data/exercises/{ex_key}.yaml")


def check_exercise_topic_lesson(exercises_by_file):
    for fname, items in exercises_by_file.items():
        topics = {it["topic"] for it in items}
        lessons = {it["lesson"][0] for it in items}
        if len(topics) != 1:
            err(f"exercises {fname}: nhiều hơn 1 topic trong cùng file: {sorted(topics)}")
        if len(lessons) != 1:
            err(f"exercises {fname}: nhiều hơn 1 lesson trong cùng file: {sorted(lessons)}")


def check_related_word(exercises_by_file, words):
    index = {(w["topic"], w["word"]) for w in words}
    for fname, items in exercises_by_file.items():
        for it in items:
            rw = it.get("related_word")
            if rw is None:
                continue
            if (it["topic"], rw) not in index:
                err(f"exercises {fname}/{it['id']}: related_word '{rw}' không resolve được ở topic '{it['topic']}'")


def check_options_answer(exercises_by_file):
    for fname, items in exercises_by_file.items():
        for it in items:
            opts = it.get("options", {})
            if set(opts.keys()) != {"A", "B", "C", "D"}:
                err(f"exercises {fname}/{it['id']}: options thiếu đủ A/B/C/D: {sorted(opts.keys())}")
            if it.get("answer") not in opts:
                err(f"exercises {fname}/{it['id']}: answer '{it.get('answer')}' không nằm trong options")


def check_passage_groups(exercises_by_file):
    for fname, items in exercises_by_file.items():
        groups = {}
        for it in items:
            pg = it.get("passage_group")
            if pg:
                groups.setdefault(pg, []).append(it)
        for pg, group_items in groups.items():
            passages = {it["passage"] for it in group_items}
            if len(passages) != 1:
                err(f"exercises {fname}/{pg}: passage không giống hệt nhau giữa các item cùng group")
                continue
            if group_items[0]["part"] != 6:
                continue  # chỗ trống **(n)___** chỉ có ở Part 6; Part 7 là câu hỏi rời
            blanks = BLANK_RE.findall(group_items[0]["passage"])
            if len(blanks) != len(group_items):
                err(
                    f"exercises {fname}/{pg}: số chỗ trống trong passage ({len(blanks)}) "
                    f"khác số item của group ({len(group_items)})"
                )


def check_tokens_json(words):
    """Chỉ có hiệu lực sau M2 (khi tokens.json đã tồn tại) — bỏ qua êm trước đó."""
    valid_keys = {f"{w['topic']}:{w['word']}" for w in words}
    checked = 0
    for tokens_file in sorted(LESSONS_DIR.glob("*/tokens.json")):
        checked += 1
        data = json.loads(tokens_file.read_text(encoding="utf-8"))
        for version in ("chem", "english"):
            for para in data.get(version, []):
                for tok in para:
                    if isinstance(tok, dict) and "w" in tok and tok["w"] not in valid_keys:
                        err(f"{tokens_file}: token {{w: {tok['w']!r}}} không resolve được về data/words")
    if checked == 0:
        print("  (bỏ qua: chưa có tokens.json — chạy tokenize_stories.py ở M2 trước)")
    else:
        print(f"  đã kiểm {checked} file tokens.json")


def main():
    if not TAXONOMY_YAML.exists():
        sys.exit("Thiếu data/taxonomy.yaml — chạy scripts/build_taxonomy.py trước.")
    taxonomy = yaml.safe_load(TAXONOMY_YAML.read_text(encoding="utf-8"))

    words = load_words()
    exercises_by_file = load_exercises()

    check_taxonomy_consistency(words, taxonomy)
    check_duplicate_keys(words)
    check_example_markers(words)
    check_lessons_complete(words, exercises_by_file)
    check_exercise_topic_lesson(exercises_by_file)
    check_related_word(exercises_by_file, words)
    check_options_answer(exercises_by_file)
    check_passage_groups(exercises_by_file)
    print("Kiểm tra tokens.json (M2, nếu có):")
    check_tokens_json(words)

    if errors:
        print(f"\n{len(errors)} lỗi:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    n_ex = sum(len(v) for v in exercises_by_file.values())
    print(f"\nOK — {len(words)} từ, {n_ex} câu bài tập, 28 bài học đều hợp lệ.")


if __name__ == "__main__":
    main()
