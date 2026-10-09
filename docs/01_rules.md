# ĐẶC TẢ BỘ LUẬT CHẨN ĐOÁN LÂM SÀNG (RULE-BASED KNOWLEDGE BASE)
**Phân hệ:** Phản vệ, Mày đay cấp, Mày đay cảm ứng (CIndU) & Mày đay tự phát mạn tính (CSU)  
**Tài liệu cơ sở:** Bản chốt chuyên môn 11.9.2026, biên bản thống nhất 22.9.2026, Thông tư 51/2017/TT-BYT & Hướng dẫn Quốc tế EAACI/GA²LEN/EuroGuiDerm/APAAACI.

---

## I. THỨ TỰ ƯU TIÊN SUY DIỄN (DIAGNOSTIC HIERARCHY)
Bộ máy suy luận (`src/classify.py`) duyệt các luật theo 5 tầng ưu tiên từ khẩn cấp đến mạn tính:
* **Tầng 1 (Tối khẩn):** Sốc phản vệ (`R-SOC`)
* **Tầng 2 (Cấp cứu đe dọa tính mạng):** Phản vệ (`R01-PV`, `R02-PV`, `R03-PV`)
* **Tầng 3 (Khởi phát cấp tính < 6 tuần):** 
  * Mày đay cấp có dấu hiệu nặng (`R01-CAP-NANG`, `R02-CAP-NANG`)
  * Mày đay cấp thông thường (`R01-CAP-THUONG`)
* **Tầng 4 (Khởi phát mạn tính > 6 tuần có yếu tố kích thích - CIndU):**
  * CIndU Da vẽ nổi (`R-CindU-01`)
  * CIndU Cholinergic (`R-CindU-02`)
  * CIndU Do lạnh (`R-CindU-03`)
  * CIndU Khác (`R-CindU-04`)
* **Tầng 5 (Khởi phát mạn tính > 6 tuần tự phát - CSU):**
  * CSU Type I (`R-CSU-T1-01`, `R-CSU-T1-02`)
  * CSU Type IIb (`R-CSU-T2-01`)
  * CSU Chồng lấp / Overlap (`R-CSU-OVL-01`)
  * CSU Không xác định / Unknown (`R-CSU-UNK-01`, `R-CSU-UNK-02`)
* **Tầng 6 (Mặc định / Ngoại lệ):** Chưa đủ dữ liệu / Tiếp tục theo dõi (`R-DEFAULT`, `R-PV-THEODOI`)

---

## II. BỘ LUẬT PHÂN LOẠI CHI TIẾT

### 1. PHÂN HỆ PHẢN VỆ & SỐC PHẢN VỆ

