# Hệ thống Rule-Based hỗ trợ phân loại bệnh án mày đay và phản vệ

Ứng dụng Python/Streamlit minh họa cách áp dụng bộ quy tắc YAML để suy luận trên dữ liệu bệnh án dạng JSON. Dự án có ba phân hệ độc lập:

- **Phản vệ và sốc phản vệ**
- **Mày đay cấp**
- **Mày đay mạn tính** (CIndU và CSU)

Người dùng có thể chọn ca giả định, tải hồ sơ JSON/CSV, xem các quy tắc được đánh giá và đọc giải thích kết quả. Đây là dự án thử nghiệm/phục vụ phát triển, **không phải thiết bị y tế hay công cụ chẩn đoán đã được thẩm định**.

## Yêu cầu

- Python 3.9.6 trở lên
- pip

Các thư viện trực tiếp được khai báo trong `requirements.txt`: Streamlit 1.50.0 và PyYAML 6.0.3.

## Cài đặt và chạy trên Windows

Từ thư mục gốc của repository, tạo môi trường ảo và cài dependencies:

```powershell
py -m venv mayday_rb
.\mayday_rb\Scripts\python.exe -m pip install --upgrade pip
.\mayday_rb\Scripts\python.exe -m pip install -r requirements.txt
```

Khởi chạy ứng dụng:

```powershell
.\mayday_rb\Scripts\python.exe -m streamlit run main.py
```

Mở URL được Streamlit in ra trong terminal (thường là `http://localhost:8501`). Có thể dừng ứng dụng bằng `Ctrl+C`.

## Sử dụng demo

1. Chọn phân hệ bệnh án ở đầu trang.
2. Ở thanh bên, chọn ca giả định mẫu, tải hồ sơ `.json`/`.csv` hoặc chọn **Nhập theo mẫu engine** và điền tại tab **Nhập bệnh án**.
3. Kiểm tra dữ liệu hiển thị; có thể bật phần đối chiếu JSON và chỉnh sửa dữ liệu để thử các trường hợp biên.
4. Chọn **Phân loại và giải thích**.
5. Đọc trạng thái, kết luận (nếu có), các trường còn thiếu, quy tắc khớp/chặn và tab **Logic suy luận**.

Demo chỉ chạy bộ luật tương ứng với phân hệ được chọn; việc chọn phân hệ không tự chuyển đổi hoặc ánh xạ dữ liệu từ một biểu mẫu khác.

### Định dạng dữ liệu đầu vào

JSON có thể là object dữ liệu trực tiếp theo cấu trúc CANONICAL mà bộ luật sử dụng:

```json
{
  "tuoi": 28,
  "huyet_ap_tam_thu_thap_nhat": 80,
  "huyet_ap_tam_thu_nen": 120,
  "trieu_chung_da_hien_tai_pv": {
    "danh_sach_chon": ["Sẩn phù"]
  }
}
```

Hoặc dùng envelope có trường `du_lieu`:

```json
{
  "du_lieu": {
    "tuoi": 28,
    "huyet_ap_tam_thu_thap_nhat": 80,
    "huyet_ap_tam_thu_nen": 120
  }
}
```

Tên trường và kiểu dữ liệu cần phù hợp với bộ luật của phân hệ. CSV được đọc từ **dòng dữ liệu đầu tiên**; tiêu đề cột phải là tên trường CANONICAL. Giá trị số và `true`/`false` được chuyển đổi tự động; các kiểu dữ liệu lồng nhau nên dùng JSON.

Với JSON RAW dạng các bảng HIS có `hanh_chinh`, demo cho chọn bệnh nhân/lượt khám và mapping có giới hạn: tuổi, giới tính, HATT thấp nhất trong lượt khám cho Phản vệ và IgE sau xác nhận. Trường không có nguồn giữ `null`; không suy triệu chứng từ ICD hoặc thuốc. Phạm vi mapping và cách bổ sung dữ kiện tại tab **Nhập bệnh án** được ghi trong [hướng dẫn nhập liệu](docs/07_patient_input_mapping.md). Ứng dụng chưa có mapping RAW/legacy tổng quát, không tự điền giá trị còn thiếu và không thực thi JSON Schema để xác thực upload. Các file trong `schema/` là tài liệu hợp đồng dữ liệu tham khảo, không phải bảo đảm rằng input được runtime xác thực theo schema.

### Trạng thái kết quả

