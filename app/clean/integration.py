import pandas as pd


# ============================================================
# INTEGRATE CSV + API + SQLITE
# ============================================================

def integrate_data(
    students,
    api,
    db,
):

    """
    Integrate the main sources:

    CSV + API + SQLite
    """

    result = (
        students
        .merge(
            api,
            on="student_id",
            how="inner",
        )
        .merge(
            db,
            on="student_id",
            how="left",
        )
    )

    return result


# ============================================================
# INTEGRATE ALL SOURCES
# ============================================================

def integrate_all_data(
    main_data: pd.DataFrame,
    mongodb_data: pd.DataFrame | None = None,
    web_data: pd.DataFrame | None = None,
) -> pd.DataFrame:

    """
    Merge all sources using student_id.

    Main source:
        CSV + API + SQLite

    Additional sources:
        MongoDB
        Web Scraping
    """

    result = main_data.copy()

    # --------------------------------------------------------
    # Normalize main student_id
    # --------------------------------------------------------

    result["student_id"] = pd.to_numeric(
        result["student_id"],
        errors="coerce",
    )

    # --------------------------------------------------------
    # Generic source merge function
    # --------------------------------------------------------

    def merge_source(
        current,
        source_df,
        source_name,
    ):

        if (
            source_df is None
            or source_df.empty
        ):

            return current

        source = source_df.copy()

        # ----------------------------------------------------
        # Check student_id
        # ----------------------------------------------------

        if "student_id" not in source.columns:

            raise ValueError(
                f"{source_name} source must "
                "contain student_id."
            )

        # ----------------------------------------------------
        # Normalize student_id
        # ----------------------------------------------------

        source["student_id"] = pd.to_numeric(
            source["student_id"],
            errors="coerce",
        )

        source = source.dropna(
            subset=["student_id"]
        )

        # ----------------------------------------------------
        # Remove duplicates
        # ----------------------------------------------------

        source = source.drop_duplicates(
            subset=["student_id"],
            keep="first",
        )

        # ----------------------------------------------------
        # Handle duplicate column names
        # ----------------------------------------------------

        overlapping = [
            column
            for column in source.columns
            if (
                column != "student_id"
                and column in current.columns
            )
        ]

        rename_map = {
            column:
            f"{column}__{source_name}"
            for column in overlapping
        }

        source = source.rename(
            columns=rename_map
        )

        # ----------------------------------------------------
        # Outer merge
        # ----------------------------------------------------

        merged = current.merge(
            source,
            on="student_id",
            how="outer",
        )

        # ----------------------------------------------------
        # Fill missing values
        # ----------------------------------------------------

        for column in overlapping:

            backup = (
                f"{column}__{source_name}"
            )

            if backup in merged.columns:

                if column in merged.columns:

                    merged[column] = (
                        merged[column]
                        .combine_first(
                            merged[backup]
                        )
                    )

                else:

                    merged[column] = (
                        merged[backup]
                    )

                merged.drop(
                    columns=[backup],
                    inplace=True,
                )

        return merged

    # ========================================================
    # ADD MONGODB
    # ========================================================

    result = merge_source(
        result,
        mongodb_data,
        "mongodb",
    )

    # ========================================================
    # ADD WEB SCRAPING
    # ========================================================

    result = merge_source(
        result,
        web_data,
        "web",
    )

    # ========================================================
    # FINAL STUDENT ID
    # ========================================================

    result["student_id"] = pd.to_numeric(
        result["student_id"],
        errors="coerce",
    )

    result = result.dropna(
        subset=["student_id"]
    ).copy()

    result["student_id"] = (
        result["student_id"]
        .astype(int)
    )

    return (
        result
        .drop_duplicates(
            subset=["student_id"],
            keep="first",
        )
        .sort_values("student_id")
        .reset_index(drop=True)
    )


# ============================================================
# TRANSFORMATION
# ============================================================

def transform_data(df):

    df = df.copy()

    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    for column in [
        "age",
        "gpa",
        "attendance",
        "avg_score",
    ]:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # --------------------------------------------------------
    # Age
    # --------------------------------------------------------

    if (
        "age" in df.columns
        and df["age"].notna().any()
    ):

        df["age"] = (
            df["age"]
            .fillna(
                df["age"].median()
            )
            .round()
            .astype(int)
        )

    # --------------------------------------------------------
    # GPA
    # --------------------------------------------------------

    if (
        "gpa" in df.columns
        and df["gpa"].notna().any()
    ):

        df["gpa"] = (
            df["gpa"]
            .fillna(
                df["gpa"].median()
            )
            .round(2)
        )

    # --------------------------------------------------------
    # Attendance
    # --------------------------------------------------------

    if (
        "attendance" in df.columns
        and df["attendance"].notna().any()
    ):

        df["attendance"] = (
            df["attendance"]
            .fillna(
                df["attendance"].median()
            )
            .round(2)
        )

    # --------------------------------------------------------
    # Average Score
    # --------------------------------------------------------

    if (
        "avg_score" in df.columns
        and df["avg_score"].notna().any()
    ):

        df["avg_score"] = (
            df["avg_score"]
            .fillna(
                df["avg_score"].median()
            )
            .round(2)
        )

    # --------------------------------------------------------
    # Performance Level
    # --------------------------------------------------------

    if "gpa" in df.columns:

        df["performance_level"] = pd.cut(
            df["gpa"],
            bins=[
                -0.01,
                1.99,
                2.49,
                2.99,
                3.49,
                4.01,
            ],
            labels=[
                "At Risk",
                "Acceptable",
                "Good",
                "Very Good",
                "Excellent",
            ],
        ).astype("string")

    # --------------------------------------------------------
    # Attendance Status
    # --------------------------------------------------------

    if "attendance" in df.columns:

        df["attendance_status"] = (
            df["attendance"].apply(
                lambda value:
                "Good"
                if (
                    pd.notna(value)
                    and value >= 75
                )
                else "Low"
            )
        )

    return df