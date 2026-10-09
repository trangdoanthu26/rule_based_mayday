
*(Bệnh án điều trị Mày đay cấp tính - 22.9.2026)*

## Quy ước dữ liệu chung
* **Missing**: `null` (Chưa thu thập / Để trống).
* **Unknown**: Chuỗi `"unknown"` hoặc số `-1` (Đã hỏi nhưng Bác sĩ / Bệnh nhân không biết / không rõ).
* **Not applicable**: `"N/A"` (Không áp dụng cho trường hợp này).

---

### A0. Mã hồ sơ & Phân loại

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ma_benh_nhan`** | Mã bệnh nhân HIS | string | null | Regex mã bệnh nhân | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có** | Link với HIS khi đăng ký khám. |
| **`chan_doan_chinh_cap`** | Chẩn đoán chính mày đay cấp tính | object | null | • `Mày đay cấp có dấu hiệu nặng`<br>• `Mày đay cấp thông thường`<br>• `Ban và phát ban khác (ghi rõ: ...)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Auto-điền từ mục 4 (`chan_doan_xac_dinh_cap`), hiển thị badge ở đầu trang. |
| **`ma_ho_so`** | Mã hồ sơ bệnh án mày đay cấp | string | null | Mã hệ thống tự sinh | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Hệ thống tự sinh, không cho sửa tay. |
| **`de_tai_ai`** | Phân loại lượt nghiên cứu Đề tài AI | string | null | • `Lần 1`<br>• `Lần 2`<br>• `Kiểm tra lại` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |

---