- `CLASSIFIED`: bộ luật chọn được một nhãn phân loại.
- `THEODOIPV`: nhánh theo dõi phản vệ được kích hoạt; đây không phải nhãn bệnh.
- `INSUFFICIENT_DATA`: thiếu dữ kiện có thể ảnh hưởng đến kết quả.
- `NEEDS_REVIEW`: có dữ liệu sai kiểu hoặc kết quả cần người có chuyên môn rà soát.
- `UNRESOLVED`: chưa có luật đích phù hợp.
- `INVALID_DATA`, `OUT_OF_SCOPE`: các trạng thái được engine hỗ trợ cho những trường hợp tương ứng.

`UNKNOWN` không được mặc định xem là `FALSE`; do đó thiếu dữ liệu có thể khiến kết quả cần bổ sung hoặc rà soát thay vì đưa ra phân loại.

## Chạy kiểm thử

```powershell
.\mayday_rb\Scripts\python.exe -m unittest discover -s tests -v
```

Các kiểm thử bao phủ engine, định tuyến ba phân hệ, ca logic giả định và giao diện Streamlit. Tham khảo kết quả chạy test tại thời điểm hiện tại; các tài liệu trạng thái và rà soát có thể ghi nhận test hoặc vấn đề còn mở.

## Cấu trúc repository

```text
.
├── main.py                  # Giao diện demo Streamlit
├── requirements.txt         # Dependencies Python
├── rules/                   # Bộ luật YAML theo phân hệ
├── schema/                  # JSON Schema tham khảo theo biểu mẫu
├── src/
│   ├── classify.py          # Engine nạp và đánh giá luật
│   ├── pipeline.py          # Nạp engine và định tuyến theo phân hệ
│   ├── patient_input.py     # Input theo engine và mapping RAW giới hạn
│   ├── preprocess.py        # Tiền xử lý tiện ích
│   ├── validate.py          # Tiện ích validation
│   ├── anonymize.py         # Tiện ích khử định danh
│   └── evaluate.py          # Tiện ích đánh giá
├── data/synthetic/          # Ca giả định và kết quả kiểm thử logic
├── tests/                   # Bộ kiểm thử unittest
└── docs/                    # Workflow, bộ luật, từ điển dữ liệu, changelog
```

`src/preprocess.py` và `src/anonymize.py` có các hàm tiện ích độc lập nhưng hiện không được gọi bởi demo hoặc `classify_form`; `src/validate.py` và `src/evaluate.py` hiện còn trống. Engine vẫn tự kiểm tra cấu trúc YAML của bộ luật khi nạp, nhưng chưa có bước xác thực hồ sơ bệnh nhân theo JSON Schema. Vì vậy, pipeline tự động từ hồ sơ RAW đến kết quả (bao gồm validation và đánh giá) hiện chưa được triển khai.

### Luồng dữ liệu mục tiêu: RAW → kết quả

Luồng dưới đây mô tả pipeline nên xây dựng khi tích hợp đầy đủ các bước. Đây là **thiết kế mục tiêu**, không phải mô tả những gì demo đang tự động thực hiện.

```text
Hồ sơ RAW
   ↓
Tiếp nhận và kiểm tra định dạng/cấu trúc
   ↓
Tách thông tin định danh và nhãn đánh giá khỏi dữ liệu suy luận
   ↓
Ánh xạ trường RAW → CANONICAL
   ↓
Tiền xử lý và tạo biến dẫn xuất
   ↓
Xác thực dữ liệu CANONICAL
   ↓
Khử định danh khi phù hợp với mục đích sử dụng
   ↓
Định tuyến đúng phân hệ → chạy bộ luật YAML
   ↓
Trả kết quả, trạng thái, giải thích, trường thiếu và thông tin phiên bản luật

Bộ dữ liệu có nhãn ──→ đối chiếu với kết quả sau suy luận để đánh giá riêng
```

