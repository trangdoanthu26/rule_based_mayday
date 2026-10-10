# Kiểm tra logic bằng bệnh án giả định

**Ngày:** 10/10/2026. **Nguồn kiểm tra:** YAML `1.2.1`, engine hiện tại và [workflow](02_workflow.md). Chỉ kiểm tra tính nhất quán trong repo; không xác nhận tiêu chí y khoa từ nguồn bên ngoài. Không sửa source, schema hoặc điều kiện YAML trong đợt này.

## Dữ liệu và cách chạy

- [138 bệnh án giả định](../data/synthetic/rule_logic_cases.json): các bản ghi đầy đủ, cố định, không chứa tên/định danh bệnh nhân; dữ liệu suy diễn nằm trong `du_lieu`.
- [Test hồi quy](../tests/test_rule_logic_cases.py): chỉ truyền `du_lieu` vào engine; kiểm tra trạng thái, nhãn, rule được chọn, kết quả điều kiện, tính lặp lại và không sửa input.
- [Kết quả chạy và hash](../data/synthetic/rule_logic_results.json): kết quả từng ca, các rule khớp/chặn, trường thiếu, coverage TRUE/FALSE/UNKNOWN và replay RAW của 53 fixture cũ. Hash engine, YAML, fixture và phiên bản Python/PyYAML xác định đúng nội dung working tree đã kiểm tra; Git HEAD riêng lẻ không đủ.

```sh
.venv/bin/python -m unittest discover -s tests -v
```

`expected_engine` là kỳ vọng hành vi hiện tại được đối chiếu từ YAML/source; **không phải nhãn chuẩn lâm sàng**. `workflow_gap` liên kết vấn đề ở bảng dưới. Ba ca ghi `exception: TypeError` để lưu hành vi lỗi hiện tại. Hai test `expectedFailure` yêu cầu engine xử lý kiểu dữ liệu sai mà không crash/không phân loại sốc; chúng vẫn chưa đạt. Không sửa kỳ vọng thành kết quả bệnh mong muốn để làm báo cáo đẹp hơn.

Các giá trị âm/không trong ca đối chứng được khai báo chủ động để cô lập từng nhánh. Không dùng chúng làm giá trị mặc định khi một bệnh án thực sự thiếu trường. Đây là dữ liệu theo các path YAML cho kiểm tra lõi, chưa phải bệnh án RAW đã qua schema/mapping được duyệt.

## Kết quả thực thi

**33 test methods: 31 đạt, 2 lỗi đã biết được đánh dấu `expectedFailure`.** Các test theo fixture kiểm tra 138 ca bằng `subTest`; không có nghĩa là 138 test methods hay toàn bộ logic bệnh đúng.

| Kết quả trực tiếp trên 138 ca | Số ca |
| --- | ---: |
| CLASSIFIED | 94 |
| INSUFFICIENT_DATA | 18 |
| NEEDS_REVIEW | 6 |
| UNRESOLVED | 17 |
| ERROR — TypeError | 3 |

22/23 rule có ví dụ TRUE, FALSE và UNKNOWN. `R01-CAP-THUONG` chỉ có FALSE/UNKNOWN. Có **17/18 rule đích khớp TRUE**, và **11/12 nhãn bệnh xuất hiện ở đầu ra**; không tính hai nhãn theo dõi/chưa đủ dữ kiện là bệnh. Coverage này ở cấp rule, không phải coverage mọi tổ hợp hoặc mọi điều kiện lá. Các ca HATT boolean bị kết luận sốc vẫn nằm trong 94 ca CLASSIFIED để không che lỗi dữ liệu.

Các nhóm được thử: ba kịch bản phản vệ, đếm hệ cơ quan, tác nhân/đường hít; tuổi và HATT ngay trước/tại/sau ngưỡng; giảm 30% HA nền; từng dấu nặng cấp; mốc 1008 giờ/6 tuần; bốn thể CIndU, test khác và xung đột; bốn tổ hợp CSU GĐ1, GĐ2, Stella, 59/60/61 ngày, thiếu ELISA và sentinel/sai kiểu.

Replay riêng **53 fixture cũ**, truyền `du_lieu` nguyên trạng, không mapping: **34 INSUFFICIENT_DATA, 19 NEEDS_REVIEW, 0 CLASSIFIED**. Đây là kiểm tra tương thích RAW với lõi hiện tại, không phải đánh giá sau pipeline và không được thay accuracy lịch sử bằng một chỉ số accuracy mới từ lượt này. File phản vệ có 19 record dù tên ghi 20.

## Phát hiện và bằng chứng cần review

