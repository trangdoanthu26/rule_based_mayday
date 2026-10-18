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
| **TC-PV-06** | Theo dõi phản vệ | Mẫu Phản vệ đủ dữ kiện, cả ba kịch bản PV và R-SOC đều FALSE; không cần cờ tích tay | `R-PV-THEODOI` | **THEODOIPV** |
| **TC-PV-07** | Thiếu dữ kiện | Mẫu Phản vệ thiếu tuổi, HATT hoặc triệu chứng có thể đổi kết luận | Rule ưu tiên còn UNKNOWN | **INSUFFICIENT_DATA** kèm `missing_fields` |
| **TC-CAP-01** | Mày đay cấp thường | Nổi sẩn phù hình vòng 2 ngày (<6 tuần), không phù mạch mặt, diện tích <20% BSA, không nôn, không khó thở | `R01-CAP-THUONG` | **Mày đay cấp thông thường** |
| **TC-CAP-02** | Mày đay cấp nặng | Mày đay cấp kèm phù mạch môi/lưỡi/thanh quản, phải vào viện cấp cứu | `R02-CAP-NANG-PHUMACH` | **Mày đay cấp có dấu hiệu nặng** |
| **TC-CAP-03** | Mày đay cấp nặng | Có sẩn phù và tổn thương lan rộng >50% BSA, >50 nốt kèm nôn hoặc thở khò khè | `R03-CAP-NANG-CONLAI` | **Mày đay cấp có dấu hiệu nặng** |
| **TC-CAP-04** | Mày đay cấp nặng | Qua cổng cấp, danh sách triệu chứng da chứa `Ngứa nhiều` | `R01-CAP-NANG-NGUA` | **Mày đay cấp có dấu hiệu nặng** |
| **TC-CAP-05** | Chưa đủ dữ kiện loại dấu nặng | Qua cổng cấp, có sẩn phù nhưng thiếu bằng chứng phủ định một nhánh nặng | `R01-CAP-THUONG` còn UNKNOWN | **INSUFFICIENT_DATA** kèm trường thiếu |
| **TC-VAL-01** | Dữ liệu không hợp lệ | Huyết áp tâm thu ghi nhận nhỏ hơn huyết áp tâm trương (SBP 70, DBP 90) | Lỗi logic sinh hiệu | **Validation Error** |

---

