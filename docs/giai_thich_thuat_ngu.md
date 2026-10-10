# Giải thích thuật ngữ và phân nhóm bệnh án synthetic

## Specs và chuẩn bị môi trường trước khi chạy

**Bổ sung hướng dẫn:** 10/10/2026, 09:18:36 (UTC+07:00). **Người sửa đổi:** Đồng Minh Dương.

| Thành phần | Yêu cầu / trạng thái |
| --- | --- |
| Hệ điều hành | Hướng dẫn cho macOS/Linux (bash/zsh), Windows PowerShell và Windows CMD. Môi trường thực thi đã kiểm tra là macOS; chưa chạy trực tiếp trên Windows/Linux. |
| Python | Đã kiểm tra Python **3.9.6**. Streamlit 1.50.0 yêu cầu Python >=3.9, loại trừ 3.9.7 theo [metadata PyPI](https://pypi.org/project/streamlit/1.50.0/). Phiên bản khác cần cài dependency và chạy test để xác nhận tương thích. |
| Thư viện | `PyYAML==6.0.3`, `streamlit==1.50.0` trong [requirements.txt](../requirements.txt); pip tự cài phụ thuộc của chúng. |
| Thư mục chạy | Root `rule_based_mayday/`, nơi có `main.py`, `requirements.txt`, `src/`, `rules/`, `data/`, `docs/` và `tests/`. Mở terminal tại đây trước khi chạy lệnh. |
| Môi trường ảo | `.venv` riêng cho mỗi máy/OS; không copy `.venv` của người khác hoặc commit nó lên Git. |
| Dữ liệu/cấu hình | Giữ `rules/classification_rules.yaml`, `data/synthetic/rule_logic_cases.json` và `docs/diagrams/` cùng source. Không cần bệnh án thật. |
| Kết nối | Cần truy cập PyPI khi cài dependency. Demo chạy local, không cần API key hoặc dịch vụ AI để suy diễn. |
| Trình duyệt | Chrome/Edge/Firefox để mở `http://127.0.0.1:8501`; không cần extension ChatGPT hoặc cài Graphviz cho demo này. |

### macOS / Linux — bash hoặc zsh

Chạy lần đầu tại root repo, trước khi đã kích hoạt môi trường khác:

```sh
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -c "import sys; print(sys.executable); assert sys.prefix != sys.base_prefix"
python -m pip install -r requirements.txt
python -m pip check
python -m unittest discover -s tests -v
python -m streamlit run main.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

Nếu chọn một phiên bản Python cụ thể đã cài trên máy, dùng executable tương ứng ở bước tạo, ví dụ `python3.12 -m venv .venv`. Không tạo lại đè môi trường đang dùng bằng Python khác; cần một môi trường mới riêng cho phiên bản đó.

### Windows — PowerShell

Mở PowerShell tại root repo. Các lệnh sau dùng Python 3 được Python launcher `py` chọn:

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.executable); assert sys.prefix != sys.base_prefix"
python -m pip install -r requirements.txt
python -m pip check
python -m unittest discover -s tests -v
python -m streamlit run main.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

Nếu không có lệnh `py`, kiểm tra `python --version` rồi dùng `python -m venv .venv`. Nếu có nhiều phiên bản, có thể chọn rõ bằng `py -3.12 -m venv .venv` khi Python 3.12 đã cài. Dòng in `sys.executable` phải trỏ vào `.venv\Scripts\python.exe`, không phải Python toàn hệ thống.

Nếu PowerShell chặn `Activate.ps1`, chuyển sang CMD ở mục dưới hoặc gọi trực tiếp Python của `.venv`; không cần đổi execution policy:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m streamlit run main.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

### Windows — Command Prompt (CMD)

Mở CMD tại root repo; không dùng lệnh `source` của macOS/Linux:

```bat
py -3 --version
py -3 -m venv .venv
.venv\Scripts\activate.bat
python -c "import sys; print(sys.executable); assert sys.prefix != sys.base_prefix"
python -m pip install -r requirements.txt
python -m pip check
python -m unittest discover -s tests -v
python -m streamlit run main.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

### Mở lại demo và đọc kết quả kiểm tra

- Khi `.venv` đã có và dependency đã cài, lần mở terminal tiếp theo chỉ cần kích hoạt đúng theo shell, rồi chạy `python -m streamlit run main.py --server.address 127.0.0.1 --server.port 8501`. Không cần tạo lại `.venv` mỗi lần.
- Mở URL Streamlit in ra; dừng server bằng **Ctrl+C**, sau đó gõ `deactivate` để thoát môi trường đã kích hoạt. Nếu cổng 8501 đang có server khác, chọn `--server.port 8502` và mở URL tương ứng.
- Lệnh cài đúng là **`python -m pip install -r requirements.txt`**, không phải `pip install -m requirements.txt`. Nếu thiếu module, kiểm tra executable và cài lại trong đúng `.venv`.
- Bản đã kiểm tra gần nhất có **43 test methods: 41 đạt, 2 expectedFailure** của F-12 còn mở; `OK (expected failures=2)` không có nghĩa engine hết lỗi. Số test có thể đổi khi cộng tác viên thêm/sửa code.

Các lệnh tạo/kích hoạt và cách gọi trực tiếp Python trong môi trường dựa trên [tài liệu Python venv](https://docs.python.org/3/library/venv.html). Hướng dẫn dưới đây giải thích dữ liệu, kết quả và cách check logic sau khi demo đã mở.

---

**Ngày ghi nhận:** 10/10/2026, 06:47:31 (UTC+07:00). **Người ghi:** Đồng Minh Dương.

**Nguồn:** [main.py](../main.py), [bộ luật](../rules/classification_rules.yaml) và dữ liệu trong `data/synthetic/`. Số liệu dưới đây được chạy lại trực tiếp bằng `ClinicalRuleEngine` trong `.venv`, chỉ truyền `du_lieu`, không dùng nhãn/kỳ vọng làm dữ kiện. YAML phiên bản **1.2.1**; SHA-256: `aff477a8d5e698ed8c03559272c67a9f1e747fe77f693148e469257624dd9ff6`.

## 1. ISSUE_HELP là gì?

`ISSUE_HELP` là dictionary **mã vấn đề → câu giải thích** dùng cho giao diện. Ví dụ `ISSUE_HELP["F-12"]` cung cấp nội dung cảnh báo về lỗi công thức HATT (huyết áp tâm thu).

Các mã F-01–F-13 là ID của phát hiện trong [báo cáo kiểm tra logic](06_rule_logic_review.md). Chúng không phải mã bệnh, rule ID hoặc trạng thái bệnh án. Dictionary này không được dùng để suy diễn, đổi ngưỡng, chọn nhãn, validate hoặc sửa dữ liệu.

Trong demo, trường `workflow_gap` của **ca gốc** trỏ đến một ID để hiện lời giải thích; F-01/F-12 còn được hiển thị nổi bật ở đầu trang. Đây là chú thích đã ghi cho ca, không phải bộ phát hiện lỗi tự động đầy đủ. Sửa JSON có thể tạo lỗi khác mà chú thích ca gốc không bao quát. Riêng cảnh báo HATT boolean kiểm tra giá trị hiện tại ở UI, nhưng vẫn không sửa kết quả engine.

| Mã | Nội dung ISSUE_HELP hiện tại |
| --- | --- |
| F-01 | Cấp thông thường chưa khả đạt: cùng biến triệu chứng đang được yêu cầu vừa là object vừa là chuỗi. |
| F-02 | Tuổi dưới một tháng, 10,5 và 17,5 chưa được các khoảng sốc hiện tại bao phủ; không tự làm tròn tuổi. |
| F-03 | Đúng 6 tuần: cấp dùng <=1008 giờ, mạn dùng >6 tuần; ranh giới và nguồn thời gian cần chốt. |
| F-04 | R03 dùng tác nhân nghi ngờ thay tiêu chí dị nguyên đã biết; các rule phản vệ chưa kiểm tra thời điểm. |
| F-05 | Sốc chỉ tham chiếu R02/R03; ca chỉ đạt R01 dù HATT thấp vẫn không vào rule sốc hiện tại. |
| F-06 | CIndU khác chưa loại Ice cube dương; Adrenergic chưa có nhánh; nhiều test dương cần chính sách phân thể. |
| F-07 | Chưa có validator enum/range: giá trị test sai có thể được coi là không dương; HATT âm vẫn có thể thỏa rule. |
| F-08 | Stella FALSE/UNKNOWN vẫn có thể vào CSU GĐ2 vì IgE <40; YAML khác workflow, chưa có nhánh loại cohort. |
| F-09 | Thiếu sàng lọc phản vệ chung có thể chặn CSU dù xét nghiệm đầy đủ; không tự điền Không vào trường thiếu. |
| F-10 | CIndU được chọn trước CSU khi cùng khớp; điều kiện cohort và biểu diễn đồng mắc chưa chốt. |
| F-11 | ASST null có thể kích hoạt fallback ngoài CSU; rule UNKNOWN ưu tiên cao vẫn có thể chặn fallback. |
| F-12 | Công thức HATT thiếu kiểm tra kiểu: chuỗi/list/object có thể crash; boolean có thể bị kết luận sốc sai. |
| F-13 | Lý do UNKNOWN có thể bị lẫn với lỗi kiểu từ nhánh OR đã đủ bằng chứng, làm sai lý do cần rà soát. |

## 2. STATUS_HELP là gì?

`STATUS_HELP` là dictionary **trạng thái đầu ra → câu giải thích**. Engine xác định `result["status"]`; UI tra dictionary này để giải thích kết quả. Dictionary không tự phân loại bệnh án. Các ca được sinh có `expected_engine` để kiểm tra hành vi dự kiến; thống kê bên dưới dùng **kết quả engine chạy lại**, không chỉ đếm metadata đó.

| Trạng thái | Câu hiển thị hiện tại | Cách hiểu khi check logic |
| --- | --- | --- |
| `CLASSIFIED` | Có nhãn theo YAML hiện tại. | Có nhãn theo YAML; chưa chứng minh nhãn đúng về chuyên môn hoặc input đã được validator kiểm tra. F-12 có thể khiến dữ liệu bool vẫn có nhãn sốc. |
| `INSUFFICIENT_DATA` | Thiếu dữ kiện hoặc chưa đủ thời gian; xem rule chặn và trường cần bổ sung. | Chưa kết luận bệnh. Có thể thiếu dữ kiện, hoặc dữ kiện đã biết nhưng chưa đủ thời gian; missing_fields không nhất thiết có phần tử. |
| `NEEDS_REVIEW` | Chưa có kết luận bệnh: có xung đột hoặc dữ liệu cần rà soát; xem điều kiện và trace của các rule chặn. | Chưa kết luận bệnh; có thể do sai kiểu hoặc nhiều rule khác nhãn cùng ưu tiên. Không tự chọn một nhãn để bỏ cảnh báo. |
| `UNRESOLVED` | Không có rule đích phù hợp sau đánh giá hiện tại. | Không có rule đích phù hợp trong lần đánh giá hiện tại; không đồng nghĩa không mắc bệnh hay dữ liệu đã hợp lệ. |

Phân biệt ba loại tên:

- **TRUE/FALSE/UNKNOWN:** kết quả một điều kiện/rule; UNKNOWN là chưa đánh giá được, không phải FALSE.
- **CLASSIFIED/INSUFFICIENT_DATA/NEEDS_REVIEW/UNRESOLVED:** trạng thái xử lý toàn bệnh án.
- **Phản vệ, CSU type 1, CSU unknown…:** nhãn bệnh/endotype. `CSU unknown` là nhãn từ tổ hợp xét nghiệm đủ bằng chứng, khác UNKNOWN do thiếu test.

Danh mục có **14 nhãn đích = 12 nhãn bệnh + 2 nhãn theo dõi**, không phải 14 trạng thái hoặc 14 bệnh. Hai nhãn theo dõi dùng `INSUFFICIENT_DATA`; `predicted_label` vẫn null khi chưa kết luận bệnh, dù rule theo dõi đã khớp. `INVALID_DATA`/`OUT_OF_SCOPE` thuộc pipeline chưa triển khai, không nằm trong bốn nhóm đầu ra trực tiếp đang thống kê.

## 3. Thống kê bộ 138 ca sinh mới

Nguồn: [rule_logic_cases.json](../data/synthetic/rule_logic_cases.json). Đây là bộ ca được dùng trong Streamlit. **135 ca trả về một trong bốn trạng thái; 3 ca phát sinh exception.** Giữ cả ba ca lỗi trong tổng số 138, không loại khỏi mẫu số.

| Nhóm | Số ca | Một mã bệnh án minh họa | Kết quả thực tế |
| --- | ---: | --- | --- |
| `CLASSIFIED` | 94 | `PV-01` | Nhãn: Phản vệ; rule: `R02-PV`; priority 2. |
| `INSUFFICIENT_DATA` | 18 | `CSU-DAYS-59` | Nhãn: null; rule: `R-DEFAULT`; priority 8. |
| `NEEDS_REVIEW` | 6 | `CINDU-TIE` | Nhãn: null; rule: `null`; priority 6. |
| `UNRESOLVED` | 17 | `PV-03` | Nhãn: null; rule: `null`; priority 99. |
| Exception — TypeError | 3 | `SOC-MISSING-80`, `SOC-INVALID-LIST`, `SOC-INVALID-OBJECT` | Engine không trả kết quả; không tự gán vào một STATUS_HELP. UI bắt lỗi thực thi. |

### Giải thích bốn bệnh án đại diện

**1. `PV-01` → CLASSIFIED.** Ca có tác nhân thức ăn nghi ngờ, da có sẩn phù và hô hấp có khó thở; HATT thấp nhất/nền đều 120, tuổi 30. R02 đạt hai hệ cơ quan; R03 cũng TRUE vì tác nhân không qua đường hít và có hô hấp. R-SOC FALSE. Hai rule phản vệ có cùng nhãn/priority 2 nên không xung đột; engine chọn R02 làm đại diện theo ID. Nhãn chính là Phản vệ.

**2. `CSU-DAYS-59` → INSUFFICIENT_DATA.** Ca vào CSU GĐ1, ASST dương nhưng `so_ngay_theo_doi = 59`, trong khi các rule endotype GĐ1 yêu cầu >=60. R-DEFAULT TRUE do chưa đủ thời gian, được chọn ở priority 8. `predicted_label = null`; `missing_fields = []` vì số ngày đã có, chỉ chưa đạt mốc. Đây không phải CSU unknown và không phải lỗi thiếu một key JSON.

**3. `CINDU-TIE` → NEEDS_REVIEW.** Ca mạn có kích thích, cả da vẽ nổi và cholinergic dương. R-CindU-01 và R-CindU-02 đều TRUE, cùng priority 6 nhưng khác nhãn. Engine giữ cả hai trong `matched_rule_ids`/`blocking_rule_ids`, không chọn rule đại diện; nhãn và `matched_rule_id` đều null. Chính sách đa thể cần được chốt.

**4. `PV-03` → UNRESOLVED.** Tác nhân nghi ngờ và da dương đơn lẻ, không có hô hấp/tuần hoàn/tiêu hóa nặng đủ để đạt các rule phản vệ; các dữ kiện còn lại không vào nhánh cấp, CIndU, CSU hoặc theo dõi. Mọi rule đích FALSE nên engine trả priority 99, không có nhãn/rule/chặn. Không được diễn giải thành kết luận bệnh nhân khỏe mạnh.

### Danh sách mã đầy đủ theo trạng thái

Các ID dưới đây thuộc riêng bộ 138 ca mới. Nhóm CLASSIFIED vẫn chứa ca cố ý sai dữ liệu như HATT bool; đây là **hành vi hiện tại**, không phải danh sách bệnh án đã được chuyên môn xác nhận.

#### CLASSIFIED — 94 ca

- `PV-01`, `PV-02`, `PV-NON-2`, `PV-05`, `PV-HIT-KHONG`, `PV-06`
- `PV-07`, `PV-09`, `PV-10`, `PV-TACNHAN-thuc_an`, `PV-TACNHAN-thuoc`, `PV-TACNHAN-con_trung_dot`
- `PV-TACNHAN-khac`, `SOC-0.083--0.1`, `SOC-0.083-0`, `SOC-0.083-0.1`, `SOC-0.99--0.1`, `SOC-0.99-0`
- `SOC-0.99-0.1`, `SOC-1--0.1`, `SOC-1-0`, `SOC-1-0.1`, `SOC-5--0.1`, `SOC-5-0`
- `SOC-5-0.1`, `SOC-10--0.1`, `SOC-10-0`, `SOC-10-0.1`, `SOC-11--0.1`, `SOC-11-0`
- `SOC-11-0.1`, `SOC-17--0.1`, `SOC-17-0`, `SOC-17-0.1`, `SOC-18--0.1`, `SOC-18-0`
- `SOC-18-0.1`, `SOC-GAP-0.05`, `SOC-GAP-10.5`, `SOC-GAP-17.5`, `SOC-NEN-139.9`, `SOC-NEN-140`
- `SOC-NEN-140.1`, `SOC-NEN-NOTNEEDED`, `CAP-NANG-PHUMACH`, `CAP-NANG-NGUA`, `CAP-NANG-CANVIEN`, `CAP-NANG-CHITIET`
- `CAP-NANG-BSA`, `CAP-NANG-NOT`, `CAP-NANG-NON`, `CAP-NANG-DAUBUNG`, `CAP-NANG-BUONNON`, `CAP-NANG-VITRI-Mi mắt`
- `CAP-NANG-VITRI-Lưỡi`, `CAP-NANG-VITRI-Thanh quản`, `CAP-NANG-VITRI-Môi`, `CAP-NANG-HOHAP-Thở khò khè`, `CAP-NANG-HOHAP-Nghẹn họng`, `CAP-6TUAN-1007.9`
- `CAP-6TUAN-1008`, `SOC-PRIORITY`, `CINDU-da_ve_noi`, `CINDU-cholinergic`, `CINDU-lanh_temptest`, `CINDU-lanh_cucda`
- `CINDU-ap_luc_cham`, `CINDU-anh_sang`, `CINDU-nuoc`, `CINDU-khac`, `CINDU-NONENUM`, `CSU-T1-GD1`
- `CSU-T2-FC`, `CSU-T2-IGE`, `CSU-OVL-FC`, `CSU-OVL-IGE`, `CSU-UNK-GD1`, `CSU-OVL-ONE-MISSING`
- `CSU-DAYS-60`, `CSU-DAYS-61`, `CSU-BOUND-tuoi-16`, `CSU-BOUND-thoi_gian_ngung_khang_histamine_asst-8`, `CSU-BOUND-thoi_gian_ngung_corticoid_asst-30`, `CSU-WEEKS-6.01`
- `CSU-GD2-(+)`, `CSU-GD2-(−)`, `CSU-STELLA-False-39.9`, `CSU-STELLA-None-39.9`, `CSU-STELLA-True-None`, `CSU-CINDU`
- `NEGATIVE-SBP`, `SOC-INVALID-BOOL-TRUE`, `SOC-INVALID-BOOL-FALSE`, `CINDU-WEEKS-6.01`

#### INSUFFICIENT_DATA — 18 ca

- `PV-08`, `SOC-MISSING-None`, `SOC-MISSING--1`, `SOC-MISSING-unknown`, `SOC-NEN-MISSING`, `CINDU-OTHER-MISSING`
- `CSU-DAYS-59`, `CSU-DAYS-None`, `CSU-MISSING-igg_khang_fceria_ket_qua`, `CSU-MISSING-igg_khang_ige_ket_qua`, `CSU-MISSING-ige_khang_il24_ket_qua`, `CSU-GD2-None`
- `CSU-STELLA-None-40`, `CSU-STELLA-False--1`, `CSU-ASST-None`, `CSU-NO-PV`, `EMPTY`, `DEFAULT-NO-CSU`

#### NEEDS_REVIEW — 6 ca

- `CAP-THUONG-OBJECT`, `CAP-THUONG-STRING`, `CAP-ANH-None`, `CAP-ARRAY`, `CINDU-TIE`, `CINDU-ICE-OTHER`

#### UNRESOLVED — 17 ca

- `PV-03`, `PV-04`, `PV-NON-1`, `PV-HIT-CO`, `CAP-6TUAN-1008.1`, `CAP-ANH-Không`
- `CSU-BOUND-tuoi-15.9`, `CSU-BOUND-thoi_gian_ngung_khang_histamine_asst-7.9`, `CSU-BOUND-thoi_gian_ngung_corticoid_asst-29.9`, `CSU-WEEKS-5.99`, `CSU-WEEKS-6`, `CSU-STELLA-False-40`
- `CSU-ASST-(+/−)`, `CSU-ASST-(-)`, `CINDU-WEEKS-5.99`, `CINDU-WEEKS-6`, `CINDU-ADRENERGIC`

## 4. Đối chiếu 53 bệnh án synthetic cũ

Bốn file legacy dưới đây khác bộ 138 ca mới. Chạy `du_lieu` nguyên trạng, **chưa mapping/preprocessing**, cho 34 INSUFFICIENT_DATA và 19 NEEDS_REVIEW; không có CLASSIFIED/UNRESOLVED. Đây là kiểm tra tương thích với lõi, không phải accuracy sau pipeline. Không cộng file `rule_logic_results.json` như một tập bệnh án: đó là kết quả/audit, không phải input mới.

| File nguồn | Số ca | CLASSIFIED | INSUFFICIENT_DATA | NEEDS_REVIEW | UNRESOLVED |
| --- | ---: | ---: | ---: | ---: | ---: |
| [10_benh_an_cap_thuong_va_cap_nang.json](../data/synthetic/10_benh_an_cap_thuong_va_cap_nang.json) | 10 | 0 | 10 | 0 | 0 |
| [12_benh_an_CSU.json](../data/synthetic/12_benh_an_CSU.json) | 12 | 0 | 12 | 0 | 0 |
| [12_benh_an_CindU.json](../data/synthetic/12_benh_an_CindU.json) | 12 | 0 | 12 | 0 | 0 |
| [20_benh_an_phan_ve_soc_phan_ve.json](../data/synthetic/20_benh_an_phan_ve_soc_phan_ve.json) | 19 | 0 | 0 | 19 | 0 |

File phản vệ mang tên “20” nhưng thực tế có 19 record. ID legacy có thể trùng giữa các file; dùng **file nguồn + ID** để nhận diện, không chỉ ID.

**10_benh_an_cap_thuong_va_cap_nang.json:**

- `INSUFFICIENT_DATA`: `BA_7642`, `BA_8319`, `BA_5129`, `BA_8303`, `BA_9273`, `BA_8180`, `BA_8086`, `BA_3755`, `BA_7632`, `BA_8435`.

**12_benh_an_CSU.json:**

- `INSUFFICIENT_DATA`: `BA_2951`, `BA_9385`, `BA_4658`, `BA_7891`, `BA_9042`, `BA_4931`, `BA_2322`, `BA_2606`, `BA_9032`, `BA_6148`, `BA_5120`, `BA_7166`.

**12_benh_an_CindU.json:**

- `INSUFFICIENT_DATA`: `BA_5842`, `BA_8347`, `BA_3756`, `BA_3899`, `BA_8367`, `BA_8314`, `BA_5289`, `BA_7632`, `BA_7612`, `BA_7811`, `BA_8312`, `BA_3921`.

**20_benh_an_phan_ve_soc_phan_ve.json:**

- `NEEDS_REVIEW`: `BA_4190`, `BA_2452`, `BA_9983`, `BA_4413`, `BA_3511`, `BA_7997`, `BA_5806`, `BA_5587`, `BA_2323`, `BA_5952`, `BA_9371`, `BA_2814`, `BA_8625`, `BA_6486`, `BA_6608`, `BA_7353`, `BA_8367`, `BA_9281`, `BA_2355`.

## 5. LAYERS là gì và sáu tầng hoạt động thế nào?

`LAYERS` trong `main.py` là tuple chứa **tên tầng + danh sách rule ID**, dùng để nhóm và hiển thị giao diện. Nó không tạo sáu engine riêng, không tính lại điều kiện và không quyết định nhãn. Toàn hệ thống đang dùng một `ClinicalRuleEngine` đọc YAML.

| Tầng | Rule trong giao diện | Vai trò |
| --- | --- | --- |
| T1 · Sốc phản vệ | `R-SOC` | Kết luận ưu tiên 1 nếu R02 hoặc R03 phản vệ TRUE và tụt HATT theo tuổi/nền. R-SOC phụ thuộc rule ở T2: vị trí T1 trên UI không có nghĩa nó tính trước các phụ thuộc. |
| T2 · Phản vệ và theo dõi | `R01-PV`, `R02-PV`, `R03-PV`, `R-PV-THEODOI` | Ba kịch bản phản vệ ưu tiên 2; theo dõi ưu tiên 3. Rule cảnh báo trả INSUFFICIENT_DATA, không phải một bệnh mới. |
| T3 · Mày đay cấp | `R-SANGLOC-CAP`, `R01-CAP-NANG`, `R01-CAP-THUONG` | R-SANGLOC-CAP là điều kiện cơ sở; nặng ưu tiên 4, thường ưu tiên 5. Xét dấu nặng trước, thường cần đủ bằng chứng loại nặng. F-01 hiện chặn nhánh thường. |
| T4 · Mày đay cảm ứng mạn tính — CIndU | `R-CindU-00`, `R-CindU-01`, `R-CindU-02`, `R-CindU-03`, `R-CindU-04` | Sàng lọc mạn >6 tuần/có kích thích, rồi test phân thể; các rule đích ưu tiên 6. Hai thể khác nhãn cùng TRUE cần review. |
| T5 · Mày đay tự phát mạn tính — CSU | `R-CSU-00`, `R-GD-01`, `R-GD-02`, `R-CSU-T1-01`, `R-CSU-T1-02`, `R-CSU-T2-01`, `R-CSU-OVL-01`, `R-CSU-UNK-01`, `R-CSU-UNK-02` | R-CSU-00 → R-GD-01/02 → type 1/type 2/overlap/unknown, ưu tiên 7. GĐ1 có mốc >=60 ngày; GĐ2 theo Stella/IgE hiện tại trong YAML, còn lệch F-08. |
| T6 · Chưa đủ dữ kiện / ngoại lệ | `R-DEFAULT` | R-DEFAULT ưu tiên 8 cho ASST null hoặc GĐ1 chưa đủ thời gian. Không phải bộ xử lý tất cả lỗi; trạng thái thiếu/review có thể phát sinh ở bất kỳ tầng nào. |

### Hai pha của engine

#### Pha 1 — tính kết quả từng rule, chưa chọn nhãn bệnh

Mỗi rule trả TRUE, FALSE hoặc UNKNOWN từ dữ kiện bệnh án. Một rule có thể dùng kết quả của rule khác qua `ref_rule`; đó là **phụ thuộc**. Rule cơ sở như R-CSU-00 kiểm tra điều kiện vào nhóm, không tự trả nhãn bệnh.

Ví dụ `R-SOC` cần biết `R02-PV` hoặc `R03-PV` có đạt tiêu chí phản vệ không, rồi mới kết hợp với điều kiện tụt huyết áp:

1. Khi đang tính R-SOC mà một rule tham chiếu chưa có kết quả, engine tính rule tham chiếu đó trước. Nếu rule ấy lại tham chiếu rule khác, engine tiếp tục giải quyết phụ thuộc trước khi dùng kết quả.
2. Kết quả được lưu trong **cache**, tức bảng nhớ tạm cho lần phân loại. Ví dụ bảng có `R02-PV: TRUE`, `R03-PV: FALSE`.
3. R-SOC lấy hai kết quả đó để xét điều kiện phản vệ, kết hợp điều kiện huyết áp và trả kết quả của chính nó. Nếu một rule khác cũng cần R02-PV, engine lấy TRUE đã lưu, không tính lại R02-PV trong lần chạy đó.
4. Engine tính cả các rule còn lại ở nhánh cấp, CIndU, CSU và theo dõi. Nó không dừng ngay khi thấy một rule TRUE; các tầng thấp vẫn có kết quả để đưa vào trace.

**Cache được tạo mới mỗi lần gọi phân loại**, không dùng chung giữa bệnh án A và B. Sửa JSON rồi bấm phân loại lại cũng bắt đầu với cache mới. Cache lưu cả UNKNOWN và không tự đổi UNKNOWN thành FALSE. Cache này khác kết quả được Streamlit giữ trong màn hình sau lần chạy trước.

Ví dụ giả định: nếu R02-PV TRUE và điều kiện tụt huyết áp của R-SOC TRUE thì R-SOC TRUE. Nếu R02-PV TRUE nhưng điều kiện tụt huyết áp FALSE thì R-SOC FALSE; thỏa phản vệ không tự chứng minh thỏa sốc.

#### Pha 2 — dùng các kết quả đã tính để chọn kết luận

Sau khi có kết quả toàn bộ rule, engine xét rule đích theo priority nhỏ nhất còn có khả năng ảnh hưởng kết luận. Nếu cả sốc (priority 1) và phản vệ (priority 2) TRUE, chọn sốc làm nhãn chính; các rule phản vệ cùng khớp vẫn được ghi lại.

- TRUE ở tầng thấp không vượt qua UNKNOWN ưu tiên cao nếu UNKNOWN đó có thể đổi kết luận.
- Các rule khác nhãn cùng ưu tiên TRUE → NEEDS_REVIEW; cùng nhãn/trạng thái có thể dùng một rule đại diện.
- Mọi rule đích FALSE → UNRESOLVED; không cần R-DEFAULT TRUE.

**Thứ tự tính phụ thuộc khác thứ tự chọn nhãn.** R-SOC nằm ở T1 trên giao diện nhưng cần kết quả các rule phản vệ ở T2. Tầng T1–T6 không phải lịch chạy lần lượt để chọn ngay nhãn đầu tiên khớp.

Vì vậy, **tầng là cách tổ chức nghiệp vụ/hiển thị; status là kết quả xử lý; ISSUE_HELP là lời chú thích lỗi**. Ví dụ CINDU-TIE dừng cần review ở T4; CSU-DAYS-59 được rule T6 theo dõi; PV-03 không có rule đích nào được chọn.

## 6. Cách kiểm tra lại trên demo

1. Mở Streamlit và chọn **Tất cả** ở sidebar để tìm cả bốn mã `PV-01`, `CSU-DAYS-59`, `CINDU-TIE`, `PV-03`.
2. Chọn lần lượt từng ca, bấm **Phân loại và giải thích**; đối chiếu bảng trạng thái ở mục 3.
3. Mở **Sáu tầng suy diễn**, xem rule cơ sở/tham chiếu và trace của rule khớp/chặn. `matched_rule_ids` là các rule đích TRUE, không phải tất cả đều là nhãn chính.
4. Nếu sửa JSON, kỳ vọng ca gốc không tự cập nhật; sửa một biến mỗi lần và ghi kỳ vọng cho biến thể trước khi chạy lại. Chọn ca mới sẽ nạp lại JSON và xóa kết quả cũ.

Lần chạy đầu, dùng đầy đủ các lệnh tạo `.venv`, cài dependency và chạy test ở phần **Specs và chuẩn bị môi trường trước khi chạy** đầu tài liệu; chọn đúng macOS/Linux, PowerShell hoặc CMD.

Số liệu là ảnh chụp của engine/YAML tại ngày ghi nhận; cần chạy lại khi code/rule đổi. Không sửa `main.py`, engine hoặc các fixture trong tác vụ viết tài liệu này; chưa thực hiện mapping legacy, xác nhận chuyên môn hay kiểm tra bệnh án thật.
