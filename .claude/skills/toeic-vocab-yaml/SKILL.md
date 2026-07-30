---
name: toeic-vocab-yaml
description: Chuyển một danh sách/bảng từ vựng TOEIC theo chủ đề thành file dữ liệu YAML dùng làm data file cho trang web học từ (Hugo + GitHub Pages). Sinh đầy đủ các trường word, pos, ipa, meaning, topic, sub-topic, level, forms (họ từ), collocations (kèm nghĩa tiếng Việt), example (câu có đánh dấu từ đích + bản dịch) và note (cặp từ dễ nhầm). HÃY DÙNG skill này bất cứ khi nào người dùng đưa một danh sách hoặc bảng từ TOEIC và muốn tạo file YAML, data file, hay dữ liệu từ vựng cho website — kể cả khi họ chỉ dán bảng từ kèm tên chủ đề mà không nói rõ chữ "YAML", "data file" hay "skill". Also use for English requests like "turn this TOEIC word list into a YAML data file", "generate vocab data for my Hugo site", or "make a YAML file from these TOEIC words".
---

# TOEIC Vocab → YAML data file

Sinh file dữ liệu YAML cho từng (chủ đề / chủ đề con) TOEIC, để dùng làm **data file** trong thư mục `data/words/` của một trang Hugo. Một file YAML = một chủ đề chính; các entry bên trong được phân biệt bằng trường `sub-topic`.

Người dùng thường cung cấp một danh sách từ hoặc dán thẳng một bảng (từ + IPA + loại từ + nghĩa + collocation) từ tài liệu của họ. Việc của skill là **giữ nguyên dữ liệu đã có** và **bổ sung phần còn thiếu** (forms, nghĩa của collocation, câu ví dụ có đánh dấu + bản dịch, level, note) theo đúng schema bên dưới.

---

## Quy tắc đầu ra

Bắt buộc tuân thủ, vì đầu ra sẽ được lưu thẳng thành file `.yaml` và nạp vào trang web:

- Chỉ xuất ra **nội dung YAML**. KHÔNG kèm giải thích, KHÔNG bọc trong dấu ``` code fence, không có chữ nào trước hoặc sau.
- Cấp cao nhất là một **LIST** (mỗi entry bắt đầu bằng `-`), KHÔNG bọc trong bất kỳ key nào.
- Mỗi entry gồm các trường theo **đúng thứ tự**: `word`, `pos`, `ipa`, `meaning`, `topic`, `sub-topic`, `story`, `level`, `forms`, `collocations`, `example`, `note`.
  - `sub-topic` **luôn giữ trường** để schema đồng đều giữa mọi file. Chủ đề có chủ đề con → điền slug. Chủ đề KHÔNG có chủ đề con → để **null** (viết `sub-topic:` rồi bỏ trống, KHÔNG dùng `""`).
  - `note` chỉ thêm khi từ dễ nhầm với từ khác; không có thì bỏ hẳn.
- Ngôn ngữ: `meaning`, mọi trường `vi`, và `note` viết bằng **TIẾNG VIỆT**. Phần còn lại bằng tiếng Anh.
- File đầu ra lưu vào thư mục words, đặt tên file theo định dạng slug.yaml (VD: general-business.yaml)

---

## Schema từng trường

- **word** — dạng gốc (nguyên thể / số ít), viết thường. Mỗi từ chỉ lấy MỘT nghĩa phù hợp nhất với ngữ cảnh công sở TOEIC. Đây cũng là khóa định danh của thẻ trong `localStorage`, nên phải là dạng chuẩn, ổn định.
- **pos** — một giá trị duy nhất: `noun` / `verb` / `adjective` / `adverb` / `preposition` / `phrasal verb`. Nếu nguồn ghi kiểu `n/v`, chọn loại từ đúng với nghĩa đang lấy; nếu cả hai đều quan trọng, ưu tiên loại từ hay được TOEIC test cho từ đó.
- **ipa** — phiên âm IPA đặt trong hai dấu gạch chéo, có dấu trọng âm chính `ˈ`, ví dụ `"/kəmˈplaɪ/"`. Nếu nguồn đã có IPA thì dùng lại, chỉ chuẩn hóa định dạng.
- **meaning** — nghĩa tiếng Việt ngắn gọn, theo **ngữ cảnh TOEIC** chứ không phải nghĩa từ điển chung.
- **topic** — slug chủ đề chính, lấy **đúng** từ bảng slug (xem `data/slugs/category-slug.md`).
- **sub-topic** — slug chủ đề con, lấy **đúng** từ bảng slug. Nếu chủ đề chính không có chủ đề con thì vẫn giữ trường nhưng để **null** (`sub-topic:` bỏ trống, không `""`).
- **lession** — Lấy theo tên bài học nơi chứa từ vựng, lấy **đúng**  đối chiếu theo `lesson-NN.md`). ( VD: lesson-01)
- **level** — mục tiêu điểm: `600` / `750` / `900` tùy độ khó và tần suất (`600` = cơ bản, hay gặp; `900` = nâng cao, ít gặp). Tự đánh giá cho từng từ. **KHÔNG** bọc trong ngoặc kép (đây là số).
- **forms** — họ từ, đặt khóa theo loại từ. CHỈ đưa dạng có thật, **KHÔNG bịa**. Bỏ khóa nào không tồn tại. Nếu một loại từ có hai dạng, để value là list.
  ```yaml
  forms:
    verb: "succeed"
    noun: "success"
    adjective: "successful"
    adverb: "successfully"
  # ví dụ có hai danh từ:
  # noun: ["negotiation", "negotiator"]
  ```
  Cấu trúc này cho phép sinh câu hỏi Part 5 dạng "chọn đúng dạng từ": bốn phương án chính là bốn form.
- **collocations** — 2–4 cụm đi kèm hay gặp trong TOEIC. Mỗi cụm là một object có `en` (cụm tiếng Anh) và `vi` (nghĩa tiếng Việt). Nếu nguồn đã có cụm tiếng Anh, giữ nguyên và **bổ sung bản dịch `vi`**.
- **example** — một câu tự nhiên trong ngữ cảnh công sở, có `en` và `vi`:
  - `en`: bọc **từ đích** trong dấu ngoặc nhọn `{…}`, viết đúng **DẠNG ĐÃ CHIA** phù hợp với câu, ví dụ `{complied}`, `{efficiently}`. Dấu `{…}` là để template khoét thành chỗ trống cho câu hỏi Part 5 — không được bỏ.
  - `vi`: bản dịch tiếng Việt của câu, **KHÔNG** có dấu ngoặc nhọn.
- **note** — chỉ thêm khi từ dễ nhầm với từ khác (ví dụ `affect`/`effect`, `efficient`/`effective`, `stationary`/`stationery`), hoặc khi từ có bẫy TOEIC (nghĩa kép, phát âm lạ, danh từ không đếm được, giới từ cố định). Trong bảng nguồn, ký hiệu ⚠️ là dấu hiệu rõ ràng nên tạo `note`. Viết bằng tiếng Việt. Không có thì bỏ hẳn trường.

---

## Bảng slug chủ đề & chủ đề con

Bảng slug **không nằm trong file này** — đọc file `data/slugs/category-slug.md` (từ thư mục gốc của project) để lấy danh sách `topic`/`sub-topic` hợp lệ và bảng ánh xạ sang tên gốc trước khi sinh dữ liệu. `topic` và `sub-topic` phải copy **chính xác** slug từ file đó. Mỗi file YAML tương ứng một `topic` (đặt tên file theo slug, ví dụ `personnel.yaml`).

---

## Quy tắc an toàn YAML

- Bọc **TẤT CẢ** giá trị chữ trong dấu ngoặc kép: `word`, `ipa`, `meaning`, mọi `en`/`vi`, mọi value trong `forms`, `note`. Chỉ riêng `level` không bọc.
- Nếu trong chuỗi có dấu ngoặc kép, escape nó hoặc dùng ngoặc đơn cho giá trị đó.
- Cẩn thận từ bị YAML tự hiểu sai kiểu (`no`, `yes`, `on`, `off` → true/false). Nhờ luôn bọc ngoặc kép cho value chữ nên rủi ro này được loại bỏ.

---

## Ví dụ định dạng

Làm đúng theo mẫu này. Ví dụ đầu có `sub-topic` với slug (chủ đề chính có chủ đề con); ví dụ sau vẫn giữ trường `sub-topic` nhưng để **null** (chủ đề chính không có chủ đề con).

```yaml
- word: "comply"
  pos: "verb"
  ipa: "/kəmˈplaɪ/"
  meaning: "tuân thủ, làm đúng quy định"
  topic: "general-business"
  sub-topic: "contracts-negotiation"
  lesson: "lession-01"
  level: 600
  forms:
    verb: "comply"
    noun: "compliance"
    adjective: "compliant"
  collocations:
    - en: "comply with regulations"
      vi: "tuân thủ các quy định"
    - en: "comply with a request"
      vi: "đáp ứng một yêu cầu"
  example:
    en: "All new employees must {comply} with the company's safety guidelines."
    vi: "Tất cả nhân viên mới phải tuân thủ các quy định an toàn của công ty."
  note: "Luôn đi với giới từ 'with': comply with sth. Đừng nhầm với 'apply'."

