
import logging
import pandas as pd
from pymongo import MongoClient


def extract_mongodb(
    uri="mongodb://localhost:27017/",
    database_name="student_data",
    collection_name="students"
):
    """
    Extract student data from MongoDB.
    """

    logging.info("MongoDB extraction started")

    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=5000
    )

    try:
        # Test MongoDB connection
        client.admin.command("ping")

        db = client[database_name]
        collection = db[collection_name]

        # Get all documents without MongoDB's internal _id
        records = list(
            collection.find({}, {"_id": 0})
        )

        df = pd.DataFrame(records)

        logging.info(
            "MongoDB records extracted: %s",
            len(df)
        )

        return df

    except Exception as exc:
        logging.error(
            "MongoDB extraction failed: %s",
            exc
        )
        raise

    finally:
        client.close()
