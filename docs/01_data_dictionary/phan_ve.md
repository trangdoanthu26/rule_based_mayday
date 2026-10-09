*(Bệnh án điều trị Sốc phản vệ / Phản vệ 22.9.2026)*

## Quy ước dữ liệu chung
* **Missing**: `null` (Chưa thu thập / Để trống).
* **Unknown**: Chuỗi `"unknown"` hoặc số `-1` (Đã hỏi nhưng Bác sĩ / Bệnh nhân không biết / không rõ).
* **Not applicable**: `"N/A"` (Không áp dụng cho trường hợp này).

---

### A0. Mã hồ sơ & Phân loại

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ma_benh_nhan`** | Mã định danh bệnh nhân | string | null | *TODO: Bác sĩ/IT xác nhận định dạng Regex mã bệnh nhân HIS* | Missing: `null`<br>Unknown: *TODO: Cho phép khi cấp cứu chưa rõ danh tính?*<br>N/A: `"N/A"` | **Có** | Link với HIS khi đăng ký khám, không cho sửa tay. |
| **`chan_doan_chinh_pv`** | Chẩn đoán chính sốc phản vệ / phản vệ | string | null | • `Sốc phản vệ`<br>• `Phản vệ` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Auto-điền từ mục 1 (`muc_do_phan_ve`), hiển thị badge ở đầu trang. |
| **`ma_ho_so`** | Mã hồ sơ bệnh án phản vệ | string | null | *TODO: Định dạng sinh mã tự động của hệ thống?* | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Hệ thống tự sinh khi tạo bệnh án mới, không cho sửa tay. |
| **`de_tai_ai`** | Phân loại lượt nghiên cứu Đề tài cấp Bộ AI | string | null | • `Lần 1`<br>• `Lần 2`<br>• `Kiểm tra lại` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Bác sĩ chọn khi khám. |

---

### A1. Hành chính

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ho_ten`** | Họ và tên bệnh nhân | string | null | Chuỗi ký tự họ tên | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có** | Link với HIS. |
| **`ngay_sinh`** | Ngày tháng năm sinh | string | YYYY-MM-DD | Ngày hợp lệ $\le$ ngày hiện tại | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`gioi_tinh`** | Giới tính bệnh nhân | string | null | *TODO: Bác sĩ xác nhận danh mục giới tính chuẩn (Nam, Nữ, Khác?)* | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`so_dien_thoai`** | Số điện thoại liên hệ | string | null | *TODO: Xác nhận Regex SĐT (10 số?)* | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có** | Link với HIS. |
| **`nghe_nghiep`** | Nghề nghiệp bệnh nhân | string | null | *TODO: Bác sĩ cung cấp danh mục nghề nghiệp đóng hay nhập tự do?* | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`dan_toc`** | Dân tộc bệnh nhân | string | null | *TODO: Danh mục 54 dân tộc Việt Nam hay chuỗi tự do?* | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`dia_chi_so_nha_thon_pho`** | Địa chỉ - Số nhà, thôn, phố | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`dia_chi_xa_phuong`** | Địa chỉ - Xã / Phường | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`dia_chi_tinh_tp`** | Địa chỉ - Tỉnh / Thành phố | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`noi_lam_viec`** | Nơi làm việc hiện tại | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`bhyt_so_the`** | Số thẻ bảo hiểm y tế | string | null | *TODO: Xác nhận định dạng chuẩn 15 ký tự BHYT?* | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`bhyt_gia_tri_den`** | Hạn thẻ BHYT đến ngày | string | YYYY-MM-DD | Định dạng ngày hợp lệ | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`nguoi_nha_ho_ten_dia_chi`** | Họ tên và địa chỉ người nhà | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`nguoi_nha_so_dien_thoai`** | Số điện thoại người nhà | string | null | Chuỗi số điện thoại | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`thoi_diem_kham_lan_dau`** | Thời điểm khám lần đầu tại viện | string | YYYY-MM-DDTHH:mm:ss | Định dạng Datetime ISO 8601 | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`ngay_bat_dau_dieu_tri_ngoai_tru`** | Ngày bắt đầu điều trị | string | YYYY-MM-DD | Định dạng ngày hợp lệ | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS (Nhãn: "Ngày bắt đầu/kết thúc điều trị"). |
| **`ngay_ket_thuc_dieu_tri_ngoai_tru`** | Ngày kết thúc điều trị | string | YYYY-MM-DD | Ngày hợp lệ $\ge$ ngày bắt đầu | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |

