# ĐẶC TẢ BỘ LUẬT CHẨN ĐOÁN LÂM SÀNG (RULE-BASED KNOWLEDGE BASE)
**Phân hệ:** Phản vệ, Mày đay cấp, Mày đay cảm ứng (CIndU) & Mày đay tự phát mạn tính (CSU)  
**Tài liệu cơ sở:** Bản chốt chuyên môn 11.9.2026, biên bản thống nhất 22.9.2026, Thông tư 51/2017/TT-BYT & Hướng dẫn Quốc tế EAACI/GA²LEN/EuroGuiDerm/APAAACI.

---

## I. THỨ TỰ ƯU TIÊN SUY DIỄN (DIAGNOSTIC HIERARCHY)
Bộ máy suy luận (`src/classify.py`) dùng ba bộ YAML độc lập theo mẫu bệnh án được chọn: `phan_ve_rules.yaml`, `cap_rules.yaml`, `man_rules.yaml`. Priority chỉ so sánh các rule trong cùng mẫu. Các tầng dưới đây là nhóm trình bày của từng phân hệ, không phải thứ tự xuyên ba biểu mẫu:
* **Tầng 1 (Tối khẩn):** Sốc phản vệ (`R-SOC`)
* **Tầng 2 (Cấp cứu đe dọa tính mạng):** Phản vệ (`R01-PV`, `R02-PV`, `R03-PV`)
* **Tầng 3 (Khởi phát cấp tính < 6 tuần):** 
  * Mày đay cấp có dấu hiệu nặng (`R01-CAP-NANG-NGUA`, `R02-CAP-NANG-PHUMACH`, `R03-CAP-NANG-CONLAI`)
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
* **Fallback theo phân hệ:** `R-PV-THEODOI` chỉ trong mẫu Phản vệ; `R-DEFAULT` chỉ trong mẫu Mạn.

---

## II. BỘ LUẬT PHÂN LOẠI CHI TIẾT

### 1. PHÂN HỆ PHẢN VỆ & SỐC PHẢN VỆ

| Rule ID | Kết luận | Logic điều kiện (Pseudocode) | Tiêu chí y khoa |
| :--- | :--- | :--- | :--- |
| **`R01-PV`** | **Phản vệ** (Kịch bản 1) | `(yeu_to_nghi_ngo_pv_thuc_an == "Không" AND yeu_to_nghi_ngo_pv_thuoc == "Không" AND yeu_to_nghi_ngo_pv_con_trung_dot == "Không" AND yeu_to_nghi_ngo_pv_khac == "Không")` <br>AND `trieu_chung_da_hien_tai_pv IN ("Phù mạch", "Sẩn phù", "Ban dát sẩn")` <br>AND `(trieu_chung_ho_hap_hien_tai_pv IN ("Khó thở", "Thở khò khè", "Khàn giọng", "Tiếng rít thanh quản", "Ngừng thở") OR trieu_chung_tuan_hoan_hien_tai_pv IN ("Tụt huyết áp / sốc", "Tím tái", "Ngất"))` | **Không rõ tác nhân dị ứng**:<br>Da/niêm mạc cấp tính VÀ có biểu hiện Hô hấp hoặc Tuần hoàn. |
| **`R02-PV`** | **Phản vệ** (Kịch bản 2) | `(yeu_to_nghi_ngo_pv_thuc_an == "Có" OR yeu_to_nghi_ngo_pv_thuoc == "Có" OR yeu_to_nghi_ngo_pv_con_trung_dot == "Có" OR yeu_to_nghi_ngo_pv_khac == "Có")` <br>AND **Đạt $\ge$ 2 trong 4 hệ thống cơ quan:**<br>1. Da: `Phù mạch`, `Sẩn phù`, `Ban dát sẩn`<br>2. Hô hấp: `Khó thở`, `Thở khò khè`, `Khàn giọng`, `Tiếng rít thanh quản`, `Ngừng thở`<br>3. Tuần hoàn: `Tụt huyết áp / sốc`, `Ngất`<br>4. Tiêu hóa nặng: `dau_bung_quan_that == true` OR `non_so_lan >= 2` | **Tiếp xúc tác nhân nguy cơ cao**:<br>Xuất hiện tổn thương $\ge 2/4$ hệ thống: Da, Hô hấp, Tuần hoàn, Tiêu hóa nặng. |
| **`R03-PV`** | **Phản vệ** (Kịch bản 3) | `(yeu_to_nghi_ngo_pv_* == "Có")` <br>AND `[` `(tac_nhan_hit_vao_pv == "Không" AND trieu_chung_ho_hap_hien_tai_pv IN ("Khó thở", "Thở khò khè", "Khàn giọng", "Tiếng rít thanh quản", "Ngừng thở"))` <br>OR `trieu_chung_tuan_hoan_hien_tai_pv IN ("Tụt huyết áp / sốc", "Ngất")` `]` | **Tiếp xúc dị nguyên đã biết**:<br>Xuất hiện Hô hấp (khi dị nguyên không qua đường hít) HOẶC Tuần hoàn. |
| **`R-SOC`** | **Sốc phản vệ** | `(R01-PV OR R02-PV OR R03-PV)` AND tụt HATT: từ lúc sinh đến `<1` tuổi `<70`; `1≤tuổi<11` `<70+2×tuổi`; `11≤tuổi<18` `<90`; `tuổi≥18` `<90` hoặc `<0.7×HATT nền`. | Trục tuổi liên tục theo xác nhận chuyên môn ngày 18/10/2026. HATT bằng ngưỡng chưa thỏa điều kiện `<`. |
| **`R-PV-THEODOI`** | **Theo dõi phản vệ** (`THEODOIPV`) | `NOT(R-SOC OR R01-PV OR R02-PV OR R03-PV)` chỉ khi cả bốn rule đều FALSE và bệnh án đã được chọn là mẫu Phản vệ. | Nếu rule còn UNKNOWN, giữ `INSUFFICIENT_DATA` và `missing_fields`; không khẳng định đã loại trừ phản vệ. Không dùng cờ tích tay. |

