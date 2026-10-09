# BỘ KỊCH BẢN KIỂM THỬ LÂM SÀNG (TEST CASES SPECIFICATION)
**Phân hệ:** Phản vệ, Sốc phản vệ & Mày đay cấp tính  
**Mục đích:** Kiểm tra tính chính xác của bộ máy suy diễn Rule-based trước khi triển khai thực tế.

---

## 1. Ma trận kịch bản kiểm thử (Test Matrix)

| Mã test case | Nhóm bệnh mục tiêu | Mô tả tình huống lâm sàng | Quy tắc kỳ vọng | Nhãn dự đoán kỳ vọng |
| :--- | :--- | :--- | :--- | :--- |
| **TC-PV-01** | Sốc phản vệ | Người lớn (28t), ăn hải sản, nổi sẩn phù + tụt HA (80/50 mmHg, HA nền 120/80) | `R-SOC` | **Sốc phản vệ** |
| **TC-PV-02** | Sốc phản vệ | Trẻ em 5 tuổi, tiêm kháng sinh, ngất, HATT đo được 75 mmHg (< 70 + 2*5 = 80) | `R-SOC` | **Sốc phản vệ** |
| **TC-PV-03** | Phản vệ (Kịch bản 1) | Không rõ dị nguyên, đột ngột nổi phù mạch mặt + khó thở, co thắt thanh quản | `R01-PV` | **Phản vệ** |
| **TC-PV-04** | Phản vệ (Kịch bản 2) | Dị nguyên thức ăn, nổi mày đay toàn thân kèm đau bụng quặn thắt + nôn 3 lần | `R02-PV` | **Phản vệ** |
| **TC-PV-05** | Phản vệ (Kịch bản 3) | Dị nguyên thuốc đã biết, xuất hiện tụt huyết áp/sốc nhưng không có triệu chứng da | `R03-PV` | **Phản vệ** |
| **TC-PV-06** | Theo dõi phản vệ | Có tiếp xúc dị nguyên, ngứa nhẹ, bác sĩ tích cờ chưa đủ dữ kiện phân loại | `R-PV-THEODOI` | **Theo dõi phản vệ (Chưa đủ dữ kiện)** |
| **TC-CAP-01** | Mày đay cấp thường | Nổi sẩn phù hình vòng 2 ngày (<6 tuần), không phù mạch mặt, diện tích <20% BSA, không nôn, không khó thở | `R01-CAP-THUONG` | **Mày đay cấp thông thường** |
| **TC-CAP-02** | Mày đay cấp nặng | Mày đay cấp kèm phù mạch môi/lưỡi/thanh quản, phải vào viện cấp cứu | `R01-CAP-NANG` | **Mày đay cấp có dấu hiệu nặng** |
| **TC-CAP-03** | Mày đay cấp nặng | Mày đay cấp lan rộng >50% BSA, sẩn phù >50 nốt kèm nôn ói và thở khò khè | `R01-CAP-NANG` | **Mày đay cấp có dấu hiệu nặng** |
| **TC-VAL-01** | Dữ liệu không hợp lệ | Huyết áp tâm thu ghi nhận nhỏ hơn huyết áp tâm trương (SBP 70, DBP 90) | Lỗi logic sinh hiệu | **Validation Error** |

---

