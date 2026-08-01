#!/usr/bin/env python3
"""Tokenize truyện thành chip từ vựng bấm được — sinh content/lessons/lesson-NN/tokens.json.

Script một lần (docs/plan.md §6.3, M2). Đọc data/story/story-{en,vi}/story-NN.md
(nguồn gốc, giữ nguyên — §12.3 Q8), KHÔNG đọc content/lessons/.../_index.md.

Thuật toán:
  1. Tập từ ứng viên của một bài = data/words lọc theo ĐÚNG (lesson, topic) — topic lấy
     từ data/slugs/story-slug.md, giống hệt cách scripts/migrate_stories.py làm ở M1
     (tránh lẫn dữ liệu của 20 từ trùng tên có bản sao ở topic khác nhưng cùng lesson).
  2. Với mỗi từ, sinh bảng surface-form -> "<topic>:<word>" từ: chính `word`, mọi giá trị
     trong `forms` (string hoặc list), mọi `collocations.en`, cộng biến thể chia động từ
     đều (-s/-es/-ed/-ies/-ied/-ing/-ly) áp cho TỪ CUỐI của cụm (vd "comply with" ->
     cũng thử "complies with"). Hyphen/space được coi là tương đương ("check-out" ~
     "check out").
  3. Quét từng vùng **…** trong truyện, khớp không phân biệt hoa thường:
     a. khớp thẳng trong bảng surface-form ở bước 2, hoặc
     b. khớp qua fallback bỏ dần từ giới từ/tiểu từ ở cuối cụm ("comply with" -> "comply"
        nếu "comply" có trong bảng nhưng "comply with" thì không), hoặc
     c. khớp qua danh sách ngoại lệ tay OVERRIDES (từ trong truyện lệch khỏi headword
        chính thức — vd "the bill" ~ "check", "to go" ~ "takeout" — đã khảo sát trên
        toàn bộ 28×2 file, xem §3.2/§6.3 của plan).
     Vùng nào không khớp bước nào ở trên thì GIỮ NGUYÊN LÀ TEXT THƯỜNG (bỏ dấu **,
     không tạo chip) — áp dụng cho cả tên riêng lẫn từ thật sự chưa khớp được.
  4. Ca cụm bị tách rời `**put**  …  **on hold**` (chỉ có ở lesson-01) được GHÉP LẠI
     thành một vùng trước khi quét, vì đây là annotation tay duy nhất thật sự cần thiết
     (không phải lỗi khớp từ — hai vùng bold rời nhau trong nguồn).
  5. Ở bản VI, phần `(nghĩa tiếng Việt)` ngay sau một chip khớp được CẮT BỎ khỏi text
     (nghĩa đã có sẵn trong data/words, hiện qua nút "Hiện nghĩa" ở client).
  6. In báo cáo mọi vùng bold KHÔNG khớp được (trừ danh sách override) để người dùng
     review tay — đo được ở corpus thật: "round-trip" (lesson-09) và "check-out"/"check
     out" (lesson-10) không có headword tương ứng trong data/words, cần người quyết định
     (thêm từ mới hay sửa truyện) — không tự ý đoán.
"""
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
STORY_VI_DIR = ROOT / "data/story/story-vi"
STORY_EN_DIR = ROOT / "data/story/story-en"
STORY_SLUG_MD = ROOT / "data/slugs/story-slug.md"
WORDS_DIR = ROOT / "data/words"
LESSONS_DIR = ROOT / "content/lessons"

ROW_RE = re.compile(
    r"^\|\s*\d+\s*\|\s*[^|]+?\s*\|\s*`lesson-(\d+)\.md`\s*\|\s*`([a-z0-9-]+)`\s*\|"
    r"\s*([^|]+?)\s*\|\s*`([a-z0-9-]+)`\s*\|\s*$",
    re.M,
)
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
GLOSS_RE = re.compile(r"^\s*\([^)]*\)")
TEASER_RE = re.compile(r"^\*Hết Chương.+\*\s*$", re.M)
SPLIT_PUT_ON_HOLD_RE = re.compile(r"\*\*put\*\*(.{1,25}?)\*\*on hold\*\*", re.IGNORECASE)

