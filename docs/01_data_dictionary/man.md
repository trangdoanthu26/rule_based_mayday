Dưới đây là việc chuyển đổi toàn bộ đặc tả **BỆNH ÁN MÀY ĐAY MẠN TÍNH** (Bản chốt chuyên môn) thành:
1. **`docs/data_dictionary/man.md`**: Từ điển dữ liệu dạng Markdown chuẩn, giữ nguyên 100% tên biến của Bác sĩ, không suy đoán.
2. **`schema/man_schema.json`**: JSON Schema Draft-07 kỹ thuật được ánh xạ trực tiếp từ file từ điển.
3. **Danh sách câu hỏi `TODO`**: Các điểm cần làm rõ với Bác sĩ chủ nhiệm đề tài.

---

# TẬP TIN 1: `docs/data_dictionary/man.md`
*(Bệnh án điều trị Mày đay mạn tính - Bản chốt 11.9.2026 & Bổ sung 22.9.2026)*

## Quy ước dữ liệu chung
* **Missing**: `null` (Chưa thu thập / Để trống).
* **Unknown**: Chuỗi `"unknown"` hoặc số `-1` (Đã hỏi nhưng Bác sĩ / Bệnh nhân không biết / không rõ).
* **Not applicable**: `"N/A"` (Không áp dụng cho trường hợp này).

---

### A0. Mã hồ sơ & Phân loại (Đầu trang bệnh án)

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ma_benh_nhan`** | Mã bệnh nhân HIS | string | null | Regex mã bệnh nhân HIS | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có** | Link với HIS khi đăng ký khám, không cho sửa tay. |
| **`chan_doan_chinh`** | Chẩn đoán phân loại thể bệnh mày đay mạn (trang bìa) | object (checkbox nhiều lựa chọn) | null | • Nhóm CSU: `Mày đay tự phát mạn tính (CSU)` kèm thể: `Type I`, `Type IIb`, `Chồng lấp`, `Không xác định`<br>• Nhóm CIndU: `Mày đay cảm ứng mạn tính (CIndU)` kèm thể: `Da vẽ nổi`, `Mày đay cholinergic`, `Mày đay do lạnh`, `Mày đay adrenergic`, `Mày đay do ánh sáng`, `Mày đay do nước`, `Khác (ghi rõ: ...)`<br>• `Phù mạch đơn thuần` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Cho phép tick đồng thời CSU và CIndU (CSU đồng mắc CIndU). Hiển thị dạng badge ở đầu trang. Hệ thống auto-gợi ý từ mục 2.4 và mục 4. |
| **`ma_ho_so`** | Mã hồ sơ bệnh án tự sinh | string | null | Mã hệ thống tự sinh | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Không cho sửa tay. |
| **`de_tai_ai`** | Phân loại lượt nghiên cứu Đề tài AI | string | null | • `Lần 1`<br>• `Lần 2`<br>• `Kiểm tra lại` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |

---

### A1. Hành chính (Trang BM-10)

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ho_ten`** | Họ và tên bệnh nhân | string | null | Chuỗi ký tự họ tên | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có** | Link với HIS. |
| **`ngay_sinh`** | Ngày tháng năm sinh | string | YYYY-MM-DD | Định dạng ngày hợp lệ | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
| **`gioi_tinh`** | Giới tính | string | null | *TODO: Danh mục từ HIS (Nam, Nữ, Khác)?* | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |
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
| **`ngay_ket_thuc_dieu_tri_ngoai_tru`** | Ngày kết thúc điều trị ngoại trú | string | YYYY-MM-DD | Định dạng ngày hợp lệ $\ge$ ngày bắt đầu | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với HIS. |

---

### A2. Chẩn đoán tuyến trước & Kết quả điều trị bảo hiểm

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`chan_doan_tuyen_truoc`** | Chẩn đoán tuyến trước | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`chan_doan_ban_dau_phong_kham`** | Chẩn đoán ban đầu phòng khám | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`chan_doan_tai_kham`** | Bảng lưới chẩn đoán tái khám (lần 1-4) | array (grid) | null | Cột: `Lần tái khám` (1-4), `Chẩn đoán` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập, có nút thêm/xoá dòng. |
| **`benh_phu`** | Bệnh phụ kèm theo | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`ket_qua_dieu_tri_bao_hiem`** | Kết quả điều trị theo bảo hiểm | object | null | • `Khỏi bệnh`<br>• `Đỡ`<br>• `Không đỡ`<br>• `Nặng hơn`<br>• `Chết`<br>• `Biến chứng (ghi rõ: ...)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |

---

### B1. Phần lưu trữ

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ngay_kham`** | Ngày khám bệnh | string | YYYY-MM-DD | Định dạng ngày hợp lệ | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tự động chọn theo HIS. |
| **`bac_si_kham`** | Bác sĩ khám | string | null | Tên tài khoản bác sĩ | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tự động điền theo tài khoản BS đăng nhập. |

---

### B2. Định hướng chẩn đoán căn nguyên