| Rule ID | Kết luận | Logic điều kiện (Pseudocode) | Tiêu chí y khoa |
| :--- | :--- | :--- | :--- |
| **`R01-PV`** | **Phản vệ** (Kịch bản 1) | `(yeu_to_nghi_ngo_pv_thuc_an == "Không" AND yeu_to_nghi_ngo_pv_thuoc == "Không" AND yeu_to_nghi_ngo_pv_con_trung_dot == "Không" AND yeu_to_nghi_ngo_pv_khac == "Không")` <br>AND `trieu_chung_da_hien_tai_pv IN ("Phù mạch", "Sẩn phù", "Ban dát sẩn")` <br>AND `(trieu_chung_ho_hap_hien_tai_pv IN ("Khó thở", "Thở khò khè", "Khàn giọng", "Tiếng rít thanh quản", "Ngừng thở") OR trieu_chung_tuan_hoan_hien_tai_pv IN ("Tụt huyết áp / sốc", "Tím tái", "Ngất"))` | **Không rõ tác nhân dị ứng**:<br>Da/niêm mạc cấp tính VÀ có biểu hiện Hô hấp hoặc Tuần hoàn. |
| **`R02-PV`** | **Phản vệ** (Kịch bản 2) | `(yeu_to_nghi_ngo_pv_thuc_an == "Có" OR yeu_to_nghi_ngo_pv_thuoc == "Có" OR yeu_to_nghi_ngo_pv_con_trung_dot == "Có" OR yeu_to_nghi_ngo_pv_khac == "Có")` <br>AND **Đạt $\ge$ 2 trong 4 hệ thống cơ quan:**<br>1. Da: `Phù mạch`, `Sẩn phù`, `Ban dát sẩn`<br>2. Hô hấp: `Khó thở`, `Thở khò khè`, `Khàn giọng`, `Tiếng rít thanh quản`, `Ngừng thở`<br>3. Tuần hoàn: `Tụt huyết áp / sốc`, `Ngất`<br>4. Tiêu hóa nặng: `dau_bung_quan_that == true` OR `non_so_lan >= 2` | **Tiếp xúc tác nhân nguy cơ cao**:<br>Xuất hiện tổn thương $\ge 2/4$ hệ thống: Da, Hô hấp, Tuần hoàn, Tiêu hóa nặng. |
| **`R03-PV`** | **Phản vệ** (Kịch bản 3) | `(yeu_to_nghi_ngo_pv_* == "Có")` <br>AND `[` `(tac_nhan_hit_vao_pv == "Không" AND trieu_chung_ho_hap_hien_tai_pv IN ("Khó thở", "Thở khò khè", "Khàn giọng", "Tiếng rít thanh quản", "Ngừng thở"))` <br>OR `trieu_chung_tuan_hoan_hien_tai_pv IN ("Tụt huyết áp / sốc", "Ngất")` `]` | **Tiếp xúc dị nguyên đã biết**:<br>Xuất hiện Hô hấp (khi dị nguyên không qua đường hít) HOẶC Tuần hoàn. |
| **`R-SOC`** | **Sốc phản vệ** | `(R02-PV == True OR R03-PV == True)` <br>AND Tụt huyết áp theo tuổi:<br>• `tuoi >= 0.083 AND tuoi < 1`: `huyet_ap_tam_thu_thap_nhat < 70`<br>• `tuoi >= 1 AND tuoi <= 10`: `huyet_ap_tam_thu_thap_nhat < (70 + 2 * tuoi)`<br>• `tuoi >= 11 AND tuoi <= 17`: `huyet_ap_tam_thu_thap_nhat < 90`<br>• `tuoi >= 18`: `(huyet_ap_tam_thu_thap_nhat < 90 OR huyet_ap_tam_thu_thap_nhat < 0.7 * huyet_ap_tam_thu_nen)` | **Phản vệ kèm tụt huyết áp:**<br>1 tháng - 1 tuổi: HATT < 70 mmHg<br>1 - 10 tuổi: HATT < (70 + 2*tuổi)<br>11 - 17 tuổi: HATT < 90 mmHg<br>$\ge 18$ tuổi: HATT < 90 mmHg hoặc giảm > 30% nền. |
| **`R-PV-THEODOI`** | **Cảnh báo theo dõi phản vệ** | `tiep_tuc_theo_doi_chua_du_du_kien == true` OR (Tiếp xúc dị nguyên AND có 1 triệu chứng da nhưng chưa đủ tiêu chuẩn 2 hệ cơ quan) | Chưa đủ dữ kiện để phân loại tại thời điểm đánh giá, nhắc nhở theo dõi sát. |

---

### 2. PHÂN HỆ MÀY ĐAY CẤP TÍNH (< 6 TUẦN)

* **Điều kiện tiên quyết (`R-SANGLOC-CAP`):**  
  `hien_tai_co_san_phu == "Có"` AND `dac_diem_san_phu_cap` có dạng bờ rõ (`Hình vòng`, `Hình tròn`, `Hình bản đồ`) AND `thoi_gian_khoi_phat_gio <= 1008` (không quá 6 tuần) AND `anh_san_phu == "Có"`.