1. **Tiếp nhận RAW:** đọc tệp, xác nhận định dạng và cấu trúc cơ bản. Tệp lỗi hoặc không đọc được phải bị từ chối với thông báo rõ ràng.
2. **Tách dữ liệu:** tách PII (thông tin định danh) và metadata khỏi phần dữ liệu lâm sàng. Nhãn thật, nếu có trong bộ dữ liệu nghiên cứu, phải được giữ riêng và tuyệt đối không gửi vào engine.
3. **Ánh xạ RAW → CANONICAL:** chuyển tên trường và giá trị theo từng nguồn dữ liệu sang hợp đồng CANONICAL của phân hệ. Ghi nhận giá trị không ánh xạ được; không tự suy diễn giá trị còn thiếu thành “Không”.
4. **Tiền xử lý:** chuẩn hóa định dạng và tính các biến dẫn xuất mà luật cần. Chỉ thực hiện phép biến đổi đã được quy định, đồng thời giữ khả năng truy vết nguồn gốc dữ liệu.
5. **Xác thực CANONICAL:** kiểm tra kiểu, miền giá trị, đơn vị và ràng buộc giữa trường trước khi suy luận. Hợp đồng đầu vào suy luận cần tách khỏi schema bệnh án đầy đủ nếu schema đầy đủ yêu cầu chẩn đoán hoặc nhãn không được phép làm đầu vào.
6. **Khử định danh:** trước khi lưu trữ, chia sẻ hoặc xử lý ngoài môi trường có quyền truy cập phù hợp, loại bỏ/che thông tin nhận dạng không cần thiết. Nếu cần tạo biến từ ngày sinh hoặc thông tin định danh, thực hiện phép tính được cho phép trước khi loại bỏ nguồn đó; không xem khử định danh là bảo đảm chống tái nhận dạng tuyệt đối.
7. **Định tuyến và suy luận:** chọn đúng một trong ba phân hệ `phan_ve`, `cap`, `man`, rồi gọi engine với dữ liệu CANONICAL đã kiểm tra. Engine trả trạng thái, nhãn nếu đủ căn cứ, luật khớp/chặn, trường thiếu, trace và phiên bản/hash bộ luật.
8. **Trả và lưu kết quả:** trình bày kết luận cùng giới hạn/cảnh báo; kiểm soát quyền truy cập và lưu vết theo chính sách dữ liệu của hệ thống.
9. **Đánh giá riêng:** chỉ với bộ dữ liệu có nhãn, so sánh kết quả suy luận với nhãn thật sau khi suy luận hoàn tất để tính các chỉ số. Đây là luồng đánh giá tập dữ liệu, không phải bước bắt buộc cho mỗi hồ sơ sử dụng thông thường.

**Tình trạng triển khai hiện tại:** demo đọc JSON/CSV đơn giản hoặc ca giả định, cho phép chọn phân hệ, rồi chuyển dữ liệu trực tiếp vào engine. Đã có mapping RAW → CANONICAL giới hạn qua giao diện; chưa có xác thực hồ sơ đầu vào bằng schema, pipeline tiền xử lý/khử định danh tự động hoặc module đánh giá hoàn chỉnh. Các bước này cần được triển khai và kiểm thử trước khi coi luồng trên là pipeline vận hành.

### Gọi engine từ Python

```python
from src.pipeline import classify_form, load_engines

engines = load_engines()
patient_data = {
    "tuoi": 28,
    "huyet_ap_tam_thu_thap_nhat": 80,
    "huyet_ap_tam_thu_nen": 120,
}

result = classify_form("phan_ve", patient_data, engines)
print(result["status"], result["predicted_label"])
```

`form_type` nhận một trong các giá trị `phan_ve`, `cap`, hoặc `man`. `patient_data` cần là object CANONICAL; hàm này không tự đọc envelope `du_lieu`.

## Tài liệu liên quan

- [Tổng quan dự án](docs/00_overview.md)
- [Bộ quy tắc](docs/01_rules.md)
- [Workflow](docs/02_workflow.md)
- [Từ điển dữ liệu](docs/01_data_dictionary/)
- [Các ca kiểm thử](docs/04_test_cases.md)
- [Changelog và hướng dẫn demo](docs/05_changelog.md)
- [Rà soát logic luật](docs/06_rule_logic_review.md)
- [Nhập bệnh án và mapping RAW](docs/07_patient_input_mapping.md)
- [Mức độ sẵn sàng triển khai và các vấn đề còn mở](docs/03_implementation_readiness.md)

## An toàn dữ liệu và giới hạn sử dụng

- Chỉ dùng dữ liệu giả định hoặc dữ liệu đã được phê duyệt và khử định danh phù hợp. Không tải thông tin định danh bệnh nhân thật lên demo nếu chưa có phê duyệt, kiểm soát truy cập và biện pháp bảo vệ dữ liệu thích hợp.
- Các bộ ca trong repository phục vụ kiểm thử giả định; kết quả trên các ca này không chứng minh độ chính xác hoặc khả năng tổng quát hóa trên bệnh án thực tế.
- Quy tắc trong YAML và đầu ra của ứng dụng cần được chuyên gia y tế kiểm tra. Không dùng kết quả để thay thế đánh giá lâm sàng, quyết định cấp cứu hoặc hướng dẫn của nhân viên y tế.
- Các điều kiện chuyên môn, mapping dữ liệu và một số hạn chế triển khai còn được ghi nhận trong tài liệu rà soát; cần giải quyết và thẩm định trước mọi mục đích sử dụng lâm sàng.