#### B2.1. Thời gian diễn biến và biểu hiện trong quá trình bệnh

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`thoi_gian_khoi_phat_tuan`** | Thời gian từ khi khởi phát bệnh | number | tuần | $\ge 0$ (Mạn tính khi $> 6$ tuần) | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Link với BN nhập, BS chỉnh sửa được. |
| **`bieu_hien_qua_trinh_benh`** | Biểu hiện trong quá trình bệnh | string | null | • `Chỉ sẩn phù`<br>• `Chỉ phù mạch`<br>• `Sẩn phù + phù mạch` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. Điều khiển hiển thị mục 2.2 và 2.3. |
| **`uu_the_san_phu_va_phu_mach`** | Ưu thế xuất hiện thường xuyên hơn | string | null | • `Sẩn phù`<br>• `Phù mạch`<br>• `Tương đương` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Chỉ hiện khi `bieu_hien_qua_trinh_benh` = 'Sẩn phù + phù mạch'. |
| **`trieu_chung_xuat_hien_truoc`** | Triệu chứng nào xuất hiện trước | string | null | • `Sẩn phù`<br>• `Phù mạch`<br>• `Đồng thời` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Chỉ hiện khi có cả hai triệu chứng. |

#### B2.2. Đặc điểm sẩn phù (Hiện khi tick Sẩn phù hoặc Sẩn phù + phù mạch)

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`hoan_canh_xuat_hien_san_phu`** | Hoàn cảnh xuất hiện sẩn phù | object (checkbox nhiều lựa chọn) | null | • `1. Một cách ngẫu nhiên`<br>• `2. Khi có các yếu tố kích thích`: 2.1 Cọ xát/gãi, 2.2 Nóng/vận động/cay nóng/xúc động, 2.3 Tì đè/vật nặng, 2.4 Vật cụ thể (ghi rõ: ...), 2.5 Lạnh, 2.6 Nóng, 2.7 Rung, 2.8 Ánh sáng, 2.9 Nước, 2.10 Khác (ghi rõ: ...)<br>• `Cả hai: ngẫu nhiên và khi có kích thích` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Link với BN nhập, BS sửa được. Cho phép chọn nhiều yếu tố (đồng mắc CIndU). |
| **`trong_dot_co_san_phu`** | Trong đợt bệnh này có sẩn phù | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Khái niệm trong đợt bệnh của BA mạn. |
| **`anh_san_phu`** | Ảnh sẩn phù | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Tự động tick Có nếu BN có ảnh. |
| **`dac_diem_san_phu`** | Lưới đặc điểm tổn thương sẩn phù | object | null | • Dạng: `Hình vòng (bờ rõ)`, `Hình đứt đoạn (bờ rõ)`, `Hình bản đồ (bờ rõ)`, `Hình tròn (bờ rõ)`, `Dát sẩn (bờ không rõ)`, `Hình dải`, `Hình chấm` (Kích thước: Đồng đều / Không đồng đều ... mm), `Hình halo` (Kích thước: Đồng đều / Không đồng đều ... mm)<br>• Thời gian tồn tại TB: *TODO: Đơn vị?*<br>• Thời điểm: `Ban ngày`, `Chiều tối`, `Đêm`, `Không cố định`<br>• Số lượng: `<20 nốt`, `20-50 nốt`, `>50 nốt`<br>• Vị trí: `Bất kỳ`, `Đặc biệt (ghi rõ)`<br>• Tình trạng dùng thuốc: `Không dùng`, `Có dùng` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Thêm cột tình trạng dùng thuốc khi quan sát theo chốt 22.9. |
| **`yeu_to_lam_nang_san_phu`** | Yếu tố làm nặng sẩn phù | object (checkbox nhiều lựa chọn) | null | • `Không có`<br>• `Stress`<br>• `Chu kỳ kinh nguyệt`<br>• `Nhiễm trùng`<br>• `NSAIDs`<br>• `Thức ăn (ghi rõ: ...)`<br>• `Thuốc khác (ghi rõ: ...)`<br>• `Khác (ghi rõ: ...)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Checkbox nhiều lựa chọn. |

#### B2.3. Đặc điểm phù mạch (Hiện khi tick Phù mạch hoặc Sẩn phù + phù mạch)

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`trong_dot_co_phu_mach`** | Trong đợt bệnh này có phù mạch | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Tự động hiện theo câu hỏi trước. |
| **`anh_phu_mach`** | Ảnh phù mạch | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Nút tải ảnh lên. |
| **`so_lan_phu_mach_tung_xay_ra`** | Số lần phù mạch từng xảy ra | integer | lần | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Number input. |
| **`so_lan_phu_mach_nang_can_vien`** | Số lần phù mạch nặng cần vào viện đợt này | integer | lần | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Number input. |
| **`vi_tri_phu_mach`** | Vị trí phù mạch | object (checkbox) | null | • `Một bên`<br>• `Hai bên`<br>• `Mi mắt`<br>• `Lưỡi`<br>• `Môi`<br>• `Các phần khác của mặt`<br>• `Thanh quản`<br>• `Bàn tay`<br>• `Bàn chân`<br>• `Sinh dục`<br>• `Vị trí khác (ghi rõ: ...)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Checkbox nhiều lựa chọn. |
| **`hoan_canh_xuat_hien_phu_mach`** | Hoàn cảnh xuất hiện phù mạch | object (checkbox) | null | • `1. Một cách ngẫu nhiên`<br>• `2. Sau yếu tố kích thích`: 2.1 Áp lực/tì đè, 2.2 Sau ngủ dậy, 2.3 Lạnh, 2.4 Khác (ghi rõ: ...)<br>• `3. Sau khi dùng thuốc`: 3.1 NSAIDs, 3.2 Ức chế men chuyển, 3.3 Opioids, 3.4 Thuốc khác (ghi rõ: ...) | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Cấu trúc hóa theo mã quy ước phần B. |
| **`thoi_gian_ton_tai_phu_mach`** | Thời gian tồn tại trung bình của phù mạch | object | giờ | Lựa chọn: `<1 giờ`, `1-6 giờ`, `6-12 giờ`, `12-24 giờ`, `24-48 giờ`, `48-72 giờ`, `>72 giờ`, `Không rõ`<br>Kèm: `Tình trạng dùng thuốc khi quan sát` (Không dùng / Có dùng) | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | **Có điều kiện** | Lưu kèm trạng thái có/không dùng thuốc. |
| **`yeu_to_lam_nang_phu_mach`** | Yếu tố làm nặng phù mạch | object (checkbox) | null | • `Không có`<br>• `Stress`<br>• `Nhiễm trùng`<br>• `NSAIDs`<br>• `Kinh nguyệt`<br>• `Thuốc (ghi rõ: ...)`<br>• `Thức ăn (ghi rõ: ...)`<br>• `Khác (ghi rõ: ...)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Checkbox nhiều lựa chọn. |

#### B2.4. Test đặc hiệu (ASST cho CSU và Test kích thích cho CIndU)

##### 1. Nhóm ASST (Autologous Serum Skin Test)
| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`luu_huyet_thanh`** | Có lưu huyết thanh hay không | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Điều kiện bắt buộc của đề tài. |
| **`ngay_thuc_hien_uas7_luu_huyet_thanh`** | Ngày thực hiện UAS7 và lưu huyết thanh | string | YYYY-MM-DD | Định dạng ngày hợp lệ | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Đánh giá cùng ngày lưu huyết thanh. |
| **`asst_ket_qua`** | Kết quả test lẩy da huyết thanh tự thân ASST | string | null | • `(+)`<br>• `(−)`<br>• `(+/−)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Dấu ấn phân type CSU. |
| **`ngung_khang_histamine_truoc_asst`** | Tình trạng ngừng kháng histamine trước test | string | null | • `Không sử dụng`<br>• `.... ngày` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Cần ngừng $\ge 8$ ngày. |
| **`thoi_gian_ngung_khang_histamine_asst`** | Số ngày ngừng kháng histamine trước ASST | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi chọn '.... ngày'. |
| **`ngung_corticoid_truoc_asst`** | Tình trạng ngừng corticoid trước test | string | null | • `Không sử dụng`<br>• `.... ngày` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Cần ngừng $\ge 30$ ngày (1 tháng). |
| **`thoi_gian_ngung_corticoid_asst`** | Số ngày ngừng corticoid trước ASST | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi chọn '.... ngày'. |
| **`ten_ngung_thuoc_khac_truoc_asst`** | Tên thuốc khác cần ngừng trước ASST | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Ô nhập chữ. |
| **`thoi_gian_ngung_thuoc_khac_asst`** | Số ngày ngừng thuốc khác trước ASST | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi có thuốc khác. |
| **`asst_duong_kinh_histamin`** | Đường kính sẩn chứng dương Histamin | number | mm | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`asst_duong_kinh_nacl`** | Đường kính sẩn chứng âm NaCl 0.9% | number | mm | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`asst_duong_kinh_huyet_thanh`** | Đường kính sẩn huyết thanh tự thân | number | mm | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`san_phu_asst`** | Xuất hiện sẩn phù tại vị trí tiêm | string | null | • `có`<br>• `không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox/radio. |
| **`do_asst`** | Xuất hiện quầng đỏ tại vị trí tiêm | string | null | • `có`<br>• `không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox/radio. |
| **`asst_dau_nrs`** | Mức độ đau theo thang NRS tại chỗ test | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang điểm đau 0-10. |
| **`asst_ngua_nrs`** | Mức độ ngứa theo thang NRS tại chỗ test | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang điểm ngứa 0-10. |
| **`asst_bong_rat_nrs`** | Mức độ bỏng rát theo thang NRS tại chỗ test | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang điểm bỏng rát 0-10. |