### A1. Hành chính (Tái sử dụng nguyên bộ biến với BA phản vệ)

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ho_ten`** | Họ và tên bệnh nhân | string | null | Chuỗi ký tự họ tên | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có** | Link với HIS. |
| **`ngay_sinh`** | Ngày tháng năm sinh | string | YYYY-MM-DD | Định dạng ngày hợp lệ | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`gioi_tinh`** | Giới tính | string | null | *TODO: Danh mục từ HIS?* | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`so_dien_thoai`** | Số điện thoại liên hệ | string | null | Chuỗi SĐT | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có** | Link với HIS. |
| **`nghe_nghiep`** | Nghề nghiệp | string | null | *TODO: Danh mục nghề nghiệp?* | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`dan_toc`** | Dân tộc | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`dia_chi_so_nha_thon_pho`** | Địa chỉ - Số nhà, thôn, phố | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`dia_chi_xa_phuong`** | Địa chỉ - Xã / Phường | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`dia_chi_tinh_tp`** | Địa chỉ - Tỉnh / Thành phố | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`noi_lam_viec`** | Nơi làm việc | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`bhyt_so_the`** | Số thẻ BHYT | string | null | Chuỗi thẻ BHYT | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`bhyt_gia_tri_den`** | Hạn thẻ BHYT đến ngày | string | YYYY-MM-DD | Định dạng ngày hợp lệ | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`nguoi_nha_ho_ten_dia_chi`** | Họ tên địa chỉ người nhà | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`nguoi_nha_so_dien_thoai`** | Số điện thoại người nhà | string | null | Chuỗi SĐT | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`thoi_diem_kham_lan_dau`** | Thời điểm khám lần đầu | string | YYYY-MM-DDTHH:mm:ss | Định dạng Datetime ISO 8601 | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`ngay_bat_dau_dieu_tri_ngoai_tru`** | Ngày bắt đầu điều trị ngoại trú | string | YYYY-MM-DD | Định dạng ngày hợp lệ | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`ngay_ket_thuc_dieu_tri_ngoai_tru`** | Ngày kết thúc điều trị ngoại trú | string | YYYY-MM-DD | Định dạng ngày hợp lệ | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |

---

### A2. Chẩn đoán tuyến trước & Kết quả bảo hiểm

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`chan_doan_tuyen_truoc`** | Chẩn đoán tuyến trước | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`chan_doan_ban_dau_phong_kham`** | Chẩn đoán ban đầu phòng khám | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`chan_doan_tai_kham`** | Lưới chẩn đoán tái khám | array (grid) | null | *TODO: Cấu trúc các cột trong bảng?* | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`benh_phu`** | Bệnh phụ | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`ket_qua_dieu_tri_bao_hiem`** | Kết quả điều trị theo bảo hiểm | object | null | • `Khỏi bệnh`<br>• `Đỡ`<br>• `Không đỡ`<br>• `Nặng hơn`<br>• `Chết`<br>• `Biến chứng (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |

---

### B0. Phần lưu trữ

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ngay_kham`** | Ngày khám bệnh | string | YYYY-MM-DD | Định dạng ngày hợp lệ | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tự động chọn theo HIS. |
| **`bac_si_kham`** | Bác sĩ khám | string | null | Tên tài khoản bác sĩ | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tự động điền theo tài khoản BS. |

---

### B1. Triệu chứng lâm sàng

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`thoi_gian_khoi_phat_gio`** | Thời gian khởi phát bệnh quy đổi về giờ | number | giờ | Số giờ $\ge 0$ (Quy ước: ngày $\times$ 24) | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Lưu chuẩn hoá về số giờ dù trên app chọn đơn vị ngày hay giờ. |

#### B1.1. Triệu chứng da/niêm mạc

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`trieu_chung_da_hien_tai`** | Triệu chứng da đợt hiện tại | object (checkbox + text) | null | Danh sách: `Phù mạch`, `Sẩn phù`, `Ban dát sẩn`, `Không có`, `Khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`tien_su_benh_nen_lien_quan_da`** | Tiền sử/bệnh nền da liên quan | object (checkbox + text) | null | Danh sách: `Mày đay mạn tính`, `Tiền sử phù mạch tái diễn`, `Rối loạn tế bào mast`, `Viêm da cơ địa`, `Không có`, `Khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`dien_bien_da`** | Diễn biến triệu chứng da | object | null | • `Lần đầu xuất hiện`<br>• `Lần thứ ...` (kèm: `Tăng nặng` / `Không đổi`) | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`hien_tai_co_san_phu`** | Hiện tại có sẩn phù | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`anh_san_phu`** | Ảnh sẩn phù | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tự động tick Có nếu BN có ảnh. |
| **`dac_diem_san_phu_cap`** | Lưới chi tiết dạng tổn thương sẩn phù | array (grid) | null | Mỗi dòng gồm:<br>• Dạng: `Hình vòng`, `Hình đứt đoạn`, `Hình bản đồ`, `Hình tròn`, `Dát sẩn`, `Khác (ghi rõ)`<br>• Kích thước: mm<br>• Thời gian tồn tại: *TODO: Đơn vị?*<br>• Thời điểm: `Ban ngày`, `Chiều tối`, `Đêm`, `Không cố định` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Bảng nhập liệu mỗi dòng = 1 dạng tổn thương được tick. |
| **`so_luong_san_phu`** | Số lượng sẩn phù (trong 24h nhiều nhất) | string | nốt | • `<20 nốt`<br>• `20-50 nốt`<br>• `>50 nốt` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tách từ bảng dạng tổn thương. `>50 nốt` là tiêu chí nhóm nặng. |
| **`muc_do_lan_rong_va_phan_bo_ton_thuong`** | Mức độ lan rộng & phân bố tổn thương | object | null | • Lan rộng: `>50% BSA`, `≤50% BSA`<br>• Phân bố: `Bất kỳ`, `Toàn thân`, `Đặc biệt (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tách từ bảng dạng tổn thương. `>50% BSA` là tiêu chí nhóm nặng. |
| **`hien_tai_co_phu_mach`** | Hiện tại có phù mạch | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`anh_phu_mach`** | Ảnh phù mạch | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tự động tick Có nếu BN có ảnh. |
| **`so_lan_phu_mach_tung_xay_ra`** | Số lần phù mạch từng xảy ra | integer | lần | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`so_lan_phu_mach_nang_can_vien`** | Số lần phù mạch nặng cần đến viện đợt này | integer | lần | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Link với BN nhập. Nếu $\ge 1$ là dấu hiệu nặng. |
| **`vi_tri_phu_mach`** | Vị trí phù mạch | object (checkbox + text) | null | Danh sách: `Một bên`, `Hai bên`, `Mi mắt`, `Lưỡi`, `Thanh quản`, `Môi`, `Bàn tay`, `Bàn chân`, `Các phần khác của mặt`, `Sinh dục`, `Vị trí khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox nhiều lựa chọn. |
| **`thoi_gian_ton_tai_phu_mach`** | Thời gian tồn tại trung bình của phù mạch | string | giờ | • `<1`<br>• `1-6`<br>• `6-12`<br>• `12-24`<br>• `24-48`<br>• `48-72`<br>• `>72`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Radio 1 lựa chọn. |

#### B1.2. Triệu chứng hô hấp

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`trieu_chung_ho_hap_co_khong`** | Có triệu chứng hô hấp hay không | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. Nếu 'Không' ẩn các trường phụ. |
| **`trieu_chung_ho_hap_hien_tai`** | Triệu chứng hô hấp đợt hiện tại | object (checkbox + text) | null | Danh sách: `Thở khò khè`, `Nghẹn họng`, `Khó thở / thở rít`, `Đau / tức ngực`, `Không có`, `Khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Chỉ hiện khi `trieu_chung_ho_hap_co_khong` = 'Có'. |
| **`tien_su_benh_nen_ho_hap`** | Tiền sử/bệnh nền hô hấp | object (checkbox + text) | null | Danh sách: `Hen phế quản`, `Bệnh phổi tắc nghẽn mạn tính`, `Viêm mũi dị ứng`, `Không có`, `Khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`dien_bien_ho_hap`** | Diễn biến hô hấp | object | null | • `Lần đầu xuất hiện`<br>• `Lần thứ ...` (kèm: `Tăng nặng` / `Không đổi`) | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Chỉ hiện khi `trieu_chung_ho_hap_co_khong` = 'Có'. |

#### B1.3. Triệu chứng tiêu hoá

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`trieu_chung_tieu_hoa_co_khong`** | Có triệu chứng tiêu hoá hay không | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. Nếu 'Không' ẩn các trường phụ. |
| **`trieu_chung_tieu_hoa_hien_tai`** | Triệu chứng tiêu hoá đợt hiện tại | object | null | • `Nôn: số lần ...`<br>• `Đau bụng quặn thắt`<br>• `Buồn nôn / tiêu chảy`<br>• `Không có`<br>• `Khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Chỉ hiện khi `trieu_chung_tieu_hoa_co_khong` = 'Có'. |
| **`tien_su_benh_nen_tieu_hoa`** | Tiền sử/bệnh nền tiêu hoá | object | null | • `Bệnh tiêu hoá mạn tính (ghi rõ)`<br>• `Không có`<br>• `Khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`dien_bien_tieu_hoa`** | Diễn biến triệu chứng tiêu hoá | object | null | • `Lần đầu xuất hiện`<br>• `Lần thứ ...` (kèm: `Tăng nặng` / `Không đổi`) | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Chỉ hiện khi `trieu_chung_tieu_hoa_co_khong` = 'Có'. |

---

### B2. Định hướng căn nguyên mày đay cấp

#### B2.1. Hoàn cảnh xuất hiện và tiền sử dị ứng

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`yeu_to_nghi_ngo_thuc_an`** | Yếu tố nghi ngờ đợt này - Thức ăn | object | null | • `Có (ghi rõ)`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`thoi_gian_tiep_xuc_khoi_phat_thuc_an`** | Thời gian tiếp xúc thức ăn đến khởi phát | number | *TODO: Đơn vị phút hay giờ?* | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`tien_su_phan_ung_yeu_to_thuc_an`** | Tiền sử phản ứng với thức ăn nghi ngờ | object | null | • `Có (ghi rõ biểu hiện)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`tien_su_phan_ve_di_ung_khac_thuc_an`** | Tiền sử phản vệ/dị ứng khác với thức ăn | object | null | • `Không`<br>• `Phản vệ (ghi rõ)`<br>• `Dị ứng (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`yeu_to_nghi_ngo_thuoc`** | Yếu tố nghi ngờ đợt này - Thuốc | object | null | • `Có (ghi rõ)`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`thoi_gian_tiep_xuc_khoi_phat_thuoc`** | Thời gian tiếp xúc thuốc đến khởi phát | number | *TODO: Đơn vị?* | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`tien_su_phan_ung_yeu_to_thuoc`** | Tiền sử phản ứng với thuốc nghi ngờ | object | null | • `Có (ghi rõ biểu hiện)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`tien_su_phan_ve_di_ung_khac_thuoc`** | Tiền sử phản vệ/dị ứng khác với thuốc | object | null | • `Không`<br>• `Phản vệ (ghi rõ)`<br>• `Dị ứng (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`yeu_to_nghi_ngo_con_trung_dot`** | Yếu tố nghi ngờ đợt này - Côn trùng đốt | object | null | • `Có (ghi rõ)`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`thoi_gian_tiep_xuc_khoi_phat_con_trung_dot`** | Thời gian côn trùng đốt đến khởi phát | number | *TODO: Đơn vị?* | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`tien_su_phan_ung_yeu_to_con_trung_dot`** | Tiền sử phản ứng với côn trùng đốt | object | null | • `Có (ghi rõ biểu hiện)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`tien_su_phan_ve_di_ung_khac_con_trung_dot`** | Tiền sử phản vệ/dị ứng khác côn trùng | object | null | • `Không`<br>• `Phản vệ (ghi rõ)`<br>• `Dị ứng (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`yeu_to_nghi_ngo_khac`** | Yếu tố nghi ngờ đợt này - Khác | object | null | • `Có (ghi rõ)`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`thoi_gian_tiep_xuc_khoi_phat_khac`** | Thời gian tiếp xúc yếu tố khác đến khởi phát | number | *TODO: Đơn vị?* | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`tien_su_phan_ung_yeu_to_khac`** | Tiền sử phản ứng với yếu tố khác | object | null | • `Có (ghi rõ biểu hiện)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`tien_su_phan_ve_di_ung_khac_khac`** | Tiền sử phản vệ/dị ứng khác với yếu tố khác | object | null | • `Không`<br>• `Phản vệ (ghi rõ)`<br>• `Dị ứng (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |

#### B2.2. Tình trạng nhiễm trùng liên quan

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`sot`** | Bệnh nhân có sốt hay không | object | null | • `Có: ... °C`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`sot_nhiet_do_c`** | Nhiệt độ sốt | number | °C | Số thực 1 chữ số thập phân (*TODO: Ngưỡng 35.0-43.0?*) | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Ô nhập số. |
| **`nhiem_trung_ho_hap`** | Nhiễm trùng đường hô hấp | object (checkbox + text) | null | • `Có`<br>• `Ghi rõ` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`lien_quan_thoi_gian_nhiem_trung_ho_hap`** | Mối liên quan thời gian nhiễm trùng hô hấp | object | null | • `Đồng thời`<br>• `Trước: cách ...`<br>• `Sau: cách ...` (*TODO: Đơn vị?*) | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi `nhiem_trung_ho_hap` được tick. |
| **`nhiem_trung_tieu_hoa`** | Nhiễm trùng đường tiêu hoá | object (checkbox + text) | null | • `Có`<br>• `Ghi rõ` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`lien_quan_thoi_gian_nhiem_trung_tieu_hoa`** | Mối liên quan thời gian nhiễm trùng tiêu hoá | object | null | • `Đồng thời`<br>• `Trước: cách ...`<br>• `Sau: cách ...` (*TODO: Đơn vị?*) | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi `nhiem_trung_tieu_hoa` được tick. |
| **`nhiem_trung_tiet_nieu`** | Nhiễm trùng đường tiết niệu | object (checkbox + text) | null | • `Có`<br>• `Ghi rõ` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`lien_quan_thoi_gian_nhiem_trung_tiet_nieu`** | Mối liên quan thời gian nhiễm trùng tiết niệu | object | null | • `Đồng thời`<br>• `Trước: cách ...`<br>• `Sau: cách ...` (*TODO: Đơn vị?*) | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi `nhiem_trung_tiet_nieu` được tick. |
| **`nhiem_trung_da`** | Nhiễm trùng tại da | object (checkbox + text) | null | • `Có`<br>• `Ghi rõ` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`lien_quan_thoi_gian_nhiem_trung_da`** | Mối liên quan thời gian nhiễm trùng da | object | null | • `Đồng thời`<br>• `Trước: cách ...`<br>• `Sau: cách ...` (*TODO: Đơn vị?*) | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi `nhiem_trung_da` được tick. |
| **`nhiem_trung_khac`** | Nhiễm trùng cơ quan khác | object (checkbox + text) | null | • `Có`<br>• `Ghi rõ` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`lien_quan_thoi_gian_nhiem_trung_khac`** | Mối liên quan thời gian nhiễm trùng khác | object | null | • `Đồng thời`<br>• `Trước: cách ...`<br>• `Sau: cách ...` (*TODO: Đơn vị?*) | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi `nhiem_trung_khac` được tick. |

---

### B3. Cận lâm sàng

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`wbc`** | Số lượng bạch cầu WBC | number | *TODO: Đơn vị (G/L?)* | *TODO: Khoảng hợp lệ?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`eo`** | Bạch cầu ái toan Eosinophil | number | *TODO: Đơn vị (G/L hay %?)* | *TODO: Khoảng hợp lệ?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`ba_bach_cau`** | Bạch cầu ái kiềm Basophil | number | *TODO: Đơn vị (G/L hay %?)* | *TODO: Khoảng hợp lệ?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`crp`** | Định lượng CRP | number | *TODO: Đơn vị (mg/L hay mg/dL?)* | *TODO: Khoảng hợp lệ?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`mau_lang_1h`** | Tốc độ máu lắng 1 giờ | number | *TODO: Đơn vị (mm?)* | *TODO: Khoảng hợp lệ?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`mau_lang_2h`** | Tốc độ máu lắng 2 giờ | number | *TODO: Đơn vị (mm?)* | *TODO: Khoảng hợp lệ?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`ft3`** | Hormone Free T3 | number | *TODO: Đơn vị (pmol/L hay pg/mL?)* | *TODO: Khoảng hợp lệ?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`ft4`** | Hormone Free T4 | number | *TODO: Đơn vị (pmol/L hay ng/dL?)* | *TODO: Khoảng hợp lệ?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`tsh`** | Hormone TSH | number | *TODO: Đơn vị (uIU/mL?)* | *TODO: Khoảng hợp lệ?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`ige_toan_phan`** | Nồng độ IgE toàn phần | number | *TODO: Đơn vị (UI/mL?)* | *TODO: Khoảng hợp lệ?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`anti_tpo`** | Kháng thể Anti-TPO | number | *TODO: Đơn vị (UI/mL?)* | *TODO: Khoảng hợp lệ?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`ana_hep2`** | Kháng thể ANA HEp-2 | string | null | *TODO: Danh mục kết quả (Âm tính / Dương tính / Hiệu giá)?* | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`sieu_am_tuyen_giap`** | Kết quả siêu âm tuyến giáp | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`xet_nghiem_khac`** | Xét nghiệm khác | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`can_lam_sang_chu_y_cap`** | Cận lâm sàng chú ý | string | null | Văn bản tự do | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Textarea tự do. |

---

### B4. Chẩn đoán xác định

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`chan_doan_xac_dinh_cap`** | Chẩn đoán xác định thể mày đay cấp | object | null | • `Mày đay cấp có dấu hiệu nặng`<br>• `Mày đay cấp thông thường`<br>• `Ban và phát ban khác (ghi rõ: ...)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có** | BS nhập. Trường bắt buộc. |
| **`dau_hieu_nang_chi_tiet`** | Chi tiết dấu hiệu nặng (ít nhất 1 tiêu chí) | array (checkbox) | null | • `Phù mạch đáng kể`<br>• `Sẩn phù lan rộng >50% BSA hoặc >50 nốt/24h`<br>• `Triệu chứng hô hấp nhưng chưa đủ tiêu chuẩn phản vệ`<br>• `Triệu chứng tiêu hóa nhưng chưa đủ tiêu chuẩn phản vệ` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi chọn `Mày đay cấp có dấu hiệu nặng`. Hệ thống auto-gợi ý. |
| **`can_nguyen_yeu_to_nghi_ngo`** | Căn nguyên hoặc yếu tố nghi ngờ | object | null | • `Chưa xác định`<br>• `Thức ăn (ghi rõ)`<br>• `Thuốc (ghi rõ)`<br>• `Nhiễm trùng (ghi rõ)`<br>• `Khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |

---

### B5. Bệnh sử - Tiền sử

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`da_dieu_tri_dot_nay`** | Đã điều trị bệnh đợt này hay chưa | string | null | • `Có`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Link với BN nhập. Nếu 'Có' mở bảng danh sách thuốc. |
| **`danh_sach_thuoc_da_dieu_tri`** | Danh sách thuốc đã điều trị đợt này | array (grid) | null | Cột: `Tên thuốc`, `Liều dùng`, `Thời gian dùng`, `Tuân thủ (Đều/Không đều/Không rõ)`, `Đáp ứng (Hoàn toàn/Một phần/Không đáp ứng/Không rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi `da_dieu_tri_dot_nay` = 'Có'. |
| **`so_lan_may_day_cap_truoc_do`** | Số lần bị mày đay cấp trước đó | integer | lần | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`tuoi_lan_dau_bi_benh`** | Tuổi lần đầu bị bệnh mày đay | integer | tuổi | *TODO: Khoảng tuổi (0-120)?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`dot_gan_nhat_cach`** | Đợt gần nhất cách thời điểm hiện tại | string | *TODO: Đơn vị?* | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`thoi_gian_keo_dai_trung_binh_moi_dot`** | Thời gian kéo dài trung bình mỗi đợt bệnh | string | *TODO: Đơn vị?* | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`tien_su_gia_dinh_cap`** | Tiền sử gia đình mắc bệnh liên quan | object | null | • `Có (ghi rõ: thành viên – bệnh lý – diễn biến)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |

---

### B6. Theo dõi điều trị

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`dien_dieu_tri`** | Diện điều trị | string | null | • `Ngoại trú`<br>• `Nội trú` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Auto-gợi ý 'Nội trú' nếu có dấu hiệu nặng. Mở bảng 6a hoặc 6b tương ứng. |
| **`theo_doi_ngoai_tru_lan_kham`** | Lưới theo dõi ngoại trú theo lần khám | array (grid) | null | Cột: `Lần khám`, `Ngày khám`, `BS khám`, `Diễn biến bệnh`, `Phương án điều trị (Tăng/Giảm/Giữ/Ngừng + Lý do)`, `Thuốc`, `Liều`, `Thời gian`, `Ghi chú CLS` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi `dien_dieu_tri` = 'Ngoại trú'. |
| **`ket_qua_cuoi_dot_ngoai_tru`** | Kết quả cuối đợt điều trị ngoại trú | string | null | • `Khỏi bệnh`<br>• `Nhập viện`<br>• `Chuyển mày đay mạn tính` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi `dien_dieu_tri` = 'Ngoại trú'. Nếu chọn 'Nhập viện' tự động mở bảng 6b. |
| **`theo_doi_noi_tru_ngay_dieu_tri`** | Lưới theo dõi nội trú theo ngày | array (grid) | null | Cột: `Ngày điều trị`, `Ngày`, `BS khám`, `Diễn biến sẩn phù`, `Diễn biến phù mạch`, `Cơ quan khác`, `Dấu hiệu sinh tồn (Nhiệt độ, HA, Mạch, Nhịp thở, SpO2)`, `Thuốc`, `Liều`, `Đường dùng`, `Thời gian`, `Ghi chú CLS` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi `dien_dieu_tri` = 'Nội trú'. |
| **`ket_qua_cuoi_dot_noi_tru`** | Kết quả cuối đợt điều trị nội trú | object | null | • `Ra viện`<br>• `Chuyển viện`<br>• `Khác (ghi rõ)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi `dien_dieu_tri` = 'Nội trú'. |