---

### 2. PHÂN HỆ MÀY ĐAY CẤP TÍNH (< 6 TUẦN)

* **Điều kiện tiên quyết (`R-SANGLOC-CAP`):**  
  `hien_tai_co_san_phu == "Có"` AND `dac_diem_san_phu_cap` có dạng bờ rõ (`Hình vòng`, `Hình tròn`, `Hình bản đồ`) AND `thoi_gian_khoi_phat_gio <= 1008` (không quá 6 tuần) AND `anh_san_phu == "Có"`.

| Rule ID | Kết luận | Logic điều kiện (Pseudocode) | Tiêu chí y khoa |
| :--- | :--- | :--- | :--- |
| **`R01-CAP-NANG-NGUA`** | **Mày đay cấp có dấu hiệu nặng** | Qua `R-SANGLOC-CAP` AND `trieu_chung_da_hien_tai.danh_sach_chon` chứa `Ngứa nhiều`. | Priority 4. |
| **`R02-CAP-NANG-PHUMACH`** | **Mày đay cấp có dấu hiệu nặng** | Qua cổng AND (`danh_sach_chon` chứa `Phù mạch đáng kể` OR vị trí Mi mắt/Lưỡi/Thanh quản/Môi OR số lần cần viện ≥1 OR `dau_hieu_nang_chi_tiet` chứa `Phù mạch đáng kể`). | Priority 4; trường chi tiết phải có bằng chứng âm tính rõ để loại dấu nặng. |
| **`R03-CAP-NANG-CONLAI`** | **Mày đay cấp có dấu hiệu nặng** | Qua cổng AND `trieu_chung_da_hien_tai.danh_sach_chon` chứa `Sẩn phù` AND (tiêu hóa, hô hấp, BSA >50% hoặc >50 nốt). | Priority 4; yêu cầu cả cổng `hien_tai_co_san_phu` và triệu chứng `Sẩn phù` theo xác nhận ngày 18/10/2026. |
| **`R01-CAP-THUONG`** | **Mày đay cấp thông thường** | Qua cổng AND danh sách da chứa `Sẩn phù` AND NOT(any_of ba `ref_rule` Cấp nặng). | Priority 5; UNKNOWN ở bất kỳ nhánh nặng cần thiết vẫn chặn kết luận thường. |

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
