
import pandas as pd


def clean_mongodb(df):
    """
    Clean MongoDB data and return a cleaned DataFrame.
    MongoDB results remain separate from the main integrated dataset.
    """

    data = df.copy()

    # --------------------------------
    # Normalize column names
    # --------------------------------
    data.columns = [
        str(col).strip().lower().replace(" ", "_")
        for col in data.columns
    ]

    # Support both "name" and "student_name"
    if "name" in data.columns and "student_name" not in data.columns:
        data.rename(
            columns={"name": "student_name"},
            inplace=True
        )

    # --------------------------------
    # Convert student_id
    # --------------------------------
    if "student_id" in data.columns:
        data["student_id"] = pd.to_numeric(
            data["student_id"],
            errors="coerce"
        )

        # Remove duplicate student records
        data = data.drop_duplicates(
            subset=["student_id"],
            keep="first"
        ).copy()

    # --------------------------------
    # Clean student name
    # --------------------------------
    if "student_name" in data.columns:

        data["student_name"] = (
            data["student_name"]
            .astype("string")
            .str.strip()
        )

        data.loc[
            data["student_name"].isna()
            | (data["student_name"] == ""),
            "student_name"
        ] = "Unknown"

    # --------------------------------
    # Clean age
    # --------------------------------
    if "age" in data.columns:

        data["age"] = pd.to_numeric(
            data["age"],
            errors="coerce"
        )

        valid_age = data["age"].between(16, 80)

        median_age = data.loc[
            valid_age,
            "age"
        ].median()

        if pd.isna(median_age):
            median_age = 20

        data.loc[
            ~valid_age | data["age"].isna(),
            "age"
        ] = median_age

        data["age"] = (
            data["age"]
            .round()
            .astype(int)
        )

    # --------------------------------
    # Clean email
    # --------------------------------
    if "email" in data.columns:

        data["email"] = (
            data["email"]
            .astype("string")
            .str.strip()
        )

        valid_email = data["email"].str.match(
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
            na=False
        )

        data.loc[
            ~valid_email | data["email"].isna(),
            "email"
        ] = "unknown@example.com"

    # --------------------------------
    # Clean major
    # --------------------------------
    if "major" in data.columns:

        data["major"] = (
            data["major"]
            .astype("string")
            .str.strip()
        )

        # Normalize common variations
        data["major"] = data["major"].replace({
            "computer science": "Computer Science",
            "Computer science": "Computer Science",
            "computer Science": "Computer Science",
            " computer science ": "Computer Science",
            "AI": "Artificial Intelligence",
            "ai": "Artificial Intelligence",
        })

        valid_majors = {
            "Computer Science",
            "Artificial Intelligence",
            "Information Technology",
            "Business Administration",
            "Medicine",
            "Data Science",
            "Information Systems",
            "Cyber Security",
        }

        data.loc[
            ~data["major"].isin(valid_majors)
            | data["major"].isna(),
            "major"
        ] = "Unknown"

    # --------------------------------
    # Clean city
    # --------------------------------
    if "city" in data.columns:

        data["city"] = (
            data["city"]
            .astype("string")
            .str.strip()
            .str.title()
        )

    # --------------------------------
    # Clean GPA
    # --------------------------------
    if "gpa" in data.columns:

        data["gpa"] = pd.to_numeric(
            data["gpa"],
            errors="coerce"
        )

        valid_gpa = data["gpa"].between(0, 4)

        median_gpa = data.loc[
            valid_gpa,
            "gpa"
        ].median()

        if pd.isna(median_gpa):
            median_gpa = 0

        data.loc[
            ~valid_gpa | data["gpa"].isna(),
            "gpa"
        ] = median_gpa

        data["gpa"] = data["gpa"].round(2)

    return data