- word: "efficient"
  pos: "adjective"
  ipa: "/ɪˈfɪʃnt/"
  meaning: "hiệu quả, làm việc ít lãng phí thời gian và nguồn lực"
  topic: "manufacturing"
  sub-topic:
  level: 750
  forms:
    adjective: "efficient"
    noun: "efficiency"
    adverb: "efficiently"
  collocations:
    - en: "an efficient system"
      vi: "một hệ thống hiệu quả"
    - en: "work efficiently"
      vi: "làm việc một cách hiệu quả"
  example:
    en: "The new software helped the team work more {efficiently} than before."
    vi: "Phần mềm mới giúp cả nhóm làm việc hiệu quả hơn trước."
  note: "Phân biệt 'efficient' (làm việc ít lãng phí nguồn lực) với 'effective' (đạt được kết quả mong muốn)."
```

---

## Cách nhận đầu vào & xử lý

Người dùng cung cấp:
- Một **slug chủ đề** (`topic`), và nếu có, một **slug chủ đề con** (`sub-topic`) — copy từ bảng slug.
- Một **danh sách từ** hoặc một **bảng dán thẳng** từ tài liệu.

Cách xử lý:
1. **Ưu tiên dữ liệu người dùng đã có.** Nếu bảng đã có IPA, loại từ, nghĩa, hay collocation tiếng Anh → giữ lại, chỉ chuẩn hóa định dạng và bổ sung phần thiếu (`vi` cho collocation, `forms`, `example`, `level`, `note`).
2. **Điền `topic`/`sub-topic` giống nhau cho mọi entry trong batch** đúng theo slug người dùng đưa. Nếu chủ đề không có chủ đề con, vẫn giữ trường `sub-topic` nhưng để **null**.
3. Nếu người dùng **không đưa danh sách từ** mà chỉ đưa chủ đề, sinh khoảng 40–60 từ TOEIC hay gặp nhất cho (chủ đề / chủ đề con) đó, rồi áp dụng schema.
4. Nếu người dùng chưa nêu slug hoặc slug không khớp bảng, hỏi lại ngắn gọn slug chính xác trước khi sinh.

**Làm từng chủ đề con một, mỗi lần ~40–60 từ.** Chất lượng nghĩa/ví dụ đều tay hơn và khớp với việc tách file theo chủ đề. Nếu người dùng lỡ nhận đầu ra kèm dòng ```` ``` ````, nhắc họ xóa hai dòng đó trước khi lưu `.yaml`.

---

## Mẫu lệnh gọi (để người dùng điền)

```
Tạo file YAML từ vựng TOEIC cho:
- topic (slug): 【ví dụ: personnel】
- sub-topic (slug): 【ví dụ: salary-benefits — bỏ dòng này nếu chủ đề không có chủ đề con】
- Danh sách từ (mỗi từ một dòng, hoặc dán bảng):
【dán danh sách/bảng từ vào đây】
```