| ID | Bằng chứng / hành vi hiện tại | Ý nghĩa và việc cần chốt |
| --- | --- | --- |
| **F-12 — lỗi thực thi** | `SOC-MISSING-80`, `SOC-INVALID-LIST/OBJECT` gây TypeError; `SOC-INVALID-BOOL-TRUE/FALSE` trả sốc. Nhánh `<_formula` kiểm tra biến dùng tính ngưỡng nhưng không kiểm tra kiểu của HATT trước `actual < threshold`. | Sửa lỗi kỹ thuật bằng kiểm tra operand số hữu hạn, loại bool; giữ test lỗi trước khi sửa. Không cần thay ngưỡng bệnh để sửa lỗi này. |
| **F-01 — cấp thường không khả đạt với JSON** | `CAP-THUONG-OBJECT/STRING`: object làm phép bằng chuỗi UNKNOWN; scalar làm path `.danh_sach_chon` sai kiểu. Cấp thường vừa cần object để có sẩn phù, vừa cần loại hai so sánh scalar. | Chốt path riêng cho ngứa nhiều/phù mạch đáng kể và kiểu triệu chứng; sửa đồng bộ nhánh nặng/thường, schema, mapping và test. Không đổi object thành chuỗi để né lỗi. |
| **F-02 — khoảng tuổi bỏ trống** | `SOC-GAP-0.05/10.5/17.5`: HATT 80 và đủ phản vệ nhưng R-SOC FALSE; chọn phản vệ. | Workflow đã yêu cầu chốt khoảng liên tục/chính sách dưới một tháng. Engine chưa biết những khoảng này là vấn đề cần review. Không tự làm tròn tuổi. |
| **F-03 — đúng sáu tuần** | `CAP-6TUAN-1008` vào cấp; `CSU-WEEKS-6` và `CINDU-WEEKS-6` không vào mạn. | YAML dùng cấp `<=1008`, mạn `>6`; tiêu đề dùng cấp `<6`. Chốt dấu tại mốc và nguồn thời gian chung; đừng tự sửa thành hai ngưỡng khác nhau. |
| **F-04 — nghi ngờ/đã biết và thời điểm** | `PV-06` vào R03 chỉ từ tác nhân nghi ngờ + ngất. Không có điều kiện thời điểm khởi phát trong các rule phản vệ. | Workflow có đề cập nhưng chưa có path/mapping/điều kiện được duyệt. Thiếu dữ liệu mẫu không xác nhận được tiêu chí này. |
| **F-05 — phạm vi rule sốc** | `PV-07`: R01 TRUE, HATT 80 nhưng R-SOC FALSE vì chỉ tham chiếu R02/R03. | Đây là đúng YAML hiện tại. Cần quyết định chuyên môn có mở rộng phạm vi R-SOC không; chưa tự coi YAML là đáp án bệnh đúng. |
| **F-06 — CIndU khác/đa thể** | `CINDU-ICE-OTHER`: lạnh và khác cùng TRUE vì nhóm khác không loại Ice cube dương; trả NEEDS_REVIEW. `CINDU-ADRENERGIC`: test có trong schema nhưng YAML không đọc, trả UNRESOLVED. | Chốt loại trừ đầy đủ, ánh xạ Adrenergic và chính sách nhiều thể. Hành vi tie hiện tại không tự giải quyết đồng mắc. |
| **F-07 — enum/range chưa được validate** | `CINDU-NONENUM`: `abc != (+)` cho phép kết luận khác; `NEGATIVE-SBP`: -2 cho sốc; `CSU-ASST-(-)` và `CSU-ASST-(+/−)` trả UNRESOLVED. | Validator/preprocessor phải phân biệt enum sai, ký hiệu legacy được phép và kết quả chưa rõ. Engine không có miền enum nên không tự biến `(+/−)` thành UNKNOWN. |
| **F-08 — Stella khác workflow** | `CSU-STELLA-False-39.9` và `CSU-STELLA-None-39.9` vẫn vào GĐ2 từ IgE <40. Stella FALSE, IgE 40 trả UNRESOLVED; chưa có R-GD-03/OUT_OF_SCOPE. | Workflow yêu cầu đầy đủ Stella, còn YAML dùng `stella_dat OR IgE<40`. Chốt nguồn Stella, tách tuyển nghiên cứu khỏi chẩn đoán và sửa rule tương ứng sau khi duyệt. |
| **F-09 — sàng lọc xuyên biểu mẫu** | `CSU-NO-PV`: CSU có thể TRUE nhưng rule phản vệ UNKNOWN chặn kết luận; replay RAW cũ không có ca CLASSIFIED. | Chốt sàng lọc chung/applicability dựa trên dữ kiện; không điền tất cả `_pv` là Không khi thiếu. |
| **F-10 — cohort và đồng mắc** | `CSU-CINDU`: cả CSU/CIndU TRUE, chọn CIndU theo priority; R-CSU-00 chưa kiểm tra đầy đủ CSU đơn thuần/loại trừ như workflow. | Chốt kết luận chính/phụ và tiêu chí nghiên cứu. Trace có nhiều rule không thay hợp đồng đồng mắc. |
| **F-11 — fallback không có phạm vi** | `DEFAULT-NO-CSU`: ASST null vẫn khớp R-DEFAULT dù R-CSU-00 FALSE. `CSU-ASST-None`: R-DEFAULT TRUE nhưng UNKNOWN priority 7 chặn, matched_rule_id null. | Không dùng thiếu ASST làm fallback chung; ghi rõ cách định tuyến trạng thái. Ca thiếu ELISA và thiếu ASST không luôn chọn R-DEFAULT. |
| **F-13 — lý do UNKNOWN lan từ nhánh đã đủ** | `CAP-ANH-None`: thiếu ảnh nhưng trả NEEDS_REVIEW vì engine gom INVALID_TYPE từ các phép so sánh scalar/object trong dependency closure, dù dấu nặng riêng đã TRUE. | Phân biệt nguyên nhân thực sự làm rule UNKNOWN với trace UNKNOWN ở nhánh đã được OR giải quyết. Chốt trường cấp trước, rồi bổ sung hồi quy cho nguyên nhân chặn. |

