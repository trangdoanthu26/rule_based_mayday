# Rà soát workflow và mức sẵn sàng triển khai

> **Demo Streamlit — cập nhật 10/10/2026:** `main.py` minh họa 14 đầu ra hiện có (12 bệnh + 2 trạng thái theo dõi), sáu tầng và ba SVG Archify. Streamlit 1.50.0/PyYAML 6.0.3 đã cài trong `.venv` trước khi chạy test; sau cập nhật cảnh báo, bộ kiểm thử có 43 test methods, 41 đạt và 2 `expectedFailure` của engine. Xem [changelog/hướng dẫn demo](05_changelog.md) để đọc cảnh báo và tái hiện ca. Demo không đóng gate dữ liệu/chuyên môn hay triển khai pipeline RAW.

> **Bằng chứng kiểm thử bổ sung — 10/10/2026:** [138 ca giả định](06_rule_logic_review.md) cho 11 nhãn bệnh; cấp thường chưa khả đạt, lỗi kiểu HATT trong công thức còn mở. Hiện 33 test methods gồm 31 đạt và 2 `expectedFailure`, không phải bộ kiểm thử hoàn toàn đạt. Replay RAW 53 fixture cho 34 INSUFFICIENT_DATA/19 NEEDS_REVIEW; vẫn chưa đánh giá sau mapping/pipeline. Phát hiện này giới hạn nhận định “lõi đã hoàn thiện” bên dưới: lõi đã triển khai theo đợt đầu, còn lỗi kỹ thuật F-12/F-13 và các gate nghiệp vụ.

> **Cập nhật sau triển khai lõi — 10/10/2026:** `src/classify.py` đã thực hiện ba task của [plan lõi](superpowers/plans/2026-10-09-rule-engine-core.md). PyYAML `6.0.3` đã cài trong `.venv`; `python -m unittest discover -s tests -v` đạt **27 tests**; YAML là phiên bản `1.2.1`. Cập nhật này thay thế các ghi chú trạng thái “chưa triển khai” bên dưới; các gate B-01–B-07 vẫn mở.

**Bắt đầu:** 09/10/2026; **cập nhật:** 10/10/2026. **Nền code:** `34a1ad1`, working tree có các tài liệu mới và các file đã bị xóa từ trước. **Phạm vi người dùng đã chọn:** lõi kỹ thuật trước, pipeline sau.

AGENTS.md được bổ sung trong lúc rà soát với yêu cầu không dùng sub-agent hoặc cơ chế tương đương. Đã cập nhật plan sang thực thi trực tiếp và tự review; giữ nguyên file hướng dẫn do người dùng thay đổi.

Rà soát này kiểm tra [workflow](02_workflow.md) với [báo cáo khám phá](explore_codebase.md), [đặc tả luật](01_rules.md), source và hợp đồng schema. Diagram đã được người dùng mở và sử dụng thành công. Việc đó xác nhận diagram sử dụng được; chưa xác nhận các mapping hoặc tiêu chí chuyên môn đang còn mở.

## Kết luận sẵn sàng

| Phần | Trạng thái | Ý nghĩa |
| --- | --- | --- |
| Diagram và trình tự tổng quát | Đủ để dùng làm tài liệu làm việc | Không cần tiếp tục sửa DevTools để lập plan Python. |
| Nạp luật, phụ thuộc, logic ba trạng thái, chọn kết luận | Đã triển khai; còn lỗi kỹ thuật | 27 test đợt đầu đạt; bộ ca bổ sung phát hiện F-12/F-13. Chưa xác nhận đầy đủ tiêu chí y khoa. |
| Mapping, schema đầu vào và các điều kiện chuyên môn | Còn quyết định chặn | Chưa được tuyên bố pipeline đầy đủ sẵn sàng. |
| Code/test thực thi | Lõi đã triển khai | PyYAML nằm trong `.venv`; pipeline/schema adapter/evaluator vẫn chưa triển khai. |
| Sử dụng bệnh án thật / khẳng định kết quả nghiên cứu | Chưa đủ cơ sở | Lõi được sửa không tự làm các tiêu chí lâm sàng đúng hoặc tái lập accuracy 81,13%. |

## Những điểm phải xử lý trước pipeline

### 1. UNKNOWN ở nhóm không áp dụng có thể chặn mọi kết luận