##### 2. Nhóm Test Da vẽ nổi (FricTest - Dermographism)
| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`da_ve_noi_ket_qua`** | Kết quả test da vẽ nổi FricTest | string | null | • `(+)`<br>• `(−)`<br>• `(+/−)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tiêu chuẩn chẩn đoán Da vẽ nổi. |
| **`ngung_khang_histamine_truoc_fric`** | Ngừng kháng histamine trước test | string | null | • `Không sử dụng`<br>• `.... ngày` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/dropdown. |
| **`thoi_gian_ngung_khang_histamine_fric`** | Số ngày ngừng kháng histamine | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi chọn '.... ngày'. |
| **`ngung_corticoid_truoc_fric`** | Ngừng corticoid trước test | string | null | • `Không sử dụng`<br>• `.... ngày` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/dropdown. |
| **`thoi_gian_ngung_corticoid_fric`** | Số ngày ngừng corticoid | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi chọn '.... ngày'. |
| **`ten_ngung_thuoc_khac_truoc_fric`** | Tên thuốc khác cần ngừng | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Ô nhập chữ. |
| **`thoi_gian_ngung_thuoc_khac_fric`** | Số ngày ngừng thuốc khác | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi có thuốc khác. |
| **`fric_score`** | Điểm ngưỡng FricTest | number | điểm | *TODO: Bác sĩ cho biết dải điểm Fric (0-4)?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Number input. |
| **`san_phu_fric`** | Xuất hiện sẩn phù FricTest | string | null | • `có`<br>• `không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox/radio. |
| **`do_fric`** | Xuất hiện quầng đỏ FricTest | string | null | • `có`<br>• `không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox/radio. |
| **`da_ve_noi_dau_nrs`** | Điểm đau NRS | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang NRS. |
| **`da_ve_noi_ngua_nrs`** | Điểm ngứa NRS | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang NRS. |
| **`da_ve_noi_bong_rat_nrs`** | Điểm bỏng rát NRS | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang NRS. |

##### 3. Nhóm Test Cholinergic (Do nóng / gắng sức)
| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`cholinergic_ket_qua`** | Kết quả test kích thích Cholinergic | string | null | • `(+)`<br>• `(−)`<br>• `(+/−)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tiêu chuẩn chẩn đoán Cholinergic. |
| **`ngung_khang_histamine_truoc_cholinergic`** | Ngừng kháng histamine trước test | string | null | • `Không sử dụng`<br>• `.... ngày` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/dropdown. |
| **`thoi_gian_ngung_khang_histamine_cholinergic`** | Số ngày ngừng kháng histamine | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi chọn '.... ngày'. |
| **`ngung_corticoid_truoc_cholinergic`** | Ngừng corticoid trước test | string | null | • `Không sử dụng`<br>• `.... ngày` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/dropdown. |
| **`thoi_gian_ngung_corticoid_cholinergic`** | Số ngày ngừng corticoid | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi chọn '.... ngày'. |
| **`ten_ngung_thuoc_khac_truoc_cholinergic`** | Tên thuốc khác cần ngừng | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Ô nhập chữ. |
| **`thoi_gian_ngung_thuoc_khac_cholinergic`** | Số ngày ngừng thuốc khác | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi có thuốc khác. |
| **`cholinergic_xuat_hien_sau_phut`** | Thời gian xuất hiện tổn thương sau kích thích | number | phút | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Đọc kết quả ngay và sau 10 phút. |
| **`san_phu_cholinergic`** | Xuất hiện sẩn phù nhỏ 1-3mm | string | null | • `có`<br>• `không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Đặc trưng của cholinergic. |
| **`do_cholinergic`** | Xuất hiện quầng đỏ | string | null | • `có`<br>• `không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox/radio. |
| **`cholinergic_dau_nrs`** | Điểm đau NRS | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang NRS. |
| **`cholinergic_ngua_nrs`** | Điểm ngứa NRS | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang NRS. |
| **`cholinergic_bong_rat_nrs`** | Điểm bỏng rát NRS | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang NRS. |

