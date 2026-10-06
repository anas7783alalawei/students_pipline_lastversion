import pandas as pd


def validate_mongodb(df):
    """
    التحقق من صحة بيانات MongoDB.

    يتم اكتشاف الأخطاء في بيانات MongoDB قبل مرحلة التنظيف.
    الدالة ترجع:

    1. valid_df:
       البيانات الأصلية بعد التحقق.

    2. problems_df:
       جميع الأخطاء المكتشفة، لكي يتم حفظها في:
       data/rejected/rejected_mongodb_records.csv
    """

    data = df.copy()
    problems = []

    # ============================================================
    # 1) التأكد من وجود student_id
    # ============================================================

    if "student_id" not in data.columns:
        raise ValueError(
            "MongoDB data must contain student_id"
        )

    # ============================================================
    # 2) student_id مفقود
    # ============================================================

    missing_id = data["student_id"].isna()

    for idx in data.index[missing_id]:
        problems.append({
            "row": idx,
            "student_id": "",
            "field": "student_id",
            "error": "Missing student_id"
        })

    # ============================================================
    # 3) student_id مكرر
    # ============================================================

    duplicate_id = data["student_id"].duplicated(
        keep="first"
    )

    for idx in data.index[duplicate_id]:
        problems.append({
            "row": idx,
            "student_id": data.loc[idx, "student_id"],
            "field": "student_id",
            "error": "Duplicate student_id"
        })

    # ============================================================
    # 4) التحقق من العمر
    # ============================================================

    if "age" in data.columns:

        # نعتبر العمر النصي خطأ في بيانات MongoDB الخام
        invalid_age_type = (
            data["age"].notna()
            & ~data["age"].map(
                lambda x: isinstance(x, (int, float))
                and not isinstance(x, bool)
            )
        )

        for idx in data.index[invalid_age_type]:
            problems.append({
                "row": idx,
                "student_id": data.loc[idx, "student_id"],
                "field": "age",
                "error": "Age must be a number"
            })

        # التحقق من المجال 16 - 80
        numeric_age = pd.to_numeric(
            data["age"],
            errors="coerce"
        )

        invalid_age_range = (
            numeric_age.notna()
            & numeric_age.between(16, 80).eq(False)
        )

        for idx in data.index[invalid_age_range]:
            problems.append({
                "row": idx,
                "student_id": data.loc[idx, "student_id"],
                "field": "age",
                "error": "Age must be between 16 and 80"
            })

    # ============================================================
    # 5) التحقق من GPA
    # ============================================================

    if "gpa" in data.columns:

        invalid_gpa_type = (
            data["gpa"].notna()
            & ~data["gpa"].map(
                lambda x: isinstance(x, (int, float))
                and not isinstance(x, bool)
            )
        )

        for idx in data.index[invalid_gpa_type]:
            problems.append({
                "row": idx,
                "student_id": data.loc[idx, "student_id"],
                "field": "gpa",
                "error": "GPA must be a number"
            })

        numeric_gpa = pd.to_numeric(
            data["gpa"],
            errors="coerce"
        )

        invalid_gpa_range = (
            numeric_gpa.notna()
            & numeric_gpa.between(0, 4).eq(False)
        )

        for idx in data.index[invalid_gpa_range]:
            problems.append({
                "row": idx,
                "student_id": data.loc[idx, "student_id"],
                "field": "gpa",
                "error": "GPA must be between 0 and 4"
            })

    # ============================================================
    # 6) التحقق من Attendance
    # ============================================================

    if "attendance" in data.columns:

        invalid_attendance_type = (
            data["attendance"].notna()
            & ~data["attendance"].map(
                lambda x: isinstance(x, (int, float))
                and not isinstance(x, bool)
            )
        )

        for idx in data.index[invalid_attendance_type]:
            problems.append({
                "row": idx,
                "student_id": data.loc[idx, "student_id"],
                "field": "attendance",
                "error": "Attendance must be a number without %"
            })

        numeric_attendance = pd.to_numeric(
            data["attendance"],
            errors="coerce"
        )

        invalid_attendance_range = (
            numeric_attendance.notna()
            & numeric_attendance.between(0, 100).eq(False)
        )

        for idx in data.index[invalid_attendance_range]:
            problems.append({
                "row": idx,
                "student_id": data.loc[idx, "student_id"],
                "field": "attendance",
                "error": "Attendance must be between 0 and 100"
            })

    # ============================================================
    # 7) التحقق من Email
    # ============================================================

    if "email" in data.columns:

        email = data["email"].astype("string")

        invalid_email = (
            email.notna()
            & ~email.str.match(
                r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
                na=False
            )
        )

        for idx in data.index[invalid_email]:
            problems.append({
                "row": idx,
                "student_id": data.loc[idx, "student_id"],
                "field": "email",
                "error": "Invalid email"
            })

    # ============================================================
    # 8) التحقق من Major
    # ============================================================

    if "major" in data.columns:

        missing_major = (
            data["major"].isna()
            | data["major"].astype("string").str.strip().eq("")
        )

        for idx in data.index[missing_major]:
            problems.append({
                "row": idx,
                "student_id": data.loc[idx, "student_id"],
                "field": "major",
                "error": "Missing major"
            })

    # ============================================================
    # 9) التحقق من City
    # ============================================================

    if "city" in data.columns:

        city_with_spaces = (
            data["city"].notna()
            & data["city"].astype("string").ne(
                data["city"].astype("string").str.strip()
            )
        )

        for idx in data.index[city_with_spaces]:
            problems.append({
                "row": idx,
                "student_id": data.loc[idx, "student_id"],
                "field": "city",
                "error": "City contains leading or trailing spaces"
            })

    # ============================================================
    # 10) التحقق من Status
    # ============================================================

    if "status" in data.columns:

        invalid_status = (
            data["status"].notna()
            & ~data["status"].astype("string").isin(
                ["Active", "Inactive"]
            )
        )

        for idx in data.index[invalid_status]:
            problems.append({
                "row": idx,
                "student_id": data.loc[idx, "student_id"],
                "field": "status",
                "error": "Invalid status"
            })

    # ============================================================
    # 11) التحقق من Student Name
    # ============================================================

    if "student_name" in data.columns:

        name_with_spaces = (
            data["student_name"].notna()
            & data["student_name"].astype("string").ne(
                data["student_name"].astype("string").str.strip()
            )
        )

        for idx in data.index[name_with_spaces]:
            problems.append({
                "row": idx,
                "student_id": data.loc[idx, "student_id"],
                "field": "student_name",
                "error": "Student name contains leading or trailing spaces"
            })

    # ============================================================
    # 12) التحقق من avg_score
    # ============================================================

    if "avg_score" in data.columns:

        invalid_avg_score_type = (
            data["avg_score"].notna()
            & ~data["avg_score"].map(
                lambda x: isinstance(x, (int, float))
                and not isinstance(x, bool)
            )
        )

        for idx in data.index[invalid_avg_score_type]:
            problems.append({
                "row": idx,
                "student_id": data.loc[idx, "student_id"],
                "field": "avg_score",
                "error": "Average score must be a number"
            })

        numeric_avg_score = pd.to_numeric(
            data["avg_score"],
            errors="coerce"
        )

        invalid_avg_score_range = (
            numeric_avg_score.notna()
            & numeric_avg_score.between(0, 100).eq(False)
        )

        for idx in data.index[invalid_avg_score_range]:
            problems.append({
                "row": idx,
                "student_id": data.loc[idx, "student_id"],
                "field": "avg_score",
                "error": "Average score must be between 0 and 100"
            })

    # ============================================================
    # 13) التحقق من Performance Level
    # ============================================================

    if {
        "performance_level",
        "avg_score"
    }.issubset(data.columns):

        numeric_score = pd.to_numeric(
            data["avg_score"],
            errors="coerce"
        )

        expected_performance = pd.Series(
            index=data.index,
            dtype="object"
        )

        expected_performance.loc[
            numeric_score >= 90
        ] = "Excellent"

        expected_performance.loc[
            (numeric_score >= 70)
            & (numeric_score < 90)
        ] = "Good"

        expected_performance.loc[
            numeric_score < 70
        ] = "Average"

        invalid_performance = (
            numeric_score.notna()
            & data["performance_level"].notna()
            & (
                data["performance_level"].astype("string")
                != expected_performance.astype("string")
            )
        )

        for idx in data.index[invalid_performance]:
            problems.append({
                "row": idx,
                "student_id": data.loc[idx, "student_id"],
                "field": "performance_level",
                "error": "Performance level does not match avg_score"
            })

    # ============================================================
    # 14) التحقق من courses
    # ============================================================

    if "courses" in data.columns:

        for idx in data.index:

            courses = data.loc[idx, "courses"]

            if isinstance(courses, list):

                # إزالة الفراغات من أسماء المواد للفحص
                cleaned_courses = [
                    str(course).strip()
                    for course in courses
                ]

                # اكتشاف المواد المكررة
                if len(cleaned_courses) != len(
                    set(cleaned_courses)
                ):
                    problems.append({
                        "row": idx,
                        "student_id": data.loc[idx, "student_id"],
                        "field": "courses",
                        "error": "Duplicate course found"
                    })

    # ============================================================
    # إنشاء DataFrame للأخطاء
    # ============================================================

    problems_df = pd.DataFrame(problems)

    # إذا لم توجد أخطاء، نضمن وجود الأعمدة
    if problems_df.empty:

        problems_df = pd.DataFrame(
            columns=[
                "row",
                "student_id",
                "field",
                "error"
            ]
        )

    return data, problems_df