# Bảng dạng-chia đều
SUFFIXES_ES = re.compile(r"(s|x|z|ch|sh)$")

# Ngoại lệ tay: từ trong truyện lệch khỏi headword chính thức. Khoá = (lesson_id,
# text bold viết thường, đã chuẩn hoá khoảng trắng); value = "<topic>:<word>" đích.
# Đã khảo sát trực tiếp trên data/story/ + data/words/ (không phải đoán) — mỗi ca đều
# ghi rõ vì sao không tự khớp được.
OVERRIDES = {
    # "transfer a call" là headword, nhưng truyện chia động từ + đổi mạo từ
    # "transfer the call" / "transferred the call" — 3 từ, cụm dài hơn 1 từ khoá.
    ("lesson-01", "transfer the call"): "offices:transfer a call",
    ("lesson-01", "transferred the call"): "offices:transfer a call",
    # "check" (dining-out) không có form/collocation nào chứa "the bill" — truyện
    # dùng từ đồng nghĩa thay vì headword.
    ("lesson-12", "the bill"): "dining-out:check",
    # "takeout" chỉ có collocation "for here or to go", không phải "to go" đứng riêng.
    ("lesson-12", "to go"): "dining-out:takeout",
    # "inventory" (purchasing) không có collocation "take inventory" đăng ký sẵn.
    ("lesson-15", "take inventory"): "purchasing:inventory",
    # collocation đăng ký là "post a job opening" / "in recognition of sth" — truyện chỉ
    # bold cụm con ở giữa/cuối, không phải prefix nên STRIP_LEADING_WORDS không tự rút ra được.
    ("lesson-03", "job opening"): "personnel:vacancy",
    ("lesson-04", "in recognition of"): "personnel:recognition",
}

# Biết trước nhưng KHÔNG override — story dùng từ không có trong data/words, cần
# người quyết định (thêm headword mới hay sửa truyện), không phải lỗi tokenizer:
#   - "round-trip" (lesson-09, travel): không có ở word/forms/collocations nào.
#   - "check-out" / "check out" (lesson-10, travel): headword đăng ký là "check in",
#     không phải cặp check-in/check-out — map bừa sang "check in" sẽ sai nghĩa.
KNOWN_UNRESOLVED = {
    ("lesson-09", "round-trip"),
    ("lesson-10", "check-out"),
    ("lesson-10", "check out"),
    # Bold nhưng không có headword/form/collocation nào tương ứng trong data/words —
    # đã tra toàn bộ 558 từ, không phải lỗi khớp mà là truyện dùng từ ngoài danh sách.
    ("lesson-06", "void"),
    ("lesson-12", "banquet"),
    ("lesson-12", "host"),
    ("lesson-15", "retail"),
    ("lesson-21", "hardware"),
}

STRIP_TRAILING_WORDS = {"with", "on", "to", "for", "by", "of", "up", "out", "in", "from", "at", "about"}
# Để rút gọn collocation dài thành cụm ngắn hơn thật sự xuất hiện trong truyện, vd
# collocation "on arrival" của "departure" -> truyện chỉ bold "arrival".
STRIP_LEADING_WORDS = {"on", "a", "an", "the", "in", "to", "for", "at", "by"}


def is_cvc(word):
    """Consonant-Vowel-Consonant cuối từ ngắn (jam, stop, plan…) -> nhân đôi phụ âm khi thêm hậu tố."""
    if len(word) < 3 or word[-1] in "aeiouwxy" or word[-2] not in "aeiou":
        return False
    return len(word) < 4 or word[-3] not in "aeiou"


