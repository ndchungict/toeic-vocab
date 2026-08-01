#!/usr/bin/env python3
"""
Bootstrap parser: TOEIC exercise-NN.md  ->  draft YAML.

This is a first-pass mechanical extractor, not a guaranteed-correct converter.
Hand-edited Markdown varies (extra blank lines, multi-paragraph explanations,
a missing blank in a passage, etc.), so every item is meant to be spot-checked
against the source before being treated as final. Items the script can't parse
cleanly are still emitted with a `# REVIEW:` comment above them on stderr and
a `_review: true` marker in the YAML, rather than being silently dropped.

Usage (from the repo root):
    python3 .claude/skills/toeic-execise-to-yaml/scripts/parse_execise.py \
        exercises/exercise-01.md exercise-01 > data/exercises/exercise-01.yaml

Source is always the local exercises/ directory; output always goes to data/exercises/.

Requires: PyYAML (pip install pyyaml --break-system-packages)
"""

import re
import sys


def die_usage():
    print(__doc__, file=sys.stderr)
    sys.exit(1)


def yaml_str(s):
    """Quote a scalar as a YAML double-quoted string, escaping safely."""
    if s is None:
        return "null"
    s = s.strip()
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def yaml_block(s, indent="    "):
    """Render a multi-line string as a YAML block scalar (|)."""
    s = s.strip("\n")
    lines = s.split("\n")
    out = ["|"]
    for line in lines:
        out.append(indent + line if line else "")
    return "\n".join(out)


def extract_section(text, start_pat, end_pats):
    m = re.search(start_pat, text)
    if not m:
        return ""
    start = m.end()
    end = len(text)
    for ep in end_pats:
        em = re.search(ep, text[start:])
        if em:
            end = min(end, start + em.start())
    return text[start:end]


def parse_lesson(text):
    m = re.search(r"lesson-(\d+)", text)
    return f"lesson-{m.group(1)}" if m else None


def parse_part5_questions(section_text):
    """Returns list of dicts: number, question, options(dict A-D)"""
    items = []
    pattern = re.compile(
        r"\*\*(\d+)\.\*\*\s*(.+?)\n\s*\(A\)\s*(.+?)\s*\(B\)\s*(.+?)\s*\(C\)\s*(.+?)\s*\(D\)\s*(.+?)\s*(?=\n\n|\*\*\d+\.\*\*|\Z)",
        re.DOTALL,
    )
    for m in pattern.finditer(section_text):
        num, q, a, b, c, d = m.groups()
        items.append({
            "number": int(num),
            "question": " ".join(q.split()),
            "options": {
                "A": " ".join(a.split()),
                "B": " ".join(b.split()),
                "C": " ".join(c.split()),
                "D": " ".join(d.split()),
            },
        })
    return items


