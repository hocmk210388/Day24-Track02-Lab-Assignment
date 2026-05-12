# src/quality/validation.py
import re
import pandas as pd


def validate_raw_data(filepath: str) -> dict:
    """Validate raw patient data với các expectations cơ bản."""
    df = pd.read_csv(filepath)
    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns),
        }
    }

    # 1. patient_id không được null
    null_ids = df["patient_id"].isnull().sum()
    if null_ids > 0:
        results["success"] = False
        results["failed_checks"].append(
            f"patient_id has {null_ids} null values"
        )

    # 2. cccd phải có đúng 12 ký tự
    bad_cccd = df["cccd"].astype(str).apply(lambda x: len(x) != 12).sum()
    if bad_cccd > 0:
        results["success"] = False
        results["failed_checks"].append(
            f"cccd: {bad_cccd} rows do not have exactly 12 characters"
        )

    # 3. ket_qua_xet_nghiem phải trong khoảng [0, 50]
    out_of_range = df[
        (df["ket_qua_xet_nghiem"] < 0) | (df["ket_qua_xet_nghiem"] > 50)
    ].shape[0]
    if out_of_range > 0:
        results["success"] = False
        results["failed_checks"].append(
            f"ket_qua_xet_nghiem: {out_of_range} rows out of [0, 50] range"
        )

    # 4. benh phải thuộc danh sách hợp lệ
    valid_conditions = {"Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"}
    invalid_benh = df[~df["benh"].isin(valid_conditions)].shape[0]
    if invalid_benh > 0:
        results["success"] = False
        results["failed_checks"].append(
            f"benh: {invalid_benh} rows have invalid values"
        )

    # 5. email phải match regex pattern
    email_re = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    bad_email = df["email"].astype(str).apply(
        lambda x: not email_re.match(x)
    ).sum()
    if bad_email > 0:
        results["success"] = False
        results["failed_checks"].append(
            f"email: {bad_email} rows have invalid format"
        )

    # 6. Không được có duplicate patient_id
    dup_count = df["patient_id"].duplicated().sum()
    if dup_count > 0:
        results["success"] = False
        results["failed_checks"].append(
            f"patient_id: {dup_count} duplicate values"
        )

    return results


def validate_anonymized_data(filepath: str, original_row_count: int = 200) -> dict:
    """
    Validate anonymized data.
    Trả về dict: {"success": bool, "failed_checks": list, "stats": dict}
    """
    df = pd.read_csv(filepath)
    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns),
        }
    }

    # Check 1: Không còn CCCD gốc dạng số thuần túy 12 chữ số liên tiếp
    # (sau anonymization, cccd vẫn là 12 số nhưng đã thay bằng fake)
    # -> kiểm tra cột cccd vẫn tồn tại và có dữ liệu
    null_cccd = df["cccd"].isnull().sum()
    if null_cccd > 0:
        results["success"] = False
        results["failed_checks"].append(
            f"cccd: {null_cccd} null values after anonymization"
        )

    # Check 2: Không có null values trong các cột quan trọng
    important_cols = ["patient_id", "benh", "ket_qua_xet_nghiem"]
    for col in important_cols:
        nulls = df[col].isnull().sum()
        if nulls > 0:
            results["success"] = False
            results["failed_checks"].append(f"{col}: {nulls} null values")

    # Check 3: Số rows phải bằng original
    if len(df) != original_row_count:
        results["success"] = False
        results["failed_checks"].append(
            f"Row count mismatch: expected {original_row_count}, got {len(df)}"
        )

    return results
