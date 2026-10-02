import json
import glob

def load_all_cases(file_paths):
    all_cases = []
    for path in file_paths:
        with open(path, "r", encoding="utf-8") as f:
            cases = json.load(f)
            all_cases.extend(cases)
    return all_cases

# Danh sách các file JSON bệnh án của bạn
file_list = [
    "12_benh_an_CindU.json",
    "12_benh_an_CSU.json",
    "20_benh_an_phan_ve_soc_phan_ve.json",
    "10_benh_an_cap_thuong_va_cap_nang.json"
]

# Nạp toàn bộ dữ liệu
dataset = load_all_cases(file_list)
print(f"Tổng số bệnh án đã nạp: {len(dataset)}")



def classify_rule_based(du_lieu: dict) -> str:
    # 1. SỐC PHẢN VỆ & PHẢN VỆ
    tuan_hoan_list = du_lieu.get("trieu_chung_tuan_hoan_hien_tai", [])
    if isinstance(tuan_hoan_list, str):
        tuan_hoan_list = [tuan_hoan_list]

    is_soc = ("Tụt huyết áp / sốc" in tuan_hoan_list) or ("Ngất" in tuan_hoan_list)
    if is_soc:
        return "Sốc phản vệ"

    co_da = len(du_lieu.get("trieu_chung_da_hien_tai_pv", du_lieu.get("trieu_chung_da_hien_tai", []))) > 0
    co_ho_hap = du_lieu.get("trieu_chung_ho_hap_co_khong") == "Có" or len(du_lieu.get("trieu_chung_ho_hap_hien_tai_pv", [])) > 0
    co_tuan_hoan = du_lieu.get("trieu_chung_tuan_hoan_co_khong") == "Có"
    co_tieu_hoa = du_lieu.get("trieu_chung_tieu_hoa_co_khong") == "Có" or len(du_lieu.get("trieu_chung_tieu_hoa_hien_tai_pv", [])) > 0

    he_co_quan_cnt = sum([co_da, co_ho_hap, co_tuan_hoan, co_tieu_hoa])
    co_yeu_to_nghi_ngo = any([
        du_lieu.get("yeu_to_nghi_ngo_pv_thuc_an") not in [None, "Không", ""],
        du_lieu.get("yeu_to_nghi_ngo_pv_thuoc") not in [None, "Không", ""],
        du_lieu.get("yeu_to_nghi_ngo_pv_con_trung_dot") not in [None, "Không", ""]
    ])
    if he_co_quan_cnt >= 2 and co_yeu_to_nghi_ngo:
        return "Phản vệ"

    # 2. MÀY ĐAY CẢM ỨNG MẠN TÍNH (CIndU)
    da_ve_noi = du_lieu.get("da_ve_noi_ket_qua") == "(+)" or du_lieu.get("fric_score") is not None
    choline = du_lieu.get("cholinergic_ket_qua") == "(+)"
    lanh = du_lieu.get("lanh_temptest_ket_qua") == "(+)" or du_lieu.get("lanh_cucda_ket_qua") == "(+)"
    cindu_khac = any([
        du_lieu.get("ap_luc_cham_ket_qua") == "(+)",
        du_lieu.get("anh_sang_ket_qua") == "(+)",
        du_lieu.get("nuoc_ket_qua") == "(+)",
        du_lieu.get("khac_ket_qua") == "(+)"
    ])

    if da_ve_noi:
        return "Mày đay CindU da vẽ nổi"
    if choline:
        return "Mày đay CindU Choline (do nóng)"
    if lanh:
        return "Mày đay CindU do lạnh"
    if cindu_khac:
        return "Mày đay CindU khác"

    # 3. MÀY ĐAY MẠN TÍNH TỰ PHÁT (CSU)
    asst_pos = (du_lieu.get("asst_ket_qua") == "(+)") or (du_lieu.get("asst_phan_loai_ket_qua") == "(+)")
    igg_pos = (du_lieu.get("igg_khang_fceria_ket_qua") == "(+)") or (du_lieu.get("igg_khang_ige_ket_qua") == "(+)")
    il24_pos = (du_lieu.get("ige_khang_il24_ket_qua") == "(+)")
    tg_man = du_lieu.get("thoi_gian_khoi_phat_tuan")

    if tg_man is not None and tg_man >= 6:
        if il24_pos and not igg_pos and not asst_pos:
            return "Mày đay CSU type 1"
        elif igg_pos and not il24_pos:
            return "Mày đay CSU type 2"
        elif il24_pos and igg_pos:
            return "Mày đay CSU overlap"
        elif not il24_pos and not igg_pos:
            return "Mày đay CSU unknown"
        elif il24_pos:
            return "Mày đay CSU type 1"
        elif igg_pos:
            return "Mày đay CSU type 2"
        else:
            return "Mày đay CSU unknown"

    # 4. MÀY ĐAY CẤP TÍNH (CẤP THƯỜNG & CẤP NẶNG)
    so_luong_san_phu = str(du_lieu.get("so_luong_san_phu", ""))
    lan_rong = str(du_lieu.get("muc_do_lan_rong_va_phan_bo_ton_thuong", ""))
    phu_mach = du_lieu.get("hien_tai_co_phu_mach") == "Có" or len(du_lieu.get("vi_tri_phu_mach", [])) > 0
    dien_dieu_tri = du_lieu.get("dien_dieu_tri")

    is_nang = (
        ">50" in so_luong_san_phu or 
        ">50%" in lan_rong or 
        phu_mach or 
        dien_dieu_tri == "Nội trú"
    )

    if is_nang:
        return "Cấp nặng"
    else:
        return "Cấp thường"

import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report

# 1. Trích xuất nhãn thực tế và chạy hàm dự đoán
y_true = [case["nhan"] for case in dataset]
y_pred = [classify_rule_based(case["du_lieu"]) for case in dataset]

# 2. Lấy danh sách các nhãn duy nhất
unique_labels = sorted(list(set(y_true + y_pred)))

# 3. Tính ma trận nhầm lẫn (Confusion Matrix)
cm = confusion_matrix(y_true, y_pred, labels=unique_labels)

# 4. Chuyển thành DataFrame hiển thị bảng rõ ràng
cm_df = pd.DataFrame(
    cm,
    index=[f"Thực tế: {label}" for label in unique_labels],
    columns=[f"Dự đoán: {label}" for label in unique_labels]
)

print("=== BẢNG CONFUSION MATRIX ===")
print(cm_df)

# 5. Xuất báo cáo đánh giá chi tiết (Accuracy, Precision, Recall, F1-Score)
print("\n=== BÁO CÁO HIỆU NĂNG CHI TIẾT (METRICS REPORT) ===")
print(classification_report(y_true, y_pred, labels=unique_labels, zero_division=0))



import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(12, 10))
sns.heatmap(cm_df, annot=True, fmt="d", cmap="Blues", cbar=False)
plt.title("Biểu đồ Ma trận Nhầm lẫn (Confusion Matrix Heatmap)", fontsize=14, fontweight="bold")
plt.xlabel("Nhãn do Rule-Based Dự Đoán", fontsize=12)
plt.ylabel("Nhãn Thực Tế (Ground Truth)", fontsize=12)
plt.xticks(rotation=45, ha="right")
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig("confusion_matrix_heatmap.png", dpi=300)
plt.show()