---

### A2. Chẩn đoán tuyến trước & Kết quả điều trị bảo hiểm

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`chan_doan_tuyen_truoc`** | Chẩn đoán của tuyến trước chuyển đến | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`chan_doan_ban_dau_phong_kham`** | Chẩn đoán ban đầu tại phòng khám | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`chan_doan_tai_kham`** | Lịch sử chẩn đoán tại các lần tái khám | array (grid) | null | *TODO: Bác sĩ xác nhận cấu trúc từng cột trong bảng chan_doan_tai_kham?* | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Bảng nhập liệu cho phép thêm/xoá dòng. |
| **`benh_phu`** | Bệnh phụ kèm theo | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`ket_qua_dieu_tri_bao_hiem`** | Kết quả điều trị theo bảo hiểm | object | null | • `Khỏi bệnh`<br>• `Đỡ`<br>• `Không đỡ`<br>• `Nặng hơn`<br>• `Chết`<br>• `Biến chứng (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. Kèm ô nhập chi tiết nếu chọn Biến chứng. |

---

### B0. Phần lưu trữ

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ngay_kham`** | Ngày thực hiện khám bệnh | string | YYYY-MM-DD | Định dạng ngày hợp lệ | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tự động chọn theo ngày BN đăng ký trên HIS. |
| **`bac_si_kham`** | Tên bác sĩ thực hiện khám | string | null | Tên tài khoản bác sĩ | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tự động điền theo tài khoản bác sĩ đăng nhập. |

---

### B1. Chẩn đoán sốc phản vệ / Phản vệ

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`muc_do_phan_ve`** | Mức độ phân loại phản vệ | string | null | • `Sốc phản vệ`<br>• `Phản vệ` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Bắt buộc TRỪ KHI tick `tiep_tuc_theo_doi_chua_du_du_kien`. Auto-điền vào A0. |
| **`soc_phan_ve_tieu_chi`** | Tiêu chí chẩn đoán sốc phản vệ | array (checkbox) | null | • `HATT < 90 mmHg hoặc giảm > 30% so với huyết áp nền`<br>• `Dấu hiệu giảm tưới máu/suy tuần hoàn` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Chỉ hiện khi `muc_do_phan_ve` = 'Sốc phản vệ'. Auto-gợi ý từ mục 2.5. |
| **`phan_ve_tieu_chi`** | Tiêu chí chẩn đoán phản vệ (đạt ít nhất 1/3) | array (checkbox) | null | • `Da/niêm mạc + Hô hấp hoặc Tuần hoàn`<br>• `Dị nguyên nghi ngờ + ≥ 2/4 hệ: Da/niêm mạc – Hô hấp – Tuần hoàn – Tiêu hoá`<br>• `Dị nguyên đã biết + tụt huyết áp` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Chỉ hiện khi `muc_do_phan_ve` = 'Phản vệ'. Gợi ý từ mục 2 và 3. |
| **`tiep_tuc_theo_doi_chua_du_du_kien`** | Cờ đánh dấu chưa đủ dữ kiện phân loại | boolean | null | `true`, `false` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Khi tick = `true`, cho phép bỏ qua bắt buộc chọn `muc_do_phan_ve`. |

---

