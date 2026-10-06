import json
import logging
import os
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# ============================================================
# SOURCES
# ============================================================

from app.sources.csv_source import extract_csv
from app.sources.api_source import extract_api
from app.sources.database_source import extract_database
from app.sources.mongodb_source import extract_mongodb
from app.sources.web_scraper import extract_web_source


# ============================================================
# VALIDATION
# ============================================================

from app.validation.quality import (
    validate_student_source,
    validate_api_source,
    validate_db_source,
)

from app.validation.mongodb_validation import validate_mongodb


# ============================================================
# CLEANING
# ============================================================

from app.clean.cleaner import (
    clean_students,
    clean_api,
    clean_db,
)

from app.clean.mongodb_cleaner import clean_mongodb


# ============================================================
# INTEGRATION + TRANSFORMATION
# ============================================================

from app.clean.integration import (
    integrate_data,
    integrate_all_data,
    transform_data,
)


# ============================================================
# OUTPUT + LOGGING
# ============================================================

from app.output.mongodb_loader import load_final_to_mongodb
from app.utils.logger import setup_logger


# ============================================================
# PROJECT SETTINGS
# ============================================================

ROOT = Path(__file__).resolve().parent

# Load .env
load_dotenv(ROOT / ".env")


# ============================================================
# REPAIR INVALID VALUES
# ============================================================

def repair_invalid_values(
    students,
    api,
    db,
    rejected,
):

    students = students.copy()
    api = api.copy()
    db = db.copy()
    rejected = rejected.copy()

    # ========================================================
    # FIX AGE
    # ========================================================

    if "age" in students.columns:

        students["age"] = pd.to_numeric(
            students["age"],
            errors="coerce",
        )

        valid_age = students["age"].between(16, 80)

        age_median = students.loc[
            valid_age,
            "age",
        ].median()

        if pd.isna(age_median):
            age_median = 20

        invalid_age = (
            students["age"].notna()
            & ~valid_age
        )

        for idx in students.index[invalid_age]:

            sid = students.at[idx, "student_id"]
            old_value = students.at[idx, "age"]

            students.at[idx, "age"] = age_median

            rejected.loc[len(rejected)] = [
                sid,
                "Invalid Age",
                "CSV",
                "age",
                old_value,
                age_median,
                "Corrected with median age",
            ]

        missing_age = students["age"].isna()

        for idx in students.index[missing_age]:

            sid = students.at[idx, "student_id"]

            students.at[idx, "age"] = age_median

            rejected.loc[len(rejected)] = [
                sid,
                "Missing Age",
                "CSV",
                "age",
                "",
                age_median,
                "Filled with median age",
            ]

    # ========================================================
    # FIX GPA
    # ========================================================

    if "gpa" in api.columns:

        api["gpa"] = pd.to_numeric(
            api["gpa"],
            errors="coerce",
        )

        valid_gpa = api["gpa"].between(0, 4)

        gpa_median = api.loc[
            valid_gpa,
            "gpa",
        ].median()

        if pd.isna(gpa_median):
            gpa_median = 0

        invalid_gpa = (
            api["gpa"].notna()
            & ~valid_gpa
        )

        for idx in api.index[invalid_gpa]:

            sid = api.at[idx, "student_id"]
            old_value = api.at[idx, "gpa"]

            api.at[idx, "gpa"] = gpa_median

            rejected.loc[len(rejected)] = [
                sid,
                "Invalid GPA",
                "API",
                "gpa",
                old_value,
                gpa_median,
                "Corrected with median GPA",
            ]

        missing_gpa = api["gpa"].isna()

        for idx in api.index[missing_gpa]:

            sid = api.at[idx, "student_id"]

            api.at[idx, "gpa"] = gpa_median

            rejected.loc[len(rejected)] = [
                sid,
                "Missing GPA",
                "API",
                "gpa",
                "",
                gpa_median,
                "Filled with median GPA",
            ]

    # ========================================================
    # FIX ATTENDANCE
    # ========================================================

    if "attendance" in api.columns:

        api["attendance"] = pd.to_numeric(
            api["attendance"],
            errors="coerce",
        )

        valid_attendance = api["attendance"].between(
            0,
            100,
        )

        attendance_median = api.loc[
            valid_attendance,
            "attendance",
        ].median()

        if pd.isna(attendance_median):
            attendance_median = 0

        invalid_attendance = (
            api["attendance"].notna()
            & ~valid_attendance
        )

        for idx in api.index[invalid_attendance]:

            sid = api.at[idx, "student_id"]
            old_value = api.at[idx, "attendance"]
            api["attendance"] = pd.to_numeric(api["attendance"], errors="coerce").astype(float)
            api.at[idx, "attendance"] = attendance_median

            rejected.loc[len(rejected)] = [
                sid,
                "Invalid Attendance",
                "API",
                "attendance",
                old_value,
                attendance_median,
                "Corrected with median attendance",
            ]

        missing_attendance = api["attendance"].isna()

        for idx in api.index[missing_attendance]:

            sid = api.at[idx, "student_id"]

            api.at[idx, "attendance"] = attendance_median

            rejected.loc[len(rejected)] = [
                sid,
                "Missing Attendance",
                "API",
                "attendance",
                "",
                attendance_median,
                "Filled with median attendance",
            ]

    # ========================================================
    # FIX DATABASE SCORE
    # ========================================================

    if "avg_score" in db.columns:

        db["avg_score"] = pd.to_numeric(
            db["avg_score"],
            errors="coerce",
        )

        valid_score = db["avg_score"].between(
            0,
            100,
        )

        score_median = db.loc[
            valid_score,
            "avg_score",
        ].median()

        if pd.isna(score_median):
            score_median = 0

        invalid_score = (
            db["avg_score"].notna()
            & ~valid_score
        )

        for idx in db.index[invalid_score]:

            sid = db.at[idx, "student_id"]
            old_value = db.at[idx, "avg_score"]

            db.at[idx, "avg_score"] = score_median

            rejected.loc[len(rejected)] = [
                sid,
                "Invalid Score",
                "DATABASE",
                "avg_score",
                old_value,
                score_median,
                "Corrected with median score",
            ]

        missing_score = db["avg_score"].isna()

        for idx in db.index[missing_score]:

            sid = db.at[idx, "student_id"]

            db.at[idx, "avg_score"] = score_median

            rejected.loc[len(rejected)] = [
                sid,
                "Missing Score",
                "DATABASE",
                "avg_score",
                "",
                score_median,
                "Filled with median score",
            ]

    return students, api, db, rejected


