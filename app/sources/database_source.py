import sqlite3
import pandas as pd
import logging

def extract_database(path):
    logging.info("Database extraction started")
    with sqlite3.connect(path) as conn:
        query = """
        SELECT e.student_id, COUNT(*) AS courses_count,
               ROUND(AVG(e.score), 2) AS avg_score,
               GROUP_CONCAT(c.course_name, ' | ') AS courses,
               GROUP_CONCAT(e.semester, ' | ') AS semesters
        FROM enrollments e
        JOIN courses c ON c.course_id = e.course_id
        GROUP BY e.student_id
        """
        df = pd.read_sql_query(query, conn)
    logging.info("Database records: %s", len(df))
    return df