def inflect_last_token(phrase):
    parts = phrase.split(" ")
    last = parts[-1]
    prefix = parts[:-1]

    def join(w):
        return " ".join(prefix + [w]) if prefix else w

    variants = {phrase}
    if SUFFIXES_ES.search(last):
        variants.add(join(last + "es"))
    elif last.endswith("y") and len(last) > 1 and last[-2] not in "aeiou":
        variants.add(join(last[:-1] + "ies"))
    else:
        variants.add(join(last + "s"))

    doubled = last + last[-1] if is_cvc(last) else last
    if last.endswith("e"):
        variants.add(join(last + "d"))
    elif last.endswith("y") and len(last) > 1 and last[-2] not in "aeiou":
        variants.add(join(last[:-1] + "ied"))
    else:
        variants.add(join(last + "ed"))
        variants.add(join(doubled + "ed"))

    if last.endswith("e") and not last.endswith("ee"):
        variants.add(join(last[:-1] + "ing"))
    else:
        variants.add(join(last + "ing"))
        variants.add(join(doubled + "ing"))

    variants.add(join(last + "ly"))
    return variants


def flatten_forms(forms):
    values = []
    for v in forms.values():
        values.extend(v) if isinstance(v, list) else values.append(v)
    return values


def add_candidate(lookup, surface, key):
    surface = re.sub(r"\s+", " ", surface.strip().lower())
    if not surface:
        return
    bases = {surface, surface.replace("-", " "), surface.replace(" ", "-")}
    words = surface.split(" ")
    if len(words) > 1 and words[0] in STRIP_LEADING_WORDS:
        bases.add(" ".join(words[1:]))
    for variant in set(bases):
        lookup.setdefault(variant, key)
        for infl in inflect_last_token(variant):
            lookup.setdefault(infl, key)


def build_lookup(words):
    lookup = {}
    for w in words:
        key = f"{w['topic']}:{w['word']}"
        add_candidate(lookup, w["word"], key)
        for v in flatten_forms(w["forms"]):
            add_candidate(lookup, v, key)
        for c in w["collocations"]:
            add_candidate(lookup, c["en"], key)
    return lookup


def parse_story_slug_table():
    text = STORY_SLUG_MD.read_text(encoding="utf-8")
    rows = {}
    for ln, topic, _title, _slug in ROW_RE.findall(text):
        rows[f"lesson-{ln}"] = topic
    return rows


def load_words_by_lesson_topic():
    index = defaultdict(list)
    for f in sorted(WORDS_DIR.glob("*.yaml")):
        for w in yaml.safe_load(f.read_text(encoding="utf-8")):
            for lesson_id in w["lesson"]:
                index[(lesson_id, w["topic"])].append(w)
    return index


def resolve_in(text_norm, lookup):
    if text_norm in lookup:
        return lookup[text_norm]
    if re.fullmatch(r"put\s+.+\s+on hold", text_norm) and "put on hold" in lookup:
        return lookup["put on hold"]
    parts = text_norm.split(" ")
    while len(parts) > 1 and parts[-1] in STRIP_TRAILING_WORDS:
        parts = parts[:-1]
        candidate = " ".join(parts)
        if candidate in lookup:
            return lookup[candidate]
    return None


def resolve(lesson_id, text_norm, lookup, global_lookup):
    """-> (key, matched:bool). Ưu tiên bảng của riêng bài học (tránh lẫn 20 từ trùng
    tên có bản sao ở topic khác); chỉ rơi xuống bảng toàn cục (558 từ) khi bài học
    hiện tại không có ứng viên nào khớp — xử lý ca truyện nhắc lại từ đã dạy ở bài
    trước (vd "clearance sale" dạy ở lesson-15, được nhắc lại ở lesson-16)."""
    key = resolve_in(text_norm, lookup)
    if key:
        return key, True

    override = OVERRIDES.get((lesson_id, text_norm))
    if override:
        return override, True

    key = resolve_in(text_norm, global_lookup)
    if key:
        return key, True

    return None, False