### B2. Biểu hiện lâm sàng

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`thoi_gian_khoi_phat_pv`** | Thời gian từ khi khởi phát phản vệ | number | *TODO: Bác sĩ xác nhận đơn vị (phút hay giờ hay ngày?)* | *TODO: Bác sĩ cho biết khoảng giá trị tối thiểu / tối đa?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Link với BN nhập. |

#### B2.1. Triệu chứng da/niêm mạc

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`trieu_chung_da_hien_tai_pv`** | Triệu chứng da đợt hiện tại | object (checkbox + text) | null | Danh sách: `Phù mạch`, `Sẩn phù`, `Ban dát sẩn`, `Không có`, `Khác`<br>Ô phụ: `Khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Mục 2.1, cột 'Triệu chứng trong đợt hiện tại'. |
| **`tien_su_benh_nen_lien_quan_da_pv`** | Tiền sử/bệnh nền liên quan đến da | object (checkbox + text) | null | Danh sách: `Mày đay mạn tính`, `Tiền sử phù mạch tái diễn`, `Rối loạn tế bào mast`, `Viêm da cơ địa`, `Không có`, `Khác`<br>Ô phụ: `Khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Mục 2.1, cột 'Tiền sử/bệnh nền liên quan'. |
| **`dien_bien_da_pv`** | Diễn biến triệu chứng da | object | null | • `Lần đầu xuất hiện`<br>• `Lần thứ ...` (kèm: `Tăng nặng` / `Không đổi`) | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/checkbox kết hợp. |
| **`hien_tai_co_san_phu_pv`** | Hiện tại khám có sẩn phù | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/dropdown 1 lựa chọn. |
| **`anh_san_phu_pv`** | Ảnh sẩn phù tải lên | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tự động tick Có nếu BN tải ảnh. |
| **`dac_diem_san_phu_pv`** | Đặc điểm tổn thương sẩn phù | object | null | • Dạng: `Hình vòng`, `Hình đứt đoạn`, `Hình bản đồ`, `Hình tròn`, `Dát sẩn`, `Khác`<br>• Kích thước: *TODO: Đơn vị?*<br>• Thời gian tồn tại: *TODO: Đơn vị?*<br>• Thời điểm: `Ban ngày`, `Chiều tối`, `Đêm`, `Không cố định`<br>• Số lượng: `<20`, `20-50`, `>50`<br>• Mức độ: `>50% BSA`, `≤50% BSA`, `Bất kỳ`, `Toàn thân`, `Đặc biệt` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Bảng dạng tổn thương tổng hợp. |
| **`so_luong_san_phu_pv`** | Số lượng sẩn phù đợt này | string | nốt | • `<20 nốt`<br>• `20-50 nốt`<br>• `>50 nốt` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tách từ `dac_diem_san_phu_pv` ngày 22.9. |
| **`muc_do_lan_rong_va_phan_bo_ton_thuong_pv`** | Mức độ lan rộng & phân bố tổn thương | object | null | • Mức độ: `>50% BSA`, `≤50% BSA`<br>• Phân bố: `Bất kỳ`, `Toàn thân`, `Đặc biệt (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tách từ `dac_diem_san_phu_pv` ngày 22.9. |
| **`hien_tai_co_phu_mach_pv`** | Hiện tại có phù mạch | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/dropdown 1 lựa chọn. |
| **`anh_phu_mach_pv`** | Ảnh phù mạch | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tự động tick Có nếu BN tải ảnh. |
| **`so_lan_phu_mach_tung_xay_ra_pv`** | Số lần phù mạch từng xảy ra | integer | lần | *TODO: Khoảng hợp lệ ($\ge 0$)?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Number input. |
| **`so_lan_phu_mach_nang_can_vien_pv`** | Số lần phù mạch nặng cần đến viện đợt này | integer | lần | *TODO: Khoảng hợp lệ ($\ge 0$)?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Number input. |
| **`vi_tri_phu_mach_pv`** | Vị trí giải phẫu phù mạch | object (checkbox + text) | null | Danh sách: `Một bên`, `Hai bên`, `Mi mắt`, `Lưỡi`, `Thanh quản`, `Môi`, `Bàn tay`, `Bàn chân`, `Các phần khác của mặt`, `Sinh dục`, `Vị trí khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox nhiều lựa chọn. |
| **`thoi_gian_ton_tai_phu_mach_pv`** | Thời gian tồn tại trung bình của phù mạch | string | giờ | • `<1`<br>• `1-6`<br>• `6-12`<br>• `12-24`<br>• `24-48`<br>• `48-72`<br>• `>72`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Radio 1 lựa chọn. |

