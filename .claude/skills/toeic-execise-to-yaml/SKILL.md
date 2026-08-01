---
name: toeic-execise-to-yaml
description: Convert TOEIC exercise Markdown files from the local `exercises/` folder (the ones with a vocab table, Part 5/6/7 questions, and an answer+explanation section, e.g. exercise-01.md ... exercise-28.md) into structured YAML exercise data files written to `data/exercises/exercise-NN.yaml`. Use this whenever the user asks to "bóc tách bài tập", "chuyển exercise sang yaml", extract/parse/migrate TOEIC exercise markdown into YAML, or mentions the `exercises/exercise-NN.md` files needing a data format. Also use for batch-converting all 28 files at once, or for adding new exercise files to an existing YAML dataset in the same schema.
---

# TOEIC Exercise Markdown → YAML Converter

Converts the `exercises/exercise-NN.md` files (vocab table + Part 5/6/7 questions +
answer/explanation section) into the YAML exercise schema used by the TOEIC site.

**Paths (fixed, always local — never fetch from GitHub):**

| | Path |
|---|---|
| Source | `exercises/exercise-NN.md` (in this repo, read with the Read tool) |
| Output | `data/exercises/exercise-NN.yaml` |

Create `data/exercises/` if it doesn't exist yet. One output file per source file,
same `NN` number, e.g. `exercises/exercise-01.md` → `data/exercises/exercise-01.yaml`.

## Source file shape (what to expect)

Each exercise-NN.md follows this structure (confirmed against exercise-01.md):

```
# EXERCISE NN — <TOPIC LABEL>

> File luyện tập cho **lesson-NN** (...). Gồm bảng từ vựng, bài tập TOEIC (Part 5/6/7)
> và đáp án + giải thích. Truyện chêm & bản tiếng Anh nằm ở `lessions/lesson-NN.md`.
> NN từ (...).

## Bảng tổng hợp từ vựng
| Từ | Phiên âm (IPA) | Loại | Nghĩa | Collocation thường gặp | Ví dụ câu tiếng Anh |
|...]

## Bài tập TOEIC (tự làm trước, chưa xem đáp án)

### Part 5 — Incomplete Sentences
**1.** <sentence with ______>
(A) opt1 (B) opt2 (C) opt3 (D) opt4
... (repeats, ~12 items)

### Part 6 — Text Completion
**Questions 13–16** refer to the following memo.
> <passage with (13)______ (14)______ (15)______ (16)______ inline>
**13.** (A)... (B)... (C)... (D)...  **14.** (A)... ...  (all 4 blanks' options on one or two lines)
... (repeats for a second passage, e.g. 17-20)

### Part 7 — Reading Comprehension
**Questions 21–23** refer to the following notice.
> <passage, no blanks>
**21.** <question> (A)... (B)... (C)... (D)...
... (repeats per question, then a second passage e.g. 24-26)

## Đáp án & giải thích
### Part 5
1. **B (convene)** — explanation in Vietnamese, mentions why others are wrong.
...
### Part 6
13. **A (notify)** — explanation.
...
### Part 7
21. **B** — explanation.   <-- NOTE: no "(word)" here, since Part 7 questions are
                                comprehension questions, not vocab-in-blank questions.
...
```

**Important quirks to watch for per file** (don't assume every file is identical —
skim the raw file first):
- Some files may only have one Part 6 passage instead of two, or a different number
  of Part 7 question groups. Count the actual `**NN.**` markers, don't assume 12/8/6.
- The vocab table's "Loại" column uses short POS tags (`n`, `v`, `adj`, `v/n`, `phr`) —
  normalize these when producing `related_word` / vocab cross-references (see below).
- Part 5/6 answer explanations embed the correct word in parentheses after the letter,
  e.g. `**B (convene)**` — extract both the letter AND the word.
- Part 7 answer lines are usually just the letter (`**B**`), no word, for pure
  comprehension questions. BUT "closest in meaning to ___" items (vocab-in-context,
  still Part 7) keep the `**B (distributed)**` form like Part 5/6 — the script tries
  both patterns per item, but skim the answer key yourself too since this is exactly
  the kind of inconsistency regex can misjudge.

## Conversion workflow

1. **Read the local source file** at `exercises/exercise-NN.md` with the Read tool.
   Do not fetch anything over the network — the markdown in the working tree is the
   source of truth, including uncommitted edits.
2. **Run the bootstrap parser** (`scripts/parse_execise.py`) on that file path.
   It handles the mechanical extraction (splitting Part 5/6/7, pairing questions with
   answer-key lines, pulling the passage for Part 6/7) and emits a first-draft YAML.
   It is a *bootstrap*, not a guaranteed-correct final output — regex parsing of
   hand-written Markdown will occasionally misfire (e.g. a passage with an extra blank
   line, or an explanation that spans two paragraphs). Always read its output and spot
   check it against the source before treating it as final, especially:
   - Part 6/7 passages (multi-line blockquotes are the most fragile part to parse)
   - Any question where `options` has fewer/more than 4 entries (parser flags these
     with a `# REVIEW` comment)
3. **Fill in fields the source file doesn't state explicitly**: `topic`, `lesson`,
   `level`. Derive `lesson` from the blockquote intro (e.g. "lesson-01"). `topic` and
   `level` aren't in the exercise file itself — take them from the topic's word-list YAML
   (`data/words/<topic>.yaml`) whenever one exists, so the two datasets stay consistent:
   `topic` = that file's topic slug (the exercise title names it, e.g. "EXERCISE 01 —
   OFFICES" → `offices`), and `level` = the `level:` of the item's `related_word` entry.
   Items with `related_word: null` get `level: null` — don't guess. Only ask the user if
   no word-list file covers that lesson.