##### 4. Nhóm Test Lạnh (TempTest & Cục đá - Cold Urticaria)
| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`lanh_temptest_ket_qua`** | Kết quả test lạnh bằng thiết bị TempTest | string | null | • `(+)`<br>• `(−)`<br>• `(+/−)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Xác định ngưỡng nhiệt độ. |
| **`ngung_khang_histamine_truoc_lanh_temptest`** | Ngừng kháng histamine trước test | string | null | • `Không sử dụng`<br>• `.... ngày` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/dropdown. |
| **`thoi_gian_ngung_khang_histamine_lanh_temptest`** | Số ngày ngừng kháng histamine | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi chọn '.... ngày'. |
| **`ngung_corticoid_truoc_lanh_temptest`** | Ngừng corticoid trước test | string | null | • `Không sử dụng`<br>• `.... ngày` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/dropdown. |
| **`thoi_gian_ngung_corticoid_lanh_temptest`** | Số ngày ngừng corticoid | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi chọn '.... ngày'. |
| **`ten_ngung_thuoc_khac_truoc_lanh_temptest`** | Tên thuốc khác cần ngừng | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Ô nhập chữ. |
| **`thoi_gian_ngung_thuoc_khac_lanh_temptest`** | Số ngày ngừng thuốc khác | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi có thuốc khác. |
| **`lanh_temptest_nguong_nhiet_do`** | Ngưỡng nhiệt độ gây xuất hiện sẩn | number | °C | *TODO: Dải nhiệt độ (4 - 25°C)?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Number input. |
| **`san_phu_lanh_temptest`** | Xuất hiện sẩn phù TempTest | string | null | • `có`<br>• `không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox/radio. |
| **`do_lanh_temptest`** | Xuất hiện quầng đỏ TempTest | string | null | • `có`<br>• `không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox/radio. |
| **`lanh_temptest_dau_nrs`** | Điểm đau NRS | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang NRS. |
| **`lanh_temptest_ngua_nrs`** | Điểm ngứa NRS | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang NRS. |
| **`lanh_temptest_bong_rat_nrs`** | Điểm bỏng rát NRS | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang NRS. |
| **`lanh_cucda_ket_qua`** | Kết quả test chườm cục đá (Ice cube test) | string | null | • `(+)`<br>• `(−)`<br>• `(+/−)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Test chuẩn đoán mày đay do lạnh. |
| **`ngung_khang_histamine_truoc_lanh_cucda`** | Ngừng kháng histamine trước test | string | null | • `Không sử dụng`<br>• `.... ngày` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/dropdown. |
| **`thoi_gian_ngung_khang_histamine_lanh_cucda`** | Số ngày ngừng kháng histamine | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi chọn '.... ngày'. |
| **`ngung_corticoid_truoc_lanh_cucda`** | Ngừng corticoid trước test | string | null | • `Không sử dụng`<br>• `.... ngày` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/dropdown. |
| **`thoi_gian_ngung_corticoid_lanh_cucda`** | Số ngày ngừng corticoid | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi chọn '.... ngày'. |
| **`ten_ngung_thuoc_khac_truoc_lanh_cucda`** | Tên thuốc khác cần ngừng | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Ô nhập chữ. |
| **`thoi_gian_ngung_thuoc_khac_lanh_cucda`** | Số ngày ngừng thuốc khác | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi có thuốc khác. |
| **`lanh_cucda_xuat_hien_sau_phut`** | Thời gian xuất hiện sau khi bỏ đá ra | number | phút | $\ge 0$ (thường sau 10 phút) | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Number input. |
| **`san_phu_lanh_cucda`** | Xuất hiện sẩn phù test cục đá | string | null | • `có`<br>• `không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox/radio. |
| **`do_lanh_cucda`** | Xuất hiện quầng đỏ test cục đá | string | null | • `có`<br>• `không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox/radio. |
| **`lanh_cucda_dau_nrs`** | Điểm đau NRS | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang NRS. |
| **`lanh_cucda_ngua_nrs`** | Điểm ngứa NRS | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang NRS. |
| **`lanh_cucda_bong_rat_nrs`** | Điểm bỏng rát NRS | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang NRS. |

