# Kế hoạch xây dựng website TOEIC Vocab

> **Bản 2** — đã đọc mockup thật trong `mockup/`. Mọi phần dựa trên file thật (mockup + dữ liệu),
> không phỏng đoán.
>
> Ngày lập: 2026-08-01 · Repo: `ndchungict/toeic-vocab` · Nhánh: `main`
>
> **Thay đổi lớn so với bản 1:** mockup là một **SPA client-side 9 màn hình**, không phải site
> nhiều trang. Điều này thay đổi §3, §4, §5, §9. Ba giả định ở bản 1 đã bị mockup bác bỏ
> (TTS, popover từ trong truyện, flashcard) — xem §10.1.

---

## Mục lục

1. [Phân tích mockup](#1-phân-tích-mockup)
2. [Phân tích dữ liệu](#2-phân-tích-dữ-liệu)
3. [Đối chiếu mockup ↔ dữ liệu thật](#3-đối-chiếu-mockup--dữ-liệu-thật--khoảng-cách-phải-lấp)
4. [Kiến trúc: SPA hay nhiều trang?](#4-kiến-trúc-spa-hay-nhiều-trang)
5. [Kiến trúc nội dung Hugo](#5-kiến-trúc-nội-dung-hugo)
6. [Chuyển dữ liệu thô → Hugo + JSON](#6-chuyển-dữ-liệu-thô--hugo--json)
7. [Thiết kế theme & layout](#7-thiết-kế-theme--layout)
8. [Cấu hình Hugo](#8-cấu-hình-hugo)
9. [GitHub Actions & deploy](#9-github-actions--deploy)
10. [Cây thư mục dự kiến](#10-cây-thư-mục-dự-kiến)
11. [Giai đoạn triển khai](#11-giai-đoạn-triển-khai-milestones)
12. [Giả định & câu hỏi còn mở](#12-giả-định--câu-hỏi-còn-mở)

---

## 1. Phân tích mockup

### 1.1 Nguồn

| File | Vai trò |
|---|---|
| `mockup/TOEIC Vocab.dc.html` | **App root** — toàn bộ state, dữ liệu mẫu, design tokens, khung xem 2 thiết bị |
| `mockup/AppShell.dc.html` | Khung điều hướng — bottom tab (mobile) / sidebar (desktop), header, theme toggle |
| `mockup/Screens.dc.html` | **9 màn hình** + popover, dùng chung cho cả mobile lẫn desktop |
| `mockup/TOEIC Vocab.html` | Bản standalone đã build (388 KB) — không phải nguồn để đọc |
| `mockup/support.js` | Runtime của Claude Design (React + DSL `x-dc`) — không dùng cho site thật |

Mockup viết bằng DSL riêng (`<sc-if>`, `<sc-for>`, `<dc-import>`, `{{ }}`) + một class React
(`DCLogic`). Style là **inline style object**, không có file CSS — nên "tái hiện CSS" nghĩa là
**dịch inline style sang SCSS**, không phải copy stylesheet.

> 🔎 Dòng 34 của app root ghi rõ định hướng kỹ thuật, coi như yêu cầu từ chính mockup:
> *"Project Aria · 27 từ · truyện chêm + bài tập Part 5·6·7 · **trang tĩnh Hugo, tương tác
> client-side**"*. Và thanh địa chỉ trong khung desktop hiển thị `ndchungict.github.io`.

### 1.2 Danh sách màn hình (9 màn)

Điều hướng bằng `app.go(screen)` — **không có URL**, state giữ trong React.

| # | key | Tiêu đề | Phụ đề | Nút back → |
|---|---|---|---|---|
| 1 | `home` | Trang chủ | Cùng học từ mới hôm nay nhé! | — |
| 2 | `vocab` | Từ vựng | `N` từ · tìm & lọc | — |
| 3 | `detail` | *(tên từ)* | *(loại từ · IPA)* | `vocab` |
| 4 | `flashcard` | Flashcard | Ôn tập lặp lại ngắt quãng | — |
| 5 | `stories` | Truyện chêm | Học từ qua ngữ cảnh | — |
| 6 | `reader` | *(tên chương)* | `N` từ mới trong truyện | `stories` |
| 7 | `exercise` | Bài tập TOEIC | Part 5 · 6 · 7 · điền từ đang học | `home` |
| 8 | `result` | Kết quả bài tập | Xem lại từng câu kèm giải thích | `exercise` |
| 9 | `progress` | Tiến độ học | Theo dõi hành trình của bạn | — |

**Điều hướng chính:**
- **Mobile** — bottom tab bar 5 mục: Trang chủ · Từ vựng · Thẻ · Truyện · Tiến độ
  *(Bài tập KHÔNG có trong tab bar — vào từ trang chủ)*
- **Desktop** — sidebar trái 246px, 6 mục: thêm **Bài tập**. Có logo "V" + "VocabTOEIC /
  Tự học từ vựng", widget "Mục tiêu hôm nay" + progress bar, nút đổi theme ở đáy.
- **Header** — mobile 46px status bar giả + hàng title/back/theme; desktop 66px với
  title/subtitle + badge streak `🔥 5 ngày`.
- Alias màn hình khi tô sáng nav: `detail→vocab`, `reader→stories`, `result→exercise`.

### 1.3 Chi tiết từng màn (những gì phải dựng lại)

**1. Home** — hero gradient tím (`--primary` → `#8b5cf6`, radius 20px): lời chào, "Mục tiêu hôm
nay `N/M` từ" + progress bar trắng, 2 nút *Học flashcard* / *Làm bài tập*. Dưới là 3 stat card
(Đã thuộc `N/M` · Tiến độ `%` · Chuỗi streak `N 🔥`), khối "Bài học hiện tại" (card truyện có
icon sách, nhãn `Bài 1 · OFFICES`, tiêu đề, `N từ mới · truyện chêm`, mũi tên), và "Khám phá" —
3 card: Từ vựng / Truyện chêm / Bài tập.

**2. Vocab** — ô tìm kiếm (`placeholder: "Tìm từ hoặc nghĩa…"`, có icon kính lúp), rồi **4 nhóm
pill lọc**: `Chủ đề` · `Mốc điểm` · `Loại từ` · `Bài học`. Mỗi nhóm có pill "Tất cả". Pill mốc
điểm khi active tô **màu riêng của level**, các pill khác tô `--primary`. Dòng "`N` từ" +
link *Xoá bộ lọc*. Lưới card `repeat(auto-fill, minmax(228px,1fr))`. Mỗi card: từ (18px/800),
loại từ, IPA + nút loa, nghĩa, badge `TOEIC <level>`, nút ♥ (yêu thích), nút ✓ *Đánh dấu / Đã
thuộc*. Có trạng thái rỗng: *"Không tìm thấy từ phù hợp."*

**3. Detail** — card đầu: từ 30px, badge level, loại từ, IPA + nút **Nghe**, nghĩa 17px, 2 nút
*Đánh dấu đã thuộc* / *Yêu thích*. Rồi 2 cột: **Họ từ** (mỗi dòng: nhãn loại từ + giá trị + nút
loa) và **Cụm từ thường gặp** (en + nút loa + vi). Rồi **Câu ví dụ** (highlight từ đích nền
`--primary-soft`, có nút loa, kèm bản dịch in nghiêng), **Ghi chú** (chỉ khi có), và **Xuất hiện
trong truyện** — các nút dẫn sang chương chứa từ đó.

**4. Flashcard** — progress bar + `i/N`. Thẻ lật 3D (`perspective:1400px`, `rotateY(180deg)`,
`transition .55s`, cao 360px). Mặt trước: badge level, từ 32px, IPA, nút **Nghe**, gợi ý *"Chạm
để xem nghĩa"*. Mặt sau: nghĩa 23px + câu ví dụ (highlight) + bản dịch. Nút *Xem nghĩa*, sau khi
lật hiện 4 nút đánh giá **Chưa nhớ / Khó / Được / Dễ** (đỏ/cam/xanh dương/xanh lá, viền 1.6px).
Hết phiên: màn "Hoàn thành phiên học!" + nút *Học phiên mới*.

**5. Stories** — lưới card `minmax(280px,1fr)`: badge level + badge trạng thái (**Sắp có** /
**Đã đọc** / **Chưa đọc**), tiêu đề, tóm tắt, `N từ mới · <chủ đề>`. Card `coming` bị mờ
(`opacity .62`) và không bấm được.

**6. Reader** — segmented control **Truyện chêm / Bản tiếng Anh**, nút **Hiện nghĩa / Ẩn nghĩa**
(chỉ hiện ở chế độ chêm). Tóm tắt. Bố cục 2 cột: cột trái (flex 2) là truyện — mỗi đoạn
`font-size 16.5px, line-height 1.95`, **từ vựng là chip bấm được** (nền `--primary-soft`, chữ
`--primary`, bold, radius 6px) → mở popover; khi bật "Hiện nghĩa" thì chèn ` (nghĩa)` màu
`--muted` ngay sau chip. Cột phải (flex 1) là danh sách **Từ mới (N)** — mỗi thẻ có từ, badge
level, `IPA · nghĩa`, nút *Nghe*.

**7. Exercise** — thanh tiến độ **sticky top** + "Đã trả lời `N/M`". Rồi từng Part:
- **Part 5** (`kind: sentences`) — câu có chỗ trống; chỗ trống hiện **đáp án đã chọn** (gạch chân
  `--primary`), chưa chọn thì hiện `?`. 4 lựa chọn dạng lưới 2×2, mỗi nút có ô chữ cái A/B/C/D.
- **Part 6** (`kind: passages`) — khối passage viền trái 3px `--primary`, có `heading` + `meta`;
  các chỗ trống render **inline trong passage**, hiện đáp án đã chọn hoặc `(13)`. Bên dưới liệt
  kê "Câu 13/14/15/16" với 4 lựa chọn dạng compact.
- **Part 7** (`kind: reading`) — passage trong khối nền `--surface-2`, rồi từng câu hỏi có
  `prompt` + 4 lựa chọn xếp dọc.
- Nút nộp bài xanh lá `#16a34a`: *"Nộp bài · chấm điểm (N/M)"*.

**8. Result** — hero gradient: `score/total` 44px, `Đúng N%`, điểm từng Part. Rồi từng nhóm Part,
mỗi câu là 1 card: nhãn câu + badge **Đúng / Sai / Chưa làm**, đề bài, 4 lựa chọn tô màu
(xanh = đáp án đúng `✓ Đáp án`, đỏ = *Bạn chọn* nếu sai), và khối **Giải thích** nền `--surface-2`.
Cuối: 2 nút *Làm lại* / *Về trang chủ*.

**9. Progress** — 4 stat card (Đã thuộc · Tiến độ % · Streak · Đã ôn thẻ). Biểu đồ cột **7 ngày
gần đây** (cột gradient `--primary`→`#8b5cf6`, cao 150px, nhãn T2…CN). **Phân bố theo mốc điểm**
— mỗi level một hàng: badge + thanh tiến độ tô màu level + `done/total`. **Phân bố theo chủ đề**
— lưới, mỗi ô có nhãn + `done/total` + thanh tiến độ.

**Popover từ (dùng chung)** — overlay `rgba(10,10,20,.5)`, hộp `max-width 420px`: từ + badge
level, `loại từ · IPA`, nghĩa, 2 nút *Nghe phát âm* / *Xem chi tiết*, nút ✕.

### 1.4 Component tái sử dụng (rút ra từ mockup)

| Component | Dùng ở màn |
|---|---|
| **Badge level** (`TOEIC <n>`, màu riêng theo level) | vocab, detail, flashcard, stories, reader, progress, popover |
| **Nút loa TTS** (3 cỡ: 26/28px ô vuông, và nút "Nghe" có chữ) | vocab, detail ×3, flashcard, reader |
| **Stat card** (nhãn nhỏ + số 26px) | home, progress |
| **Progress bar** (h 7–9px, radius, `transition width .4s`) | shell, home, flashcard, exercise, progress |
| **Card mặt phẳng** (`--surface` + `1px --border` + radius 16–18px + padding 15–20px) | mọi màn |
| **Nút chọn đáp án** (ô chữ cái + nội dung, 2 biến thể compact/thường) | exercise |
| **Pill lọc** (radius 999px) | vocab |
| **Segmented control** (nền `--surface-2`, item active nền `--surface` + shadow) | reader, app root |
| **Chip từ trong truyện** | reader |
| **Hero gradient** (`--primary`→`#8b5cf6`) | home, result |
| **Nhãn section** (12–13px, 800, uppercase, `letter-spacing .06em`, `--faint`) | mọi màn |

### 1.5 Design tokens (trích nguyên văn)

**Màu — CSS custom properties, có đủ 2 theme:**

| Token | Light | Dark |
|---|---|---|
| `--studio` | `#e8eaf3` | `#080910` |
| `--bg` | `#f6f7fb` | `#0f1118` |
| `--surface` | `#ffffff` | `#171a24` |
| `--surface-2` | `#eef0f6` | `#1c2029` |
| `--elev` | `#ffffff` | `#1f232f` |
| `--border` | `#e6e8f0` | `#282d3a` |
| `--border-strong` | `#d5d8e4` | `#39404f` |
| `--text` | `#1a1d27` | `#e9ebf4` |
| `--muted` | `#6b7186` | `#98a0b4` |
| `--faint` | `#9aa0b2` | `#6b7386` |
| `--primary` | `#5b52e8` | `#8b83ff` |
| `--primary-soft` | `#eceafe` | `rgba(139,131,255,.16)` |
| `--ring` | `rgba(91,82,232,.4)` | `rgba(139,131,255,.45)` |

**Màu ngữ nghĩa (hardcode trong mockup, nên nâng thành token):**
`#8b5cf6` (tím cuối gradient) · `#16a34a` (nút nộp bài) · `#22c55e`/`#4ade80` (đã thuộc) ·
`#f43f5e` (yêu thích) · `#ef4444` (sai) · `#e11d48`/`#d97706`/`#2563eb`/`#16a34a` (4 mức flashcard).

**Màu badge theo level** (`LC` trong `Screens.dc.html`):

| Level | Light fg / bg | Dark fg / bg |
|---|---|---|
| 450 | `#15a34a` / `#e7f7ed` | `#5be08a` / `rgba(34,197,94,.15)` |
| 600 | `#0d9488` / `#def5f2` | `#2dd4bf` / `rgba(13,148,136,.16)` |
| 750 | `#2f6bed` / `#e7effd` | `#8aa6ff` / `rgba(59,110,240,.18)` |
| 860 | `#7c3aed` / `#f0e9fe` | `#c4a2ff` / `rgba(139,92,246,.18)` |
| 900 | `#e11d48` / `#fde7ec` | `#fb7185` / `rgba(244,63,94,.15)` |

⚠️ **Level 450 và 860 không tồn tại trong dữ liệu thật** (chỉ có 600/750/900) — xem §3.

**Typography** — `'Be Vietnam Pro', system-ui, sans-serif`, weights **300;400;500;600;700;800**
(nạp từ Google Fonts CDN trong mockup → **phải tự host**, xem §7.2). Font này phủ đủ tiếng Việt.

Thang cỡ chữ dùng thật: `10 · 11 · 11.5 · 12 · 12.5 · 13 · 13.5 · 14 · 14.5 · 15 · 15.5 · 16 ·
16.5 · 17 · 18 · 19 · 20 · 21 · 22 · 23 · 26 · 30 · 32 · 44` px.
`letter-spacing`: `-.02em` (heading lớn), `.06em`–`.1em` (nhãn uppercase).
`line-height`: `1.15` (title) · `1.5`–`1.65` (thường) · `1.75`–`1.95` (đọc truyện).

**Spacing / hình khối** — gap `2·3·6·7·8·9·10·11·12·14·16·18px`; padding card `14–24px`;
**radius**: `6` (chip) · `7–9` (badge/ô chữ cái) · `10–13` (nút) · `14–16` (card) · `18–22`
(card lớn/thẻ) · `999px` (pill) · `41/54px` (khung điện thoại).
**Shadow**: `0 2px 8px -3px rgba(0,0,0,.2)` (segment) · `0 6px 16px -6px var(--ring)` ·
`0 10px 24px -10px` · `0 18px 36px -16px var(--ring)` (hero) · `0 20px 40px -22px` (thẻ) ·
`0 30px 60px -20px` (popover).
**Transition**: `width .3s/.4s` · `all .15s ease` · `transform .55s cubic-bezier(.4,0,.2,1)` ·
`background .3s ease`.

**Responsive / layout** — mobile khung `390×844` (nội dung 378px), desktop `1180px`.
Max-width nội dung theo màn: `1060px` (home, vocab) · `1000px` (detail, stories, reader,
progress) · `820px` (exercise, result) · `640px` (flashcard).
Lưới đều dùng `repeat(auto-fill/auto-fit, minmax(<n>px, 1fr))` → **tự co giãn, không cần media
query cho phần lưới**. Khác biệt mobile↔desktop nằm ở **shell** (tab bar vs sidebar), không ở
nội dung — cả 2 layout dùng chung `Screens`.

**Icon** — inline SVG, `stroke-width 1.9–2.4`, `stroke-linecap/linejoin: round`, viewBox 24.
Bộ icon: home, vocab (sách), flashcard, stories, exercise, progress, back (chevron trái),
chevron phải, loa, kính lúp, tim, check, mặt trời, mặt trăng, cúp. **Không dùng icon font.**

### 1.6 Tương tác & state (bắt buộc phải có)

State gốc trong `TOEIC Vocab.dc.html`, **persist vào `localStorage` key `toeic:v2`**:

```js
{ theme, masteredIds, favIds, readIds, srs }
```

| Tính năng | Chi tiết trong mockup |
|---|---|
| **Theme sáng/tối** | toggle ở shell + app root; persist |
| **Đánh dấu đã thuộc** | `masteredIds[]`, toggle ở vocab card + detail |
| **Yêu thích** | `favIds[]`, nút ♥ |
| **Đã đọc truyện** | `readIds[]`, tự set khi mở reader |
| **Lọc từ vựng** | `{q, topic, level, lesson, pos}` — q khớp cả `word` lẫn `meaning`, **không** persist |
| **Flashcard + SRS** | Leitner box: `again→0`, `hard→max(1,box)`, `good→box+1`, `easy→box+2`; **box ≥ 3 + rating good/easy ⇒ tự đánh dấu đã thuộc**. Phiên = 8 thẻ random. `srs = {id: {box, seen}}` |
| **TTS phát âm** | `window.speechSynthesis`, `lang='en-US'`, `rate=0.9`, **xoá `{}` trước khi đọc**, `cancel()` trước mỗi lần đọc |
| **Làm bài & chấm** | chọn đáp án → khoá sau khi nộp → màn kết quả có điểm từng part + giải thích |
| **Popover từ** | mở từ chip trong truyện và từ danh sách "Từ mới" |
| **Streak / mục tiêu ngày** | **hardcode** `streak: 5, todayGoal: 12, todayDone: 4+good+easy` — chưa có logic thật (xem §12 Q4) |
| **Biểu đồ 7 ngày** | **dữ liệu giả** `[3,5,2,6,4,7,mastered.size]` (xem §12 Q4) |

---

## 2. Phân tích dữ liệu

Số liệu lấy trực tiếp từ `data/` (parse bằng PyYAML).

### 2.1 Tổng quan

| Nguồn | Số file | Định dạng | Nội dung |
|---|---|---|---|
| `data/words/` | 13 | YAML (list phẳng) | 558 entry (537 từ duy nhất) |
| `data/story/story-en/` | 28 | Markdown | Truyện tiếng Anh |
| `data/story/story-vi/` | 28 | Markdown | Truyện chêm tiếng Việt |
| `data/exercises/` | 28 | YAML (list phẳng) | 704 câu (Part 5/6/7) |
| `data/slugs/` | 2 | Markdown (bảng) | Bảng tra chủ đề & 28 chương |

Trục nối 4 nguồn là **`lesson-NN`** (NN = 01…28).

### 2.2 `data/slugs/` — hai bảng tra

Hugo **không** load `.md` trong `data/` (chỉ `.yaml/.json/.toml/.xml/.csv`) → phải chuyển sang
YAML (§6.2).

**`category-slug.md`** — 13 topic, 30 sub-topic:

| topic | sub-topic |
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

Dòng 23–29 có **nhãn tiếng Việt cho sub-topic** (`banking` = "Ngân hàng"…) — nguồn duy nhất.
⚠️ **Không có nhãn tiếng Việt cho 13 topic chính** → §12 Q1.

**`story-slug.md`** — 28 chương *"Project Aria"*, có: số chương, **Hồi** (I–IV), topic, tên chương
EN, story slug.

| Hồi | Chương | Chủ đề |
|---|---|---|
| I — Khởi đầu | 1–8 | offices ×2, personnel ×2, general-business ×4 |
| II — Ra thế giới | 9–16 | travel ×2, dining-out ×2, finance-budgeting ×2, purchasing ×2 |
| III — Khủng hoảng & tôi luyện | 17–24 | manufacturing ×2, corporate-development ×2, technical-areas ×2, housing-property ×2 |
| IV — Định đoạt | 25–28 | health ×2, entertainment ×2 |

Mỗi topic đúng 2 lesson, trừ `general-business` (4). Đây là **truyện dài liền mạch, có cốt
truyện, nhân vật xuyên suốt**, nhiều chương kết bằng câu dẫn sang chương sau → **thứ tự bài học
có ý nghĩa**.

### 2.3 `data/words/*.yaml`

Một file = một topic, tên file = slug. List phẳng. Schema **đồng nhất 100%** trên 558 entry:

| Field | Kiểu | Có | Ghi chú |
|---|---|---|---|
| `word` | string | 558 | dạng gốc, viết thường |
| `pos` | string | 558 | noun 396 · verb 89 · adjective 58 · phrasal verb 8 · preposition 5 · adverb 2 |
| `ipa` | string | 558 | |
| `meaning` | string | 558 | tiếng Việt |
| `topic` | string | 558 | slug |
| `sub-topic` | string \| null | 558 | **null ở 209 entry** |
| `lesson` | list[string] | 558 | luôn là mảng |
| `level` | int | 558 | **600 (211) · 750 (240) · 900 (107)** |
| `forms` | map | 558 | value là string **hoặc list** |
| `collocations` | list[{en,vi}] | 558 | 2–4 cụm |
| `example` | {en,vi} | 558 | `en` bọc từ đích trong `{…}` |
| `note` | string | **210** | chỉ khi từ dễ nhầm |

**Bốn điểm phải xử lý:**

1. `example.en` chứa marker `{…}` (558/558) — parse thành highlight. Mockup có sẵn hàm
   `parseEx()` dùng regex `/\{([^}]+)\}/g` → port nguyên sang JS của site.
2. `forms` value **string hoặc list** (`noun: ["chair", "chairperson"]`). Mockup **luôn giả định
   string** (`w.forms[k]` render thẳng) → JS của site phải xử lý cả 2, nếu không sẽ hiện
   `chair,chairperson` dính liền.
3. `sub-topic: null` ở 209/558 entry.
4. **`word` KHÔNG duy nhất** — 558 entry / 537 từ. **20 từ nằm ở 2–3 chủ đề với nghĩa khác nhau:**

   | Từ | Chủ đề |
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

   ⚠️ **Mockup dùng `word` làm khóa ở khắp nơi**: `masteredIds`, `favIds`, `srs`, `vocabBy{}`,
   `selWord`, `newWords[]`, `tok.w`. Với 20 từ này, khóa sẽ **đụng độ** — đánh dấu đã thuộc
   `stock` (finance) sẽ đánh dấu luôn `stock` (purchasing), và `vocabBy` sẽ **mất một trong hai
   entry**. **Bắt buộc đổi khóa thành `<topic>:<word>`** ở mọi chỗ. Xem §3 và §12 Q2.

Phân bố từ/chủ đề: general-business 85 · finance-budgeting 52 · personnel 49 · offices 44 ·
purchasing 40 · travel 40 · housing-property 39 · health 37 · technical-areas 36 ·
corporate-development 35 · entertainment 35 · manufacturing 34 · dining-out 32.
Mỗi bài 15–29 từ; cả 28 bài đều được phủ.

### 2.4 `data/story/`

Markdown thuần, không front matter. Cấu trúc:

```markdown
# LESSON 01 — OFFICES: Họp & Ủy ban · Thư từ & Liên lạc      ← dòng 1
                                                              ← dòng 2 trống
> **Chương 1** của truyện dài *"Project Aria"* — ...          ← dòng 3–5 blockquote
> 27 từ (mục 9.1 + 9.2 trong `vocab-list.md`).                   (chương, số từ, nhân vật)
> Nhân vật chính: **Diane Whitfield** (CEO), ...
                                                              ← dòng 6 trống
---                                                           ← dòng 7
                                                              ← dòng 8 trống
### Chapter 1 — The Vote        (CHỈ bản EN, từ dòng 9)       ← dòng 9+ thân truyện
---                                                           ← dòng cuối
```

**Đánh dấu từ vựng khác nhau giữa 2 bản** — đây là điểm mấu chốt cho màn Reader:

- **VI:** `**từ_EN** (nghĩa tiếng Việt)` → `gửi một **memo** (thông báo nội bộ) tới toàn bộ
  **board of directors** (hội đồng quản trị)`. Có dạng tách rời: `**put** người đó **on hold** (cho giữ máy)`
- **EN:** chỉ `**từ**`, **không** có ngoặc dịch, và **đã chia thì** → `**enclosed**`, `**notified**`,
  `**convened**`. Cũng có dạng tách rời: `**put** him **on hold**`

**Lỗi & khác biệt đã phát hiện:**

| Vấn đề | Chi tiết | Xử lý |
|---|---|---|
| ⚠️ **3 file EN lẫn bản VI** | `story-en/story-02.md`, `03`, `14` chứa cả bản VI rồi mới tới `### Chapter`. Heading ở dòng **29 / 31 / 23** thay vì 9. | Cắt từ `### Chapter` trở đi; **kiểm tra tay 3 file** |
| VI không có `### Chapter` | 0/28 file VI có; 28/28 file EN có | Lấy tên chương từ `story-slug.md` |
| H1 dùng nhãn tự do | `# LESSON 11 — DINING OUT: Đặt bàn · Tiếp khách…` nhưng `dining-out` **không có sub-topic** | H1 chỉ là text hiển thị, không dùng làm slug |
| Câu dẫn chương sau | `*Hết Chương N. Chương sau (lesson-NN): …*` cuối bản VI | Tách thành `teaser` |
| `story-28` | có `*(HỒI KẾT)*` | giữ nguyên |

**Git:** `data/lessions/` (56 file, sai chính tả) đã xoá khỏi working tree **nhưng chưa commit**;
`data/story/` chưa track → dọn ở M0.

### 2.5 `data/exercises/*.yaml`

Một file = một bài (`exercise-01.yaml` ↔ `lesson-01`). **Ánh xạ 1:1 tuyệt đối** — đã kiểm cả 28
file: mỗi file chỉ có **một** `topic` và **một** `lesson`, khớp `story-slug.md`.

Tổng **704 câu**: Part 5 = 326 · Part 6 = 210 · Part 7 = 168 (~25 câu/bài).

Schema **khác nhau theo part**:

| Field | Part 5 (326) | Part 6 (210) | Part 7 (168) |
|---|:---:|:---:|:---:|
| `id`,`part`,`topic`,`lesson`,`level`,`related_word`,`options`,`answer`,`explanation_vi` | ✅ | ✅ | ✅ |
| `question` | ✅ | ❌ **không có** | ✅ |
| `passage_group`, `passage` | ❌ | ✅ | ✅ |

- **Part 6 không có `question`** — chỗ trống nằm trong `passage` dạng `**(13)______**`.
- `passage` **lặp nguyên văn** ở mọi item cùng `passage_group` → phải group lại khi render.
- `passage` và `explanation_vi` chứa **Markdown** → phải `markdownify`.
- `related_word`: 527 non-null / 177 null. **Đã verify 100% non-null resolve được** về
  `data/words/` → an toàn làm khóa join (dùng cho "câu này liên quan từ nào").
- `id` thật: `exercise-01-p5-01` (SKILL.md ghi `ex01-p5-01` — dữ liệu thật là chuẩn).

---

## 3. Đối chiếu mockup ↔ dữ liệu thật — khoảng cách phải lấp

Mockup dùng **dữ liệu mẫu viết tay cho riêng lesson-01** (27 từ, 3 truyện, 1 đề). Dữ liệu thật
lớn hơn ~20× và **schema lệch ở nhiều chỗ**. Đây là phần rủi ro cao nhất của dự án.

### 3.1 Bảng lệch schema

| Mục | Mockup | Dữ liệu thật | Cách lấp |
|---|---|---|---|
| **`level`** | 450, 600, 750, 860, 900 | chỉ **600, 750, 900** | Sinh filter/badge/dashboard **từ level thật có trong dữ liệu**, không hardcode 5 mức. Giữ nguyên bảng màu, chỉ dùng 3 mức. §12 Q3 |
| **`topic`** | `office`, `communication` | đó là **sub-topic** (`meetings-committees`, `correspondence`); topic thật là `offices` | Filter "Chủ đề" phải **2 tầng**: 13 topic → 30 sub-topic. §12 Q5 |
| **`pos`** | có `phrase` | có `phrasal verb`, `preposition` | Mở rộng `posLabel`: thêm `phrasal verb`→"cụm động từ", `preposition`→"giới từ" |
| **`forms`** | value luôn string | có thể là **list** | JS phải xử lý cả 2 kiểu |
| **Khóa từ** | `word` | `word` **không duy nhất** (20 trùng) | Đổi mọi khóa sang `<topic>:<word>` |
| **Truyện** | mảng token `['text', {w:'memo'}, …]` | Markdown `**memo** (nghĩa)` | **Script tokenize** — việc lớn nhất, §6.3 |
| **Từ đã chia** | `{w:'enclose', label:'enclosed'}` | EN có `**enclosed**` | Cần **map dạng chia → lemma** |
| **Cụm tách rời** | `{w:'put sb on hold', label:'put him on hold'}` = 1 chip | `**put** him **on hold**` = 2 vùng bold rời | Cần **annotation tay** cho các ca này |
| **Story `summary`** | có | **không có** | Sinh từ blockquote/`teaser`, hoặc viết 28 tóm tắt. §12 Q6 |
| **Story `newWords`** | có | **không có** | **Suy ra được** từ `data/words` (lọc `lesson`) |
| **Story `level`** | có | **không có** | Suy ra = level phổ biến nhất / trung vị của từ trong bài |
| **Story `coming`** | có | **không có** | Đặt `false` cho cả 28 (dữ liệu đã đủ) |
| **Part 6 passage** | `template` với `{13}` | `passage` với `**(13)______**` | Đổi regex sang `/\*\*\((\d+)\)_+\*\*/g` |
| **Part 7** | `body`, `prompt`, `n` | `passage`, `question`, không có `n` | Map `question`→`prompt`; `n` = số thứ tự parse từ `id` |
| **Giải thích** | `explain` | `explanation_vi` | Đổi tên khi build JSON |
| **Passage heading/meta** | `heading` + `meta` tách riêng | nằm **trong** `passage` (`**MEMORANDUM**`, `**To:** …`) | Tách 2 dòng đầu, hoặc render cả khối. §12 Q7 |
| **Quy mô đề** | 1 đề 26 câu | **28 đề × ~25 câu** | Bài tập phải **theo từng bài học** |
| **Quy mô từ** | 27 từ 1 lưới | **558 từ** | Cần phân trang / lazy render |

### 3.2 Ba việc khó nhất

1. **Tokenize truyện** (§6.3) — biến 56 file Markdown thành mảng token có `{w: <khóa từ>}`.
   Khó vì: từ ở bản EN đã chia (`convened` → `convene`), cụm bị tách (`put … on hold`), và một
   từ có thể trùng tên ở 2 chủ đề. Không thể tự động 100% → cần script + báo cáo ca không khớp
   để sửa tay.
2. **Quy mô 558 từ ở màn Vocab** — mockup render thẳng cả lưới. 558 card DOM một lúc sẽ giật
   trên mobile. Cần phân trang hoặc render dần (xem §7.4).
3. **Streak / mục tiêu ngày / biểu đồ 7 ngày** — mockup **hardcode** hoàn toàn. Muốn chạy thật
   phải tự thiết kế: lưu lịch sử học theo ngày vào localStorage. §12 Q4.

---

## 4. Kiến trúc: SPA hay nhiều trang?

Đây là quyết định gốc, chi phối mọi phần sau.

Mockup **không có URL** — 9 màn chuyển bằng `app.go()`. Nhưng mockup tự ghi *"trang tĩnh Hugo,
tương tác client-side"* và vẽ thanh địa chỉ `ndchungict.github.io`.

| PA | Mô tả | Ưu | Nhược |
|---|---|---|---|
| **A. SPA thuần** | Hugo sinh 1 trang + JSON; JS lo tất cả | Bám mockup 100%, dễ nhất | Không có URL chia sẻ được, không SEO, mất hoàn toàn giá trị của Hugo |
| **B. MPA thuần** | Mỗi màn 1 trang Hugo, không JS state | SEO tốt | **Không dựng lại được mockup** — flashcard/quiz/filter/popover buộc phải có JS |
| **C. Hybrid (đề xuất)** | Hugo sinh trang thật cho phần **nội dung**; JS island cho phần **ứng dụng**; điều hướng giữa "màn" dùng URL thật | Giữ đúng giao diện mockup, có URL + SEO, tận dụng Hugo | Phức tạp hơn A |

**Chọn PA C.** Phân vai:

| Màn mockup | Cách làm | URL |
|---|---|---|
| `home` | Trang Hugo tĩnh; các số liệu (đã thuộc/streak) do JS điền từ localStorage | `/` |
| `stories` | Trang Hugo, render 28 card từ dữ liệu build-time | `/lessons/` |
| `reader` | **Trang Hugo cho mỗi chương** (28 trang) — truyện render sẵn HTML; JS chỉ lo toggle chêm/EN, hiện nghĩa, popover | `/lessons/lesson-01/` |
| `detail` | **Trang Hugo cho mỗi từ** (558 trang) — nội dung render sẵn | `/words/<topic>/<word>/` |
| `vocab` | Trang Hugo + **JS island**: fetch `words.json`, lọc & render client-side | `/words/` (+ `?q=&topic=&level=` để chia sẻ được) |
| `flashcard` | Trang Hugo rỗng + **JS island** (SRS thuần client) | `/flashcard/` |
| `exercise` | **Trang Hugo cho mỗi bài** — đề render sẵn HTML; JS lo chọn/nộp/chấm | `/lessons/lesson-01/exercise/` |
| `result` | **Không phải trang riêng** — cùng trang exercise, JS đổi view sau khi nộp | `…/exercise/#result` |
| `progress` | Trang Hugo rỗng + **JS island** (đọc localStorage) | `/progress/` |

Lý do tách như vậy: **cái gì phái sinh từ dữ liệu → Hugo render sẵn** (SEO, không cần JS, hiện
ngay). **Cái gì phái sinh từ trạng thái người dùng → JS** (không thể biết lúc build).

Hệ quả với `result`: mockup coi nó là màn riêng và bottom-tab đổi theo alias `result→exercise`.
Gộp vào trang exercise là đúng tinh thần đó và tránh mất state khi chuyển trang.

---

## 5. Kiến trúc nội dung Hugo

### 5.1 Content vs Data

**Văn xuôi sửa tay → `content/`. Dữ liệu do skill sinh → `data/`. Trạng thái người dùng → localStorage.**

| Nguồn | Đích | Lý do |
|---|---|---|
| Truyện EN/VI | `content/lessons/lesson-NN/` | Văn xuôi, cần URL + SEO, sẽ sửa tay. **Bắt buộc**: Hugo không load `.md` từ `data/` |
| `data/words/*.yaml` | **giữ nguyên** | Dữ liệu thuần, do skill `toeic-vocab-yaml` sinh |
| `data/exercises/*.yaml` | **giữ nguyên** | Do skill `toeic-execise-to-yaml` sinh; SKILL.md đã ghi *"Hugo picks it up as `site.Data.exercises`"* |
| `data/slugs/*.md` | → `data/taxonomy.yaml` | Hugo không đọc `.md` trong `data/` |

### 5.2 Cấu trúc `content/`

```
content/
├── _index.md                     # home
├── lessons/
│   ├── _index.md                 # màn "stories" — 28 card
│   ├── lesson-01/                # leaf bundle
│   │   ├── index.md              #   front matter + truyện VI (đã tokenize)
│   │   ├── story-en.md           #   page resource: truyện EN (đã tokenize)
│   │   └── exercise.md           #   page resource: trang bài tập (nested page)
│   └── … lesson-28/
├── words/
│   ├── _index.md                 # màn "vocab" (JS island)
│   └── _content.gotmpl           # Content Adapter → 558 trang detail
├── topics/
│   ├── _index.md
│   └── _content.gotmpl           # Content Adapter → 13 trang
├── flashcard/_index.md           # JS island
└── progress/_index.md            # JS island
```

Lesson dùng **leaf bundle**: truyện EN là page resource, lấy bằng
`(.Resources.Get "story-en.md").Content`. Lý do gộp 1 URL thay vì tách `/vi/` `/en/`: cùng một
nội dung, tách 2 URL sẽ chia nhỏ SEO và tạo duplicate content; mockup cũng dùng **toggle tại chỗ**.

> Đây **không** phải Hugo multilingual. Giao diện chỉ tiếng Việt (mọi nhãn trong mockup đều
> tiếng Việt); EN/VI là 2 phiên bản của *nội dung học*, không phải 2 bản dịch của website.

### 5.3 Trang bài tập

Mockup gộp cả Part 5/6/7 vào **một đề**. Dữ liệu thật là 28 đề riêng → mỗi bài học một trang
bài tập: `/lessons/lesson-01/exercise/`, dựng từ `data/exercises/exercise-01.yaml`.

### 5.4 Taxonomies

```toml
[taxonomies]
  topic    = "topics"      # 13 term
  subtopic = "subtopics"   # 30 term
  act      = "acts"        # 4 term (Hồi I…IV)
```

Gắn trên lesson page. **Không** làm taxonomy cho `level`/`pos` — chúng là thuộc tính của *từ*
(data) và mockup đã lọc chúng ở client. Sinh trang taxonomy cho chúng là thừa.

### 5.5 URL

Project site (`github.com/ndchungict/toeic-vocab`) → mọi URL dưới `/toeic-vocab/`.

| Trang | URL |
|---|---|
| Home | `/toeic-vocab/` |
| Danh sách truyện | `/toeic-vocab/lessons/` |
| Chương | `/toeic-vocab/lessons/lesson-01/` |
| Bài tập | `/toeic-vocab/lessons/lesson-01/exercise/` |
| Danh sách từ | `/toeic-vocab/words/` |
| Chi tiết từ | `/toeic-vocab/words/offices/board-of-directors/` |
| Chủ đề | `/toeic-vocab/topics/offices/` |
| Flashcard | `/toeic-vocab/flashcard/` |
| Tiến độ | `/toeic-vocab/progress/` |

URL chi tiết từ **bắt buộc có `topic`** vì `word` không duy nhất (§2.3 điểm 4).

### 5.6 Archetypes

`archetypes/lessons.md` — chỉ dùng cho chương viết tay mới (29+); 28 chương hiện có sinh bằng
script migrate (§6.1).

---

## 6. Chuyển dữ liệu thô → Hugo + JSON

| Loại | Cơ chế | Khi nào |
|---|---|---|
| Truyện → content | **Script migrate 1 lần**, commit | M1 |
| `data/slugs/*.md` → YAML | **Script 1 lần** | M1 |
| Tokenize truyện | **Script 1 lần** + review tay | M2 |
| Trang topic (13), trang từ (558) | **Content Adapter** | mỗi build |
| Từ vựng & bài tập trong trang | **data file + partial** | mỗi build |
| `words.json` cho JS island | **Custom output format** | mỗi build |

### 6.1 Truyện → `content/lessons/` : script **một lần**, rồi commit

**Chọn: `scripts/migrate_stories.py` chạy 1 lần, output commit; sau đó `content/` là source of truth.**

Vì sao không sinh lại mỗi build:
1. Truyện là văn xuôi **sẽ được sửa tay** — sinh lại sẽ đè mất chỉnh sửa.
2. **3 file EN đang lỗi** (§2.4) — sửa là thao tác tay một lần, không phải quy tắc lặp được.
   Để generator chạy mãi thì phải nhét special-case cho 3 file vào code.
3. Metadata parse từ **bảng Markdown** — mong manh; parse 1 lần rồi đóng băng thành front matter
   an toàn hơn.
4. Content trong git = diff/review được, build nhanh.

Vì sao không dùng Content Adapter cho truyện: adapter chỉ đọc được `data/` hoặc `assets/`, mà
`.md` trong `data/` thì Hugo không load. Vòng vèo mà không lợi gì.

Thuật toán: parse `story-slug.md` → dict theo `lesson-NN`; với mỗi NN, bỏ 8 dòng đầu bản VI,
lấy từ `### Chapter` trở đi ở bản EN (tự xử lý đúng 3 file lỗi), tách `teaser` cuối bản VI, suy
`subtopics` từ `data/words`. Front matter:

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
summary: ""            # ← cần điền, §12 Q6
level: 750             # ← trung vị level của từ trong bài
characters:
  - { name: "Diane Whitfield", role: "CEO" }
teaser: "Chương sau (lesson-02): …"
weight: 1
---
```

### 6.2 `data/slugs/*.md` → `data/taxonomy.yaml` : script **một lần**

```yaml
topics:
  offices:
    slug: "offices"
    label_vi: "Văn phòng"          # ⚠️ phải điền tay, §12 Q1
    label_en: "Offices"
    subtopics:
      - { slug: "meetings-committees", label_vi: "Họp & Ủy ban" }
      - { slug: "correspondence",      label_vi: "Thư từ & Liên lạc" }
acts:
  - slug: "hoi-i-khoi-dau"
    label: "Hồi I — Khởi đầu"
    lessons: ["lesson-01", "…", "lesson-08"]
    summary: "dựng bối cảnh, quyết định làm Project Aria…"
```

`label_vi` của sub-topic lấy từ dòng 23–29 `category-slug.md`; `summary` của hồi lấy từ mục
"Cấu trúc 4 hồi". **13 nhãn topic phải điền tay.**

### 6.3 Tokenize truyện — việc khó nhất

Màn Reader cần mỗi từ vựng là **chip bấm được**. Mockup biểu diễn bằng mảng token; dữ liệu thật
là Markdown `**từ**`. Cần chuyển đổi có kiểm soát.

**Chọn: `scripts/tokenize_stories.py` chạy 1 lần, ghi kết quả vào front matter dạng cấu trúc,
KHÔNG parse `**bold**` lúc runtime.** Lý do: khớp `**enclosed**` → `enclose` cần từ điển dạng
chia + xử lý ca ngoại lệ; làm ở build-time bằng Go template thì không khả thi, và làm ở runtime
JS thì lặp lại chi phí trên mọi lượt truy cập.

Thuật toán:
1. Lấy tập từ ứng viên của bài = mọi entry `data/words` có `lesson` chứa `lesson-NN`.
2. Sinh **bảng dạng chia → lemma** từ chính dữ liệu: `word` + mọi giá trị trong `forms`
   (nhớ `forms` có thể là list) + biến thể quy tắc (`-s`, `-ed`, `-ing`, `-ly`).
3. Quét từng vùng `**…**`, khớp không phân biệt hoa thường; ghi
   `{w: "<topic>:<word>", label: "<nguyên văn trong truyện>"}`.
4. Ở bản VI, **cắt bỏ** `(nghĩa)` ngay sau chip — nghĩa đã có trong dữ liệu từ vựng, hiện qua
   nút "Hiện nghĩa" như mockup.
5. **Báo cáo** mọi vùng `**…**` không khớp được → sửa tay. Dự kiến các ca: cụm tách rời
   (`**put** him **on hold**`), tên riêng in đậm (`**Diane Whitfield**` — **không phải** từ vựng,
   phải loại), từ ngoài danh sách bài.
6. Ghi ra `content/lessons/lesson-NN/tokens.json` (page resource) hoặc front matter `paragraphs`.

⚠️ **Tên riêng in đậm là bẫy lớn**: blockquote metadata và thân truyện đều in đậm tên nhân vật.
Script phải chỉ nhận vùng bold **khớp danh sách từ vựng của bài**, mọi thứ khác giữ nguyên text.

### 6.4 Trang topic & trang từ : **Content Adapter**

Hugo ≥ 0.126 có `_content.gotmpl` sinh page từ data lúc build — đúng cho dữ liệu **thuần phái
sinh, không sửa tay**.

```go-html-template
{{/* content/words/_content.gotmpl */}}
{{ range $topic, $words := site.Data.words }}
  {{ range $words }}
    {{ $.AddPage (dict
        "path"   (printf "%s/%s" $topic (urlize .word))
        "title"  .word
        "params" (dict "entry" . "key" (printf "%s:%s" $topic .word))
    ) }}
  {{ end }}
{{ end }}
```

`path` **phải** gồm `topic` để 20 từ trùng không đè nhau.

> **Fallback** nếu phải pin Hugo < 0.126: `scripts/gen_pages.py` sinh stub front matter, chạy
> trong CI trước `hugo`.

### 6.5 `words.json` cho JS island

Màn Vocab / Flashcard / Progress cần toàn bộ 558 từ ở client. Sinh bằng Hugo custom output
format:

```
/toeic-vocab/words/index.json
```

Payload rút gọn (chỉ field mà 3 màn đó dùng — **không** kèm `collocations`/`note`, chúng chỉ cần
ở trang detail đã render sẵn):

```json
[{ "k":"offices:agenda", "w":"agenda", "p":"noun", "i":"/əˈdʒendə/",
   "m":"chương trình họp", "t":"offices", "s":"meetings-committees",
   "l":["lesson-01"], "v":600, "u":"/toeic-vocab/words/offices/agenda/",
   "ex":"The first item on the {agenda} is the budget.", "exv":"…" }]
```

Ước tính ~150 KB thô / ~35 KB gzip cho 558 từ — chấp nhận được. Key viết tắt để giảm ~30% dung
lượng. `fingerprint` để cache vĩnh viễn.

### 6.6 Bài tập trong trang

Đọc thẳng `site.Data.exercises`, render sẵn HTML (đề + lựa chọn), và nhúng đáp án dạng:

```html
<script type="application/json" id="ex-answers">{"exercise-01-p5-01":{"a":"B","e":"…"}}</script>
```

Static site thì **ai xem source cũng thấy đáp án** — không chống được, và cũng không cần vì đây
là công cụ tự học. Không obfuscate.

Ba partial phải viết cẩn thận:
- `word/example.html` — parse `{…}`: `replaceRE` `\{([^}]+)\}` → `<mark>`
- `word/forms.html` — `reflect.IsSlice` để xử lý string-vs-list
- `exercise/part6.html` — group theo `passage_group`, render passage **một lần**, regex chỗ trống
  `\*\*\((\d+)\)_+\*\*`

---

## 7. Thiết kế theme & layout

### 7.1 Custom theme

**Theme tự viết, đặt thẳng ở `layouts/` + `assets/` (không tạo `themes/`).** Mockup có ngôn ngữ
thiết kế riêng và rất cụ thể; mọi theme có sẵn đều phải gỡ bỏ nhiều hơn là tận dụng.

### 7.2 Tái hiện CSS

Mockup **không có file CSS** — toàn bộ là inline style object trong JS. Nên công việc là **dịch
sang SCSS**, lấy §1.5 làm nguồn token:

```
assets/scss/
├── main.scss
├── _tokens.scss       # 13 CSS var × 2 theme + màu level + màu ngữ nghĩa + shadow/radius scale
├── _base.scss         # reset (* box-sizing, html/body margin 0), scrollbar, typography
├── _shell.scss        # sidebar desktop / bottom-tab mobile / header
└── components/        # _card, _badge, _pill, _segmented, _word-card, _flashcard,
                       # _quiz, _reader, _popover, _stat, _progressbar, _hero
```

Build bằng **Hugo Pipes + libsass (có sẵn trong hugo-extended)** — không cần Node:

```go-html-template
{{ $css := resources.Get "scss/main.scss" | toCSS (dict "outputStyle" "compressed") | fingerprint }}
<link rel="stylesheet" href="{{ $css.RelPermalink }}" integrity="{{ $css.Data.Integrity }}">
```

**Theme sáng/tối:** mockup đổi theme bằng cách thay object CSS var trên thẻ bọc. Trên site làm
bằng `<html data-theme="light|dark">` + `:root[data-theme=…]`, cộng `@media (prefers-color-scheme: dark)`
làm mặc định. Phải đặt **script chống nháy (FOUC)** đọc localStorage trong `<head>`, chạy trước
khi render.

**Font — bắt buộc tự host.** Mockup nạp Be Vietnam Pro từ Google Fonts CDN; trên GitHub Pages
phải đưa vào `assets/fonts/` + `@font-face` + `font-display: swap`, **subset `latin` + `latin-ext`
+ `vietnamese`**, chỉ lấy weight thật dùng (300/400/500/600/700/800 — cân nhắc bỏ 300 nếu không
dùng). Lý do: không phụ thuộc bên thứ ba, nhanh hơn, không rò rỉ IP người dùng.

### 7.3 Template cần tạo

```
layouts/
├── _default/{baseof,list,single,taxonomy,term}.html
├── index.html                       # home
├── lessons/{list,single}.html       # stories / reader
├── words/{list,single}.html         # vocab (island) / detail
├── topics/{list,single}.html
├── flashcard/list.html              # island
├── progress/list.html               # island
├── 404.html
└── partials/
    ├── head.html                    # meta, OG, CSS, script chống nháy theme
    ├── shell/{sidebar,tabbar,header}.html
    ├── ui/{badge-level,speak-button,stat-card,progress-bar,section-label,pill,segmented}.html
    ├── icons/*.html                 # 15 inline SVG (§1.5)
    ├── word/{card,example,forms,collocations,note}.html
    ├── lesson/{card,story,new-words,nav-prev-next}.html
    └── exercise/{section,part5,part6,part7,answers-json}.html
```

### 7.4 JavaScript

Vanilla JS, bundle bằng `js.Build` (esbuild có sẵn trong Hugo). Không framework — mockup dùng
React nhưng đó là do công cụ dựng mockup, không phải yêu cầu.

```
assets/js/
├── store.js         # localStorage 'toeic:v2': theme, mastered, fav, read, srs, history
├── theme.js         # toggle + đồng bộ data-theme
├── speak.js         # TTS: speechSynthesis, xoá {}, lang en-US, rate .9, cancel() trước
├── vocab-list.js    # island: fetch words.json, lọc, phân trang, sync ?query
├── flashcard.js     # island: chọn 8 thẻ, lật 3D, Leitner box, auto-mastered khi box>=3
├── quiz.js          # chọn/nộp/chấm, đổi sang view kết quả
├── reader.js        # toggle chêm/EN, hiện nghĩa, popover
├── progress.js      # island: dashboard từ localStorage
└── word-actions.js  # nút đã thuộc / yêu thích (dùng chung nhiều màn)
```

**Quy tắc bắt buộc:** mọi khóa trong `store.js` là `<topic>:<word>`, **không** phải `word`
(§2.3 điểm 4). Ghi rõ trong comment, kèm hàm `key(topic, word)` duy nhất để không ai viết tay.

**Quy mô 558 từ ở màn Vocab:** không render hết một lượt. Đề xuất: lọc trên mảng JS (nhanh, 558
phần tử là không đáng kể) nhưng **chỉ render 60 card đầu**, thêm nút "Xem thêm" hoặc
`IntersectionObserver`. Mockup không có phân trang vì chỉ có 27 từ — đây là điều chỉnh **bắt
buộc do quy mô**, không phải thêm tính năng.

---

## 8. Cấu hình Hugo

```toml
baseURL                = "https://ndchungict.github.io/toeic-vocab/"
languageCode           = "vi-VN"
defaultContentLanguage = "vi"
title                  = "VocabTOEIC — Tự học từ vựng"
enableRobotsTXT        = true
enableGitInfo          = true
hasCJKLanguage         = false
timeZone               = "Asia/Ho_Chi_Minh"

[taxonomies]
  topic    = "topics"
  subtopic = "subtopics"
  act      = "acts"

[markup.goldmark.renderer]
  unsafe = true            # BẮT BUỘC: passage Part 6/7 và truyện có HTML inline
[markup.tableOfContents]
  startLevel = 2
  endLevel   = 3

[params]
  description    = "558 từ vựng TOEIC theo 13 chủ đề, học qua truyện dài 28 chương “Project Aria”."
  totalWords     = 537
  totalLessons   = 28
  totalTopics    = 13
  totalExercises = 704
  storyTitle     = "Project Aria"
  flashSessionSize = 8      # khớp mockup
  dailyGoal        = 12     # khớp mockup
  # màu/typography khai báo DUY NHẤT ở _tokens.scss, không lặp ở đây

[menu]
  # khớp sidebar desktop của mockup (6 mục), mobile lấy 5 mục đầu trừ "Bài tập"
  [[menu.main]]
    name = "Trang chủ" ; pageRef = "/"          ; weight = 10 ; params.icon = "home"
  [[menu.main]]
    name = "Từ vựng"   ; pageRef = "/words"     ; weight = 20 ; params.icon = "vocab"
  [[menu.main]]
    name = "Flashcard" ; pageRef = "/flashcard" ; weight = 30 ; params.icon = "flashcard"
  [[menu.main]]
    name = "Truyện chêm"; pageRef = "/lessons"  ; weight = 40 ; params.icon = "stories"
  [[menu.main]]
    name = "Bài tập"   ; pageRef = "/lessons"   ; weight = 50 ; params.icon = "exercise" ; params.desktopOnly = true
  [[menu.main]]
    name = "Tiến độ"   ; pageRef = "/progress"  ; weight = 60 ; params.icon = "progress"

[outputs]
  home = ["HTML", "RSS"]
  section = ["HTML"]

[outputFormats.WordsJSON]
  mediaType = "application/json"
  baseName  = "index"
  isPlainText = true

[minify]
  disableXML = true
```

`words.json` bật riêng ở front matter của `content/words/_index.md`:
`outputs: ["HTML", "WordsJSON"]`.

**Ba lưu ý về `baseURL`:**
1. **Project site** (`ndchungict/toeic-vocab`) → phải có hậu tố `/toeic-vocab/` và dấu `/` cuối.
2. Mọi URL trong template/JS phải qua `.RelPermalink`/`relURL` — **không hardcode `/`**. Với JS,
   truyền base qua `<body data-base="{{ "/" | relURL }}">`. Lỗi này chạy `hugo server` local vẫn
   đúng nên rất dễ lọt.
3. Custom domain sau này: đổi baseURL + thêm `static/CNAME`; workflow đã lấy baseURL động.

Thêm `static/.nojekyll` để GitHub Pages không chạy Jekyll (nếu không, thư mục bắt đầu bằng `_`
bị nuốt).

---

## 9. GitHub Actions & deploy

Dùng **GitHub Pages qua Actions**, không dùng nhánh `gh-pages` (sạch hơn: không có artifact build
trong lịch sử git). **Cần bật tay một lần:** Settings → Pages → Source = **GitHub Actions**.

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
      HUGO_VERSION: 0.148.1        # pin cứng; Content Adapter cần >= 0.126
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
        run: hugo --gc --minify --baseURL "${{ steps.pages.outputs.base_url }}/"

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

- **`hugo_extended`** bắt buộc vì dùng SCSS qua `toCSS`.
- **Pin version cứng** để build tái lập được.
- **`--baseURL` từ `configure-pages`** tự đúng cho project site / user site / custom domain.
- **`fetch-depth: 0`** — thiếu thì `enableGitInfo` cho lastmod sai âm thầm.
- Không cần Node (dùng libsass + esbuild có sẵn trong Hugo).

**`.github/workflows/validate.yml`** (chạy trên PR) — đáng làm vì dữ liệu do LLM sinh qua 2 skill,
sai sót im lặng (một `related_word` gõ nhầm) không làm vỡ build mà chỉ hỏng link:

```yaml
# 1. yamllint data/**/*.yaml
# 2. python scripts/validate_data.py:
#    - topic/sub-topic khớp taxonomy.yaml
#    - mọi related_word non-null resolve được về data/words/
#    - mọi lesson-NN có đủ: content/lessons/lesson-NN/, exercise-NN.yaml, >=1 từ
#    - mọi example.en có đúng một cặp {…}
#    - exercise-NN.yaml chỉ chứa 1 topic và 1 lesson
#    - MỌI token {w:…} trong truyện resolve được về một entry từ vựng
#    - không có khóa <topic>:<word> nào trùng
# 3. hugo --gc --minify --panicOnWarning
```

---

## 10. Cây thư mục dự kiến

```
toeic-vocab/
├── .github/workflows/{deploy,validate}.yml
├── .claude/                      # giữ nguyên (2 skill sinh dữ liệu)
├── archetypes/{default,lessons}.md
├── assets/
│   ├── scss/{main,_tokens,_base,_shell}.scss + components/
│   ├── js/{store,theme,speak,vocab-list,flashcard,quiz,reader,progress,word-actions}.js
│   └── fonts/                    # Be Vietnam Pro tự host, subset vietnamese
├── content/
│   ├── _index.md
│   ├── lessons/
│   │   ├── _index.md
│   │   └── lesson-01/ … lesson-28/     ← SINH 1 LẦN rồi sửa tay
│   │       ├── index.md                  (front matter + truyện VI đã tokenize)
│   │       ├── story-en.md               (truyện EN đã tokenize)
│   │       └── exercise.md               (trang bài tập)
│   ├── words/{_index.md,_content.gotmpl}
│   ├── topics/{_index.md,_content.gotmpl}
│   ├── flashcard/_index.md
│   └── progress/_index.md
├── data/                         ← Hugo data, KHÔNG chuyển đổi
│   ├── taxonomy.yaml             ← SINH 1 LẦN từ data/slugs/*.md
│   ├── words/*.yaml              # 13 file, 558 entry
│   ├── exercises/*.yaml          # 28 file, 704 câu
│   ├── slugs/*.md                # giữ làm tài liệu + input cho 2 skill
│   └── story/{story-en,story-vi}/# bản gốc lưu trữ (§12 Q8)
├── docs/plan.md                  ← file này
├── layouts/                      # §7.3
├── mockup/                       # mockup gốc, KHÔNG build vào site
├── scripts/
│   ├── migrate_stories.py        # 1 lần (M1)
│   ├── build_taxonomy.py         # 1 lần (M1)
│   ├── tokenize_stories.py       # 1 lần (M2) + báo cáo review
│   └── validate_data.py          # CI
├── static/{.nojekyll,favicon.ico}
├── raw/                          # nguồn nháp, .gitignore, KHÔNG dùng
├── .gitignore                    # public/, resources/, .hugo_build.lock, raw/, mockup/support.js
├── hugo.toml
└── README.md
```

---

## 11. Giai đoạn triển khai (milestones)

| # | Milestone | Nội dung | Chặn bởi |
|---|---|---|---|
| **M0** | Dọn repo & khung | Commit đổi tên `data/lessions`→`data/story`. `hugo new site`, `hugo.toml`, `.gitignore`, `.nojekyll`, `baseof` trần. Push → **deploy chạy được, có URL thật**. | — |
| **M1** | Migrate dữ liệu | `build_taxonomy.py` (+ điền tay 13 nhãn VI), `migrate_stories.py` → 28 bundle, **sửa tay 3 file lỗi**, `validate_data.py` + workflow validate. | **Q1** |
| **M2** | Tokenize truyện | `tokenize_stories.py` + **review tay danh sách không khớp** (cụm tách rời, tên riêng). Đây là mốc rủi ro cao nhất — làm sớm. | M1 |
| **M3** | Design system | `_tokens.scss` (§1.5), font tự host, `_base`, shell (sidebar/tabbar/header), theme sáng-tối + script chống nháy. **Dựng đúng 2 layout mobile/desktop.** | M0 |
| **M4** | Màn nội dung | `lessons/list` (stories), `lessons/single` (reader — chưa có JS), `words/single` (detail), `topics`. Hugo render sẵn, chưa tương tác. | M2, M3 |
| **M5** | JS nền | `store.js` (khóa `<topic>:<word>`), `theme.js`, `speak.js` (TTS), `word-actions.js` (đã thuộc/yêu thích). | M4 |
| **M6** | Màn ứng dụng | `words/list` + `vocab-list.js` (lọc 4 chiều + phân trang), `flashcard.js` (Leitner + lật 3D), `reader.js` (toggle + popover). | M5 |
| **M7** | Bài tập & kết quả | `exercise.md` × 28, `quiz.js` (chọn/nộp/chấm/kết quả có giải thích). | M5 |
| **M8** | Home & Progress | Home (số liệu do JS điền), `progress.js` (4 stat, biểu đồ 7 ngày, phân bố level & chủ đề). Cần chốt **Q4** trước. | M6, M7, **Q4** |
| **M9** | Hoàn thiện | SEO (OG, JSON-LD, sitemap), 404, a11y (contrast, focus, aria cho tab/quiz/popover, `prefers-reduced-motion` cho lật thẻ), Lighthouse, rà toàn bộ URL dưới `/toeic-vocab/`. | M8 |

**Không cần chờ gì:** M0, M3 làm được ngay.
**Rủi ro tập trung ở M2** (tokenize) — nếu trượt thì màn Reader không dựng được.

---

## 12. Giả định & câu hỏi còn mở

### 12.1 Ba giả định ở bản 1 đã bị mockup bác bỏ

| Bản 1 nói | Mockup thực tế | Ảnh hưởng |
|---|---|---|
| ~~"Không cần audio, chỉ có IPA text"~~ | **Có TTS** ở 5 màn qua `window.speechSynthesis` (`en-US`, `rate .9`, xoá `{}` trước khi đọc) | Thêm `speak.js`; không cần file audio, không cần dịch vụ ngoài |
| ~~"Tooltip từ trong truyện: mặc định KHÔNG làm vì ngoài mockup"~~ | **Có** — chip bấm được + popover + nút "Hiện nghĩa" | Thành tính năng cốt lõi; kéo theo cả §6.3 (tokenize) |
| ~~"Flashcard/progress/search là có điều kiện"~~ | **Đều có**, và flashcard có **SRS Leitner đầy đủ** | Thành 3 milestone riêng (M6, M8) |

Ngoài ra bản 1 đề xuất PA A cho trang chi tiết từ (không làm trang riêng) — mockup **có màn
`detail`** → chuyển sang làm 558 trang thật (§5.5).

### 12.2 Giả định hiện tại

| # | Giả định | Căn cứ | Rủi ro |
|---|---|---|---|
| A1 | Giao diện **một ngôn ngữ: tiếng Việt**; EN/VI chỉ là 2 phiên bản *truyện* | Mọi nhãn mockup đều tiếng Việt | Thấp |
| A2 | `baseURL` = `…/toeic-vocab/` (project site) | `git remote` + thanh địa chỉ trong mockup | Thấp |
| A3 | `content/` là source of truth cho truyện sau M1 | Văn xuôi cần sửa tay | Trung bình |
| A4 | `raw/` không dùng (bạn đã xác nhận) | deny rule + xác nhận | Không |
| A5 | Không dùng React — vanilla JS | React chỉ là công cụ dựng mockup | Thấp |
| A6 | `mockup/` giữ trong repo nhưng **không build** vào site | Là tài liệu tham chiếu | Thấp |
| A7 | Hugo ≥ 0.126 (Content Adapter) | yêu cầu kỹ thuật | Thấp, có fallback |
| A8 | Phân trang màn Vocab (60 card/lượt) là **bắt buộc do quy mô**, không phải thêm tính năng | 558 vs 27 từ trong mockup | Thấp |

### 12.3 Câu hỏi cần trả lời

**Chặn công việc:**

- **Q1 — Nhãn tiếng Việt cho 13 chủ đề chính.** Dữ liệu **chỉ có slug**; sub-topic thì có nhãn
  đủ. Mockup cho thấy quy ước đặt tên (`office` → "Văn phòng & Họp") nhưng chỉ ở mức sub-topic.
  Cần bạn cho 13 nhãn. **Chặn M1.**
- **Q4 — Streak, mục tiêu ngày, biểu đồ 7 ngày.** Mockup **hardcode** (`streak: 5`, `todayGoal: 12`,
  series `[3,5,2,6,4,7,…]`). Muốn chạy thật cần lưu lịch sử theo ngày. Ba lựa chọn:
  (a) làm thật — thêm `history: {"2026-08-01": {learned: 7}}` vào localStorage;
  (b) giữ tĩnh như mockup;
  (c) bỏ streak, chỉ giữ mục tiêu ngày.
  Đề xuất **(a)**, chi phí nhỏ và là thứ giữ người học quay lại. **Chặn M8.**

**Không chặn (có mặc định, cần xác nhận):**

- **Q2 — Khóa `<topic>:<word>`.** Mockup dùng `word`; 20 từ trùng sẽ đụng độ và làm **mất entry**
  trong `vocabBy`. Đề xuất đổi khóa. Nếu đồng ý, nên sửa luôn dòng tương ứng trong
  `toeic-vocab-yaml/SKILL.md` (đang ghi `word` là khóa localStorage) để hai bên không lệch.
- **Q3 — Level 450 và 860.** Mockup có 5 mức, dữ liệu thật chỉ có 600/750/900. Đề xuất: hiển thị
  theo dữ liệu thật (3 mức), **giữ nguyên bảng màu 5 mức** để sau này thêm từ mức 450/860 là chạy
  ngay. Hay bạn muốn map lại toàn bộ dữ liệu sang 5 mức?
- **Q5 — Bộ lọc "Chủ đề".** Mockup lọc theo cái mà dữ liệu thật gọi là **sub-topic**. Với 13 topic
  + 30 sub-topic, đề xuất **2 tầng**: chọn topic → hiện pill sub-topic của topic đó. Hay bạn muốn
  giữ một tầng phẳng 13 pill?
- **Q6 — `summary` cho 28 chương.** Mockup có; dữ liệu không. Đề xuất: lấy tạm câu `teaser` của
  chương **trước** (vì nó mô tả đúng chương này), rồi bạn duyệt/sửa. Hay bạn muốn viết mới 28 tóm tắt?
- **Q7 — `heading`/`meta` của passage Part 6/7.** Mockup tách riêng; dữ liệu gộp trong `passage`
  (`**MEMORANDUM**` + `**To:** … **From:** …`). Đề xuất: script tách 2 dòng đầu thành
  `heading`/`meta`, phần còn lại là thân. Cần kiểm tra 378 item xem có nhất quán không — nếu
  không thì render cả khối như hiện tại (mất chút thẩm mỹ, không mất thông tin).
- **Q8 — `data/story/` sau khi migrate:** giữ làm bản lưu trữ (đề xuất, chi phí ~0) hay xoá để
  tránh hai nguồn gây nhầm lẫn?
- **Q9 — Thứ tự trang chủ.** Mockup hiện "Bài học hiện tại" = `stories[0]`. Với 28 chương, đề
  xuất: hiện **chương chưa đọc đầu tiên** (dựa `readIds`), fallback về chương 1.

### 12.4 Dọn dẹp nhỏ ở M0

- Commit đổi tên `data/lessions/` → `data/story/` (56 file đang dở dang trong git status).
- Thêm `raw/` vào `.gitignore` (chưa track nhưng cũng chưa ignore).
- Sửa `toeic-execise-to-yaml/SKILL.md`: tài liệu ghi id prefix `ex01-p5-01` nhưng 704 item thật
  đều dùng `exercise-01-p5-01` — sửa tài liệu theo dữ liệu.