4. **Cross-link `related_word`.** Hard rule: `related_word` may only hold a word that
   actually exists as a `word:` entry in the topic's word-list YAML (`data/words/<topic>.yaml`).
   It is a join key into the vocab dataset, not free text.
   - Normalize the answer-key word to the lemma used in the word list before writing it,
     e.g. `enclosed` → `enclose`, `transferred` → `transfer a call`.
   - If the answer word has no matching entry, write `related_word: null` — never invent
     an entry or store the raw inflected/unlisted word. This covers most Part 7
     comprehension questions, and also Part 7 "closest in meaning to ___" items whose
     answer is a synonym outside the word list (e.g. `circulated` → `distributed`:
     neither is in the list, so `null`).
   - After generating, verify every non-null `related_word` resolves against the word
     list and report any that don't — don't ship an unresolved one silently.
5. **Write one YAML file per source file** to `data/exercises/exercise-NN.yaml` rather
   than one giant combined file, mirroring the source structure — easier to diff/review,
   and matches how the site loads per-lesson data (Hugo picks it up as
   `site.Data.exercises`).

## Output schema

Follow this shape (matches the site's exercise schema discussed earlier in this
conversation — id prefix `exercise-{NN}-p{part}-{NN}`, zero-padded per exercise file):

```yaml
# Part 5 item
- id: "exercise-01-p5-01"
  part: 5
  topic: "offices"            # fill in / confirm with user
  lesson: ["lesson-01"]
  level: null                 # fill in / confirm with user
  related_word: "convene"
  question: "The board of directors will ______ next Tuesday to vote on the expansion plan."
  options: { A: "enclose", B: "convene", C: "remind", D: "postpone" }
  answer: "B"
  explanation_vi: "\"convene a meeting\" = triệu tập họp. Các từ kia không hợp: enclose (gửi kèm), remind (nhắc), postpone (hoãn)."

# Part 6 item — same shape, plus shared passage per question group
- id: "exercise-01-p6-13"
  part: 6
  topic: "offices"
  lesson: ["lesson-01"]
  level: null
  passage_group: "p6-13-16"   # groups blanks 13-16 under the same passage
  passage: |
    MEMORANDUM
    To: All Department Heads
    From: Priya Nair, Corporate Services
    Re: Project Aria Kickoff

    Following this morning's board meeting, I am writing to (13)______ you of an
    important decision. The board has approved moving forward with Project Aria...
  related_word: "notify"
  options: { A: "notify", B: "enclose", C: "adjourn", D: "chair" }
  answer: "A"
  explanation_vi: "\"writing to notify you of a decision\" = viết để thông báo."

# Part 7 item — comprehension question, no related_word, includes passage
- id: "exercise-01-p7-21"
  part: 7
  topic: "offices"
  lesson: ["lesson-01"]
  level: null
  passage_group: "p7-21-23"
  passage: |
    NOTICE TO BOARD MEMBERS
    Please be advised that the quarterly meeting of the board of directors...
  related_word: null
  question: "Why was the notice sent?"
  options: { A: "To announce a new product", B: "To inform members of a schedule change", C: "To request a payment", D: "To advertise a job opening" }
  answer: "B"
  explanation_vi: "Thông báo gửi để báo việc dời lịch họp (từ 3/3 sang 10/3)."
```

Notes on the schema choices:
- `passage_group` lets multiple Part 6/7 questions share one passage without repeating
  it as a string per question (still repeat the actual `passage:` value per item for
  simplicity when rendering — repetition is cheap in YAML/JSON, and keeps each item
  self-contained for shuffling/rendering without a join step).
- Keep `options` as a mapping (`A:`/`B:`/`C:`/`D:`), matching the schema already agreed
  for the site.
- `level` is nullable — many exercise files don't state it; don't guess, ask the user.

## Batch conversion (all 28 files)

When asked to convert all of them:
1. Read each local file, `exercises/exercise-01.md` through `exercises/exercise-28.md`.
2. Run each through `scripts/parse_execise.py`.
3. Collect all `# REVIEW` flagged items across all 28 files into one list and show it
   to the user before finalizing — this is far more efficient than asking them to
   review 28 files individually.
4. Ask the user once for the topic/level mapping across all 28 exercises (a single
   short table), rather than asking per file.
5. Write output as `data/exercises/exercise-01.yaml` ... `data/exercises/exercise-28.yaml`.

## Script

`scripts/parse_execise.py` (inside this skill folder) — run from the repo root as:

```bash
mkdir -p data/exercises
python3 .claude/skills/toeic-execise-to-yaml/scripts/parse_execise.py \
  exercises/exercise-01.md exercise-01 > data/exercises/exercise-01.yaml
```

Whole batch:

```bash
mkdir -p data/exercises
for f in exercises/exercise-*.md; do
  slug=$(basename "$f" .md)
  python3 .claude/skills/toeic-execise-to-yaml/scripts/parse_execise.py \
    "$f" "$slug" > "data/exercises/$slug.yaml"
done
```

First positional arg is the source markdown file, second is the exercise slug used to
build `id` prefixes (e.g. `exercise-01` → ids like `exercise-01-p5-01`). It prints YAML
to stdout and any `# REVIEW: ...` warnings to stderr — always check stderr output.