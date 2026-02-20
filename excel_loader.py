import pandas as pd
import logging
from datetime import datetime


def load_chargecentres(file_path, sheet_name):
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        logging.info(f"Loaded {len(df)} records from ChargeCentres Excel.")
        return df
    except Exception as e:
        logging.exception(f"Failed to load ChargeCentres Excel: {e}")
        return None


def transform_chargecentres(df):
    try:
        # Required columns
        required_cols = ["Cost_Centre", "Description", "ServiceLine", "Care_Group", "Text12", "Budget_Holder"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # Normalize keys
        df["Cost_Centre"] = df["Cost_Centre"].astype(str).str.zfill(6).str.strip()
        df["Budget_Holder"] = df["Budget_Holder"].astype(str).str.strip()

        # Transform into BudgetCentres
        budget_df = pd.DataFrame()
        budget_df["Cost_Code"] = df["Cost_Centre"]
        budget_df["FrontLine"] = df["Description"]
        budget_df["ServiceLine"] = df["ServiceLine"]
        budget_df["CareGroup"] = df["Care_Group"]
        budget_df["IssueDate"] = df["Text12"]

        # Inactive logic based on Budget_Holder
        budget_df["Inactive"] = df["Budget_Holder"].apply(lambda x: 1 if str(x).upper() == "NOT USED" else 0)
        budget_df["ModifiedDate"] = datetime.now()

        return budget_df

    except Exception:
        logging.exception("Failed to transform ChargeCentres data.")
        return None