- **Bối cảnh:** Workflow yêu cầu không hạ tầng nếu một luật ưu tiên cao UNKNOWN, nhưng chưa chốt cách xác định các luật thực sự áp dụng cho bản ghi.
- **Vấn đề cụ thể:** Một record CSU có ASST/ELISA nhưng thiếu toàn bộ trường `_pv` làm các luật phản vệ/sốc UNKNOWN. Engine mới có thể trả thiếu dữ kiện thay vì CSU; không được giải quyết bằng cách tự điền “Không” cho triệu chứng.
- **Hướng nhỏ nhất:** Chốt dữ kiện sàng lọc phản vệ chung cho các biểu mẫu và phép xác định phạm vi áp dụng dựa trên bằng chứng. Không dùng tên file/nhãn thật hoặc thiếu trường để suy ra FALSE. Lõi đợt đầu giữ UNKNOWN và nêu luật chặn.
- **Nếu bỏ qua:** Pipeline có thể giữ lại hầu hết ca mạn hoặc bỏ sót nguy cơ khi tự mặc định không có phản vệ. **Gate B-01.**

### 2. Full schema trước preprocessing sẽ loại fixtures và yêu cầu đáp án đầu vào

- **Bối cảnh:** `schema/cap_schema.json` bắt buộc `chan_doan_xac_dinh_cap`; các fixtures chủ ý để chẩn đoán trống và dùng nhiều kiểu legacy.
- **Vấn đề cụ thể:** Validator CANONICAL chạy ngay ở bước nhận record sẽ loại cả 10 ca cấp trước khi chuyển list/chuỗi; điền nhãn thật để qua schema làm rò đáp án.
- **Hướng nhỏ nhất:** Workflow đã được làm rõ: RAW kiểm tra envelope/cấu trúc có thể chuẩn hóa; CANONICAL kiểm tra sau mapping. Hợp đồng input suy diễn không yêu cầu chẩn đoán đích. Đợt lõi không xây validator hoặc tự sửa fixtures.
- **Nếu bỏ qua:** Không còn mẫu đánh giá hợp lệ, hoặc accuracy đo được từ dữ liệu đã lộ đáp án. **Gate B-02.**

### 3. Các quyết định y khoa còn mở không được coi là đã duyệt

- **Bối cảnh:** `docs/02_workflow.md`, mục 6 vẫn liệt kê các ranh giới và điều kiện chưa thống nhất với YAML.
- **Vấn đề cụ thể:** Tuổi 10,5 và 17,5 nằm ngoài các khoảng sốc hiện có; CSU có `stella_dat=False` nhưng IgE thấp vẫn qua nhánh Stella của YAML. Sửa thứ tự luật không sửa được các điều kiện này.
- **Hướng nhỏ nhất:** Ghi quyết định cần người phụ trách chốt trong bảng bên dưới. Đợt lõi không thay ngưỡng, gộp nhóm tuổi, bổ sung R-GD-03 hay sửa điều kiện tuyển nghiên cứu.
- **Nếu bỏ qua:** Cơ chế suy diễn hoạt động đúng với một bộ tri thức vẫn có thể cho kết luận sai. **Gates B-03 đến B-06.**

### 4. Dùng một trạng thái cho dữ liệu thiếu, cảnh báo và kết luận bệnh — trước khi sửa lõi

- **Bối cảnh:** Engine hiện trả `CLASSIFIED` cho bất kỳ `target_label` nào khớp, kể cả `R-DEFAULT` và `R-PV-THEODOI`; ca RB-09 dùng tên `REVIEW` không nằm trong bảng status.
- **Vấn đề cụ thể:** Input rỗng có thể được đếm là đã phân loại bệnh; hai nhãn cùng ưu tiên có thể được chọn theo vị trí YAML. Người đánh giá sẽ đếm sai số ca đã kết luận.
- **Hướng nhỏ nhất:** Lõi hiện dùng `target_status`, UNKNOWN có lý do và xử lý xung đột cùng ưu tiên; không thêm class kết quả hoặc bảng mapping theo nội dung nhãn.
- **Còn mở:** Bước đánh giá cần phân biệt kết luận bệnh với cohort và dữ liệu ngoài phạm vi; validator/cohort pipeline vẫn phải chốt.

## Sổ quyết định cho giai đoạn pipeline

Chưa có câu trả lời chuyên môn mới trong phiên này. Các đề xuất ở cột cuối là cách dừng an toàn, không phải tiêu chí đã được duyệt.

