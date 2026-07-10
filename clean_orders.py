"""
clean_orders.py
Cleans a messy e-commerce/orders CSV export.

Fixes applied:
- Removes duplicate Order IDs (keeps first occurrence)
- Strips extra whitespace from names
- Standardizes name/city capitalization (Title Case)
- Standardizes all dates to YYYY-MM-DD
- Cleans currency values (removes $ signs, fills missing values)
- Standardizes Status values (Title Case, trims whitespace)
- Drops fully blank rows
- Flags rows with invalid/unparseable dates instead of silently guessing

Author: Tehreem Fatima
"""

import pandas as pd
import numpy as np
from datetime import datetime

INPUT_FILE = "messy_orders.csv"
OUTPUT_FILE = "cleaned_orders.csv"
LOG_FILE = "cleaning_report.txt"


def parse_date(value):
    """Try common date formats; return None if unparseable (never guess silently)."""
    if pd.isna(value) or str(value).strip() == "":
        return None
    value = str(value).strip()
    formats = ["%d/%m/%Y", "%Y-%m-%d", "%m-%d-%Y", "%d-%m-%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None  # genuinely invalid (e.g. day 31 of a 13th month)


def clean_amount(value):
    """Strip $ signs and whitespace; return NaN if missing/invalid."""
    if pd.isna(value) or str(value).strip() in ("", "NaN", "nan"):
        return np.nan
    cleaned = str(value).replace("$", "").strip()
    try:
        return round(float(cleaned), 2)
    except ValueError:
        return np.nan


def main():
    df = pd.read_csv(INPUT_FILE)
    report = []
    report.append(f"Original rows: {len(df)}")

    # Drop fully blank rows
    df = df.dropna(how="all")
    df = df[~(df.astype(str).apply(lambda x: x.str.strip()).eq("").all(axis=1))]
    report.append(f"After removing blank rows: {len(df)}")

    # Strip whitespace from text columns
    for col in ["CustomerName", "City", "Status", "Email"]:
        df[col] = df[col].astype(str).str.strip()

    # Standardize capitalization
    df["CustomerName"] = df["CustomerName"].str.title()
    df["City"] = df["City"].str.title()
    df["Status"] = df["Status"].str.title()

    # Remove duplicate Order IDs, keep first
    before = len(df)
    df = df.drop_duplicates(subset="OrderID", keep="first")
    report.append(f"Duplicate OrderIDs removed: {before - len(df)}")

    # Standardize dates, flag unparseable ones instead of guessing
    df["OrderDate_clean"] = df["OrderDate"].apply(parse_date)
    invalid_dates = df[df["OrderDate_clean"].isna()]
    report.append(f"Rows with invalid/unparseable dates (flagged, not guessed): {len(invalid_dates)}")

    # Clean amount column
    df["Amount_clean"] = df["Amount"].apply(clean_amount)
    missing_amounts = df["Amount_clean"].isna().sum()
    report.append(f"Missing/invalid amounts found: {missing_amounts}")

    # Final column order
    df_final = df[["OrderID", "CustomerName", "City", "OrderDate_clean",
                    "Amount_clean", "Status", "Email"]]
    df_final = df_final.rename(columns={
        "OrderDate_clean": "OrderDate",
        "Amount_clean": "Amount"
    })
    df_final["OrderID"] = df_final["OrderID"].astype(int)

    df_final.to_csv(OUTPUT_FILE, index=False)
    report.append(f"Final clean rows: {len(df_final)}")

    with open(LOG_FILE, "w") as f:
        f.write("\n".join(report))

    print("\n".join(report))
    print(f"\nSaved cleaned file to {OUTPUT_FILE}")
    print(f"Saved summary report to {LOG_FILE}")


if __name__ == "__main__":
    main()
