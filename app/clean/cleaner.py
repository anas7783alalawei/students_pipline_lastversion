import pandas as pd
# توحيد اسماء الاعمده اما كبتل او سمول 
def normalize_columns(df):
    df=df.copy()
    df.columns=[str(c).strip().lower().replace(" ","_") for c in df.columns]
    return df
# تنظيف البيانات الموجوده في csv
def clean_students(df):
    df=normalize_columns(df)
    df=df.drop_duplicates(subset=["student_id"], keep="first").copy()
    for col in ["student_id","age"]:
        df[col]=pd.to_numeric(df[col],errors="coerce")
    df["student_name"]=df["student_name"].astype("string").str.strip()
    df["major"]=df["major"].astype("string").str.strip().replace({"AI":"Artificial Intelligence"})
    df["city"]=df["city"].astype("string").str.strip().str.title()
    return df
# تنظيف البيانات على api
def clean_api(df):
    df=normalize_columns(df).copy()
    df["student_id"]=pd.to_numeric(df["student_id"],errors="coerce")
    df["gpa"]=pd.to_numeric(df["gpa"],errors="coerce")
    df["attendance"]=pd.to_numeric(df["attendance"],errors="coerce")
    df["status"]=df["status"].astype("string").str.strip().str.title()
    return df
# تنظيف البيانات على DB
def clean_db(df):
    df=normalize_columns(df).copy()
    df["student_id"]=pd.to_numeric(df["student_id"],errors="coerce")
    df["avg_score"]=pd.to_numeric(df["avg_score"],errors="coerce")
    return df