# ============================================================
# MOCK API SERVER
# ============================================================

class MockAPIHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path != "/students":

            self.send_response(404)
            self.end_headers()

            return

        payload = json.loads(
            (
                ROOT / "data/raw/api_mock.json"
            ).read_text(
                encoding="utf-8"
            )
        )

        body = json.dumps(payload).encode()

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()

        self.wfile.write(body)

    def log_message(self, *args):
        pass


def start_mock_api():

    server = HTTPServer(
        ("127.0.0.1", 0),
        MockAPIHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    url = (
        f"http://127.0.0.1:"
        f"{server.server_port}"
        f"/students"
    )

    return server, url


# ============================================================
# MOCK WEB SERVER
# ============================================================

class MockWebHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path != "/students":

            self.send_response(404)
            self.end_headers()

            return

        body = (
            ROOT / "data/raw/web_students.html"
        ).read_bytes()

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()

        self.wfile.write(body)

    def log_message(self, *args):
        pass


def start_mock_web():

    server = HTTPServer(
        ("127.0.0.1", 0),
        MockWebHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    url = (
        f"http://127.0.0.1:"
        f"{server.server_port}"
        f"/students"
    )

    return server, url


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline():

    start = time.time()

    setup_logger(
        str(
            ROOT / "logs/pipeline.log"
        )
    )

    logging.info(
        "================================================"
    )

    logging.info(
        "STUDENT DATA PIPELINE STARTED"
    )

    logging.info(
        "================================================"
    )

    # ========================================================
    # 1. CONFIGURATION
    # ========================================================

    mongo_uri = os.getenv(
        "MONGODB_URI",
        "mongodb://localhost:27017/",
    )

    mongo_database = os.getenv(
        "MONGODB_DATABASE",
        "student_data",
    )

    mongo_source_collection = os.getenv(
        "MONGODB_SOURCE_COLLECTION",
        "students",
    )

    mongo_final_collection = os.getenv(
        "MONGODB_FINAL_COLLECTION",
        "students_final",
    )

    # ========================================================
    # 2. EXTRACT ALL SOURCES
    #
    # كل استدعاءات مصادر البيانات موجودة هنا
    # ========================================================

    logging.info(
        "STEP 1: EXTRACTING ALL DATA SOURCES"
    )

    # --------------------------------------------------------
    # CSV
    # --------------------------------------------------------

    csv_raw = extract_csv(
        ROOT / "data/raw/students.csv"
    )

    # --------------------------------------------------------
    # API
    # --------------------------------------------------------

    api_server, api_url = start_mock_api()

    try:

        api_raw = extract_api(
            api_url
        )

    finally:

        api_server.shutdown()

    # --------------------------------------------------------
    # SQLite DATABASE
    # --------------------------------------------------------

    db_raw = extract_database(
        ROOT / "database/students.db"
    )

    # --------------------------------------------------------
    # MongoDB SOURCE
    # --------------------------------------------------------

    mongo_raw = extract_mongodb(
        uri=mongo_uri,
        database_name=mongo_database,
        collection_name=mongo_source_collection,
    )

    # --------------------------------------------------------
    # WEB SCRAPING
    # --------------------------------------------------------

    configured_web_url = os.getenv(
        "WEB_SCRAPE_URL",
        "",
    ).strip()

    web_server = None

    if configured_web_url:

        web_url = configured_web_url

        logging.info(
            "Using external Web Scraping URL: %s",
            web_url,
        )

    else:

        web_server, web_url = start_mock_web()

        logging.info(
            "Using built-in Web Scraping demo page."
        )

    try:

        web_data = extract_web_source(
            url=web_url,
            table_index=int(
                os.getenv(
                    "WEB_SCRAPE_TABLE_INDEX",
                    "0",
                )
            ),
            timeout=int(
                os.getenv(
                    "WEB_SCRAPE_TIMEOUT",
                    "10",
                )
            ),
        )

    finally:

        if web_server is not None:
            web_server.shutdown()

    logging.info(
        "All sources extracted successfully."
    )

    # ========================================================
    # 3. VALIDATION
    # ========================================================

    logging.info(
        "STEP 2: VALIDATING SOURCE DATA"
    )

    csv_errors = validate_student_source(
        csv_raw
    )

    api_errors = validate_api_source(
        api_raw
    )

    db_errors = validate_db_source(
        db_raw
    )

    mongo_validated, mongo_problems = (
        validate_mongodb(
            mongo_raw
        )
    )

    rejected = pd.concat(
        [
            csv_errors,
            api_errors,
            db_errors,
            mongo_problems,
        ],
        ignore_index=True,
    )

    rejection_columns = [
        "student_id",
        "error_reason",
        "source",
        "field",
        "old_value",
        "corrected_value",
        "action",
    ]

    for column in rejection_columns:

        if column not in rejected.columns:

            rejected[column] = ""

    rejected = rejected[
        rejection_columns
    ]

    # ========================================================
    # 4. CLEANING
    # ========================================================

    logging.info(
        "STEP 3: CLEANING SOURCE DATA"
    )

    students = clean_students(
        csv_raw
    )

    api = clean_api(
        api_raw
    )

    db = clean_db(
        db_raw
    )

    mongo_cleaned = clean_mongodb(
        mongo_validated
    )

    # ========================================================
    # 5. REPAIR INVALID VALUES
    # ========================================================

    logging.info(
        "STEP 4: REPAIRING INVALID VALUES"
    )

    students, api, db, rejected = (
        repair_invalid_values(
            students,
            api,
            db,
            rejected,
        )
    )

    # ========================================================
    # 6. INTEGRATE CSV + API + SQLITE
    # ========================================================

    logging.info(
        "STEP 5: INTEGRATING CSV + API + SQLITE"
    )

    integrated = integrate_data(
        students,
        api,
        db,
    )

    # ========================================================
    # 7. FIRST TRANSFORMATION
    # ========================================================

    logging.info(
        "STEP 6: TRANSFORMING MAIN DATA"
    )

    transformed = transform_data(
        integrated
    )

    # ========================================================
    # 8. INTEGRATE ALL SOURCES
    #
    # CSV + API + SQLite
    #       +
    # MongoDB + Web Scraping
    # ========================================================

    logging.info(
        "STEP 7: INTEGRATING ALL SOURCES"
    )

    final_data = integrate_all_data(
        main_data=transformed,
        mongodb_data=mongo_cleaned,
        web_data=web_data,
    )

    # ========================================================
    # 9. FINAL TRANSFORMATION
    # ========================================================

    logging.info(
        "STEP 8: FINAL DATA TRANSFORMATION"
    )

    final_data = transform_data(
        final_data
    )

    # ========================================================
    # 10. FINAL VALIDATION
    # ========================================================

    logging.info(
        "STEP 9: FINAL DATA VALIDATION"
    )

    final_invalid = pd.Series(
        False,
        index=final_data.index,
    )

    # --------------------------------------------------------
    # Student ID
    # --------------------------------------------------------

    if "student_id" in final_data.columns:

        final_invalid |= (
            final_data["student_id"].isna()
        )

    # --------------------------------------------------------
    # Numeric validation
    # --------------------------------------------------------

    numeric_rules = [
        ("age", 16, 80),
        ("gpa", 0, 4),
        ("attendance", 0, 100),
        ("avg_score", 0, 100),
    ]

    for column, minimum, maximum in numeric_rules:

        if column in final_data.columns:

            final_invalid |= (
                final_data[column].notna()
                & ~final_data[column].between(
                    minimum,
                    maximum,
                )
            )

    # --------------------------------------------------------
    # Remove invalid final records
    # --------------------------------------------------------

    if final_invalid.any():

        for _, row in final_data[
            final_invalid
        ].iterrows():

            rejected.loc[len(rejected)] = [
                row.get(
                    "student_id",
                    "",
                ),
                "Final validation failed",
                "FINAL",
                "",
                "",
                "",
                "Record excluded",
            ]

        final_data = final_data[
            ~final_invalid
        ].copy()

    # ========================================================
    # 11. FINAL DATA TYPE NORMALIZATION
    # ========================================================

    final_data["student_id"] = (
        pd.to_numeric(
            final_data["student_id"],
            errors="coerce",
        )
        .astype("Int64")
    )

    final_data = final_data.dropna(
        subset=["student_id"]
    ).copy()

    final_data["student_id"] = (
        final_data["student_id"]
        .astype(int)
    )

    final_data = (
        final_data
        .drop_duplicates(
            subset=["student_id"],
            keep="first",
        )
        .sort_values("student_id")
        .reset_index(drop=True)
    )

    # ========================================================
    # 12. LOAD FINAL DATA INTO MONGODB
    # ========================================================

    logging.info(
        "STEP 10: LOADING FINAL DATA INTO MONGODB"
    )

    run_id = uuid.uuid4().hex

    loaded_count = load_final_to_mongodb(
        df=final_data,
        uri=mongo_uri,
        database_name=mongo_database,
        collection_name=mongo_final_collection,
        run_id=run_id,
    )

    # ========================================================
    # 13. SAVE REJECTED RECORDS
    # ========================================================

    rejected.to_csv(
        ROOT
        / "data/rejected/rejected_records.csv",
        index=False,
    )

    # ========================================================
    # 14. PIPELINE SUMMARY
    # ========================================================

    elapsed = time.time() - start

    logging.info(
        "================================================"
    )

    logging.info(
        "PIPELINE COMPLETED SUCCESSFULLY"
    )

    logging.info(
        "CSV records       : %s",
        len(csv_raw),
    )

    logging.info(
        "API records       : %s",
        len(api_raw),
    )

    logging.info(
        "SQLite records    : %s",
        len(db_raw),
    )

    logging.info(
        "MongoDB records   : %s",
        len(mongo_raw),
    )

    logging.info(
        "Web records       : %s",
        len(web_data),
    )

    logging.info(
        "Final records     : %s",
        len(final_data),
    )

    logging.info(
        "Rejected records  : %s",
        len(rejected),
    )

    logging.info(
        "MongoDB inserted  : %s",
        loaded_count,
    )

    logging.info(
        "Processing time   : %.2f seconds",
        elapsed,
    )

    logging.info(
        "Final collection  : %s",
        mongo_final_collection,
    )

    logging.info(
        "================================================"
    )

    return final_data, rejected


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    run_pipeline()