import pandas as pd
import logging

def extract_csv(path):
    logging.info("CSV extraction started")
    df = pd.read_csv(path)
    logging.info("CSV records: %s", len(df))
    return df