| Gate | Quyết định cần chốt và nguồn | Bằng chứng cần có để mở gate | Trong lúc chưa chốt |
| --- | --- | --- | --- |
| B-01 | Sàng lọc phản vệ xuyên biểu mẫu; dị nguyên nghi ngờ/đã biết; điều kiện thời điểm (`02_workflow.md`, mục 3/6) | Tên/path biến chung, mapping có nguồn, dữ kiện đủ để nói một nhánh không áp dụng | Giữ UNKNOWN và luật chặn; không mặc định “Không”. |
| B-02 | Hợp đồng RAW/CANONICAL, sentinel, đơn vị và biến dẫn xuất; tuổi/ngày khám/số ngày theo dõi | Bảng chuyển đổi nguồn → đích, cách bảo toàn missing/unknown/N/A và input schema không chứa đáp án | Không tự parse mô tả hoặc điền tuổi/HATT/ngày; bản ghi không theo hợp đồng chưa dùng đánh giá. |
| B-03 | Khoảng tuổi liên tục, dưới một tháng, đúng sáu tuần và yêu cầu ảnh (`01_rules.md:37,45`) | Quy tắc ranh giới không chồng/lọt khoảng và ví dụ trước/tại/sau mốc | Không tự sửa số trong YAML; chưa dùng rule hiện tại cho các ca biên đó. |
| B-04 | Biến “ngứa nhiều”/“phù mạch đáng kể” và cách loại dấu nặng | Tên/path/kiểu/enum có thể biểu diễn trong schema, cùng ca nặng/thường/thiếu dữ kiện | Không dùng chẩn đoán hay ghi chú để suy ra mức độ. |
| B-05 | CSU đơn thuần, điều kiện nghiên cứu, Stella, R-GD-03 và nguồn biến còn thiếu | Phân biệt chẩn đoán bệnh với tuyển cohort; đủ nguồn tính từng điều kiện, kết quả OUT_OF_SCOPE được thống nhất | Không suy Stella từ riêng IgE; không coi ngoài nghiên cứu là không mắc CSU. |
| B-06 | Adrenergic/test khác, nhiều thể CIndU, đồng mắc CSU/CIndU, tie-break chuyên môn | Bảng test → thể bệnh và chính sách kết luận chính/phụ, ca nhiều test dương | Cùng ưu tiên khác kết luận → NEEDS_REVIEW; không chọn theo thứ tự YAML. |
| B-07 | Bảo mật và audit cho đầu vào/bản xuất, đặc biệt bệnh án thật | Danh sách trường được phép xuất, quản lý token/định danh thiếu, trách nhiệm giữ bản gốc và khóa bí mật | Đợt đầu chỉ test giả; trace lõi không chứa giá trị record; không xuất dữ liệu thật. |

Không cần chốt toàn bộ 95 TODO mới viết được lõi. Cần chốt đúng các trường mà pipeline/luật thực sự đọc trước khi mở giai đoạn tương ứng. Sổ quyết định được cập nhật bằng nguồn và người xác nhận, không chỉ đánh dấu “đã xong” theo một lượt chạy.

## Điều chỉnh tài liệu trong lần rà soát

- Làm rõ hai thời điểm RAW/CANONICAL, status và hợp đồng lõi ở `docs/02_workflow.md`.
- Ghi nhận xác nhận sử dụng diagram của người dùng; giữ nguyên receipt kiểm tra tự động thất bại và artifact đã dùng.
- Viết và thực thi plan đợt lõi với `unittest`; thêm dependency PyYAML có pin phiên bản, test loader/three-valued logic/selection và cập nhật workflow/README.
- `explore_codebase.md` giữ nguyên như ảnh chụp khảo sát ban đầu; các mô tả “workflow trống”, “chưa có gitignore” thuộc thời điểm khảo sát, không dùng làm trạng thái hiện tại.

## Ponytail: phạm vi đủ nhỏ

Tái sử dụng `src/classify.py`, chỉ thêm `requirements.txt` và một file test. Không tạo rule framework, enum ba trạng thái, DTO, service, database, API, UI, mapping tự đoán hoặc dependency test mới. Không dùng Ruby/bộ nạp thay thế để làm test PyYAML “pass”.

Đợt đầu giữ nguyên các điều kiện, ngưỡng, nhãn và ID lâm sàng; chỉ loại lỗi Markdown ở YAML, bổ sung metadata trạng thái và tăng phiên bản cho thay đổi hành vi output. Pipeline, tiền xử lý, anonymizer và evaluator có plan sau khi các gate liên quan được chốt.

**Phán định hiện tại:** Lõi kỹ thuật đã triển khai, còn lỗi F-12/F-13 được tái hiện bằng test bổ sung; pipeline đầy đủ còn bị chặn bởi hợp đồng và tiêu chí B-01–B-06. B-07 áp dụng trước giai đoạn dùng bệnh án thật/export. Không kết luận “workflow không còn vướng mắc”.

**Chưa kiểm tra:** accuracy mới và 53 fixture sau mapping/pipeline, validator RAW/CANONICAL và bệnh án thật; không thẩm định tiêu chí y khoa bên ngoài. Đã replay trực tiếp 53 fixture RAW trong lượt bổ sung, không coi là đánh giá lâm sàng. Xác nhận diagram do người dùng cung cấp, không phải agent chạy lại browser-check.