`dau_hieu_nang_chi_tiet` có trong nhánh cấp nặng nhưng thiếu trong phủ định của cấp thường. `CAP-NANG-CHITIET` hiện chọn nặng nhờ priority; khi sửa F-01 phải dùng cùng một tập dấu nặng cho cả hai nhánh để tránh khớp nặng và thường đồng thời.

## Workflow đã đủ nội dung chưa?

**Đủ mô tả luồng tổng quát; chưa đủ làm hợp đồng triển khai đã chốt.** Workflow đã có RAW/CANONICAL, missing, ưu tiên/phụ thuộc, audit, bảo mật và khoảng 20 nhóm nghiệm thu. Bằng chứng mới ở đây không đóng B-01–B-06; chỉ làm rõ từng lệch bằng record chạy được.

| Nhóm nghiệm thu trong workflow | Phạm vi đã kiểm tra | Phần vẫn còn thiếu |
| --- | --- | --- |
| RB-01–RB-12 | Một số lỗi shape, sentinel, thời gian, số đo và thiếu `_pv` tại engine | Validator RAW/CANONICAL, mapping được duyệt, đơn vị, ngày/tuổi, quan hệ liên trường và vòng re-check |
| RB-13–RB-15 | Test lõi hiện có + ca sốc/ưu tiên/UNKNOWN mới | Ca nghiệm thu theo toàn pipeline sau khi thống nhất applicability |
| RB-16–RB-19 | Từng dấu nặng, CIndU, CSU, ranh giới và thiếu test | Các sai khác F-01–F-13, tiêu chí chuyên môn và những kết quả pipeline OUT_OF_SCOPE/INVALID_DATA |
| RB-20 | Input không bị sửa, kết quả lặp lại; dữ liệu mới không chứa định danh | Ghép batch/ID, chính sách export/anonymizer và audit preprocessing; chưa kiểm thử bảo mật bệnh án thật |

Để đủ triển khai, mỗi quyết định cần ghi **path + kiểu/enum/đơn vị + nguồn/mapping + luật áp dụng + ca trước/tại/sau ngưỡng + người xác nhận/phiên bản**. Có thể tiếp tục kiểm thử bằng bệnh án giả; không cần chờ bệnh án thật. Tuy nhiên, bệnh án do AI tạo theo YAML không tự chứng minh YAML đúng với chuyên môn.

## Thứ tự xử lý tiếp

1. Sửa F-12, có test failing sẵn; xử lý nguyên nhân UNKNOWN của F-13 bằng hồi quy phù hợp.
2. Chốt B-01/B-02/B-04: input, sàng lọc chung, shape triệu chứng; dùng F-01/F-07/F-09 làm ca nghiệm thu.
3. Chốt tuổi/sáu tuần, Stella/cohort và CIndU/đồng mắc (B-03/B-05/B-06), rồi sửa YAML có phiên bản và test theo kết quả đã duyệt.
4. Triển khai validate/preprocess → pipeline → evaluate; chạy lại bộ mới và 53 fixture sau mapping. Báo cả ca lỗi/chưa kết luận trong mẫu số; không dùng lượt replay RAW này làm bằng chứng accuracy.

B-07 về dữ liệu thật/export có thể để cho giai đoạn đó; bộ ca mới chỉ dùng dữ liệu giả không có PII. `validate.py`, `pipeline.py`, `evaluate.py` vẫn chưa triển khai trong tác vụ kiểm thử này.
