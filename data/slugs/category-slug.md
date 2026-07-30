# Bảng slug chủ đề & chủ đề con

`topic` và `sub-topic` phải copy **chính xác** slug từ bảng này. Mỗi file YAML tương ứng một `topic` (đặt tên file theo slug, ví dụ `personnel.yaml`).

| # | Chủ đề (topic slug) | Chủ đề con (sub-topic slug) |
|---|---|---|
| 1 | `corporate-development` | *(không có)* |
| 2 | `dining-out` | *(không có)* |
| 3 | `entertainment` | *(không có)* |
| 4 | `finance-budgeting` | `banking` · `accounting-invoicing` · `investment` · `tax-budgeting` |
| 5 | `general-business` | `contracts-negotiation` · `mergers-restructuring` · `marketing-sales` · `warranty` · `business-planning` · `conferences` · `labor-relations` |
| 6 | `health` | *(không có)* |
| 7 | `housing-property` | `renting-buying` · `construction-specs` · `utilities-maintenance` |
| 8 | `manufacturing` | *(không có)* |
| 9 | `offices` | `meetings-committees` · `correspondence` · `equipment-furniture` · `work-procedures` |
| 10 | `personnel` | `recruitment-application` · `training-evaluation` · `salary-benefits` · `promotion-departure` |
| 11 | `purchasing` | `ordering` · `inventory-supplies` · `shipping` · `invoicing-payment` |
| 12 | `technical-areas` | *(không có)* |
| 13 | `travel` | `tickets-schedules` · `hotels` · `car-rental-commute` |

Ánh xạ chủ đề con sang tên gốc (để đối chiếu khi người dùng dán theo tài liệu):

- **finance-budgeting**: banking = Ngân hàng · accounting-invoicing = Kế toán & Hóa đơn · investment = Đầu tư · tax-budgeting = Thuế & Ngân sách
- **general-business**: contracts-negotiation = Hợp đồng & Đàm phán · mergers-restructuring = Sáp nhập & Cơ cấu công ty · marketing-sales = Marketing & Bán hàng · warranty = Bảo hành · business-planning = Lập kế hoạch kinh doanh · conferences = Hội nghị · labor-relations = Quan hệ lao động
- **housing-property**: renting-buying = Thuê & Mua · construction-specs = Xây dựng & Thông số kỹ thuật · utilities-maintenance = Điện – Gas – Bảo trì
- **offices**: meetings-committees = Họp & Ủy ban · correspondence = Thư từ & Liên lạc · equipment-furniture = Thiết bị & Nội thất · work-procedures = Quy trình làm việc
- **personnel**: recruitment-application = Tuyển dụng & Ứng tuyển · training-evaluation = Đào tạo & Đánh giá · salary-benefits = Lương & Phúc lợi · promotion-departure = Thăng chức, Khen thưởng & Nghỉ việc
- **purchasing**: ordering = Mua sắm & Đặt hàng · inventory-supplies = Kho & Vật tư · shipping = Vận chuyển · invoicing-payment = Hóa đơn & Thanh toán
- **travel**: tickets-schedules = Vé & Lịch trình · hotels = Khách sạn · car-rental-commute = Thuê xe & Đi lại hằng ngày
