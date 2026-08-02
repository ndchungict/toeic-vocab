# VocabTOEIC — Tự học từ vựng

Trang web tĩnh giúp tự học **558 thẻ từ vựng TOEIC** (537 từ khác nhau) theo 13 chủ
đề, học qua bộ truyện chêm dài 28 chương **“Project Aria”** kèm 704 câu bài tập
Part 5 · 6 · 7.

- Bản chạy thật: <https://ndchungict.github.io/toeic-vocab/>
- Sinh bằng **Hugo (extended) 0.148.1**, không dùng Node — SCSS build bằng Hugo
  Pipes, JS bundle bằng `js.Build` (esbuild có sẵn trong Hugo).
- Không có backend: toàn bộ tiến độ học nằm trong `localStorage` của trình duyệt
  (khoá `toeic:v2`).

## Các màn hình

| Trang | URL | Nội dung |
|---|---|---|
| Trang chủ | `/` | Mục tiêu hôm nay, số liệu đã thuộc/tiến độ/streak, “bài học hiện tại”, lối tắt |
| Từ vựng | `/words/` | 558 thẻ từ, tìm kiếm + lọc theo chủ đề / chủ đề con / mốc điểm |
| Chi tiết từ | `/words/<topic>/<slug>/` | Nghĩa, IPA, dạng từ, collocation, ví dụ, ghi chú, phát âm TTS |
| Flashcard | `/flashcard/` | Ôn lặp ngắt quãng, phiên 8 thẻ, 4 mức Chưa nhớ / Khó / Được / Dễ |
| Truyện chêm | `/story/` | Trang giới thiệu bộ truyện: bối cảnh, nhân vật, 4 hồi, cách học một chương |
| Danh sách chương | `/lessons/` | Lưới 28 chương kèm trạng thái đã đọc |
| Đọc chương | `/lessons/lesson-01/` | Bản chêm ↔ bản tiếng Anh, popover tra từ, cột từ mới |
| Bài tập | `/lessons/lesson-01/exercise/` | Đề Part 5·6·7 của chương, chấm điểm ngay |
| Danh sách đề | `/exercises/` | 28 đề kèm kết quả đã làm |
| Tiến độ | `/progress/` | Số liệu tổng, 7 ngày gần đây, phân bố theo mốc điểm & chủ đề |
| Taxonomy | `/topics/`, `/subtopics/`, `/acts/` | Trang tổng hợp theo chủ đề, chủ đề con, hồi truyện |

Điều hướng: sidebar 6 mục ở desktop, bottom tab 5 mục ở mobile (mục “Bài tập” chỉ
có ở desktop, vào từ trang chủ).

## Chạy tại máy

```bash
hugo server                 # dev server: http://localhost:1313/toeic-vocab/
hugo                        # build ra public/
```

Kiểm tra như CI trước khi push:

```bash
python3 scripts/validate_data.py    # đối chiếu words / exercises / lessons / taxonomy
hugo --gc --minify --panicOnWarning --baseURL "https://ndchungict.github.io/toeic-vocab/"
python3 scripts/check_links.py      # rà link nội bộ trong public/
```

> Hugo phải là bản **extended** và nên đúng **0.148.1** như CI — vài hành vi (cách
> khớp `ignoreFiles`, cảnh báo deprecated) khác nhau giữa các phiên bản, mà CI chạy
> `--panicOnWarning` nên một cảnh báo cũng đủ làm hỏng build.

## Cấu trúc

