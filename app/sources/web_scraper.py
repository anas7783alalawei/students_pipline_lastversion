import logging
from io import StringIO
from typing import Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup


def extract_web_source(
    url: str,
    table_index: int = 0,
    timeout: int = 10,
    headers: Optional[dict] = None,
) -> pd.DataFrame:

    if not url:
        logging.warning(
            "Web Scraping URL is empty."
        )

        return pd.DataFrame()

    logging.info(
        "Web Scraping started: %s",
        url,
    )

    # --------------------------------------------------------
    # HTTP Headers
    # --------------------------------------------------------

    request_headers = headers or {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/130 Safari/537.36"
        )
    }

    # --------------------------------------------------------
    # Download Web Page
    # --------------------------------------------------------

    response = requests.get(
        url,
        headers=request_headers,
        timeout=timeout,
    )

    response.raise_for_status()

    # --------------------------------------------------------
    # Parse HTML
    # --------------------------------------------------------

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    # --------------------------------------------------------
    # Check HTML Table
    # --------------------------------------------------------

    tables = soup.find_all(
        "table"
    )

    if not tables:

        raise ValueError(
            "No HTML table found on the web page."
        )

    # --------------------------------------------------------
    # Validate Table Index
    # --------------------------------------------------------

    if (
        table_index < 0
        or table_index >= len(tables)
    ):

        raise IndexError(
            f"Invalid table_index={table_index}. "
            f"Available tables: 0-{len(tables)-1}"
        )

    # --------------------------------------------------------
    # Convert HTML Table to DataFrame
    # --------------------------------------------------------

    dataframes = pd.read_html(
        StringIO(response.text)
    )

    df = dataframes[
        table_index
    ].copy()

    # --------------------------------------------------------
    # Normalize Column Names
    # --------------------------------------------------------

    df.columns = [
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
    for column in df.columns
    ]

    # --------------------------------------------------------
    # student_id is required
    # --------------------------------------------------------

    if "student_id" not in df.columns:

        raise ValueError(
            "Web table must contain "
            "'student_id' column."
        )

    # --------------------------------------------------------
    # Clean Student ID
    # --------------------------------------------------------

    df["student_id"] = pd.to_numeric(
        df["student_id"],
        errors="coerce",
    )

    df = df.dropna(
        subset=["student_id"]
    )

    # --------------------------------------------------------
    # Remove Duplicate Students
    # --------------------------------------------------------

    df = df.drop_duplicates(
        subset=["student_id"],
        keep="first",
    )

    df["student_id"] = (
        df["student_id"]
        .astype(int)
    )

    logging.info(
        "Web Scraping completed: %s records",
        len(df),
    )

    return df