def parse_answer_key_with_word(section_text):
    """Part 5/6 style: '1. **B (convene)** — explanation...'
    Returns dict number -> {letter, word, explanation}"""
    out = {}
    pattern = re.compile(
        r"^(\d+)\.\s*\*\*([A-D])\s*\(([^)]+)\)\*\*\s*[—-]\s*(.+?)(?=^\d+\.\s*\*\*|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for m in pattern.finditer(section_text):
        num, letter, word, expl = m.groups()
        out[int(num)] = {
            "letter": letter,
            "word": word.strip(),
            "explanation": " ".join(expl.split()),
        }
    return out


def parse_answer_key_no_word(section_text):
    """Part 7 style: '21. **B** — explanation...'
    Returns dict number -> {letter, explanation}"""
    out = {}
    pattern = re.compile(
        r"^(\d+)\.\s*\*\*([A-D])\*\*\s*[—-]\s*(.+?)(?=^\d+\.\s*\*\*|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for m in pattern.finditer(section_text):
        num, letter, expl = m.groups()
        out[int(num)] = {
            "letter": letter,
            "explanation": " ".join(expl.split()),
        }
    return out


def parse_passage_groups(section_text, has_blanks):
    """
    Splits a Part 6 or Part 7 section into passage groups.
    Each group starts with '**Questions NN[–MM]** refer to the following ...'
    followed by a blockquote passage, then either:
      - Part6: one/more lines of '**NN.** (A).. (B).. (C).. (D)..' possibly grouped
      - Part7: repeated '**NN.** question\\n(A)..(B)..(C)..(D)..' blocks
    Returns list of dicts: {numbers: [int,...], passage: str, questions: {...}}
    """
    groups = []
    header_pat = re.compile(
        r"\*\*Questions?\s+(\d+)(?:[–\-](\d+))?\*\*\s*refer to.*?\n"
    )
    headers = list(header_pat.finditer(section_text))
    for i, hm in enumerate(headers):
        g_start = hm.end()
        g_end = headers[i + 1].start() if i + 1 < len(headers) else len(section_text)
        block = section_text[g_start:g_end]

        first_q = int(hm.group(1))
        last_q = int(hm.group(2)) if hm.group(2) else first_q
        numbers = list(range(first_q, last_q + 1))

        # Passage = blockquote lines (lines starting with '>') up to first
        # non-blockquote content or the first '**NN.**' marker.
        passage_lines = []
        rest_start = 0
        for line in block.split("\n"):
            if line.strip().startswith(">"):
                passage_lines.append(re.sub(r"^\s*>\s?", "", line))
                rest_start += len(line) + 1
            elif not line.strip():
                rest_start += len(line) + 1
                if passage_lines:
                    continue
            else:
                break
        passage = "\n".join(passage_lines).strip()
        remainder = block[rest_start:]

        questions = {}
        if has_blanks:
            # Part 6: '**13.** (A)x (B)y (C)z (D)w' possibly several per line
            qpat = re.compile(
                r"\*\*(\d+)\.\*\*\s*\(A\)\s*(.+?)\s*\(B\)\s*(.+?)\s*\(C\)\s*(.+?)\s*\(D\)\s*(.+?)\s*(?=\*\*\d+\.\*\*|\Z)",
                re.DOTALL,
            )
            for qm in qpat.finditer(remainder):
                n, a, b, c, d = qm.groups()
                questions[int(n)] = {
                    "options": {
                        "A": " ".join(a.split()),
                        "B": " ".join(b.split()),
                        "C": " ".join(c.split()),
                        "D": " ".join(d.split()),
                    }
                }
        else:
            # Part 7: '**21.** question text\n(A)a (B)b (C)c (D)d'
            qpat = re.compile(
                r"\*\*(\d+)\.\*\*\s*(.+?)\n\s*\(A\)\s*(.+?)\s*\(B\)\s*(.+?)\s*\(C\)\s*(.+?)\s*\(D\)\s*(.+?)\s*(?=\n\n|\*\*\d+\.\*\*|\Z)",
                re.DOTALL,
            )
            for qm in qpat.finditer(remainder):
                n, q, a, b, c, d = qm.groups()
                questions[int(n)] = {
                    "question": " ".join(q.split()),
                    "options": {
                        "A": " ".join(a.split()),
                        "B": " ".join(b.split()),
                        "C": " ".join(c.split()),
                        "D": " ".join(d.split()),
                    },
                }

        groups.append({"numbers": numbers, "passage": passage, "questions": questions})
    return groups


def main():
    if len(sys.argv) != 3:
        die_usage()
    src_path, slug = sys.argv[1], sys.argv[2]

    with open(src_path, "r", encoding="utf-8") as f:
        text = f.read()

    lesson = parse_lesson(text)
    warnings = []

    # --- Question sections (before "## Đáp án") ---
    q_all = extract_section(text, r"##\s*Bài tập TOEIC", [r"##\s*Đáp án"])
    p5_q = extract_section(q_all, r"###\s*Part 5", [r"###\s*Part 6"])
    p6_q = extract_section(q_all, r"###\s*Part 6", [r"###\s*Part 7"])
    p7_q = extract_section(q_all, r"###\s*Part 7", [r"\Z"])

    # --- Answer sections (after "## Đáp án") ---
    a_all = extract_section(text, r"##\s*Đáp án", [r"##\s*Footer", r"\Z"])
    p5_a = extract_section(a_all, r"###\s*Part 5", [r"###\s*Part 6"])
    p6_a = extract_section(a_all, r"###\s*Part 6", [r"###\s*Part 7"])
    p7_a = extract_section(a_all, r"###\s*Part 7", [r"\Z"])

    # --- Parse ---
    p5_questions = parse_part5_questions(p5_q)
    p5_answers = parse_answer_key_with_word(p5_a)

    p6_groups = parse_passage_groups(p6_q, has_blanks=True)
    p6_answers = parse_answer_key_with_word(p6_a)

    p7_groups = parse_passage_groups(p7_q, has_blanks=False)
    # Part 7 usually has plain "21. **B** — ..." lines, but "closest in meaning to"
    # items are still vocab questions and keep the "22. **B (distributed)** — ..."
    # form. Try the word-bearing pattern first, then fill any gaps with the plain one.
    p7_answers = parse_answer_key_no_word(p7_a)
    p7_answers_with_word = parse_answer_key_with_word(p7_a)
    for num, ans in p7_answers_with_word.items():
        p7_answers[num] = {"letter": ans["letter"], "explanation": ans["explanation"]}
        p7_answers[num]["word"] = ans["word"]

    items = []

    # Part 5
    for q in p5_questions:
        n = q["number"]
        ans = p5_answers.get(n)
        item = {
            "id": f"{slug}-p5-{n:02d}",
            "part": 5,
            "lesson": [lesson] if lesson else None,
            "related_word": ans["word"] if ans else None,
            "question": q["question"],
            "options": q["options"],
            "answer": ans["letter"] if ans else None,
            "explanation_vi": ans["explanation"] if ans else None,
            "_review": ans is None,
        }
        if item["_review"]:
            warnings.append(f"Part5 Q{n}: no matching answer-key entry found")
        items.append(item)

    # Part 6
    for grp in p6_groups:
        group_id = f"p6-{grp['numbers'][0]}-{grp['numbers'][-1]}"
        if not grp["passage"]:
            warnings.append(f"Part6 group {group_id}: passage extraction looks empty")
        for n in grp["numbers"]:
            q = grp["questions"].get(n)
            ans = p6_answers.get(n)
            item = {
                "id": f"{slug}-p6-{n:02d}",
                "part": 6,
                "lesson": [lesson] if lesson else None,
                "passage_group": group_id,
                "passage": grp["passage"],
                "related_word": ans["word"] if ans else None,
                "options": q["options"] if q else None,
                "answer": ans["letter"] if ans else None,
                "explanation_vi": ans["explanation"] if ans else None,
                "_review": (q is None or ans is None),
            }
            if item["_review"]:
                warnings.append(f"Part6 Q{n}: missing options or answer-key entry")
            items.append(item)

    # Part 7
    for grp in p7_groups:
        group_id = f"p7-{grp['numbers'][0]}-{grp['numbers'][-1]}"
        if not grp["passage"]:
            warnings.append(f"Part7 group {group_id}: passage extraction looks empty")
        for n in grp["numbers"]:
            q = grp["questions"].get(n)
            ans = p7_answers.get(n)
            item = {
                "id": f"{slug}-p7-{n:02d}",
                "part": 7,
                "lesson": [lesson] if lesson else None,
                "passage_group": group_id,
                "passage": grp["passage"],
                "related_word": ans.get("word") if ans else None,
                "question": q["question"] if q else None,
                "options": q["options"] if q else None,
                "answer": ans["letter"] if ans else None,
                "explanation_vi": ans["explanation"] if ans else None,
                "_review": (q is None or ans is None),
            }
            if item["_review"]:
                warnings.append(f"Part7 Q{n}: missing question/options or answer-key entry")
            items.append(item)

    # --- Emit YAML by hand (full control over block scalars / quoting) ---
    out = []
    for it in items:
        out.append(f'- id: {yaml_str(it["id"])}')
        out.append(f'  part: {it["part"]}')
        out.append(f'  topic: null  # TODO fill in')
        out.append(f'  lesson: {it["lesson"] if it["lesson"] else "null"}')
        out.append(f'  level: null  # TODO fill in')
        if "passage_group" in it:
            out.append(f'  passage_group: {yaml_str(it["passage_group"])}')
            out.append(f'  passage: {yaml_block(it["passage"]) if it["passage"] else "null"}')
        out.append(f'  related_word: {yaml_str(it["related_word"]) if it["related_word"] else "null"}')
        if "question" in it:
            out.append(f'  question: {yaml_str(it["question"]) if it["question"] else "null"}')
        if it.get("options"):
            opts = it["options"]
            out.append(
                f'  options: {{ A: {yaml_str(opts["A"])}, B: {yaml_str(opts["B"])}, '
                f'C: {yaml_str(opts["C"])}, D: {yaml_str(opts["D"])} }}'
            )
        else:
            out.append('  options: null')
        out.append(f'  answer: {yaml_str(it["answer"]) if it["answer"] else "null"}')
        out.append(f'  explanation_vi: {yaml_str(it["explanation_vi"]) if it["explanation_vi"] else "null"}')
        if it["_review"]:
            out.append('  _review: true  # TODO: parser could not fully match this item, check against source')
        out.append("")

    print("\n".join(out))

    if warnings:
        print(f"\n--- {len(warnings)} REVIEW warning(s) for {src_path} ---", file=sys.stderr)
        for w in warnings:
            print(f"# REVIEW: {w}", file=sys.stderr)


if __name__ == "__main__":
    main()