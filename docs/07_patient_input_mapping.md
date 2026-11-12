# Nhập bệnh án theo engine và mapping RAW

## Nhập trực tiếp trên Streamlit

Chọn mẫu Phản vệ, Cấp hoặc Mạn, sau đó chọn nguồn **Nhập theo mẫu engine** và mở tab **Nhập bệnh án**.

Panel lấy các trường từ YAML đang chạy, gồm cả biến trong công thức, và dùng JSON Schema để tạo lựa chọn/kiểu dữ liệu. Nhập số, chọn Có/Không, chọn triệu chứng hoặc các mục của bảng sẩn phù rồi bấm **Áp dụng vào bệnh án**. Tab **Bệnh án & kết quả** dùng JSON vừa áp dụng để suy diễn. Có thể tải bệnh án dưới dạng `{"form_type": "...", "du_lieu": {...}}`.

- Số chưa nhập giữ `null`; không tự điền tuổi hoặc HATT.
- Có/Không và boolean mặc định là **Chưa có dữ liệu**.
- Một danh sách chưa được đánh giá giữ `null`. Để ghi nhận đã kiểm tra và không có mục nào, đánh dấu **Đã đánh giá mục này** với danh sách để trống; khi đó xuất `[]`.
- `dac_diem_san_phu_cap` được xuất đúng dạng array/object, ví dụ `[{"dang_ton_thuong": "Hình tròn (bờ rõ)"}]`.
- Các trường ngoài panel đã có trong bệnh án được giữ lại khi áp dụng. Với mục sẩn phù đã có, các thuộc tính bổ sung của dạng tổn thương còn được chọn cũng được giữ lại.
- Panel cũng dùng để bổ sung bệnh án đã upload. Khi JSON nguồn thay đổi, panel nạp lại dữ liệu; thay đổi trong panel chỉ có hiệu lực sau khi bấm Áp dụng.

Đây là panel của **input suy diễn**, không phải toàn bộ biểu mẫu hành chính. Schema thu thập hiện còn yêu cầu tên, điện thoại và chẩn đoán đích của mẫu Cấp; các dữ kiện này không được tự tạo để làm bản ghi đầy đủ hoặc dùng làm bằng chứng cho rule.

## Upload RAW

Nguồn **Tải file mới (.json, .csv)** vẫn nhận JSON CANONICAL/envelope. Với JSON có bảng `hanh_chinh`, giao diện nhận diện RAW và cho chọn bệnh nhân cùng lượt khám trước khi mapping. CSV chỉ hỗ trợ hàng phẳng đầu tiên, không thay bộ nối bảng RAW.

Mapper tại `src/patient_input.py` hỗ trợ các bảng `hanh_chinh`, `chan_doan`, `dhst`, `xet_nghiem`, `cdha_tdcn`, `thuoc` và yêu cầu `MA_BN_AN_DANH` nối về bảng hành chính. Mỗi bản ghi hành chính là một lựa chọn lượt khám, giữ thứ tự nguồn.

| Nguồn | Trường engine | Điều kiện mapping |
| --- | --- | --- |
| Nhóm bệnh nhân | `ma_benh_nhan` | Mã hiển thị `benh_nhan_n`; không dùng mã HIS làm input. File tách tên `benh_nhan_n.json` giữ số tương ứng. |
| `TUOI_KHI_VAO_VIEN` | `tuoi` | Sao chép tuổi không âm, hữu hạn đã ghi ở lượt chọn; không tính từ năm sinh, không làm tròn. Bác sĩ kiểm tra đơn vị tuổi của HIS. |
| `GIOI_TINH` | `gioi_tinh` | Chỉ sao chép `Nam`/`Nữ` đã có. |
| `dhst.BLOOD_PRESSURE_MAX` | `huyet_ap_tam_thu_thap_nhat` trong Phản vệ | Lấy min số dương hữu hạn trong đúng lượt khám. Không dùng làm HATT nền. |
| Mã `SHM0027`, đơn vị `IU/mL` hoặc `UI/mL` | `ige_toan_phan` hoặc `ige_toan_phan_uiml` | Chỉ áp dụng sau xác nhận của bác sĩ rằng mã này là IgE toàn phần, thuộc đúng lượt khám, có số hữu hạn không âm và không có kết quả khác nhau trong cùng lượt. |

Khi nguồn và bản ghi hành chính cùng có `TREATMENT_ID`, mapper dùng khóa khớp. Nếu không có khóa chung, chỉ nhận bản ghi nằm trong duy nhất một khoảng `IN_TIME`–`OUT_TIME` có đủ ngày/giờ của bệnh nhân. Thiếu thời điểm, khoảng bị chồng lấn hoặc không xác định được lượt thì không tự gộp. Các xét nghiệm chưa xác định vẫn xuất trong bảng ứng viên để bác sĩ đối chiếu.

Xác nhận IgE chỉ xác nhận ý nghĩa mã test; không bỏ qua kiểm tra thời điểm, đơn vị hoặc kết quả mâu thuẫn. Xác nhận được đặt lại khi đổi file, bệnh nhân, lượt khám hoặc mẫu. Bác sĩ có thể bổ sung giá trị đã kiểm chứng tại panel nếu nguồn không nối tự động được.

## Những phần giữ thiếu

Không dùng ICD/chẩn đoán nguồn làm triệu chứng hoặc kết quả test. Không suy thời gian khởi phát từ ngày nhập viện, ngày ngừng thuốc từ đơn thuốc, ngày sinh từ năm sinh, hoặc mức độ nặng từ một từ “ngứa” trong mô tả. ASST, IL-24, yếu tố dị nguyên và các mục không có nguồn xác định được giữ thiếu. Không gọi preprocessor cũ đang điền các giá trị mặc định tuổi/HATT.

Các trường chưa có dữ kiện vẫn có đúng path và giữ `null`. Vì vậy bệnh án đã mapping có thể trả `INSUFFICIENT_DATA`; bác sĩ bổ sung dữ kiện thực tế trên panel để tiếp tục test. Bản ghi đọc được bởi engine không đồng nghĩa đã đầy đủ schema thu thập hoặc đã được nghiệm thu lâm sàng.

## Kiểm tra và dữ liệu thật

Test của mapper/panel chỉ dùng hồ sơ giả. Kiểm tra gồm schema array/object, UNKNOWN, đơn vị, số sai kiểu, nguồn tham chiếu, nhiều bệnh nhân/lượt khám, kết quả xung đột, đổi nguồn và giữ nội dung bác sĩ đã chỉnh.

Dữ liệu thật và các bản xuất local được giữ trong thư mục đã Git ignore, không đưa vào fixtures hoặc commit. Thông tin mapping hiển thị trên giao diện để người dùng đối chiếu; engine chỉ nhận `du_lieu`. Các khác biệt nghiệp vụ CIndU/CSU và các rule hiện có không được sửa trong tính năng nhập liệu này.
