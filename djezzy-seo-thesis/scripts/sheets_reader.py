#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# sheets_reader.py
# =============================================================================
# Author     : Meguelati Ali Zine El Abidine
# Institution: Batna 1 University – Hadj Lakhdar | 2025–2026
# =============================================================================
# Description:
#   Reads live survey responses directly from Google Sheets (linked to
#   the Google Form created by createDjezzyForm.gs), exports them as a
#   clean CSV file, and optionally triggers the full thesis update pipeline.
#
# Usage:
#   python scripts/sheets_reader.py
#   python scripts/sheets_reader.py --run-pipeline    # also run update_thesis
#
# Prerequisites:
#   1. Run createDjezzyForm.gs once in Apps Script to create the Sheet.
#   2. Copy the Sheet ID from the Apps Script log into SHEET_ID below.
#   3. Share the Sheet with your service account email (Editor access).
#   4. credentials/service_account.json must exist.
# =============================================================================

import os
import sys
import argparse

import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account

# =============================================================================
# CONFIGURATION
# =============================================================================

CREDENTIALS_FILE = "credentials/service_account.json"
SHEET_ID         = "YOUR_GOOGLE_SHEETS_SPREADSHEET_ID"   # from Apps Script log
SHEET_TAB        = "Form Responses 1"                      # default tab name
OUTPUT_CSV       = "data/survey_data_latest.csv"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

# Column names assigned by Script 1 (data_loading.py)
CLEAN_COLUMNS = [
    "timestamp", "gender", "age_group", "education",
    "search_freq", "search_engine", "discovery_action",
    "searched_djezzy", "discovery_channel", "djezzy_page",
    "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7",
]


# =============================================================================
# GOOGLE SHEETS SERVICE
# =============================================================================

def get_sheets_service():
    """
    Authenticates with Google Sheets API v4 using a Service Account.

    Returns:
        Authenticated googleapiclient Resource for Sheets API.
    """
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


# =============================================================================
# READ ALL RESPONSES FROM GOOGLE SHEETS
# =============================================================================

def read_sheet_to_dataframe(service, sheet_id: str, tab: str) -> pd.DataFrame:
    """
    Reads all rows from a Google Sheets tab into a DataFrame.

    The first row is treated as the header (auto-generated column names
    from Google Forms). Returns raw data with original column names.

    Args:
        service:  Authenticated Sheets API service.
        sheet_id: Spreadsheet ID (from the Sheet URL or Apps Script log).
        tab:      Sheet tab name (default: "Form Responses 1").

    Returns:
        Raw DataFrame with all responses including timestamp.
    """
    result = (service.spreadsheets().values()
              .get(spreadsheetId=sheet_id, range=tab)
              .execute())

    rows = result.get("values", [])
    if not rows:
        print("  ⚠ No data found in sheet.")
        return pd.DataFrame()

    header = rows[0]
    data   = rows[1:]

    # Pad short rows with empty strings to match header length
    data = [row + [""] * (len(header) - len(row)) for row in data]

    df = pd.DataFrame(data, columns=header)
    print(f"  ✓ Read {len(df)} responses from Google Sheets "
          f"({len(df.columns)} columns)")
    return df


# =============================================================================
# RENAME COLUMNS TO SHORT VARIABLE NAMES
# =============================================================================

def rename_to_short_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renames raw Google Forms column headers to the short variable names
    used by the Python analysis scripts (Script 1 – data_loading.py).

    Maps the first 17 columns (timestamp + 16 questions) regardless of
    the original verbose question text.

    Args:
        df: Raw DataFrame from read_sheet_to_dataframe().

    Returns:
        DataFrame with short column names.
    """
    if len(df.columns) < len(CLEAN_COLUMNS):
        print(f"  ⚠ Expected {len(CLEAN_COLUMNS)} columns, "
              f"got {len(df.columns)} — skipping rename.")
        return df

    rename_map = {old: new
                  for old, new in zip(df.columns[:len(CLEAN_COLUMNS)],
                                      CLEAN_COLUMNS)}
    df = df.rename(columns=rename_map)
    return df


# =============================================================================
# EXPORT TO CSV
# =============================================================================

def export_to_csv(df: pd.DataFrame, output_path: str) -> None:
    """
    Saves the DataFrame to CSV (UTF-8 with BOM for Excel compatibility).

    Args:
        df:          DataFrame to export.
        output_path: Destination CSV file path.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"  ✓ Saved {len(df)} rows → {output_path}")


# =============================================================================
# PRINT LIVE SUMMARY
# =============================================================================

def print_live_summary(df: pd.DataFrame) -> None:
    """
    Prints a quick summary of the live dataset to the console.

    Shows:
        - Total responses
        - Gender breakdown
        - Djezzy page distribution
        - Likert means (Q1–Q7)
    """
    print("\n  ── Live Dataset Summary ──────────────────────────────────────")
    print(f"  Total responses : {len(df)}")

    if "gender" in df.columns:
        print("\n  Gender:")
        print(df["gender"].value_counts().to_string())

    if "djezzy_page" in df.columns:
        print("\n  Djezzy Google page:")
        print(df["djezzy_page"].value_counts().to_string())

    likert = [c for c in ["Q1","Q2","Q3","Q4","Q5","Q6","Q7"]
              if c in df.columns]
    if likert:
        df_l = df[likert].apply(pd.to_numeric, errors="coerce")
        print("\n  Likert means (Q1–Q7):")
        print(df_l.mean().round(2).to_string())

    print("  ──────────────────────────────────────────────────────────────")


# =============================================================================
# MAIN
# =============================================================================

def main(run_pipeline: bool = False) -> None:
    """
    Main entry point:
        1. Authenticate with Google Sheets API
        2. Read all form responses
        3. Rename columns
        4. Export to CSV
        5. (Optional) trigger the full thesis update pipeline

    Args:
        run_pipeline: If True, also runs update_thesis.regenerate_figures()
                      after exporting the CSV.
    """
    print("=" * 66)
    print("  sheets_reader.py — Live Survey Data Reader")
    print("  Author: Meguelati Ali Zine El Abidine | Batna 1 University")
    print("=" * 66)

    print("\n[1/3] Authenticating with Google Sheets API...")
    service = get_sheets_service()

    print(f"[2/3] Reading responses from Sheet: {SHEET_ID}...")
    df_raw = read_sheet_to_dataframe(service, SHEET_ID, SHEET_TAB)

    if df_raw.empty:
        print("  No responses found. Exiting.")
        return

    df = rename_to_short_columns(df_raw)
    print_live_summary(df)

    print(f"[3/3] Exporting to CSV...")
    export_to_csv(df, OUTPUT_CSV)

    if run_pipeline:
        print("\n── Triggering thesis update pipeline ─────────────────────────")
        # Add parent dir to path so update_thesis is importable
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from update_thesis import regenerate_figures
        regenerate_figures(OUTPUT_CSV, "figures")
        print("\n  ✓ Pipeline complete.")

    print("\n" + "=" * 66)
    print("  ✓ Done.")
    print("=" * 66)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Read live Google Sheets survey responses and export to CSV.")
    parser.add_argument(
        "--run-pipeline", action="store_true",
        help="Also regenerate all thesis figures after exporting CSV.")
    args = parser.parse_args()
    main(run_pipeline=args.run_pipeline)
