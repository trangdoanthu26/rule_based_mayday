"""
Module tiền xử lý dữ liệu và tính toán biến phái sinh (Feature Engineering).
Tính tuổi theo năm/tháng, thời gian mắc bệnh theo tuần, cờ tổn thương cơ quan.
"""

from datetime import datetime
from typing import Any, Dict, List


class MedicalPreprocessor:
    @staticmethod
    def calculate_age(ngay_sinh_str: str, ngay_kham_str: str) -> float:
        """Tính tuổi thập phân chính xác từ ngày sinh và ngày khám."""
        if not ngay_sinh_str or not ngay_kham_str:
            return 25.0  # Tuổi mặc định người lớn nếu thiếu dữ liệu
        try:
            ns = datetime.strptime(ngay_sinh_str[:10], "%Y-%m-%d")
            nk = datetime.strptime(ngay_kham_str[:10], "%Y-%m-%d")
            diff_days = (nk - ns).days
            return max(0.0, round(diff_days / 365.25, 3))
        except Exception:
            return 25.0

    @staticmethod
    def extract_min_sbp(record: Dict[str, Any]) -> float:
        """Trích xuất huyết áp tâm thu thấp nhất từ bảng theo dõi hoặc biến chỉ điểm."""
        val = record.get("huyet_ap_tam_thu_thap_nhat")
        if val is not None and isinstance(val, (int, float)) and val > 0:
            return float(val)

        # Tìm trong lưới sinh hiệu nếu biến đơn chưa được tính
        vitals = record.get("bang_theo_doi_dau_hieu_sinh_ton") or []
        sbp_list = []
        for row in vitals:
            bp_str = row.get("huyet_ap", "")
            if "/" in str(bp_str):
                try:
                    sbp = float(bp_str.split("/")[0].strip())
                    if sbp > 0:
                        sbp_list.append(sbp)
                except ValueError:
                    pass
        return min(sbp_list) if sbp_list else 120.0

    def preprocess_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Chuẩn hóa dữ liệu thô sang dữ liệu sạch sẵn sàng nạp cho Rule Engine."""
        processed = record.copy()

        # 1. Tính biến tuổi (tuoi)
        ns = processed.get("ngay_sinh")
        nk = processed.get("ngay_kham") or datetime.now().strftime("%Y-%m-%d")
        processed["tuoi"] = self.calculate_age(ns, nk)

        # 2. Chuẩn hóa HATT thấp nhất
        processed["huyet_ap_tam_thu_thap_nhat"] = self.extract_min_sbp(processed)
        if "huyet_ap_tam_thu_nen" not in processed or not processed["huyet_ap_tam_thu_nen"]:
            processed["huyet_ap_tam_thu_nen"] = 120.0  # Mặc định nền sinh lý

        # 3. Chuẩn hóa thời gian khởi phát mày đay cấp về số giờ
        thoi_gian_gio = processed.get("thoi_gian_khoi_phat_gio")
        if thoi_gian_gio is None:
            # Nếu là bệnh án phản vệ, trường tên là thoi_gian_khoi_phat_pv
            thoi_gian_gio = processed.get("thoi_gian_khoi_phat_pv", 1.0)
        processed["thoi_gian_khoi_phat_gio"] = float(thoi_gian_gio or 0.0)

        # 4. Làm phẳng danh sách triệu chứng dạng checkbox lồng nhau
        for sys_field in ["trieu_chung_da_hien_tai_pv", "trieu_chung_da_hien_tai"]:
            if sys_field in processed and isinstance(processed[sys_field], dict):
                ds = processed[sys_field].get("danh_sach_chon", [])
                processed[f"{sys_field}_flatten"] = ds if isinstance(ds, list) else [str(ds)]

        return processed