| Rule ID | Kết luận | Logic điều kiện (Pseudocode) | Tiêu chí y khoa |
| :--- | :--- | :--- | :--- |
| **`R01-CAP-NANG`** | **Mày đay cấp có dấu hiệu nặng** | `R-SANGLOC-CAP == True` <br>AND `[` `trieu_chung_da_hien_tai == "Phù mạch đáng kể"` OR `so_lan_phu_mach_nang_can_vien >= 1` OR `vi_tri_phu_mach IN ("Mi mắt", "Lưỡi", "Thanh quản", "Môi")` `]` | Phù mạch đáng kể ở vùng mặt/cổ/thanh quản hoặc phù mạch nặng phải cấp cứu. |
| **`R02-CAP-NANG`** | **Mày đay cấp có dấu hiệu nặng** | `R-SANGLOC-CAP == True` <br>AND `[` `trieu_chung_da_hien_tai == "Ngứa nhiều"` OR `(` `trieu_chung_da_hien_tai == "Sẩn phù"` AND `[` `trieu_chung_tieu_hoa_hien_tai IN ("nôn", "đau bụng quặn thắt")` OR `trieu_chung_ho_hap_hien_tai IN ("thở khò khè", "nghẹn họng")` OR `muc_do_lan_rong_va_phan_bo_ton_thuong == ">50% BSA"` OR `so_luong_san_phu == ">50 nốt"` `]` `)` `]` | Ngứa nhiều HOẶC sẩn phù diện rộng > 50% BSA / > 50 nốt HOẶC kèm triệu chứng tiêu hóa/hô hấp nhẹ. |
| **`R01-CAP-THUONG`** | **Mày đay cấp thông thường** | `R-SANGLOC-CAP == True` <br>AND `trieu_chung_da_hien_tai == "Sẩn phù"` <br>AND NOT `[ Tiêu chí nặng của R01-CAP-NANG và R02-CAP-NANG ]` | Sẩn phù cấp tính đơn thuần, không phù mạch đáng kể, không triệu chứng toàn thân. |

---

### 3. PHÂN HỆ MÀY ĐAY CẢM ỨNG (CIndU - CHRONIC INDUCIBLE URTICARIA)

* **Điều kiện tiên quyết (`R-CindU-00`):**  
  `thoi_gian_khoi_phat_tuan > 6` AND `hoan_canh_xuat_hien_san_phu == "Khi có các yếu tố kích thích"` AND `benh_cap_tinh_nang == "Không"` AND `thai_hoac_cho_con_bu == "Không"`.

| Rule ID | Kết luận | Logic điều kiện (Pseudocode) | Tiêu chí y khoa |
| :--- | :--- | :--- | :--- |
| **`R-CindU-01`** | **Mày đay CIndU da vẽ nổi** | `R-CindU-00 == True` AND `da_ve_noi_ket_qua == "(+)"` | FricTest / Da vẽ nổi dương tính. |
| **`R-CindU-02`** | **Mày đay CIndU Cholinergic** | `R-CindU-00 == True` AND `cholinergic_ket_qua == "(+)"` | Kích thích nóng / gắng sức dương tính sau 10 phút. |
| **`R-CindU-03`** | **Mày đay CIndU do lạnh** | `R-CindU-00 == True` AND `lanh_temptest_ket_qua == "(+)"` (hoặc `lanh_cucda_ket_qua == "(+)"`) | Xuất hiện sẩn phù sau test lạnh / tiếp xúc nhiệt lạnh. |
| **`R-CindU-04`** | **Mày đay CIndU khác** | `R-CindU-00 == True` AND `da_ve_noi_ket_qua == "(−)"` AND `cholinergic_ket_qua == "(−)"` AND `lanh_temptest_ket_qua == "(−)"` AND (`ap_luc_cham_ket_qua == "(+)"` OR `anh_sang_ket_qua == "(+)"` OR `nuoc_ket_qua == "(+)"` OR `khac_ket_qua == "(+)"`) | Âm tính với các thể thường gặp nhưng dương tính với áp lực chậm, ánh sáng, nước, rung chấn. |