##### 5. Nhóm Test Áp lực chậm (Delayed Pressure Urticaria)
| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ap_luc_cham_ket_qua`** | Kết quả test áp lực chậm (treo tạ) | string | null | • `(+)`<br>• `(−)`<br>• `(+/−)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Đọc kết quả sau 4-8 giờ. |
| **`ngung_khang_histamine_truoc_ap_luc_cham`** | Ngừng kháng histamine trước test | string | null | • `Không sử dụng`<br>• `.... ngày` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/dropdown. |
| **`thoi_gian_ngung_khang_histamine_ap_luc_cham`** | Số ngày ngừng kháng histamine | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi chọn '.... ngày'. |
| **`ngung_corticoid_truoc_ap_luc_cham`** | Ngừng corticoid trước test | string | null | • `Không sử dụng`<br>• `.... ngày` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/dropdown. |
| **`thoi_gian_ngung_corticoid_ap_luc_cham`** | Số ngày ngừng corticoid | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi chọn '.... ngày'. |
| **`ten_ngung_thuoc_khac_truoc_ap_luc_cham`** | Tên thuốc khác cần ngừng | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Ô nhập chữ. |
| **`thoi_gian_ngung_thuoc_khac_ap_luc_cham`** | Số ngày ngừng thuốc khác | integer | ngày | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi có thuốc khác. |
| **`ap_luc_cham_nguong_ap_luc`** | Ngưỡng áp lực gây tổn thương | number | *TODO: Đơn vị g/mm2 hay kg?* | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Number input. |
| **`san_phu_ap_luc_cham`** | Xuất hiện sẩn phù sau áp lực | string | null | • `có`<br>• `không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox/radio. |
| **`do_ap_luc_cham`** | Xuất hiện quầng đỏ sau áp lực | string | null | • `có`<br>• `không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox/radio. |
| **`ap_luc_cham_dau_nrs`** | Điểm đau NRS | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang NRS. |
| **`ap_luc_cham_ngua_nrs`** | Điểm ngứa NRS | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang NRS. |
| **`ap_luc_cham_bong_rat_nrs`** | Điểm bỏng rát NRS | number | điểm | 0 - 10 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Thang NRS. |

##### 6. Nhóm Test Adrenergic, Ánh sáng, Nước & Khác
| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`adrenergic_ket_qua`** | Kết quả test Adrenergic | string | null | • `(+)`<br>• `(−)`<br>• `(+/−)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tiêu chuẩn mày đay adrenergic. |
| **`adrenergic_xuat_hien_sau_phut`** | Thời gian xuất hiện sau tiêm | number | phút | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Number input. |
| **`san_phu_adrenergic`** / **`do_adrenergic`** | Biểu hiện sẩn phù / đỏ | string | null | • `có`<br>• `không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox/radio. |
| **`anh_sang_ket_qua`** | Kết quả test ánh sáng mặt trời | string | null | • `(+)`<br>• `(−)`<br>• `(+/−)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tiêu chuẩn mày đay do ánh sáng. |
| **`anh_sang_buoc_song_duong_tinh_nm`** | Bước sóng gây dương tính | number | nm | *TODO: Dải bước sóng UV (290 - 700 nm)?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Number input. |
| **`san_phu_anh_sang`** / **`do_anh_sang`** | Biểu hiện sẩn phù / đỏ | string | null | • `có`<br>• `không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox/radio. |
| **`nuoc_ket_qua`** | Kết quả test tiếp xúc với nước (Aquagenic) | string | null | • `(+)`<br>• `(−)`<br>• `(+/−)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Tiêu chuẩn mày đay do nước. |
| **`nuoc_xuat_hien_sau_phut`** | Thời gian xuất hiện sau đắp gạc nước | number | phút | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Number input. |
| **`san_phu_nuoc`** / **`do_nuoc`** | Biểu hiện sẩn phù / đỏ | string | null | • `có`<br>• `không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox/radio. |
| **`khac_ten_test`** | Tên test kích thích khác | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | VD: Rung, TempTest nóng. |
| **`khac_phuong_phap_vi_tri_thoi_gian`** | Mô tả phương pháp – vị trí – thời gian | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Textarea. |
| **`khac_ket_qua`** | Kết quả test khác | string | null | • `(+)`<br>• `(−)`<br>• `(+/−)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio/dropdown. |
| **`khac_thong_so`** | Thông số ngưỡng kích thích khác | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Input text. |
| **`san_phu_khac`** / **`do_khac`** | Biểu hiện sẩn phù / đỏ | string | null | • `có`<br>• `không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Checkbox/radio. |

