import requests
import pandas as pd
import logging

def extract_api(url, timeout=5):
    logging.info("API extraction started")
    try:
        # يرسل طلب في الحصول على البيانات 
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        #  يحول استجابه api الي ملف بايثون 
        payload = response.json()
        if not payload:
            raise ValueError("Empty API response")
        df = pd.DataFrame(payload)
        logging.info("API records: %s", len(df))
        return df
    except requests.RequestException as exc:
        logging.error("API request failed: %s", exc)
        raise
    except ValueError as exc:
        logging.error("API response invalid: %s", exc)
        raise