```
hugo.toml            Cấu hình site: menu, taxonomy, params (số từ/bài/đề), outputs
content/             Nội dung
  _index.md            Trang chủ
  story/               Trang giới thiệu bộ truyện (nội dung nằm trong front matter)
  lessons/             28 chương: lesson-NN/_index.md + tokens.json + exercise/
  words/               _content.gotmpl sinh trang từ vựng từ data/words
  exercises/           Danh sách 28 đề
  flashcard/, progress/
layouts/             Template Hugo (baseof, từng section, partials shell/word/lesson/exercise/icons)
assets/
  scss/                main.scss + _tokens/_base/_shell + components/*
  js/                  store.js dùng chung + island riêng từng màn
data/                Dữ liệu Hugo đọc lúc build (xem dưới)
scripts/             Script Python một lần + script kiểm tra
static/fonts/        Font Be Vietnam Pro self-host
archetypes/          Mẫu front matter
mockup/              Bản mockup React gốc, dùng để đối chiếu giao diện
docs/plan.md         Tài liệu phân tích & kế hoạch chi tiết (nguồn tham chiếu §…)
```

## Dữ liệu

Hugo chỉ thực sự đọc 3 thứ trong `data/`:

| Đường dẫn | Dùng ở đâu |
|---|---|
| `data/words/<topic>.yaml` | `site.Data.words` — thẻ từ, popover, cột từ mới trong Reader |
| `data/exercises/exercise-NN.yaml` | `site.Data.exercises` — câu hỏi, đáp án, giải thích |
| `data/taxonomy.yaml` | `site.Data.taxonomy` — nhãn tiếng Việt của chủ đề, chủ đề con, 4 hồi |

Ngoài ra `data/slugs/*.md` và `data/story/story-{en,vi}/*.md` là **bản gốc dạng
markdown** của bảng tra và 28 chương truyện. Hugo không đọc chúng (đã loại trừ
bằng `ignoreFiles`), chúng chỉ là đầu vào cho các script sinh dữ liệu:

| Script | Vai trò |
|---|---|
| `build_taxonomy.py` | `data/slugs/*.md` → `data/taxonomy.yaml` |
| `migrate_stories.py` | truyện gốc → front matter `content/lessons/lesson-NN/_index.md` |
| `tokenize_stories.py` | truyện gốc → `tokens.json` (token hoá để tra từ trong Reader) |
| `generate_exercise_pages.py` | sinh trang `lesson-NN/exercise/` |
| `validate_data.py` | kiểm tra tính nhất quán giữa words / exercises / lessons / taxonomy |
| `check_links.py` | rà link nội bộ trong `public/` đã build |

Bốn script đầu là **một lần rồi commit kết quả** — chạy lại chỉ khi sửa dữ liệu gốc.

Khoá định danh một thẻ từ luôn là `"<topic>:<word>"`, không bao giờ dùng `word`
đơn lẻ: có 20 từ trùng tên ở nhiều chủ đề khác nhau.

## Vài điểm dễ vấp khi sửa

- **`ignoreFiles` không chỉ áp cho `data/`.** Regex khớp trên đường dẫn của mọi thư
  mục nguồn, và dạng đường dẫn còn khác nhau theo phiên bản Hugo. Mẫu `'story/'`
  từng nuốt luôn `content/story/` — trang biến mất mà build vẫn báo thành công. Vì
  vậy mẫu hiện tại tả rõ tới `story/story-(en|vi)/`.
- **SCSS chỉ dùng `@import`.** Hugo bundle sẵn libsass, không hiểu `@use`/`@forward`.
- **`lessons/lesson-NN/` là branch bundle** nên `Kind = "section"` y hệt `/lessons/`;
  Hugo không bao giờ chọn `layouts/lessons/single.html`. Hai trường hợp được phân
  biệt trong `layouts/lessons/list.html` bằng `.Params.lesson_id`.
- **Màu và typography khai báo duy nhất ở `assets/scss/_tokens.scss`**, không lặp
  lại trong `hugo.toml`.
- Streak và “mục tiêu hôm nay” hiện để **tĩnh** theo mockup (`site.Params`), không
  tính từ dữ liệu thật.

## Triển khai

- Push lên `main` → `.github/workflows/deploy.yml` build và đẩy lên GitHub Pages.
- Pull request vào `main` → `.github/workflows/validate.yml` chạy yamllint,
  `validate_data.py`, build strict và `check_links.py`.