def tokenize_paragraph(text, lesson_id, lookup, global_lookup, is_vi, unresolved_report):
    text = SPLIT_PUT_ON_HOLD_RE.sub(lambda m: f"**put{m.group(1)}on hold**", text)

    tokens = []
    buf = []
    pos = 0
    for m in BOLD_RE.finditer(text):
        buf.append(text[pos:m.start()])
        label = m.group(1)
        text_norm = re.sub(r"\s+", " ", label.strip().lower())
        key, matched = resolve(lesson_id, text_norm, lookup, global_lookup)

        end = m.end()
        if matched:
            plain = "".join(buf)
            if plain:
                tokens.append(plain)
            buf = []
            word_part = key.split(":", 1)[1]
            token = {"w": key}
            if label != word_part:
                token["label"] = label
            tokens.append(token)
            if is_vi:
                gloss_m = GLOSS_RE.match(text[end:])
                if gloss_m:
                    end += gloss_m.end()
        else:
            buf.append(label)
            if (lesson_id, text_norm) not in KNOWN_UNRESOLVED:
                unresolved_report.append((lesson_id, "vi" if is_vi else "en", label))
        pos = end

    buf.append(text[pos:])
    tail = "".join(buf)
    if tail:
        tokens.append(tail)
    return tokens


def extract_vi_paragraphs(lesson_id):
    n = lesson_id.split("-")[1]
    lines = (STORY_VI_DIR / f"story-{n}.md").read_text(encoding="utf-8").splitlines()
    body_start = next(i for i, l in enumerate(lines) if l.strip() == "---") + 1
    body_end = next(i for i, l in enumerate(lines) if re.match(r"^\*Hết Chương", l.strip()))
    body = "\n".join(lines[body_start:body_end]).strip()
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def extract_en_paragraphs(lesson_id):
    n = lesson_id.split("-")[1]
    lines = (STORY_EN_DIR / f"story-{n}.md").read_text(encoding="utf-8").splitlines()
    chapter_idx = next(i for i, l in enumerate(lines) if l.strip().startswith("### Chapter"))
    body_start = chapter_idx + 1
    last_dash = max(i for i, l in enumerate(lines) if l.strip() == "---")
    body = "\n".join(lines[body_start:last_dash]).strip()
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def main():
    topic_by_lesson = parse_story_slug_table()
    words_index = load_words_by_lesson_topic()
    all_words = [w for ws in words_index.values() for w in ws]
    global_lookup = build_lookup(all_words)

    unresolved = []
    total_bold = 0
    total_matched = 0

    for n in range(1, 29):
        lesson_id = f"lesson-{n:02d}"
        topic = topic_by_lesson[lesson_id]
        words = words_index[(lesson_id, topic)]
        lookup = build_lookup(words)

        vi_paras = extract_vi_paragraphs(lesson_id)
        en_paras = extract_en_paragraphs(lesson_id)

        vi_before = len(unresolved)
        chem = [tokenize_paragraph(p, lesson_id, lookup, global_lookup, True, unresolved) for p in vi_paras]
        english = [tokenize_paragraph(p, lesson_id, lookup, global_lookup, False, unresolved) for p in en_paras]

        n_bold_vi = sum(len(BOLD_RE.findall(p)) for p in vi_paras)
        n_bold_en = sum(len(BOLD_RE.findall(p)) for p in en_paras)
        n_unresolved_this = len(unresolved) - vi_before
        total_bold += n_bold_vi + n_bold_en
        total_matched += n_bold_vi + n_bold_en - n_unresolved_this

        out_dir = LESSONS_DIR / lesson_id
        out_dir.mkdir(parents=True, exist_ok=True)
        with (out_dir / "tokens.json").open("w", encoding="utf-8") as f:
            json.dump({"chem": chem, "english": english}, f, ensure_ascii=False, indent=1)
            f.write("\n")

    print(f"Đã ghi tokens.json cho 28 bài học. Tổng {total_bold} vùng **bold**, khớp tự động {total_matched} ({total_matched/total_bold:.1%}).\n")

    if unresolved:
        print(f"{len(unresolved)} vùng KHÔNG khớp được (đã loại trừ {len(KNOWN_UNRESOLVED)} ca đã biết ở KNOWN_UNRESOLVED) — cần review tay:")
        for lesson_id, ver, text in unresolved:
            print(f"  - {lesson_id}/{ver}: {text!r}")
    else:
        print("Không còn vùng nào ngoài danh sách KNOWN_UNRESOLVED — chỉ còn 2 ca đã biết (round-trip, check-out) cần người quyết định thêm từ mới hay sửa truyện.")


if __name__ == "__main__":
    main()