#### B2.2. Triệu chứng hô hấp

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`trieu_chung_ho_hap_co_khong_pv`** | Có triệu chứng hô hấp hay không | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Nếu 'Không' ẩn các trường phụ bên dưới. |
| **`trieu_chung_ho_hap_hien_tai_pv`** | Triệu chứng hô hấp đợt hiện tại | object (checkbox + text) | null | Danh sách: `Tiếng rít thanh quản`, `Khó thở`, `Thở khò khè`, `Nghẹn họng`, `Viêm long đường hô hấp`, `Khàn giọng`, `Ngừng thở`, `Không có`, `Khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Chỉ hiện khi `trieu_chung_ho_hap_co_khong_pv` = 'Có'. |
| **`tien_su_benh_nen_ho_hap_pv`** | Tiền sử/bệnh nền hô hấp | object (checkbox + text) | null | Danh sách: `Hen phế quản`, `Bệnh phổi tắc nghẽn mạn tính`, `Viêm mũi dị ứng`, `Không có`, `Khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Luôn hiển thị, không phụ thuộc câu Có/Không. |
| **`dien_bien_ho_hap_pv`** | Diễn biến triệu chứng hô hấp | object | null | • `Lần đầu xuất hiện`<br>• `Lần thứ ...` (kèm: `Tăng nặng` / `Không đổi`) | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Chỉ hiện khi `trieu_chung_ho_hap_co_khong_pv` = 'Có'. |