*(Lưu ý: Tất cả các test đều có các trường phụ ngừng kháng histamine, ngừng corticoid và ngừng thuốc khác tương tự như trên).*

---

### B2.5. Thang điểm UAS7 & AAS7 (Mục 1.3)

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`uas7_bang_hang_ngay`** | Bảng lưới 7 ngày chấm điểm ngứa và sẩn phù | array (grid) | null | 7 dòng (Ngày 1-7), mỗi ngày gồm 2 cột:<br>• `ISS7` (Ngứa: 0, 1, 2, 3)<br>• `HSS7` (Sẩn phù: 0, 1, 2, 3) | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với app BN nhập tại nhà 7 ngày trước làm test ASST. |
| **`iss7_tong`** | Tổng điểm ngứa 7 ngày | integer | điểm | 0 - 21 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Auto tính từ bảng lưới. |
| **`hss7_tong`** | Tổng điểm sẩn phù 7 ngày | integer | điểm | 0 - 21 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Auto tính từ bảng lưới. |
| **`uas7_tong`** | Tổng điểm hoạt lực bệnh mày đay UAS7 | integer | điểm | 0 - 42 (`iss7_tong + hss7_tong`) | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Auto tính, chỉ số vàng đánh giá mức độ nặng của CSU. |
| **`aas7_bang_hang_ngay`** | Bảng lưới 7 ngày chấm điểm phù mạch AAS7 | array (grid) | null | 7 dòng (Ngày 1-7): sàng lọc có sưng phù (Có/Không) + 5 câu 0-3 điểm (tối đa 15 điểm/ngày) | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với app BN. |
| **`aas7_tong`** | Tổng điểm phù mạch AAS7 trong 7 ngày | integer | điểm | 0 - 105 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Auto tính điểm tổng. |

---

### B2.6. Đánh giá chất lượng cuộc sống (DLQI, UCT, AECT)

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ngay_thuc_hien_dlqi`** | Ngày thực hiện trắc nghiệm DLQI | string | YYYY-MM-DD | Định dạng ngày | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Date picker. |
| **`dlqi_diem`** | Điểm số chất lượng cuộc sống da liễu DLQI | integer | điểm | 0 - 30 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Number input. |
| **`uct_diem`** | Điểm số kiểm soát mày đay UCT ở lần khám đầu | integer | điểm | 0 - 16 ($\ge 12$ là kiểm soát tốt) | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | 4 câu hỏi (0-4 điểm/câu). |
| **`aect_diem`** | Điểm số kiểm soát phù mạch AECT | integer | điểm | 0 - 16 | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Bắt buộc nếu bệnh nhân có phù mạch. |

---

### B3. Tiền sử (Mục 2)

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`tien_su_phan_ve`** | Tiền sử bị phản vệ | object | null | • `Có (ghi rõ: ...)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Link với BN nhập, BS sửa được. |
| **`tien_su_benh_ly_co_dia`** | Tiền sử mắc bệnh lý cơ địa dị ứng | object (checkbox) | null | • Có: `Viêm da cơ địa`, `Hen`, `Viêm mũi dị ứng`, `Khác (ghi rõ)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Checkbox nhiều lựa chọn. |
| **`tien_su_di_ung`** | Tiền sử dị ứng | object (checkbox) | null | • Có: `Thuốc (ghi rõ)`, `Thức ăn (ghi rõ)`, `Dị nguyên khác (ghi rõ)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Checkbox nhiều lựa chọn. |
| **`tien_su_benh_ly_tuyen_giap`** | Tiền sử bệnh lý tuyến giáp | object | null | • `Có (ghi rõ: ...)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Liên quan chặt chẽ với CSU tự miễn. |
| **`tien_su_benh_tu_mien`** | Tiền sử bệnh tự miễn khác | object | null | • `Có (ghi rõ: ...)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Radio/dropdown. |
| **`tien_su_viem_nhiem_man`** | Tiền sử các ổ viêm nhiễm mạn tính | object | null | • `Có (ghi rõ: ...)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Radio/dropdown. |
| **`tien_su_benh_ly_khac`** | Tiền sử bệnh lý khác | object | null | • `Có (ghi rõ: ...)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Radio/dropdown. |
| **`tien_su_gia_dinh`** | Tiền sử gia đình mắc bệnh liên quan | object | null | • `Có (ghi rõ: thành viên – bệnh lý – diễn biến)`<br>• `Không`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |

---