---

### 4. PHÂN HỆ MÀY ĐAY TỰ PHÁT MẠN TÍNH (CSU)

* **Điều kiện tiên quyết (`R-CSU-00`):**  
  `csu_don_thuan == True` AND `tuoi >= 16` AND `asst_ngung_khang_histamin >= 8` (ngừng kháng H1 $\ge 8$ ngày) AND `asst_ngung_corticoid >= 30` (ngừng corticoid $\ge 1$ tháng) AND `luu_huyet_thanh == "Có"` AND `benh_cap_tinh_nang == "Không"` AND `thai_hoac_cho_con_bu == "Không"`.

* **Phân giai đoạn sàng lọc ban đầu:**
  * **Giai đoạn 1 (`R-GD-01`):** `R-CSU-00 == True` AND `asst_ket_qua == "(+)"` (Nhóm ASST dương tính).
  * **Giai đoạn 2 (`R-GD-02`):** `R-CSU-00 == True` AND `asst_ket_qua == "(−)"` AND `stella_dat == True` (Đạt tiêu chuẩn Stella: không dị ứng đồng mắc, IgE toàn phần < 40 IU/mL, test lẩy da dị nguyên hô hấp âm tính).
  * **Loại khỏi nghiên cứu (`R-GD-03`):** `R-CSU-00 == True` AND `asst_ket_qua == "(−)"` AND `stella_dat == False`.

* **Cây phân loại thể bệnh chuyên sâu (ELISA Kháng thể):**

| Rule ID | Kết luận thể bệnh | Logic điều kiện chi tiết | Diễn giải cơ chế miễn dịch |
| :--- | :--- | :--- | :--- |
| **`R-CSU-T1-01`** | **Mày đay CSU Type I** | `R-GD-01` AND `so_ngay_theo_doi >= 60` AND `igg_am == True` AND `il24_duong == True` | GĐ1 (ASST +): theo dõi $\ge 2$ tháng, IgG âm, IgE kháng IL-24 dương. |
| **`R-CSU-T1-02`** | **Mày đay CSU Type I** | `R-GD-02` AND `il24_duong == True` | GĐ2 (ASST −): IgE kháng IL-24 dương tính (Autoallergic endotype). |
| **`R-CSU-T2-01`** | **Mày đay CSU Type IIb** | `R-GD-01` AND `so_ngay_theo_doi >= 60` AND `igg_duong == True` AND `il24_am == True` | GĐ1: Tự kháng thể IgG dương tính (kháng FcεRIα/IgE), IgE kháng IL-24 âm tính (Autoimmune endotype). |
| **`R-CSU-OVL-01`** | **Mày đay CSU Chồng lấp (Overlap)** | `R-GD-01` AND `so_ngay_theo_doi >= 60` AND `igg_duong == True` AND `il24_duong == True` | GĐ1: Vừa có IgG tự kháng thể vừa có IgE kháng IL-24 dương tính. |
| **`R-CSU-UNK-01`** | **Mày đay CSU Không xác định (Unknown)** | `R-GD-01` AND `so_ngay_theo_doi >= 60` AND `igg_am == True` AND `il24_am == True` | GĐ1: Cả hai dấu ấn sinh học đều âm tính (Điểm dừng GĐ1). |
| **`R-CSU-UNK-02`** | **Mày đay CSU Không xác định (Unknown)** | `R-GD-02` AND `il24_am == True` | GĐ2: IgE kháng IL-24 âm tính (Điểm dừng GĐ2). |
| **`R-DEFAULT`** | **Chưa phân loại / Tiếp tục theo dõi** | Thiếu dữ liệu bắt buộc: `asst_ket_qua` trống OR GĐ1 mà `so_ngay_theo_doi < 60` OR thiếu kết quả ELISA tương ứng. | Chưa đủ dữ liệu kết luận thể bệnh. |