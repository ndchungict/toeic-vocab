# Kế hoạch xây dựng website TOEIC Vocab

> **Trạng thái:** Bản nháp 1 — hoàn chỉnh mọi phần TRỪ §1 (Phân tích mockup).
> Mọi phần khác dựa trên **file dữ liệu thật** đã đọc và parse, không phỏng đoán.
>
> Ngày lập: 2026-08-01 · Repo: `ndchungict/toeic-vocab` · Nhánh: `main`

---

## Mục lục

1. [Phân tích mockup](#1-phân-tích-mockup) — **CHỜ FILE**
2. [Phân tích dữ liệu](#2-phân-tích-dữ-liệu)
3. [Kiến trúc nội dung Hugo](#3-kiến-trúc-nội-dung-hugo)
4. [Chuyển dữ liệu thô → nội dung Hugo](#4-chuyển-dữ-liệu-thô--nội-dung-hugo)
5. [Thiết kế theme & layout](#5-thiết-kế-theme--layout)
6. [Cấu hình Hugo](#6-cấu-hình-hugo)
7. [GitHub Actions & deploy](#7-github-actions--deploy)
8. [Cây thư mục dự kiến](#8-cây-thư-mục-dự-kiến)
9. [Giai đoạn triển khai](#9-giai-đoạn-triển-khai-milestones)
10. [Giả định & câu hỏi còn mở](#10-giả-định--câu-hỏi-còn-mở)

---

## 1. Phân tích mockup

> ⛔ **CHƯA LÀM ĐƯỢC — chưa đọc được file.**
>
> **Đã thử:**
> 1. Quét toàn repo tìm `*.html` / `*.htm` / `*.css` / `*.jsx` / `*.tsx` → **0 kết quả**.
> 2. Link bạn gửi: `https://claude.ai/design/p/ca91e60a-7f1a-4e85-8f39-13557a18e1fd?file=TOEIC+Vocab.dc.html`
>    → **HTTP 403 Forbidden**. Đây là link chia sẻ Claude Design, không nằm trong
>    namespace artifact mà tool fetch đọc được. Thử cả bản không có query param → vẫn 403.
> 3. Liệt kê artifact được chia sẻ với tài khoản → danh sách rỗng.
> 4. `raw/` bị chặn đọc bởi deny rule trong `.claude/settings.json`
>    (`Read(raw/**)`, `Grep(raw/**)`) nên cũng không kiểm tra được ở đó.
>
> **Cần bạn làm:** mở link đó, bấm tải/copy nội dung file `TOEIC Vocab.dc.html`, rồi lưu
> vào repo tại `design/TOEIC-Vocab.dc.html`. Sau đó mục này sẽ được điền đầy đủ.

### 1.1 Checklist sẽ trích xuất khi có mockup

Khi có file, mục này phải trả lời được đúng những câu dưới đây — **không thêm tính năng
ngoài mockup**:

**A. Danh sách trang (sitemap thật của mockup)**
- [ ] Có bao nhiêu màn hình / route riêng biệt? Tên và mục đích từng màn.
- [ ] Trang chủ hiển thị gì (hero, danh sách chủ đề, tiến độ học, CTA)?
- [ ] Có trang danh sách chủ đề riêng, hay chủ đề nằm luôn ở trang chủ?
- [ ] Có trang chi tiết **từ vựng** riêng cho từng từ không, hay chỉ modal/expand?
- [ ] Trang bài học: truyện EN/VI hiển thị cùng trang (tab/toggle) hay 2 trang tách?
- [ ] Trang bài tập: cùng trang bài học hay tách riêng? Đáp án hiện ngay hay sau khi nộp?
- [ ] Có trang flashcard / luyện tập lặp lại không?
- [ ] Có trang tìm kiếm, trang "về dự án", trang 404 tùy biến không?

**B. Component tái sử dụng**
- [ ] Header / nav (mobile menu kiểu gì?), footer
- [ ] Card chủ đề — có ảnh không, có badge số từ / số bài không
- [ ] Card / row từ vựng — hiển thị field nào: `word`, `pos`, `ipa`, `meaning`,
      `forms`, `collocations`, `example`, `note`? Cái nào ẩn/hiện?
- [ ] Nút phát âm (audio) — có không? Dùng nguồn nào?
- [ ] Khối truyện chêm — cách đánh dấu từ được chêm (`**bold**` → styling gì? có tooltip
      hiện nghĩa khi hover không?)
- [ ] Toggle EN/VI
- [ ] Component câu hỏi trắc nghiệm (Part 5), khối đoạn văn + blank (Part 6),
      khối đoạn văn + câu hỏi đọc hiểu (Part 7)
- [ ] Khối đáp án + giải thích tiếng Việt
- [ ] Thanh tiến độ / trạng thái "đã học"
- [ ] Breadcrumb, phân trang, nút prev/next bài học
- [ ] Ô tìm kiếm / bộ lọc (theo `level` 600/750/900, theo `pos`, theo `sub-topic`)

**C. Design tokens**
- [ ] Bảng màu: primary / secondary / accent / success / danger / warning /
      nền / nền phụ / chữ chính / chữ phụ / viền — ghi mã hex, và có dark mode không
- [ ] Typography: font family (heading vs body vs mono), font-size scale,
      line-height, font-weight. **Lưu ý font phải hỗ trợ tiếng Việt đầy đủ**
      (Inter, Be Vietnam Pro, Nunito Sans, Source Sans 3 đều OK; nhiều font display thì không)
- [ ] Spacing scale (4px/8px base?), border-radius, shadow, transition
- [ ] Container max-width, grid columns, breakpoints responsive
- [ ] Icon set (inline SVG / icon font / thư viện nào)

**D. Ràng buộc kỹ thuật rút ra từ mockup**
- [ ] CSS: thuần / Tailwind / Bootstrap / framework khác → quyết định cách tái hiện (xem §5.2)
- [ ] JS: có tương tác gì (tab, accordion, quiz, filter, dark mode toggle, localStorage)
- [ ] Có gọi CDN ngoài không (font, icon, JS lib) → cần tự host cho GitHub Pages ổn định

### 1.2 Ảnh hưởng tới các phần khác

Ba quyết định trong plan này **phụ thuộc mockup** và đang để ở dạng có điều kiện:
- Có sinh trang chi tiết cho từng từ hay không (§3.3) → ảnh hưởng ~558 trang
- Có cần search client-side hay không (§5.5)
- Có cần trang flashcard + localStorage hay không (§9, M6)

---

## 2. Phân tích dữ liệu

Tất cả số liệu dưới đây lấy trực tiếp từ file trong `data/` (parse bằng PyYAML,
không ước lượng).

### 2.1 Tổng quan

| Nguồn | Số file | Định dạng | Nội dung |
|---|---|---|---|
| `data/words/` | 13 | YAML (list phẳng) | 558 entry từ vựng (537 từ duy nhất) |
| `data/story/story-en/` | 28 | Markdown | Truyện tiếng Anh, 1 file/bài |
| `data/story/story-vi/` | 28 | Markdown | Truyện chêm tiếng Việt, 1 file/bài |
| `data/exercises/` | 28 | YAML (list phẳng) | 704 câu hỏi (Part 5/6/7) |
| `data/slugs/` | 2 | Markdown (bảng) | Bảng tra slug chủ đề & bảng 28 chương |

**Trục tổ chức chính là `lesson-NN` (NN = 01…28)** — nó nối cả 4 nguồn lại:

```
                    data/slugs/story-slug.md   (bảng chủ)
                              │
              ┌───────────────┼───────────────┬──────────────────┐
              ▼               ▼               ▼                  ▼
   data/words/<topic>.yaml    story-vi/       story-en/     data/exercises/
   (lesson: ["lesson-01"])    story-01.md     story-01.md   exercise-01.yaml
                                                            (lesson: ["lesson-01"])
```

### 2.2 `data/slugs/` — hai bảng tra (metadata gốc)

Đây là **nguồn chân lý (source of truth) về phân loại**, nhưng viết bằng bảng Markdown
chứ không phải dữ liệu máy đọc được. Hugo **không** load được `.md` từ `data/` (chỉ đọc
`.yaml/.json/.toml/.xml/.csv`) → phải chuyển sang YAML, xem §4.2.

**`category-slug.md`** — 13 chủ đề chính, 30 chủ đề con:

| topic slug | sub-topic |
|---|---|
| `corporate-development` | *(không có)* |
| `dining-out` | *(không có)* |
| `entertainment` | *(không có)* |
| `finance-budgeting` | `banking`, `accounting-invoicing`, `investment`, `tax-budgeting` |
| `general-business` | `contracts-negotiation`, `mergers-restructuring`, `marketing-sales`, `warranty`, `business-planning`, `conferences`, `labor-relations` |
| `health` | *(không có)* |
| `housing-property` | `renting-buying`, `construction-specs`, `utilities-maintenance` |
| `manufacturing` | *(không có)* |
| `offices` | `meetings-committees`, `correspondence`, `equipment-furniture`, `work-procedures` |
| `personnel` | `recruitment-application`, `training-evaluation`, `salary-benefits`, `promotion-departure` |
| `purchasing` | `ordering`, `inventory-supplies`, `shipping`, `invoicing-payment` |
| `technical-areas` | *(không có)* |
| `travel` | `tickets-schedules`, `hotels`, `car-rental-commute` |

File này **cũng chứa bảng ánh xạ slug → tên tiếng Việt** (dòng 23–29), ví dụ
`banking` = "Ngân hàng", `salary-benefits` = "Lương & Phúc lợi". Đây là nguồn duy nhất
có nhãn tiếng Việt cho sub-topic → bắt buộc giữ lại khi chuyển sang YAML.

⚠️ **Thiếu:** không có nhãn tiếng Việt cho 13 topic chính (chỉ có slug). Xem §10 (Q3).

**`story-slug.md`** — 28 chương truyện dài *"Project Aria"* (Aster Home Technologies),
mỗi dòng có: số chương, **Hồi** (I–IV), lesson file, topic, tên chương EN, story slug.

| Hồi | Chương | Chủ đề |
|---|---|---|
| I — Khởi đầu | 1–8 | offices ×2, personnel ×2, general-business ×4 |
| II — Ra thế giới | 9–16 | travel ×2, dining-out ×2, finance-budgeting ×2, purchasing ×2 |
| III — Khủng hoảng & tôi luyện | 17–24 | manufacturing ×2, corporate-development ×2, technical-areas ×2, housing-property ×2 |
| IV — Định đoạt | 25–28 | health ×2, entertainment ×2 |

→ **Mỗi topic có đúng 2 lesson**, trừ `general-business` (4 lesson: 5–8).

→ **Nhận xét quan trọng:** đây không phải 28 bài rời rạc mà là **một truyện dài liền
mạch có cốt truyện, 4 hồi, nhân vật xuyên suốt** (Diane Whitfield, Priya Nair,
Harold Vance, Ray Osei, Auri Cortez…). Nhiều chương kết bằng câu dẫn sang chương sau.
Điều này ảnh hưởng tới UX: **thứ tự bài học có ý nghĩa**, cần nút "Chương trước / Chương
sau" và mục lục theo hồi, không chỉ là lưới card rời rạc.

### 2.3 `data/words/*.yaml` — từ vựng

Một file = một `topic`, tên file = slug (`offices.yaml`). Cấp cao nhất là **list phẳng**,
không bọc key.

Schema (đã xác nhận đồng nhất 100% trên cả 558 entry):

| Field | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| `word` | string | 558/558 | dạng gốc, viết thường |
| `pos` | string | 558/558 | noun 396 · verb 89 · adjective 58 · phrasal verb 8 · preposition 5 · adverb 2 |
| `ipa` | string | 558/558 | `"/bɔːd əv daɪˈrektəz/"` |
| `meaning` | string | 558/558 | tiếng Việt, theo ngữ cảnh TOEIC |
| `topic` | string | 558/558 | slug, khớp `category-slug.md` |
| `sub-topic` | string \| null | 558/558 | **null ở 209 entry** (topic không có sub-topic) |
| `lesson` | list[string] | 558/558 | luôn là mảng, vd `["lesson-07", "lesson-20"]` |
| `level` | int | 558/558 | 600 (211) · 750 (240) · 900 (107) |
| `forms` | map | 558/558 | key = loại từ; value là string **hoặc list** |
| `collocations` | list[{en,vi}] | 558/558 | 2–4 cụm |
| `example` | {en,vi} | 558/558 | `en` bọc từ đích trong `{…}`, `vi` không bọc |
| `note` | string | **210/558** | chỉ có khi từ dễ nhầm |

**Bốn điểm phải xử lý ở template:**

1. **`example.en` chứa marker `{…}`** — 558/558 entry đều có. Đây không phải Markdown,
   template phải tự parse: `{convened}` → `<mark class="tw">convened</mark>`.
   Marker này được thiết kế để "khoét lỗ" sinh câu hỏi Part 5 (theo `toeic-vocab-yaml/SKILL.md`).
   → cần partial `word/example.html` dùng `replaceRE`.

2. **`forms` có value không đồng nhất** — có thể là string (`noun: "committee"`) hoặc
   list (`noun: ["chair", "chairperson"]`). Template phải kiểm tra kiểu trước khi range,
   không thì vỡ. Dùng `reflect.IsSlice`.

3. **`sub-topic: null` ở 209/558 entry** — 6 topic không có sub-topic. Template lọc theo
   sub-topic phải bỏ qua nhóm null, và trang topic phải render được cả 2 dạng
   (có nhóm con / không nhóm con).

4. **`word` KHÔNG duy nhất toàn cục** — 558 entry nhưng chỉ 537 từ duy nhất.
   **20 từ xuất hiện ở 2–3 file chủ đề khác nhau, với nghĩa khác nhau:**

   | Từ | Xuất hiện ở |
   |---|---|
   | `coverage` | entertainment, general-business, health |
   | `cutting-edge`, `obsolete` | corporate-development, technical-areas |
   | `implement` | corporate-development, general-business |
   | `reservation`, `complimentary` | dining-out, travel |
   | `venue` | dining-out, general-business |
   | `server` | dining-out, technical-areas |
   | `feature` | entertainment, technical-areas |
   | `invoice`, `stock`, `surplus` | finance-budgeting, purchasing |
   | `defect` | general-business, manufacturing |
   | `expire` | general-business, travel |
   | `eligible` | health, personnel |
   | `appraisal` | housing-property, personnel |
   | `specification` | housing-property, technical-areas |
   | `streamline` | manufacturing, offices |
   | `supplies` | offices, purchasing |
   | `vacancy` | personnel, travel |

   → **Hệ quả kiến trúc:** nếu làm trang chi tiết từng từ, URL phải là
   `/words/<topic>/<word>/` chứ không phải `/words/<word>/`, nếu không các trang sẽ đè nhau.

   → **Hệ quả localStorage:** `toeic-vocab-yaml/SKILL.md` nói `word` là "khóa định danh
   của thẻ trong localStorage". Với 20 từ này khóa sẽ **đụng độ** — đánh dấu đã thuộc
   `stock` (finance) sẽ vô tình đánh dấu luôn `stock` (purchasing). Khóa phải là
   `<topic>:<word>`. Xem §10 (Q4).

Phân bố số từ / chủ đề: general-business 85 · finance-budgeting 52 · personnel 49 ·
offices 44 · purchasing 40 · travel 40 · housing-property 39 · health 37 ·
technical-areas 36 · corporate-development 35 · entertainment 35 · manufacturing 34 ·
dining-out 32. Phân bố / bài học: 15–29 từ mỗi bài, **cả 28 bài đều được phủ**.

### 2.4 `data/story/` — truyện chêm

Markdown thuần, **không có front matter**. Cấu trúc chuẩn của cả 2 phiên bản:

```markdown
# LESSON 01 — OFFICES: Họp & Ủy ban · Thư từ & Liên lạc      ← dòng 1: H1
                                                              ← dòng 2: trống
> **Chương 1** của truyện dài *"Project Aria"* — ...          ← dòng 3–5: blockquote
> 27 từ (mục 9.1 + 9.2 trong `vocab-list.md`).                   metadata (chương, số
> Nhân vật chính: **Diane Whitfield** (CEO), ...                  từ, nhân vật, hồi)
                                                              ← dòng 6: trống
---                                                           ← dòng 7: hr
                                                              ← dòng 8: trống
### Chapter 1 — The Vote        (CHỈ có ở bản EN, từ dòng 9)  ← dòng 9+: thân truyện
<thân truyện>
---                                                           ← dòng cuối: hr
```

**Cách đánh dấu từ vựng — khác nhau giữa 2 bản, đây là điểm mấu chốt:**

- **Bản VI (truyện chêm thật):** `**từ_tiếng_anh** (nghĩa tiếng Việt)`
  → `cô đã gửi một **memo** (thông báo nội bộ) tới toàn bộ **board of directors** (hội đồng quản trị)`
  Có cả dạng tách rời: `**put** người đó **on hold** (cho giữ máy)`
- **Bản EN (truyện thường):** chỉ `**từ**`, không có ngoặc dịch
  → `she had sent a **memo** to the entire **board of directors**`

→ Regex trích từ được chêm khác nhau cho 2 bản. Template có thể tận dụng: bọc `**từ**`
thành link/tooltip trỏ về entry từ vựng tương ứng (xem §10 Q6 — mặc định **không làm**
vì là tính năng ngoài mockup).

**Điểm khác biệt & lỗi dữ liệu đã phát hiện:**

| Vấn đề | Chi tiết | Xử lý |
|---|---|---|
| ⚠️ **3 file EN bị lẫn bản VI** | `story-en/story-02.md`, `story-03.md`, `story-14.md` chứa **cả bản VI rồi mới tới `### Chapter N`**. Heading `### Chapter` nằm ở dòng 29 / 31 / 23 thay vì dòng 9 như 25 file còn lại. | Sửa tay khi migrate (M1) — cắt phần VI trùng lặp |
| Bản VI không có `### Chapter` | 0/28 file VI có heading chương; 28/28 file EN có | Lấy tên chương EN từ `story-slug.md` làm nguồn chuẩn, không parse từ file |
| Tiêu đề H1 dùng nhãn tự do | `# LESSON 11 — DINING OUT: Đặt bàn · Tiếp khách & Tiệc chiêu đãi` nhưng `dining-out` **không có sub-topic** trong `category-slug.md` | Nhãn H1 là văn bản hiển thị, KHÔNG dùng làm slug. Chỉ dùng `story-slug.md` để lấy topic |
| Câu dẫn chương sau | Nhiều file VI kết bằng `*Hết Chương N. Chương sau (lesson-NN): …*` | Tách thành field `teaser` trong front matter (§10 Q7) |
| `story-28` | Tiêu đề có `*(HỒI KẾT)*` | Bình thường, giữ nguyên |

**Trạng thái git:** thư mục cũ `data/lessions/` (sai chính tả, 56 file) đã bị xóa khỏi
working tree nhưng **chưa commit**; thư mục mới `data/story/` chưa được track.
→ Việc đầu tiên của M0 là commit lại lần đổi tên này cho sạch lịch sử.

### 2.5 `data/exercises/*.yaml` — bài tập & đáp án

Một file = một bài học (`exercise-01.yaml` ↔ `lesson-01`). **Ánh xạ 1:1 tuyệt đối, đã
kiểm chứng cả 28 file**: mỗi file chỉ chứa duy nhất một `topic` và một `lesson`, và
`topic` khớp chính xác với bảng `story-slug.md`.

Tổng **704 câu**: Part 5 = 326 · Part 6 = 210 · Part 7 = 168 (trung bình 25 câu/bài).

Schema **khác nhau theo `part`** — điểm quan trọng nhất khi làm template:

| Field | Part 5 (326) | Part 6 (210) | Part 7 (168) |
|---|:---:|:---:|:---:|
| `id`, `part`, `topic`, `lesson`, `level` | ✅ | ✅ | ✅ |
| `related_word` | ✅ | ✅ | ✅ (nhiều `null`) |
| `options` (map A/B/C/D) | ✅ | ✅ | ✅ |
| `answer` (chữ cái) | ✅ | ✅ | ✅ |
| `explanation_vi` | ✅ | ✅ | ✅ |
| `question` | ✅ | ❌ **không có** | ✅ |
| `passage_group` | ❌ | ✅ | ✅ |
| `passage` | ❌ | ✅ | ✅ |

→ **Part 6 không có `question`** vì chỗ trống nằm ngay trong `passage`
(`I am writing to **(13)______** you of…`). Template Part 6 phải render passage một lần
cho cả nhóm rồi liệt kê options theo số blank — **không** render lại passage 4 lần.

→ `passage` bị **lặp nguyên văn** ở mọi item trong cùng `passage_group` (đúng chủ ý của
`toeic-execise-to-yaml/SKILL.md`: *"repetition is cheap… keeps each item self-contained"*).
Template phải **group by `passage_group`** rồi lấy passage của item đầu tiên.

→ `passage` chứa **Markdown** (`**MEMORANDUM**`, `**(13)______**`) → phải chạy qua
`markdownify`/`.RenderString`, không in thô. `explanation_vi` cũng vậy.

→ `related_word`: 527 non-null, 177 null. **Đã verify: 100% giá trị non-null đều resolve
được** về một `word` trong `data/words/` → an toàn để làm khóa join, cho phép link mỗi
câu hỏi tới thẻ từ vựng tương ứng.

→ `id` theo mẫu `exercise-01-p5-01`. Lưu ý: SKILL.md ghi mẫu `ex01-p5-01` nhưng **dữ liệu
thật dùng `exercise-01-p5-01`** — dữ liệu thật là chuẩn (xem §10.3).

### 2.6 Bảng ánh xạ tổng hợp: file → nội dung

Với `NN` = 01…28:

| Đầu vào | Đích trên site |
|---|---|
| `data/slugs/story-slug.md` dòng NN | Front matter bài học: `title`, `chapter`, `act`, `topic`, `story_slug` |
| `data/story/story-vi/story-NN.md` (bỏ 8 dòng đầu) | Thân truyện — tab **VI** |
| `data/story/story-en/story-NN.md` (từ `### Chapter` trở đi) | Thân truyện — tab **EN** |
| `data/words/<topic>.yaml` lọc `lesson` chứa `"lesson-NN"` | Danh sách từ vựng của bài |
| `data/exercises/exercise-NN.yaml` | Bài tập + đáp án của bài |
| `data/slugs/category-slug.md` | Trang chủ đề, taxonomy, nhãn hiển thị |

---

## 3. Kiến trúc nội dung Hugo

### 3.1 Nguyên tắc phân loại: cái gì là *content*, cái gì là *data*

Quy tắc quyết định: **văn xuôi do người viết & sửa tay → `content/`. Dữ liệu có cấu trúc
do skill sinh ra → `data/`.**

| Nguồn | Đích | Lý do |
|---|---|---|
| Truyện EN/VI | `content/lessons/lesson-NN/` | Là văn xuôi, cần render Markdown, cần URL riêng, cần SEO, sẽ được sửa tay. **Bắt buộc**: Hugo không load `.md` từ `data/` |
| `data/words/*.yaml` | **Giữ nguyên** ở `data/` | Dữ liệu thuần, do skill `toeic-vocab-yaml` sinh, không sửa tay. `site.Data.words` dùng được ngay |
| `data/exercises/*.yaml` | **Giữ nguyên** ở `data/` | Như trên, do skill `toeic-execise-to-yaml` sinh. SKILL.md đã ghi rõ *"Hugo picks it up as `site.Data.exercises`"* |
| `data/slugs/*.md` | → `data/taxonomy.yaml` | Hugo không đọc `.md` trong `data/`. Chuyển 1 lần sang YAML |

### 3.2 Content sections

```
content/
├── _index.md                     # Trang chủ
├── lessons/
│   ├── _index.md                 # Mục lục 28 chương, nhóm theo 4 Hồi
│   ├── lesson-01/                # ← leaf bundle
│   │   ├── index.md              #   front matter + thân truyện VI
│   │   └── story-en.md           #   page resource: thân truyện EN
│   ├── lesson-02/
│   └── … lesson-28/
├── topics/
│   ├── _index.md                 # Lưới 13 chủ đề
│   └── _content.gotmpl           # Content Adapter → sinh 13 trang (§4.3)
└── words/                        # ← CÓ ĐIỀU KIỆN, chờ mockup (§1.2)
    └── _content.gotmpl           #   sinh 558 trang /words/<topic>/<word>/
```

**Vì sao lesson dùng leaf bundle 2 file** thay vì 2 trang tách `/lessons/lesson-01/vi/`
và `/lessons/lesson-01/en/`:
- Truyện EN và VI là **cùng một nội dung**; tách 2 URL sẽ chia nhỏ tín hiệu SEO và tạo
  duplicate content.
- Người học thường **đối chiếu qua lại** EN↔VI → toggle client-side mượt hơn điều hướng.
- Trong leaf bundle, `story-en.md` là **page resource**; template lấy bằng
  `(.Resources.Get "story-en.md").Content` — Hugo vẫn render Markdown đầy đủ.
- Chỉ 1 URL/bài → prev/next chương đơn giản, `.Prev`/`.Next` trong section chạy đúng.

> Đây **không** phải Hugo multilingual (`defaultContentLanguage` + `.en.md`). Site chỉ có
> **một** ngôn ngữ giao diện là tiếng Việt; EN/VI ở đây là 2 phiên bản của *nội dung học*,
> không phải 2 bản dịch của cả website. Dùng i18n sẽ nhân đôi toàn bộ site một cách vô ích.

### 3.3 Trang chi tiết từ vựng — quyết định có điều kiện

**Chưa chốt, chờ mockup.** Ba phương án:

| PA | Mô tả | Số trang | Khi nào chọn |
|---|---|---|---|
| **A** | Không có trang riêng. Từ vựng hiển thị dạng card/accordion trong trang bài học & trang chủ đề | 0 | Mockup không có màn hình chi tiết từ → **mặc định nếu mockup im lặng** |
| **B** | Trang riêng cho mỗi entry, URL `/words/<topic>/<word>/` | 558 | Mockup có màn hình chi tiết từ |
| **C** | Như B nhưng gộp 20 từ trùng thành 1 trang đa nghĩa | 537 | Chỉ khi mockup thể hiện rõ ý "một từ, nhiều nghĩa" |

Khuyến nghị: **A** cho tới khi mockup chứng minh cần B. Lý do: 558 trang mỏng (thin
content) hại SEO hơn lợi, và mọi thông tin đã hiển thị đủ ở card.
Nếu chọn B, **bắt buộc dùng URL có `topic`** vì `word` không duy nhất (§2.3 điểm 4).

### 3.4 Taxonomies

```toml
[taxonomies]
  topic    = "topics"      # 13 term — chủ đề chính
  subtopic = "subtopics"   # 30 term — chủ đề con
  act      = "acts"        # 4 term  — Hồi I…IV của truyện
```

- `topics` & `acts` gắn trên **lesson page** → có ngay trang `/topics/offices/` (2 bài)
  và `/acts/hoi-i-khoi-dau/` (8 bài) miễn phí.
- `subtopics` gắn trên lesson page (lấy từ các sub-topic mà từ vựng của bài đó thuộc về).
- **Không** làm taxonomy cho `level` (600/750/900) và `pos` — chúng là thuộc tính của
  *từ* (data), không phải của *trang*. Lọc theo level/pos làm bằng bộ lọc client-side
  hoặc `where` trên `site.Data.words` — nhẹ hơn hẳn việc sinh trang.
- Nếu chọn PA **B** ở §3.3 thì mới cân nhắc thêm `levels` và `parts_of_speech`.

### 3.5 URL / permalinks

Repo là **project site** (`github.com/ndchungict/toeic-vocab`) → mọi URL nằm dưới
`/toeic-vocab/`.

| Trang | URL |
|---|---|
| Trang chủ | `/toeic-vocab/` |
| Mục lục bài học | `/toeic-vocab/lessons/` |
| Bài học | `/toeic-vocab/lessons/lesson-01/` |
| Danh sách chủ đề | `/toeic-vocab/topics/` |
| Chủ đề | `/toeic-vocab/topics/offices/` |
| Chủ đề con | `/toeic-vocab/subtopics/meetings-committees/` |
| Hồi | `/toeic-vocab/acts/hoi-i-khoi-dau/` |
| Từ (nếu PA B) | `/toeic-vocab/words/offices/board-of-directors/` |

Giữ `lesson-01` trong URL (thay vì slug tên chương `the-vote`) vì: thứ tự bài học có ý
nghĩa, dễ đoán, và `lesson-NN` chính là khóa join xuyên suốt dữ liệu.
`story_slug` (`the-vote`) vẫn lưu trong front matter để dùng làm anchor/nhãn.

### 3.6 Archetypes

```
archetypes/
├── default.md
└── lessons.md      # dùng cho `hugo new lessons/lesson-29/index.md`
```

`archetypes/lessons.md`:
```yaml
---
title: "Chương  — "
lesson_id: "{{ path.Base .File.Dir }}"
chapter:
act: ""
story_slug: ""
topics: []
subtopics: []
characters: []
teaser: ""
draft: true
---
```

Ghi chú: archetype chỉ hữu ích cho bài **mới viết tay** (chương 29+). 28 bài hiện có được
sinh bằng script migrate 1 lần (§4.1), không qua archetype.

---

## 4. Chuyển dữ liệu thô → nội dung Hugo

Phần có nhiều lựa chọn nhất. Kết luận: **dùng cả 3 cơ chế, mỗi cơ chế cho đúng loại dữ
liệu của nó** — không ép tất cả vào một cách.

| Loại dữ liệu | Cơ chế | Chạy khi nào |
|---|---|---|
| Truyện (28×2 file `.md`) | **Script migrate 1 lần** → commit `content/` | Một lần, ở M1 |
| `data/slugs/*.md` | **Script chuyển 1 lần** → `data/taxonomy.yaml` | Một lần, ở M1 |
| Trang chủ đề (13) | **Content Adapter** (`_content.gotmpl`) | Mỗi lần build |
| Trang từ vựng (558, nếu PA B) | **Content Adapter** | Mỗi lần build |
| Từ vựng & bài tập trong trang | **Hugo data files + partial** | Mỗi lần build |

### 4.1 Truyện → `content/lessons/` : script migrate **một lần**, rồi commit

**Chọn: script Python chạy 1 lần, output được commit; sau đó `content/` là source of truth.**

Vì sao **không** sinh lại mỗi lần build:
1. **Truyện là văn xuôi sẽ được sửa tay.** Sinh lại mỗi build sẽ đè mất mọi chỉnh sửa,
   hoặc buộc phải sửa ngược ở `data/` — một vòng lặp khó chịu.
2. **3 file EN đang lỗi** (`story-02/03/14` lẫn bản VI — §2.4). Việc sửa là thao tác tay
   một lần, không phải quy tắc lặp lại được. Nếu để generator chạy mãi thì phải nhét
   special-case cho 3 file này vào code — mã xấu và dễ mục.
3. **Metadata phải parse từ bảng Markdown** (`story-slug.md`) — mong manh. Parse 1 lần rồi
   đóng băng thành front matter an toàn hơn parse ở mỗi build.
4. Content trong git = diff xem được, review được, Hugo build nhanh và đơn giản.

Vì sao **không** dùng Content Adapter cho truyện: adapter phải đọc được nội dung từ
`data/` hoặc `assets/`, mà `.md` trong `data/` thì Hugo không load — sẽ phải chuyển truyện
sang `assets/` rồi `resources.Get` từng file. Vòng vèo hơn mà không được lợi gì, vì output
vốn là văn xuôi tĩnh.

**Script: `scripts/migrate_stories.py`** (chạy 1 lần)

Đầu vào: `data/slugs/story-slug.md`, `data/story/story-vi/*.md`, `data/story/story-en/*.md`
Đầu ra: `content/lessons/lesson-NN/index.md` + `story-en.md`

Thuật toán:
1. Parse bảng Markdown trong `story-slug.md` → dict theo `lesson-NN`:
   `{chapter, act, topic, title_en, story_slug}`
2. Với mỗi `NN`:
   - Đọc `story-vi/story-NN.md`. Bỏ **8 dòng đầu** (H1 + blockquote metadata + `---`).
     Trích từ blockquote: số từ, danh sách nhân vật (regex `\*\*([^*]+)\*\*`).
   - Đọc `story-en/story-NN.md`. Tìm dòng `^### Chapter` **đầu tiên**, lấy từ đó trở đi.
     → cách này tự xử lý đúng cả 3 file lỗi (02/03/14) vì nó bỏ mọi thứ trước heading
     chương, tức bỏ luôn phần VI bị lẫn. Vẫn **phải mắt thường kiểm tra lại 3 file này**.
   - Bỏ dòng `---` cuối file ở cả 2 bản.
   - Trích `teaser` = đoạn `*Hết Chương N. … Chương sau (lesson-NN): …*` ở cuối bản VI,
     tách khỏi thân, đưa vào front matter.
   - Suy ra `subtopics` = tập hợp `sub-topic` (bỏ null) của mọi từ trong `data/words/`
     có `lesson` chứa `"lesson-NN"`.
3. Ghi `index.md`:
   ```yaml
   ---
   title: "Chương 1 — The Vote"
   lesson_id: "lesson-01"
   chapter: 1
   act: "Hồi I — Khởi đầu"
   story_slug: "the-vote"
   topics: ["offices"]
   subtopics: ["meetings-committees", "correspondence"]
   heading_vi: "OFFICES: Họp & Ủy ban · Thư từ & Liên lạc"
   word_count_label: "27 từ"
   characters:
     - { name: "Diane Whitfield", role: "CEO" }
     - { name: "Priya Nair",      role: "Dịch vụ DN" }
     - { name: "Harold Vance",    role: "Chủ tịch HĐQT" }
   teaser: "Chương sau (lesson-02): hậu trường vận hành văn phòng…"
   weight: 1
   ---
   <thân truyện VI>
   ```
4. Ghi `story-en.md` (chỉ cần `title` tối thiểu + thân truyện EN).
5. In báo cáo: file nào thiếu field, file nào cần review tay.

**Sau khi chạy xong:** giữ `data/story/` lại trong repo như bản gốc lưu trữ (chi phí ~0),
nhưng ghi rõ trong `README` rằng `content/lessons/` mới là nơi biên tập (§10 Q8).

### 4.2 `data/slugs/*.md` → `data/taxonomy.yaml` : chuyển **một lần**

Hugo không đọc `.md` trong `data/`. Chuyển sang một file YAML duy nhất; từ đó
`data/slugs/*.md` chỉ còn vai trò tài liệu cho người (và cho 2 skill).

**Script: `scripts/build_taxonomy.py`** → `data/taxonomy.yaml`:

```yaml
topics:
  offices:
    slug: "offices"
    label_vi: "Văn phòng"          # ⚠️ CHƯA CÓ trong nguồn — xem §10 Q3
    label_en: "Offices"
    order: 9
    subtopics:
      - { slug: "meetings-committees", label_vi: "Họp & Ủy ban" }
      - { slug: "correspondence",      label_vi: "Thư từ & Liên lạc" }
      - { slug: "equipment-furniture", label_vi: "Thiết bị & Nội thất" }
      - { slug: "work-procedures",     label_vi: "Quy trình làm việc" }
acts:
  - slug: "hoi-i-khoi-dau"
    label: "Hồi I — Khởi đầu"
    lessons: ["lesson-01", "…", "lesson-08"]
    summary: "dựng bối cảnh, quyết định làm Project Aria, xây đội ngũ…"
  # … 4 hồi
```

`label_vi` cho sub-topic lấy được từ dòng 23–29 của `category-slug.md`.
`summary` cho hồi lấy được từ mục "Cấu trúc 4 hồi" của `story-slug.md`.
`label_vi` cho **topic chính thì không có trong nguồn** → phải bổ sung tay (13 dòng).

### 4.3 Trang chủ đề & trang từ (nếu có) : **Content Adapter**

Hugo ≥ 0.126 hỗ trợ **content adapter** — file `_content.gotmpl` sinh page từ data ngay
lúc build, không cần script ngoài, không sinh file rác vào git.

Dùng adapter (chứ không phải script) cho topic/word là đúng vì chúng **thuần túy phái
sinh từ data, không bao giờ sửa tay**. Thêm một chủ đề vào `taxonomy.yaml` là trang tự
xuất hiện.

`content/topics/_content.gotmpl`:
```go-html-template
{{ range $slug, $t := site.Data.taxonomy.topics }}
  {{ $words := index site.Data.words $slug }}
  {{ $.AddPage (dict
      "path"    $slug
      "kind"    "section"
      "title"   (or $t.label_vi $t.label_en)
      "params"  (dict "topic_slug" $slug
                      "subtopics"  $t.subtopics
                      "word_count" (len $words))
  ) }}
{{ end }}
```

`content/words/_content.gotmpl` (chỉ tạo nếu chốt PA B ở §3.3) — `path` **phải** gồm
topic để tránh 20 từ trùng đè nhau:
```go-html-template
{{ range $topic, $words := site.Data.words }}
  {{ range $words }}
    {{ $.AddPage (dict
        "path"   (printf "%s/%s" $topic (urlize .word))
        "title"  .word
        "params" (dict "entry" .)
    ) }}
  {{ end }}
{{ end }}
```

> **Fallback:** nếu phải pin Hugo < 0.126, thay adapter bằng `scripts/gen_pages.py` sinh
> file stub `index.md` chỉ có front matter, chạy trong CI trước `hugo`. Kém hơn (thêm
> bước, thêm file sinh ra) nhưng tương đương về kết quả.

### 4.4 Từ vựng & bài tập trong trang : **data file + partial**

Không chuyển đổi gì cả. Template đọc thẳng `site.Data`:

```go-html-template
{{/* từ vựng của bài học hiện tại */}}
{{ $lid := .Params.lesson_id }}
{{ $words := slice }}
{{ range $topic := .Params.topics }}
  {{ range (index site.Data.words $topic) }}
    {{ if in .lesson $lid }}{{ $words = $words | append . }}{{ end }}
  {{ end }}
{{ end }}

{{/* bài tập của bài học hiện tại */}}
{{ $ex := index site.Data.exercises (replace $lid "lesson-" "exercise-") }}
```

Ba partial phải viết cẩn thận (xem các "bẫy" ở §2.3, §2.5):

1. **`partials/word/example.html`** — parse marker `{…}`:
   ```go-html-template
   {{ .en | replaceRE `\{([^}]+)\}` `<mark class="tw">$1</mark>` | safeHTML }}
   ```
2. **`partials/word/forms.html`** — `forms` value có thể là string hoặc list:
   ```go-html-template
   {{ range $pos, $v := .forms }}
     {{ if reflect.IsSlice $v }}{{ delimit $v ", " }}{{ else }}{{ $v }}{{ end }}
   {{ end }}
   ```
3. **`partials/exercise/part6.html`** — group theo `passage_group`, render passage **một
   lần**, rồi render options theo từng blank:
   ```go-html-template
   {{ range $g, $items := (where $ex "part" 6) | group "passage_group" }}
     {{ (index $items 0).passage | markdownify }}
     {{ range $items }}…{{ end }}
   {{ end }}
   ```
   *(Hugo không có `groupBy` cho slice of maps — dùng vòng lặp gom vào dict theo
   `passage_group`, hoặc `where` lồng nhau trên tập `passage_group` duy nhất.)*

**Bài tập tương tác:** đáp án được nhúng vào trang dưới dạng
`<script type="application/json" id="answers">` (JSON `{id: {answer, explanation_vi}}`),
JS chấm điểm phía client sau khi nộp. Không cần backend.
Nói thẳng: static site thì **ai xem source cũng thấy đáp án** — không chống gian lận
được, và cũng không cần, vì đây là công cụ tự học. Không obfuscate cho phức tạp.

---

## 5. Thiết kế theme & layout

### 5.1 Custom theme hay theme có sẵn?

**Chọn: theme tự viết, đặt thẳng trong `layouts/` + `assets/` ở gốc repo (không tạo thư
mục `themes/`).**

Lý do:
- Yêu cầu là **bám sát mockup**. Mọi theme có sẵn (Docsy, Book, PaperMod…) đều mang theo
  ý đồ thiết kế riêng; ép nó theo mockup tốn công hơn viết mới, và mỗi lần theme update
  lại vỡ override.
- Site này chỉ có ~5 kiểu trang. Bề mặt nhỏ, không đáng trừu tượng hoá thành theme đóng gói.
- Đặt ở gốc (không `themes/`) tránh một tầng lookup, dễ debug hơn. Sau này muốn tách thành
  theme riêng thì chỉ là move file.

### 5.2 Tái hiện CSS của mockup

*(Phương án cụ thể chốt sau khi đọc mockup — §1.1 mục D.)* Hai nhánh:

**Nếu mockup là CSS thuần / CSS variables:**
Chuyển sang `assets/scss/`:
```
assets/scss/
├── main.scss
├── _tokens.scss       # CSS custom properties: màu, font, spacing, radius (§1.1 mục C)
├── _base.scss         # reset + typography
├── _layout.scss       # container, grid, header, footer
└── components/        # _card.scss, _word.scss, _story.scss, _quiz.scss, _nav.scss
```
Build bằng **Hugo Pipes + libsass (có sẵn trong hugo-extended)** — không cần Node,
CI đơn giản hơn hẳn:
```go-html-template
{{ $css := resources.Get "scss/main.scss" | toCSS (dict "outputStyle" "compressed")
           | fingerprint }}
<link rel="stylesheet" href="{{ $css.RelPermalink }}" integrity="{{ $css.Data.Integrity }}">
```

**Nếu mockup dùng Tailwind:**
Cần Node trong CI (`npm ci` + Tailwind CLI hoặc PostCSS). Chấp nhận được nhưng workflow
nặng hơn. Sẽ cân nhắc trích ra CSS thuần nếu mockup chỉ dùng một tập utility class nhỏ.

**Quy tắc chung dù nhánh nào:** không nạp tài nguyên từ CDN. Font Google phải **tự host**
(`assets/fonts/` + `@font-face` + `font-display: swap`) — GitHub Pages không có
control-plane để proxy, và CDN ngoài làm chậm + rủi ro privacy. Font **bắt buộc phủ đủ bộ
chữ tiếng Việt** (subset `latin-ext` + `vietnamese`).

### 5.3 Danh sách template cần tạo

```
layouts/
├── _default/
│   ├── baseof.html            # khung: <head>, header, main, footer, script
│   ├── list.html
│   ├── single.html
│   ├── taxonomy.html          # /topics/, /subtopics/, /acts/
│   └── term.html              # /topics/offices/, /acts/hoi-i-khoi-dau/
├── index.html                 # TRANG CHỦ  (cấu trúc chờ mockup)
├── lessons/
│   ├── list.html              # mục lục 28 chương, nhóm theo 4 Hồi
│   └── single.html            # ★ trang bài học — phức tạp nhất
├── topics/
│   ├── list.html              # lưới 13 chủ đề
│   └── single.html            # 1 chủ đề: sub-topic + từ vựng + link 2 bài học
├── words/                     # chỉ nếu chốt PA B (§3.3)
│   └── single.html
├── 404.html
└── partials/
    ├── head.html              # meta, OG, canonical, CSS, JSON-LD
    ├── header.html            # nav + logo + (search?) + (dark toggle?)
    ├── footer.html
    ├── breadcrumb.html
    ├── pagination.html
    ├── lesson/
    │   ├── meta.html          # chương, hồi, chủ đề, nhân vật, số từ
    │   ├── story-tabs.html    # ★ toggle EN/VI, render 2 nguồn Markdown
    │   ├── story-body.html    # style **từ** được chêm
    │   ├── vocab-list.html    # danh sách từ của bài (join từ site.Data.words)
    │   └── nav-prev-next.html # điều hướng chương trước/sau
    ├── word/
    │   ├── card.html          # ★ thẻ từ: word/pos/ipa/meaning/…
    │   ├── example.html       # ★ parse marker {…}
    │   ├── forms.html         # ★ xử lý value string-hoặc-list
    │   ├── collocations.html
    │   └── note.html          # chỉ render khi có (210/558 entry)
    ├── exercise/
    │   ├── section.html       # bọc cả 3 part, nhúng JSON đáp án
    │   ├── part5.html         # câu đơn + 4 options
    │   ├── part6.html         # ★ group theo passage_group, passage 1 lần, KHÔNG có question
    │   ├── part7.html         # ★ group theo passage_group, có question
    │   └── explanation.html   # đáp án + explanation_vi (markdownify)
    ├── topic/card.html
    └── icons/*.html           # inline SVG
```

★ = có bẫy dữ liệu đã nêu ở §2, phải viết cẩn thận + đối chiếu thủ công.

### 5.4 JavaScript

Vanilla JS, không framework, bundle bằng `js.Build` (esbuild có sẵn trong Hugo):
```
assets/js/
├── main.js
├── story-toggle.js     # tab EN/VI (+ ghi nhớ lựa chọn vào localStorage)
├── quiz.js             # chọn đáp án → nộp → chấm → hiện giải thích
├── vocab-filter.js     # lọc theo level / pos / sub-topic — CÓ ĐIỀU KIỆN
└── progress.js         # đánh dấu đã học — CÓ ĐIỀU KIỆN
```

⚠️ `progress.js`: khóa localStorage **bắt buộc** là `<topic>:<word>` chứ không phải
`<word>`, vì 20 từ trùng tên giữa các chủ đề (§2.3 điểm 4). Ghi rõ vào code comment.

### 5.5 Tìm kiếm — có điều kiện

Nếu mockup có ô search: sinh `index.json` bằng Hugo custom output format (toàn bộ 558 từ,
~200 KB chưa nén / ~40 KB gzip — chấp nhận được), tìm bằng Fuse.js tự host.
Nếu mockup không có: **bỏ qua**, đúng nguyên tắc "không tự nghĩ thêm tính năng".

---

## 6. Cấu hình Hugo

`hugo.toml`:

```toml
baseURL                = "https://ndchungict.github.io/toeic-vocab/"
languageCode           = "vi-VN"
defaultContentLanguage = "vi"
title                  = "TOEIC Vocab — Học từ vựng qua truyện chêm"
enableRobotsTXT        = true
enableGitInfo          = true
hasCJKLanguage         = false
timeZone               = "Asia/Ho_Chi_Minh"

[pagination]
  pagerSize = 12

[taxonomies]
  topic    = "topics"
  subtopic = "subtopics"
  act      = "acts"

[markup.goldmark.renderer]
  unsafe = true            # BẮT BUỘC: passage Part 6/7 và truyện có HTML inline
[markup.goldmark.parser.attribute]
  block = true
[markup.tableOfContents]
  startLevel = 2
  endLevel   = 3

[params]
  description    = "558 từ vựng TOEIC theo 13 chủ đề, học qua truyện dài 28 chương “Project Aria”."
  author         = "ndchungict"
  totalWords     = 537
  totalLessons   = 28
  totalTopics    = 13
  totalExercises = 704
  storyTitle     = "Project Aria"
  storyCompany   = "Aster Home Technologies"
  # màu/typography lấy từ mockup sẽ khai báo ở _tokens.scss —
  # KHÔNG khai báo trùng ở cả hai nơi

[menu]
  [[menu.main]]
    name = "Bài học"
    pageRef = "/lessons"
    weight = 10
  [[menu.main]]
    name = "Chủ đề"
    pageRef = "/topics"
    weight = 20
  # các mục còn lại điền sau khi đọc nav của mockup (§1.1 mục A)

[outputs]
  home = ["HTML", "RSS", "JSON"]      # JSON chỉ giữ nếu làm search (§5.5)

[minify]
  disableXML = true
```

**Ba điểm cần lưu ý về `baseURL`:**
1. Repo là **project site** (`ndchungict/toeic-vocab`, không phải `ndchungict.github.io`)
   → baseURL **phải có** hậu tố `/toeic-vocab/`, và **phải có dấu `/` cuối**.
2. Mọi URL trong template phải dùng `.RelPermalink` / `relURL` / `absURL` — **tuyệt đối
   không hardcode `/`**. Nếu không sẽ vỡ hết khi deploy mà chạy `hugo server` local vẫn
   đúng → lỗi này rất dễ lọt.
3. Nếu sau này gắn custom domain → đổi baseURL và thêm `static/CNAME`. Workflow ở §7 dùng
   `--baseURL ${{ steps.pages.outputs.base_url }}` nên tự thích ứng.

Thêm `static/.nojekyll` (file rỗng) để GitHub Pages không chạy Jekyll — nếu không, mọi
thư mục bắt đầu bằng `_` sẽ bị nuốt.

---

## 7. GitHub Actions & deploy

Dùng **GitHub Pages qua Actions** (`actions/deploy-pages`), không dùng nhánh `gh-pages`.
Sạch hơn: không có artifact build nằm trong lịch sử git.

**Cần bật tay một lần:** Settings → Pages → Source = **GitHub Actions**.

`.github/workflows/deploy.yml`:

```yaml
name: Deploy Hugo site to Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

# Không hủy deploy đang chạy; bỏ qua các lần chạy đang chờ ở giữa
concurrency:
  group: pages
  cancel-in-progress: false

defaults:
  run:
    shell: bash

jobs:
  build:
    runs-on: ubuntu-latest
    env:
      HUGO_VERSION: 0.148.1        # pin cứng — xem ghi chú bên dưới
      HUGO_ENVIRONMENT: production
      TZ: Asia/Ho_Chi_Minh
    steps:
      - name: Install Hugo CLI (extended)
        run: |
          wget -O ${{ runner.temp }}/hugo.deb \
            https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.deb
          sudo dpkg -i ${{ runner.temp }}/hugo.deb

      - uses: actions/checkout@v4
        with:
          fetch-depth: 0           # cần cho enableGitInfo (lastmod)

      - id: pages
        uses: actions/configure-pages@v5

      - name: Build
        run: |
          hugo --gc --minify \
            --baseURL "${{ steps.pages.outputs.base_url }}/"

      - uses: actions/upload-pages-artifact@v3
        with:
          path: ./public

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

**Quyết định & lý do:**
- **`hugo_extended`**: bắt buộc nếu dùng SCSS qua `toCSS` (§5.2). Cài bản extended ngay
  từ đầu để khỏi phải sửa workflow sau.
- **Pin `HUGO_VERSION` cứng**: build tĩnh phải tái lập được; Hugo thỉnh thoảng có breaking
  change ở template. Bump thủ công khi cần. **Content Adapter cần ≥ 0.126.**
- **`--baseURL` từ `configure-pages`**: tự đúng cho cả project site, user site lẫn custom
  domain — không phải sửa `hugo.toml` khi đổi.
- **`fetch-depth: 0`**: `enableGitInfo` cần full history để lấy `lastmod`. Bỏ dòng này thì
  lastmod sai âm thầm.
- **Không cần Node** ở nhánh SCSS. Nếu mockup dùng Tailwind thì thêm `actions/setup-node@v4`
  + `npm ci` trước bước Build.

**Workflow phụ — `.github/workflows/validate.yml`** (chạy trên PR):
```yaml
# 1. yamllint data/**/*.yaml
# 2. python scripts/validate_data.py  ← kiểm tra bất biến dữ liệu:
#    - mọi topic/sub-topic khớp taxonomy.yaml
#    - mọi related_word non-null resolve được về data/words/
#    - mọi lesson-NN có đủ: content/lessons/lesson-NN/, exercise-NN.yaml, ≥1 từ
#    - mọi example.en có đúng một cặp {…}
#    - exercise-NN.yaml chỉ chứa 1 topic và 1 lesson
# 3. hugo --gc --minify --panicOnWarning   ← build thử, fail nếu có warning
```
Đáng làm, vì dữ liệu do LLM sinh qua 2 skill — sai sót im lặng (một `related_word` gõ
nhầm) sẽ không làm vỡ build mà chỉ làm hỏng link, rất khó phát hiện bằng mắt.

---

## 8. Cây thư mục dự kiến

```
toeic-vocab/
├── .github/workflows/
│   ├── deploy.yml
│   └── validate.yml
├── .claude/                      # giữ nguyên (skill sinh dữ liệu)
│   ├── settings.json
│   └── skills/{toeic-vocab-yaml,toeic-execise-to-yaml}/
├── archetypes/
│   ├── default.md
│   └── lessons.md
├── assets/
│   ├── scss/{main,_tokens,_base,_layout}.scss  +  components/
│   ├── js/{main,story-toggle,quiz,vocab-filter,progress}.js
│   ├── fonts/                    # font tự host, có subset vietnamese
│   └── images/
├── content/
│   ├── _index.md
│   ├── lessons/
│   │   ├── _index.md
│   │   └── lesson-01/ … lesson-28/   ← SINH 1 LẦN từ data/story/, rồi sửa tay
│   │       ├── index.md              (front matter + truyện VI)
│   │       └── story-en.md           (truyện EN)
│   ├── topics/
│   │   ├── _index.md
│   │   └── _content.gotmpl           ← Content Adapter, sinh 13 trang mỗi build
│   └── words/                        ← CHỈ NẾU chốt PA B (§3.3)
│       └── _content.gotmpl
├── data/                             ← Hugo data, KHÔNG chuyển đổi
│   ├── taxonomy.yaml                 ← SINH 1 LẦN từ data/slugs/*.md
│   ├── words/*.yaml                  # 13 file, 558 entry — giữ nguyên
│   ├── exercises/*.yaml              # 28 file, 704 câu — giữ nguyên
│   ├── slugs/*.md                    # giữ làm tài liệu + input cho 2 skill
│   └── story/{story-en,story-vi}/    # giữ làm bản gốc lưu trữ (§10 Q8)
├── design/
│   └── TOEIC-Vocab.dc.html           ← CHỜ: bạn lưu mockup vào đây
├── docs/
│   └── plan.md                       ← file này
├── layouts/                          # xem §5.3
├── scripts/
│   ├── migrate_stories.py            # chạy 1 lần (M1)
│   ├── build_taxonomy.py             # chạy 1 lần (M1)
│   └── validate_data.py              # chạy trong CI
├── static/
│   ├── .nojekyll
│   └── favicon.ico
├── raw/                              # nguồn nháp, .gitignore, KHÔNG dùng cho site
├── .gitignore                        # public/, resources/, .hugo_build.lock, raw/
├── hugo.toml
└── README.md
```

---

## 9. Giai đoạn triển khai (milestones)

Thứ tự này được xếp để **mỗi milestone đều cho ra một site chạy được**, và để phần phụ
thuộc mockup bị đẩy lùi tối đa — nhờ vậy công việc dữ liệu (M0–M3) có thể bắt đầu ngay
hôm nay dù chưa có mockup.

| # | Milestone | Nội dung | Chặn bởi |
|---|---|---|---|
| **M0** | Dọn repo & khung Hugo | Commit lần đổi tên `data/lessions` → `data/story` (đang dở dang). `hugo new site`. `hugo.toml`. `.gitignore`. `static/.nojekyll`. `baseof.html` trần. Push → **workflow deploy chạy được, ra trang trắng có URL thật**. | — |
| **M1** | Migrate dữ liệu | `build_taxonomy.py` → `data/taxonomy.yaml` (+ điền tay 13 nhãn VI). `migrate_stories.py` → 28 page bundle. **Sửa tay 3 file lỗi** `story-02/03/14`. `validate_data.py` + workflow validate. | M0, **Q3** |
| **M2** | Bài học không style | `lessons/list.html` + `single.html`: hiện đủ truyện VI/EN, danh sách từ, bài tập. HTML trần, chưa CSS. Mục tiêu: **chứng minh mọi join dữ liệu đúng** trước khi động vào giao diện. | M1 |
| **M3** | Partial dữ liệu "khó" | 3 partial có bẫy (§5.3 ★): marker `{…}`, `forms` string-vs-list, group `passage_group`. Đối chiếu thủ công vài bài. | M2 |
| **M4** | **Design tokens & khung theme** | Trích tokens từ mockup → `_tokens.scss`. `baseof` + header/footer/nav thật. Font tự host. Responsive khung. | **MOCKUP (Q1)** |
| **M5** | Các trang theo mockup | Trang chủ, trang chủ đề (content adapter), card từ vựng, khối truyện, khối bài tập — dựng đúng mockup. | M4, **Q2** |
| **M6** | Tương tác | `story-toggle.js`, `quiz.js` (chấm điểm + giải thích), và — **chỉ nếu mockup có** — filter, progress/localStorage, search, dark mode. | M5 |
| **M7** | Hoàn thiện | SEO (OG, JSON-LD, sitemap), 404, a11y (contrast, focus, aria trên tab & quiz), Lighthouse, kiểm tra lại toàn bộ URL dưới `/toeic-vocab/`. | M6 |

**Làm được ngay không cần mockup:** M0 → M3. Đây cũng là phần chứa **phần lớn rủi ro kỹ
thuật**, vì rủi ro nằm ở dữ liệu (join, schema không đồng nhất, từ trùng) chứ không ở CSS.

---

## 10. Giả định & câu hỏi còn mở

### 10.1 Giả định đã đặt (sẽ hành động theo, trừ khi bạn bác lại)

| # | Giả định | Căn cứ | Rủi ro nếu sai |
|---|---|---|---|
| A1 | Site **một ngôn ngữ giao diện: tiếng Việt**. EN/VI chỉ là 2 phiên bản của *truyện*, không phải i18n toàn site. | Mọi `meaning`, `explanation_vi`, nhãn sub-topic đều tiếng Việt | Thấp — nếu sai phải bật Hugo multilingual, làm lại §3.2 |
| A2 | `baseURL = https://ndchungict.github.io/toeic-vocab/` (project site) | `git remote -v` → `ndchungict/toeic-vocab` ≠ `ndchungict.github.io` | Thấp — workflow lấy baseURL động nên tự đúng |
| A3 | `content/lessons/` là source of truth cho truyện sau M1; `data/story/` chỉ còn là bản lưu trữ | Truyện là văn xuôi cần sửa tay (§4.1) | Trung bình — nếu bạn muốn tiếp tục sửa ở `data/story/` thì phải đổi sang sinh mỗi build |
| A4 | Chưa làm trang chi tiết cho từng từ (PA A, §3.3) | Chưa có mockup chứng minh cần | Thấp — thêm sau bằng content adapter, không phải làm lại gì |
| A5 | `raw/` **không dùng** cho website (bạn đã xác nhận) | Câu trả lời của bạn + deny rule trong `.claude/settings.json` | Không |
| A6 | Không cần audio phát âm (chỉ có IPA dạng text) | Không có field audio nào trong 558 entry | Trung bình — nếu cần thì phải tìm nguồn TTS/audio |
| A7 | Chỉ có 28 bài, không mở rộng ngay | `story-slug.md` chốt "28 chương", `story-28` ghi *(HỒI KẾT)* | Thấp — cấu trúc đã sẵn sàng cho chương 29+ |
| A8 | Hugo ≥ 0.126 (để dùng Content Adapter) | Yêu cầu kỹ thuật của tính năng | Thấp — có fallback ở §4.3 |

### 10.2 Câu hỏi cần bạn trả lời

**Chặn công việc:**

- **Q1 — Mockup.** ⛔ Chặn toàn bộ §1 và M4–M6. Link `claude.ai/design/p/…` bạn gửi trả về
  **403** với tool fetch (đây là link chia sẻ Claude Design, không phải artifact URL đọc
  được). Nhờ bạn **tải file về và lưu vào `design/TOEIC-Vocab.dc.html`**.
- **Q2 — Mockup có bao nhiêu màn hình, và có màn "chi tiết một từ" không?** Quyết định
  PA A/B/C ở §3.3 → chênh lệch 558 trang. (Sẽ tự trả lời được khi có file ở Q1.)
- **Q3 — Nhãn tiếng Việt cho 13 chủ đề chính?** Nguồn dữ liệu **chỉ có slug**
  (`corporate-development`, `technical-areas`…), không có tên hiển thị tiếng Việt
  (sub-topic thì có đủ). Cần bạn cho 13 nhãn, hoặc xác nhận dùng nhãn tiếng Anh viết hoa
  (`Corporate Development`). **Chặn M1.**

**Không chặn (có mặc định hợp lý, chỉ cần xác nhận):**

- **Q4 — Khóa localStorage cho tiến độ học:** `toeic-vocab-yaml/SKILL.md` ghi `word` là
  khóa định danh, nhưng **20 từ trùng tên giữa các chủ đề** (§2.3) sẽ đụng độ. Đề xuất đổi
  sang `<topic>:<word>`. Nếu đồng ý, nên sửa luôn dòng đó trong SKILL.md để hai bên không lệch.
- **Q5 — Ba file EN lỗi** (`story-en/story-02.md`, `03`, `14` lẫn bản VI ở đầu file):
  script migrate sẽ tự cắt bỏ (lấy từ `### Chapter` trở đi). Bạn muốn **sửa luôn file gốc**
  trong `data/story/story-en/` cho sạch, hay chỉ sửa ở `content/`?
- **Q6 — Từ được chêm trong truyện** (`**memo** (thông báo nội bộ)`): có muốn biến thành
  tooltip/link trỏ về thẻ từ vựng không? Kỹ thuật làm được (đã có khóa join), nhưng đây là
  **tính năng ngoài mockup** — mặc định **không làm**, chỉ style cho nổi bật.
- **Q7 — Câu dẫn cuối chương** (`*Hết Chương 1. Chương sau (lesson-02): …*`): tách thành
  khối "Chương sau" riêng ở cuối trang, hay giữ trong thân truyện? Mặc định: tách vào front
  matter `teaser`, render thành khối riêng cạnh nút "Chương sau".
- **Q8 — `data/story/` sau khi migrate**: giữ trong repo làm bản lưu trữ (đề xuất, chi phí
  ~0), hay xóa để tránh hai nguồn dữ liệu gây nhầm lẫn?
- **Q9 — Thứ tự trang chủ**: mặc định theo **thứ tự truyện** (Chương 1→28, nhóm theo 4 Hồi)
  chứ không theo 13 chủ đề, vì đây là truyện dài liền mạch có cốt truyện. Nếu mockup ưu
  tiên lưới chủ đề thì theo mockup.

### 10.3 Việc dọn dẹp nhỏ, làm luôn ở M0

- Commit lần đổi tên `data/lessions/` → `data/story/` (56 file đang dở dang trong git status).
- Thêm `raw/` vào `.gitignore` (hiện chưa track nhưng cũng chưa ignore).
- Thống nhất `id` prefix trong `toeic-execise-to-yaml/SKILL.md`: tài liệu ghi `ex01-p5-01`
  nhưng 704 item dữ liệu thật đều dùng `exercise-01-p5-01`. Sửa tài liệu theo dữ liệu.