### B4. Cận lâm sàng chuyên sâu & Phân loại thể bệnh (Mục 3)

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`asst_hieu_so_mm`** | Hiệu số đường kính ASST | number | mm | `asst_duong_kinh_huyet_thanh - asst_duong_kinh_nacl` | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Auto tính theo mục ASST. Dương tính khi $\ge 1.5$ mm. |
| **`asst_phan_loai_ket_qua`** | Phân loại kết quả ASST | string | null | • `(+)`<br>• `(−)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Auto phân loại từ hiệu số. |
| **`igg_khang_fceria_nong_do`** | Nồng độ tự kháng thể IgG kháng FcεRIα | number | *TODO: Đơn vị?* | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Dấu ấn sinh học Type IIb. |
| **`igg_khang_fceria_ket_qua`** | Kết quả IgG kháng FcεRIα | string | null | • `(+)`<br>• `(−)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`igg_khang_ige_nong_do`** | Nồng độ tự kháng thể IgG kháng IgE | number | *TODO: Đơn vị?* | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Dấu ấn sinh học Type IIb. |
| **`igg_khang_ige_ket_qua`** | Kết quả IgG kháng IgE | string | null | • `(+)`<br>• `(−)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`ige_khang_il24_nong_do`** | Nồng độ kháng thể IgE kháng IL-24 | number | *TODO: Đơn vị?* | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Dấu ấn sinh học Type I (Tự dị ứng). |
| **`ige_khang_il24_ket_qua`** | Kết quả IgE kháng IL-24 | string | null | • `(+)`<br>• `(−)` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`bat_ket_qua`** | Kết quả test hoạt hóa bạch cầu kiềm BAT | string | null | • `(+)`<br>• `(−)`<br>• `Không làm` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Bổ sung ngoài giấy cho nghiên cứu Type IIb. |
| **`ige_khang_tpo_nong_do`** / **`ige_khang_tpo_ket_qua`** | Định lượng & kết quả IgE kháng TPO | number / string | UI/mL | Nồng độ $\ge 0$; Kết quả: `(+)`, `(−)` | Missing: `null`<br>Unknown: `-1` / `"unknown"`<br>N/A: `"N/A"` | Không | Bổ sung ngoài giấy cho nghiên cứu Type I. |
| **`phan_loai_the_benh_asst`** | Phân loại thể bệnh CSU theo bảng 3.1 BA giấy | string | null | • `Type I`<br>• `Type IIb`<br>• `Chồng lấp`<br>• `Không xác định` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Hệ thống auto-suy diễn theo logic:<br>• Type I = ASST(−), cả 2 IgG(−), IL-24(+)<br>• Type IIb = ASST(+), $\ge 1$ IgG(+), IL-24(−)<br>• Chồng lấp = ASST(+), $\ge 1$ IgG(+), IL-24(+)<br>• Không xác định = Các trường hợp còn lại. |
| **`wbc`** | Bạch cầu WBC | number | G/L | *TODO: Khoảng tham chiếu?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`eo`** | Bạch cầu ái toan Eosinophil | number | G/L hay % | *TODO: Đơn vị?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`ba_bach_cau`** | Bạch cầu ái kiềm Basophil | number | G/L hay % | *TODO: Đơn vị?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS (Giảm trong Type IIb). |
| **`crp`** | Định lượng CRP | number | mg/L | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`mau_lang_1h`** / **`mau_lang_2h`** | Tốc độ máu lắng 1h / 2h | number | mm | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`ft3`** / **`ft4`** / **`tsh`** | Xét nghiệm chức năng tuyến giáp | number | pmol/L, uIU/mL | *TODO: Khoảng tham chiếu?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`ige_toan_phan`** | Nồng độ IgE toàn phần | number | UI/mL | $\ge 0$ (Thấp trong Type IIb, cao trong Type I) | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`anti_tpo`** | Kháng thể tự miễn Anti-TPO | number | UI/mL | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`ana_hep2`** | Kháng thể kháng nhân ANA HEp-2 | string | null | *TODO: Danh mục (Âm tính / Dương tính / Hiệu giá)?* | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`sieu_am_tuyen_giap`** | Kết quả siêu âm tuyến giáp | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`xet_nghiem_khac`** | Xét nghiệm khác | string | null | Chuỗi văn bản | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |

---

### B5. Theo dõi điều trị (Mục 4)

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`tung_co_dot_benh_tuong_tu`** | Từng có đợt bệnh tương tự trong quá khứ | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Link với BN nhập. |
| **`so_lan_dot_benh_tuong_tu`** | Số lần có đợt bệnh tương tự | integer | lần | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | **Có điều kiện** | Hiện khi có đợt tương tự. |
| **`tuoi_lan_dau_bi_benh_man`** | Tuổi lần đầu tiên bị bệnh mày đay mạn | integer | tuổi | *TODO: Khoảng tuổi (0-120)?* | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Bổ sung ngoài giấy để khớp với BA cấp. |
| **`kieu_dien_bien`** | Kiểu diễn biến của bệnh | string | null | • `Gần như liên tục, hiếm khi hết hẳn`<br>• `Từng đợt, giữa các đợt hết hoàn toàn` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Radio 1 lựa chọn. |
| **`da_tung_cap_cuu_nhap_vien`** | Từng phải cấp cứu / nhập viện vì mày đay | object | null | • `Có (kèm số lần: ...)`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Đánh giá mức độ nặng tiền sử. |
| **`mo_ta_them_dien_bien_dot_truoc`** | Mô tả diễn biến các đợt bệnh trước | string | null | Văn bản tự do | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Textarea. |
| **`thoi_gian_trung_binh_moi_dot_benh`** | Thời gian trung bình mỗi đợt bệnh kéo dài | number | *TODO: Đơn vị tuần hay tháng?* | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Number input. |
| **`thuoc_da_dung_dot_nay`** | Đã dùng thuốc gì trong đợt này hay chưa | string | null | • `Có`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Nếu Có mở bảng danh sách thuốc. |
| **`danh_sach_thuoc_da_dung_dot_nay`** | Lưới danh sách thuốc đã dùng đợt này | array (grid) | null | Cột:<br>• `Tên thuốc`<br>• `Liều và thời gian dùng`<br>• `Tuân thủ` (`Đều`, `Không đều`, `Không rõ`)<br>• `Đáp ứng` (`Hoàn toàn`, `Một phần`, `Không đáp ứng`, `Không rõ`) | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | **Có điều kiện** | Đưa tuân thủ và đáp ứng vào từng dòng thuốc theo chốt 22.9. |
| **`tuan_thu_dieu_tri`** | Đánh giá tuân thủ điều trị tổng thể | string | null | • `Đều đúng đơn`<br>• `Không đều`<br>• `Tự dừng giữa chừng`<br>• `Không được kê đơn lần trước`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Mở rộng enum 4 mức theo app B.9. |
| **`dap_ung_dieu_tri`** | Đánh giá đáp ứng điều trị tổng thể | string | null | • `Hết hẳn (=Hoàn toàn)`<br>• `Đỡ nhiều`<br>• `Đỡ một phần (=Một phần)`<br>• `Không đỡ (=Không đáp ứng)`<br>• `Nặng hơn`<br>• `Không rõ` | Missing: `null`<br>Unknown: `"Không rõ"`<br>N/A: `"N/A"` | Không | Mở rộng enum 6 mức theo app B.9. |
| **`theo_doi_tai_kham_lan_kham`** | Lưới theo dõi điều trị tại các lần tái khám | array (grid) | null | Mỗi dòng = 1 lần khám, gồm các cột:<br>• `Lần khám` (tự động đánh số)<br>• `Ngày khám`<br>• `BS khám`<br>• `UAS7 - dùng thuốc (/42)`<br>• `UCT/điểm (/16)`<br>• `Test kích thích` (ghi kết quả làm lại)<br>• `Phương án điều trị` (`Tăng liều`, `Giảm liều`, `Giữ nguyên`, `Ngừng thuốc + Lý do`)<br>• `Tên thuốc`<br>• `Liều dùng`<br>• `Thời gian dùng`<br>• `Ghi chú/CLS chú ý`<br>• `Ảnh tổn thương` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Cho phép thêm/xoá dòng không giới hạn. |

---

### B6. Theo dõi tác dụng phụ của thuốc (Mục 5)

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`theo_doi_tac_dung_phu_thuoc`** | Lưới theo dõi biến cố bất lợi của thuốc | array (grid) | null | Cột:<br>• `Tên thuốc`<br>• `Liều dùng`<br>• `Tác dụng phụ`<br>• `Mức độ` (`Nhẹ`, `Trung bình`, `Nặng`)<br>• `Xử trí` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BN khai tên thuốc/liều/tác dụng phụ; BS điền mức độ/xử trí. |

---

### B7. Khám & Kế hoạch (Mục 7 - Bổ sung ngoài giấy)

| Tên trường | Ý nghĩa lâm sàng | Kiểu dữ liệu | Đơn vị | Giá trị hợp lệ | Missing / Unknown / N/A | Bắt buộc? | Ghi chú logic & UI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`sot`** / **`sot_nhiet_do_c`** | Dấu hiệu sốt & nhiệt độ đo được | object / number | °C | Có/Không; Nhiệt độ: 35.0 - 43.0 °C | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Cùng tên biến với BA cấp. |
| **`mach`** | Mạch | number | lần/phút | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`huyet_ap_tam_thu`** / **`huyet_ap_tam_truong`** | Huyết áp tâm thu / tâm trương | number | mmHg | $\ge 0$ | Missing: `null`<br>Unknown: `-1`<br>N/A: `"N/A"` | Không | Nhập từ HIS. |
| **`bat_thuong_co_quan_khac`** | Bất thường cơ quan khác khi thăm khám | object | null | • `Có (ghi rõ: ...)`<br>• `Không` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`bang_thuoc_dieu_tri`** | Lưới đơn thuốc điều trị lần khám đầu | array (grid) | null | Cột: `Nhóm thuốc`, `Hoạt chất`, `Liều mỗi lần`, `Đơn vị`, `Tần suất`, `Ngày bắt đầu`, `Ngày kết thúc` | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Đơn thuốc lần khám đầu. |
| **`ngung_thuoc_lan_sau`** | Hướng dẫn ngừng thuốc trước lần khám sau | object | null | • Có kèm bảng `ngung_thuoc_bang` (Thuốc cần ngừng, Ngừng từ ngày, Số ngày ngừng, Mục đích: làm test/UAS7)<br>• Không | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Phục vụ chuẩn bị cho làm test kích thích / ASST / lưu huyết thanh. |
| **`ngay_hen_tai_kham`** | Ngày hẹn tái khám | string | YYYY-MM-DD | Định dạng ngày hợp lệ | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | Dùng app nhắc làm UAS7 trước hẹn. |
| **`tom_tat_buoi_kham`** | Tóm tắt buổi khám bệnh | string | null | Văn bản tự do | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`huong_xu_tri_lan_sau`** | Hướng xử trí cho các lần khám tiếp theo | string | null | Văn bản tự do | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |
| **`dan_do`** | Dặn dò của bác sĩ đối với bệnh nhân | string | null | Văn bản tự do | Missing: `null`<br>Unknown: `"unknown"`<br>N/A: `"N/A"` | Không | BS nhập. |

---

