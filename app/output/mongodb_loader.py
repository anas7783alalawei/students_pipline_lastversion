import logging
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from pymongo import MongoClient


# ============================================================
# CLEAN PYTHON/PANDAS VALUE FOR MONGODB
# ============================================================

def _clean_value(value):

    if value is None:
        return None

    if isinstance(
        value,
        (list, tuple),
    ):

        return [
            _clean_value(item)
            for item in value
        ]

    if isinstance(value, dict):

        return {
            key: _clean_value(item)
            for key, item in value.items()
        }

    try:

        result = pd.isna(value)

        if isinstance(
            result,
            (bool, np.bool_),
        ) and result:

            return None

    except (
        TypeError,
        ValueError,
    ):

        pass

    if isinstance(
        value,
        np.integer,
    ):

        return int(value)

    if isinstance(
        value,
        np.floating,
    ):

        if np.isnan(value):
            return None

        return float(value)

    if isinstance(
        value,
        np.bool_,
    ):

        return bool(value)

    return value


# ============================================================
# LOAD FINAL DATASET INTO MONGODB
# ============================================================

def load_final_to_mongodb(
    df: pd.DataFrame,
    uri: str,
    database_name: str,
    collection_name: str,
    run_id: str,
) -> int:

    """
    Store the final integrated dataset
    in MongoDB.

    The collection represents
    the latest successful pipeline result.
    """

    if "student_id" not in df.columns:

        raise ValueError(
            "Final dataset must contain "
            "student_id."
        )

    if df.empty:

        logging.warning(
            "Final dataset is empty."
        )

        return 0

    # --------------------------------------------------------
    # Connect MongoDB
    # --------------------------------------------------------

    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=5000,
    )

    try:

        # ----------------------------------------------------
        # Test connection
        # ----------------------------------------------------

        client.admin.command(
            "ping"
        )

        database = client[
            database_name
        ]

        collection = database[
            collection_name
        ]

        now = datetime.now(
            timezone.utc
        )

        # ----------------------------------------------------
        # Replace previous final dataset
        # ----------------------------------------------------

        collection.delete_many({})

        documents = []

        # ----------------------------------------------------
        # Convert DataFrame → MongoDB Documents
        # ----------------------------------------------------

        for _, row in df.iterrows():

            document = {
                key: _clean_value(value)
                for key, value
                in row.to_dict().items()
            }

            # Remove MongoDB internal ID
            document.pop(
                "_id",
                None,
            )

            document[
                "pipeline_run_at"
            ] = now

            document[
                "run_id"
            ] = run_id

            document[
                "created_at"
            ] = now

            documents.append(
                document
            )

        # ----------------------------------------------------
        # Insert
        # ----------------------------------------------------

        if not documents:

            return 0

        result = collection.insert_many(
            documents,
            ordered=False,
        )

        # ----------------------------------------------------
        # Unique student ID
        # ----------------------------------------------------

        collection.create_index(
            "student_id",
            unique=True,
        )

        logging.info(
            "MongoDB final load completed."
        )

        logging.info(
            "Inserted records: %s",
            len(result.inserted_ids),
        )

        logging.info(
            "Database: %s",
            database_name,
        )

        logging.info(
            "Collection: %s",
            collection_name,
        )

        return len(
            result.inserted_ids
        )

    except Exception as exc:

        logging.error(
            "MongoDB final load failed: %s",
            exc,
        )

        raise

    finally:

        client.close()














# import logging
# from datetime import datetime, timezone

# import pandas as pd
# import numpy as np
# from pymongo import MongoClient, UpdateOne


# def _clean_value(value):
#     """
#     تنظيف القيم قبل إرسالها إلى MongoDB.

#     يتعامل مع:
#     - القيم الفارغة NaN / None
#     - القوائم Lists
#     - القواميس Dictionaries
#     - القيم الرقمية
#     - النصوص
#     - قيم Pandas / NumPy
#     """

#     # القيم الفارغة الأساسية
#     if value is None:
#         return None

#     # التعامل مع القوائم والمصفوفات
#     if isinstance(value, (list, tuple)):
#         return [_clean_value(item) for item in value]

#     # التعامل مع القواميس
#     if isinstance(value, dict):
#         return {
#             key: _clean_value(item)
#             for key, item in value.items()
#         }

#     # التعامل مع Pandas NA بأمان
#     try:
#         result = pd.isna(value)

#         # pd.isna للقيمة المفردة يعيد bool
#         if isinstance(result, (bool, np.bool_)):
#             if result:
#                 return None

#     except (TypeError, ValueError):
#         pass

#     # تحويل أنواع NumPy إلى أنواع Python العادية
#     if isinstance(value, np.integer):
#         return int(value)

#     if isinstance(value, np.floating):
#         if np.isnan(value):
#             return None
#         return float(value)

#     if isinstance(value, np.bool_):
#         return bool(value)

#     return value

# def load_final_to_mongodb(
#     df: pd.DataFrame,
#     uri: str = "mongodb://localhost:27017/",
#     database_name: str = "student_data",
#     collection_name: str = "students_final",
#     run_id: str | None = None,
# ) -> int:
#     """
#     Upsert the final integrated dataset into MongoDB.

#     `student_id` is the business key. The source collection is kept separate
#     from `students_final` so raw MongoDB data is not destroyed.
#     """
#     if "student_id" not in df.columns:
#         raise ValueError("Final dataset must contain student_id.")

#     if df.empty:
#         logging.warning("Final dataset is empty; nothing will be loaded.")
#         return 0

#     client = MongoClient(uri, serverSelectionTimeoutMS=5000)

#     try:
#         client.admin.command("ping")

#         collection = client[database_name][collection_name]
#         now = datetime.now(timezone.utc)

#         operations = []

#         for _, row in df.iterrows():
#             document = {
#                 key: _clean_value(value)
#                 for key, value in row.to_dict().items()
#             }

#             student_id = document.get("student_id")
#             if student_id is None:
#                 continue

#             document["pipeline_run_at"] = now
#             document["run_id"] = run_id

#             # Remove an old MongoDB id if one somehow exists in the dataframe.
#             document.pop("_id", None)

#             operations.append(
#                 UpdateOne(
#                     {"student_id": student_id},
#                     {
#                         "$set": document,
#                         "$setOnInsert": {
#                             "created_at": now,
#                         },
#                     },
#                     upsert=True,
#                 )
#             )

#         if not operations:
#             return 0

#         result = collection.bulk_write(
#             operations,
#             ordered=False,
#         )

#         logging.info(
#             "MongoDB final load completed | matched=%s modified=%s "
#             "inserted=%s upserts=%s",
#             result.matched_count,
#             result.modified_count,
#             result.inserted_count,
#             len(result.upserted_ids),
#         )

#         collection.create_index("student_id", unique=True)

#         return result.upserted_count + result.modified_count

#     except Exception as exc:
#         logging.error("MongoDB final load failed: %s", exc)
#         raise
#     finally:
#         client.close()
