#!/usr/bin/env python3
"""Sinh data/taxonomy.yaml từ data/slugs/*.md.

Script một lần (docs/plan.md §6.2, M1) — Hugo không load .md trong data/,
nên 2 bảng tra ở data/slugs/ phải chuyển sang YAML trước khi build.

Nguồn:
  - data/slugs/category-slug.md  -> 13 topic, 30 sub-topic + nhãn VI sub-topic
  - data/slugs/story-slug.md     -> mục "Cấu trúc 4 hồi" (act -> lesson range + tóm tắt)

label_vi / label_en của 13 topic chính không có trong data/slugs (chỉ có slug) nên
được hardcode dưới đây, đã chốt với người dùng theo đề xuất ở docs/plan.md §12.3 Q1.
"""
import re
import sys
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CATEGORY_MD = ROOT / "data/slugs/category-slug.md"
STORY_MD = ROOT / "data/slugs/story-slug.md"
OUT = ROOT / "data/taxonomy.yaml"

TOPIC_LABEL_VI = {
    "offices": "Văn phòng",
    "personnel": "Nhân sự",
    "general-business": "Kinh doanh tổng quát",
    "travel": "Du lịch & Công tác",
    "dining-out": "Ăn uống & Nhà hàng",
    "finance-budgeting": "Tài chính & Ngân sách",
    "purchasing": "Mua sắm & Cung ứng",
    "manufacturing": "Sản xuất",
    "corporate-development": "Phát triển doanh nghiệp",
    "technical-areas": "Kỹ thuật & Công nghệ",
    "housing-property": "Nhà ở & Bất động sản",
    "health": "Sức khỏe & Y tế",
    "entertainment": "Giải trí & Truyền thông",
}

# H1 của 28 file truyện dùng chữ viết tắt không khớp thẳng slug (vd "FINANCE" cho
# finance-budgeting, "HOUSING" cho housing-property) nên không parse tự động được —
# chuẩn hoá tay từ slug.
TOPIC_LABEL_EN = {
    "offices": "Offices",
    "personnel": "Personnel",
    "general-business": "General Business",
    "travel": "Travel",
    "dining-out": "Dining Out",
    "finance-budgeting": "Finance & Budgeting",
    "purchasing": "Purchasing",
    "manufacturing": "Manufacturing",
    "corporate-development": "Corporate Development",
    "technical-areas": "Technical Areas",
    "housing-property": "Housing & Property",
    "health": "Health",
    "entertainment": "Entertainment",
}


def slugify(text: str) -> str:
    text = text.replace("Đ", "D").replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text


def parse_category_slug():
    """-> (dict topic -> list[subtopic slug], dict subtopic slug -> label_vi)."""
    text = CATEGORY_MD.read_text(encoding="utf-8")

    topic_subtopics = {}
    row_re = re.compile(r"^\|\s*\d+\s*\|\s*`([a-z0-9-]+)`\s*\|\s*(.+?)\s*\|\s*$", re.M)
    for m in row_re.finditer(text):
        topic, cell = m.group(1), m.group(2)
        topic_subtopics[topic] = re.findall(r"`([a-z0-9-]+)`", cell)

    subtopic_label_vi = {}
    bullet_re = re.compile(r"^- \*\*([a-z0-9-]+)\*\*:\s*(.+)$", re.M)
    for m in bullet_re.finditer(text):
        for pair in m.group(2).split("·"):
            key, _, label = pair.strip().partition("=")
            key = key.strip().strip("`")
            if key:
                subtopic_label_vi[key] = label.strip()

    return topic_subtopics, subtopic_label_vi


def parse_acts():
    """-> list[{slug, label, lessons, summary}] từ mục 'Cấu trúc 4 hồi'."""
    text = STORY_MD.read_text(encoding="utf-8")
    section_m = re.search(r"## Cấu trúc 4 hồi\n(.+)", text, re.S)
    if not section_m:
        sys.exit("Không tìm thấy mục 'Cấu trúc 4 hồi' trong story-slug.md")

    acts = []
    line_re = re.compile(r"^- \*\*(Hồi[^*]+)\*\* \(chương (\d+)[–-](\d+)\):\s*(.+)$", re.M)
    for label, start, end, summary in line_re.findall(section_m.group(1)):
        start, end = int(start), int(end)
        acts.append({
            "slug": slugify(label),
            "label": label,
            "lessons": [f"lesson-{n:02d}" for n in range(start, end + 1)],
            "summary": summary.strip(),
        })
    return acts


def main():
    topic_subtopics, subtopic_label_vi = parse_category_slug()

    missing = sorted(set(topic_subtopics) - set(TOPIC_LABEL_VI))
    if missing:
        sys.exit(f"Thiếu label_vi/label_en cho topic: {missing}")

    topics = {}
    for topic in sorted(topic_subtopics):
        topics[topic] = {
            "slug": topic,
            "label_vi": TOPIC_LABEL_VI[topic],
            "label_en": TOPIC_LABEL_EN[topic],
            "subtopics": [
                {"slug": s, "label_vi": subtopic_label_vi.get(s, s)}
                for s in topic_subtopics[topic]
            ],
        }

    acts = parse_acts()
    if len(acts) != 4:
        sys.exit(f"Kỳ vọng 4 hồi, tìm thấy {len(acts)}")
    total_lessons = sum(len(a["lessons"]) for a in acts)
    if total_lessons != 28:
        sys.exit(f"Kỳ vọng 28 chương trong 4 hồi, tìm thấy {total_lessons}")

    data = {"topics": topics, "acts": acts}
    with OUT.open("w", encoding="utf-8") as f:
        f.write("# Sinh tự động bởi scripts/build_taxonomy.py — KHÔNG sửa tay.\n")
        f.write("# Nguồn: data/slugs/category-slug.md + data/slugs/story-slug.md\n")
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, width=1000)

    n_subtopics = sum(len(t["subtopics"]) for t in topics.values())
    print(f"Đã ghi {OUT.relative_to(ROOT)}: {len(topics)} topic, {n_subtopics} sub-topic, {len(acts)} hồi.")


if __name__ == "__main__":
    main()
