// Lưu trữ toàn cục trong localStorage, khoá "toeic:v2" — docs/plan.md §1.6.
// Mọi khoá định danh thẻ từ PHẢI là "<topic>:<word>" (Store.key), KHÔNG bao giờ
// dùng `word` đơn lẻ — 20 từ trùng tên ở nhiều topic sẽ đụng độ (§2.3 điểm 4).
// history/results chưa dùng ở M5 (đến M7/M8) nhưng khai báo sẵn shape ở đây để
// mọi script sau này đọc/ghi cùng một chỗ, không lệch nhau.
const KEY = "toeic:v2";

const DEFAULTS = {
  theme: null,
  masteredIds: [],
  favIds: [],
  readIds: [],
  srs: {},
  history: {},
  results: {},
};

function read() {
  try {
    return Object.assign({}, DEFAULTS, JSON.parse(localStorage.getItem(KEY)) || {});
  } catch (e) {
    return Object.assign({}, DEFAULTS);
  }
}

function write(data) {
  localStorage.setItem(KEY, JSON.stringify(data));
  document.dispatchEvent(new CustomEvent("store:change", { detail: data }));
}

export const Store = {
  key(topic, word) {
    return topic + ":" + word;
  },

  read,

  get(field) {
    return read()[field];
  },

  set(field, value) {
    const data = read();
    data[field] = value;
    write(data);
    return data;
  },

  has(field, item) {
    return (read()[field] || []).indexOf(item) !== -1;
  },

  // Bật/tắt 1 item trong danh sách (masteredIds, favIds, readIds…). Trả về
  // true nếu item VỪA được thêm (đang bật), false nếu vừa bị gỡ.
  toggle(field, item) {
    const data = read();
    const list = data[field] || [];
    const idx = list.indexOf(item);
    if (idx === -1) list.push(item);
    else list.splice(idx, 1);
    data[field] = list;
    write(data);
    return idx === -1;
  },

  // Thêm item vào danh sách nếu chưa có (idempotent) — dùng cho readIds khi mở
  // reader (M6): tự set, không phải toggle qua lại.
  add(field, item) {
    const data = read();
    const list = data[field] || [];
    if (list.indexOf(item) === -1) {
      list.push(item);
      data[field] = list;
      write(data);
    }
    return data;
  },
};
