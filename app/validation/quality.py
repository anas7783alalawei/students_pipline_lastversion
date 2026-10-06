
import pandas as pd

# تتحق من بيانات طالب csv
def validate_student_source(df):
    errors = []

    for _, r in df.iterrows():
        sid = r.get("student_id")

        if pd.isna(sid):
            errors.append({
                "student_id": "",
                "error_reason": "Missing student_id",
                "source": "CSV"
            })

        elif pd.notna(r.get("age")):
            if not (16 <= float(r["age"]) <= 80):
                errors.append({
                    "student_id": int(sid),
                    "error_reason": "Invalid Age",
                    "source": "CSV"
                })

    # تسجيل التكرارات، مع الاحتفاظ بأول نسخة
    dup_ids = (
        df.loc[
            df["student_id"].duplicated(keep="first"),
            "student_id"
        ]
        .dropna()
        .unique()
    )

    for sid in dup_ids:
        errors.append({
            "student_id": int(sid),
            "error_reason": "Duplicate student_id",
            "source": "CSV"
        })

    return pd.DataFrame(
        errors,
        columns=["student_id", "error_reason", "source"]
    )

# التحقق من البيانات api
def validate_api_source(df):
    errors = []

    for _, r in df.iterrows():
        sid = r.get("student_id")

        if pd.isna(sid):
            errors.append({
                "student_id": "",
                "error_reason": "Missing student_id",
                "source": "API"
            })
            continue

        if pd.notna(r.get("gpa")):
            if not (0 <= float(r["gpa"]) <= 4):
                errors.append({
                    "student_id": int(sid),
                    "error_reason": "Invalid GPA",
                    "source": "API"
                })

        if pd.notna(r.get("attendance")):
            if not (0 <= float(r["attendance"]) <= 100):
                errors.append({
                    "student_id": int(sid),
                    "error_reason": "Invalid Attendance",
                    "source": "API"
                })

    return pd.DataFrame(
        errors,
        columns=["student_id", "error_reason", "source"]
    )

# التحقق من بيانات الطلاب في db
def validate_db_source(df):
    errors = []

    for _, r in df.iterrows():
        sid = r.get("student_id")

        if pd.isna(sid):
            errors.append({
                "student_id": "",
                "error_reason": "Missing student_id",
                "source": "DATABASE"
            })
            continue

        if pd.notna(r.get("avg_score")):
            if not (0 <= float(r["avg_score"]) <= 100):
                errors.append({
                    "student_id": int(sid),
                    "error_reason": "Invalid Score",
                    "source": "DATABASE"
                })

    return pd.DataFrame(
        errors,
        columns=["student_id", "error_reason", "source"]
    )