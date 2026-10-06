import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
from app.clean.cleaner import clean_students
from app.clean.integration import integrate_data
from app.validation.quality import validate_api_source

def test_csv_loaded():
    df=pd.read_csv(Path(__file__).parents[1]/"data/raw/students.csv")
    assert len(df)>0 and "student_id" in df

def test_api_validation():
    df=pd.read_json(Path(__file__).parents[1]/"data/raw/api_mock.json")
    errors=validate_api_source(df)
    assert set(errors["student_id"])=={1006,1008}

def test_duplicate_removed():
    df=pd.read_csv(Path(__file__).parents[1]/"data/raw/students.csv")
    assert df["student_id"].duplicated().sum()==1
    assert len(clean_students(df))==9

def test_missing_age_strategy():
    df=pd.read_csv(Path(__file__).parents[1]/"data/raw/students.csv")
    cleaned=clean_students(df)
    assert cleaned["age"].isna().sum()==1

def test_integration():
    s=pd.DataFrame({"student_id":[1],"student_name":["A"],"age":[20],"major":["CS"],"city":["Sanaa"]})
    a=pd.DataFrame({"student_id":[1],"gpa":[3.0],"attendance":[80],"status":["Active"]})
    d=pd.DataFrame({"student_id":[1],"courses_count":[1],"avg_score":[80],"courses":["X"],"semesters":["S1"]})
    assert len(integrate_data(s,a,d))==1

def test_rejected_file_created():
    from main import run_pipeline
    run_pipeline()
    p=Path(__file__).parents[1]/"data/rejected/rejected_records.csv"
    assert p.exists() and len(pd.read_csv(p))>0

def test_final_dataset_created():
    p=Path(__file__).parents[1]/"data/processed/final_dataset.csv"
    assert p.exists()

def test_integrate_all_data_preserves_mongo_and_web_ids():
    from app.clean.integration import integrate_all_data

    main = pd.DataFrame({
        "student_id": [1],
        "student_name": ["A"],
        "age": [20],
        "gpa": [3.0],
        "attendance": [80],
        "avg_score": [80],
    })
    mongo = pd.DataFrame({
        "student_id": [2],
        "student_name": ["B"],
        "gpa": [3.5],
    })
    web = pd.DataFrame({
        "student_id": [3],
        "city": ["Sanaa"],
    })

    result = integrate_all_data(main, mongo, web)
    assert set(result["student_id"]) == {1, 2, 3}