#### B2.3. Triệu chứng tuần hoàn

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`trieu_chung_tuan_hoan_co_khong_pv`** | Có triệu chứng tuần hoàn hay không | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Nếu 'Không' ẩn các trường phụ bên dưới. |
| **`trieu_chung_tuan_hoan_hien_tai_pv`** | Triệu chứng tuần hoàn đợt hiện tại | object (checkbox + text) | null | Danh sách: `Ngất`, `Chóng mặt`, `Tụt huyết áp / sốc`, `Tím tái`, `Không có`, `Khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Chỉ hiện khi `trieu_chung_tuan_hoan_co_khong_pv` = 'Có'. |
| **`tien_su_benh_nen_tuan_hoan_pv`** | Tiền sử/bệnh nền tim mạch | object (checkbox + text) | null | Danh sách: `Bệnh tim mạch (ghi rõ)`, `Tiền sử ngất/choáng tái diễn`, `Không có` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Luôn hiển thị. |
| **`dien_bien_tuan_hoan_pv`** | Diễn biến triệu chứng tuần hoàn | object | null | • `Lần đầu xuất hiện`<br>• `Lần thứ ...` (kèm: `Tăng nặng` / `Không đổi`) | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Chỉ hiện khi `trieu_chung_tuan_hoan_co_khong_pv` = 'Có'. |

#### B2.4. Triệu chứng tiêu hoá

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`trieu_chung_tieu_hoa_co_khong_pv`** | Có triệu chứng tiêu hoá hay không | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Nếu 'Không' ẩn các trường phụ bên dưới. |
| **`trieu_chung_tieu_hoa_hien_tai_pv`** | Triệu chứng tiêu hoá đợt hiện tại | object | null | • `Nôn: số lần ...`<br>• `Đau bụng quặn thắt` (đau nặng)<br>• `Không có`<br>• `Khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Chỉ hiện khi `trieu_chung_tieu_hoa_co_khong_pv` = 'Có'. |
| **`tien_su_benh_nen_tieu_hoa_pv`** | Tiền sử/bệnh nền tiêu hoá | object | null | • `Bệnh tiêu hoá mạn tính (ghi rõ)`<br>• `Không có`<br>• `Khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Luôn hiển thị. |
| **`dien_bien_tieu_hoa_pv`** | Diễn biến triệu chứng tiêu hoá | object | null | • `Lần đầu xuất hiện`<br>• `Lần thứ ...` (kèm: `Tăng nặng` / `Không đổi`) | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Chỉ hiện khi `trieu_chung_tieu_hoa_co_khong_pv` = 'Có'. |

#### B2.5. Bảng theo dõi dấu hiệu sinh tồn

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`bang_theo_doi_dau_hieu_sinh_ton`** | Lưới theo dõi dấu hiệu sinh tồn cấp cứu | array (grid) | null | Cột: `Thời điểm`, `Mạch`, `Huyết áp`, `Nhịp thở`, `SpO2`, `Nhiệt độ`, `Tri giác`, `Xử trí/ghi chú`<br>*TODO: Bác sĩ cho biết chuẩn thang đo Tri giác (Glasgow hay AVPU hay tự do)?* | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Data grid thêm/xoá dòng (giấy in sẵn 3 dòng). |
| **`huyet_ap_tam_thu_nen`** | Huyết áp tâm thu nền (nếu biết) | number | mmHg | *TODO: Bác sĩ cho biết khoảng hợp lệ?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Bổ sung ngoài bệnh án giấy ngày 22.9 để tính tiêu chí giảm >30%. |
| **`huyet_ap_tam_thu_thap_nhat`** | Huyết áp tâm thu thấp nhất đo được | number | mmHg | Hệ thống tự tính Min từ bảng sinh hiệu | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Read-only. Cờ = TRUE nếu < 90 mmHg hoặc < 70% HA nền $\to$ auto gợi ý tiêu chí sốc. |

---

### B3. Định hướng căn nguyên

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`yeu_to_nghi_ngo_pv_thuc_an`** | Yếu tố nghi ngờ đợt này - Thức ăn | object | null | • `Có (ghi rõ)`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/dropdown 1 lựa chọn. |
| **`thoi_gian_tiep_xuc_khoi_phat_pv_thuc_an`** | Thời gian từ tiếp xúc thức ăn đến khởi phát | number | *TODO: Đơn vị phút hay giờ?* | *TODO: Khoảng hợp lệ?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Chỉ hiện khi nhóm Thức ăn = 'Có'. |
| **`tien_su_phan_ung_yeu_to_pv_thuc_an`** | Tiền sử phản ứng với thức ăn nghi ngờ | object | null | • `Có, số lần: ... (ghi rõ)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Radio/dropdown kèm ô nhập phụ. |
| **`tien_su_phan_ve_di_ung_khac_pv_thuc_an`** | Tiền sử phản vệ/dị ứng khác với thức ăn | object | null | • `Không`<br>• `Phản vệ (ghi rõ)`<br>• `Dị ứng (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox nhiều lựa chọn. |
| **`yeu_to_nghi_ngo_pv_thuoc`** | Yếu tố nghi ngờ đợt này - Thuốc | object | null | • `Có (ghi rõ)`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/dropdown 1 lựa chọn. |
| **`thoi_gian_tiep_xuc_khoi_phat_pv_thuoc`** | Thời gian từ tiếp xúc thuốc đến khởi phát | number | *TODO: Đơn vị?* | *TODO: Khoảng hợp lệ?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Chỉ hiện khi nhóm Thuốc = 'Có'. |
| **`tien_su_phan_ung_yeu_to_pv_thuoc`** | Tiền sử phản ứng với thuốc nghi ngờ | object | null | • `Có, số lần: ... (ghi rõ)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Radio/dropdown kèm ô nhập phụ. |
| **`tien_su_phan_ve_di_ung_khac_pv_thuoc`** | Tiền sử phản vệ/dị ứng khác với thuốc | object | null | • `Không`<br>• `Phản vệ (ghi rõ)`<br>• `Dị ứng (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox nhiều lựa chọn. |
| **`yeu_to_nghi_ngo_pv_con_trung_dot`** | Yếu tố nghi ngờ đợt này - Côn trùng đốt | object | null | • `Có (ghi rõ)`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/dropdown 1 lựa chọn. |
| **`thoi_gian_tiep_xuc_khoi_phat_pv_con_trung_dot`** | Thời gian từ côn trùng đốt đến khởi phát | number | *TODO: Đơn vị?* | *TODO: Khoảng hợp lệ?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Chỉ hiện khi Côn trùng đốt = 'Có'. |
| **`tien_su_phan_ung_yeu_to_pv_con_trung_dot`** | Tiền sử phản ứng với côn trùng đốt | object | null | • `Có, số lần: ... (ghi rõ)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Radio/dropdown kèm ô nhập phụ. |
| **`tien_su_phan_ve_di_ung_khac_pv_con_trung_dot`** | Tiền sử phản vệ/dị ứng khác côn trùng | object | null | • `Không`<br>• `Phản vệ (ghi rõ)`<br>• `Dị ứng (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox nhiều lựa chọn. |
| **`yeu_to_nghi_ngo_pv_khac`** | Yếu tố nghi ngờ đợt này - Khác | object | null | • `Có (ghi rõ)`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/dropdown 1 lựa chọn. |
| **`tac_nhan_hit_vao_pv`** | Tác nhân nghi ngờ qua đường hít | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Bổ sung 22.9. Dị nguyên hít đơn thuần không tính phản vệ. |
| **`thoi_gian_tiep_xuc_khoi_phat_pv_khac`** | Thời gian tiếp xúc yếu tố khác đến khởi phát | number | *TODO: Đơn vị?* | *TODO: Khoảng hợp lệ?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Chỉ hiện khi nhóm Khác = 'Có'. |
| **`tien_su_phan_ung_yeu_to_pv_khac`** | Tiền sử phản ứng với yếu tố khác | object | null | • `Có, số lần: ... (ghi rõ)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Radio/dropdown kèm ô nhập phụ. |
| **`tien_su_phan_ve_di_ung_khac_pv_khac`** | Tiền sử phản vệ/dị ứng khác với yếu tố khác | object | null | • `Không`<br>• `Phản vệ (ghi rõ)`<br>• `Dị ứng (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox nhiều lựa chọn. |

---

### B4. Bệnh sử - Tiền sử

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`da_dieu_tri_dot_nay_pv`** | Đã điều trị bệnh đợt này hay chưa | string | null | • `Có`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Nếu 'Có' thì mở bảng danh sách thuốc. |
| **`danh_sach_thuoc_da_dieu_tri_pv`** | Danh sách thuốc đã dùng đợt này | array (grid) | null | Cột: `Tên thuốc`, `Liều dùng`, `Thời gian dùng`, `Tuân thủ (Đều/Không đều/Không rõ)`, `Đáp ứng (Hoàn toàn/Một phần/Không đáp ứng/Không rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi `da_dieu_tri_dot_nay_pv` = 'Có'. |
| **`so_lan_phan_ve_hoac_may_day_cap_truoc_do`** | Số lần phản vệ / mày đay cấp trước đó | integer | lần | *TODO: Khoảng hợp lệ ($\ge 0$)?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Giữ nguyên văn bệnh án giấy gộp 2 bệnh. |
| **`tuoi_lan_dau_bi_benh_pv`** | Tuổi lần đầu bị bệnh | integer | tuổi | *TODO: Khoảng hợp lệ (0-120)?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Number input. |
| **`dot_gan_nhat_cach_pv`** | Đợt gần nhất cách thời điểm hiện tại | string | *TODO: Đơn vị?* | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Input text. |
| **`thoi_gian_keo_dai_trung_binh_moi_dot_pv`** | Thời gian kéo dài trung bình mỗi đợt | string | *TODO: Đơn vị?* | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Input text. |
| **`tien_su_gia_dinh_pv`** | Tiền sử gia đình mắc bệnh liên quan | object | null | • `Có (ghi rõ: thành viên – bệnh lý – diễn biến)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Radio/checkbox kết hợp. |

---

### B5. Cận lâm sàng

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`wbc_gl`** | Số lượng bạch cầu WBC | number | G/L | *TODO: Khoảng giá trị tham chiếu?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Mục 5.1. |
| **`neu_gl`** | Bạch cầu trung tính NEU | number | G/L | *TODO: Khoảng giá trị tham chiếu?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Mục 5.1. |
| **`lym_gl`** | Bạch cầu Lympho LYM | number | G/L | *TODO: Khoảng giá trị tham chiếu?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Mục 5.1. |
| **`plt_gl`** | Số lượng tiểu cầu PLT | number | G/L | *TODO: Khoảng giá trị tham chiếu?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Mục 5.1. |
| **`crp_mgl`** | Định lượng CRP | number | mg/L | *TODO: Khoảng giá trị tham chiếu?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Mục 5.1. |
| **`ige_toan_phan_uiml`** | Nồng độ IgE toàn phần | number | UI/mL | *TODO: Khoảng giá trị tham chiếu?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Mục 5.1. |
| **`nlr`** | Tỷ số NLR = NEU / LYM | number | null | Tự động tính từ `neu_gl` / `lym_gl` | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Read-only. Không cho nhập tay. |
| **`plr`** | Tỷ số PLR = PLT / LYM | number | null | Tự động tính từ `plt_gl` / `lym_gl` | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Read-only. Không cho nhập tay. |
| **`tryptase_cap_ngml`** | Tryptase cấp (trong 1-4h đầu cơn) | number | ng/mL | *TODO: Khoảng giá trị tham chiếu?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Dấu ấn quan trọng của phản vệ. |
| **`tryptase_nen_ngml`** | Tryptase nền (24-48h sau cơn) | number | ng/mL | *TODO: Khoảng giá trị tham chiếu?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Mục 5.1. |
| **`khi_mau_pv`** | Kết quả khí máu | string | null | Văn bản tự do | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Textarea, không có đơn vị cố định. |
| **`can_lam_sang_khac_pv`** | Cận lâm sàng khác | string | null | Văn bản tự do | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Textarea tự do. |

---

### B6. Phản vệ - Theo dõi điều trị

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`theo_doi_phan_ve_dieu_tri`** | Lưới theo dõi điều trị lồng 2 cấp | array (grid lồng) | null | • Cấp ngày: `Ngày thứ`, `Ngày`, `BS điều trị`<br>• Cấp thời điểm: `Giờ:phút`, `Diễn biến 5 hệ`, `Sinh hiệu`, `Tối đa 5 thuốc`, `Liều`, `Đường dùng`, `Thời gian`, `Ghi chú` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Lưới lồng 2 cấp, làm phẳng khi lưu trữ. Sửa 22.9: diễn biến dùng checkbox để chạy rule-based. |
| **`ket_qua_cuoi_ngay_pv`** | Kết quả cuối mỗi ngày điều trị | object | null | • `Hết triệu chứng`<br>• `Cải thiện một phần`<br>• `Không thay đổi`<br>• `Nặng lên`<br>• `Khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Lặp lại theo từng ngày điều trị. |
| **`ket_qua_cuoi_dot_pv`** | Kết quả cuối toàn bộ đợt điều trị | object | null | • `Ra viện`<br>• `Chuyển viện`<br>• `Tử vong`<br>• `Khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Bổ sung 22.9 để có kết cục nghiên cứu. |

---

