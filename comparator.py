import pandas as pd
import logging


def compare_chargecentres_to_datatable(budget_df, datatable_df):
    try:
        logging.info("Starting comparison...")

        # ---------------------------
        # Validate required columns
        # ---------------------------
        required_budget_cols = ["Cost_Code", "FrontLine", "Inactive"]
        required_sql_cols = ["BudgetCode", "BudgetShortName", "Inactive"]

        for col in required_budget_cols:
            if col not in budget_df.columns:
                raise KeyError(f"Missing column in budget_df: {col}")

        for col in required_sql_cols:
            if col not in datatable_df.columns:
                raise KeyError(f"Missing column in datatable_df: {col}")

        # ---------------------------
        # Normalize keys
        # ---------------------------
        budget_df["Cost_Code"] = budget_df["Cost_Code"].astype(str).str.zfill(6).str.strip()
        datatable_df["BudgetCode"] = datatable_df["BudgetCode"].astype(str).str.zfill(6).str.strip()

        budget_df["FrontLine"] = budget_df["FrontLine"].astype(str).str.strip()
        datatable_df["BudgetShortName"] = datatable_df["BudgetShortName"].astype(str).str.strip()

        budget_df["Inactive"] = budget_df["Inactive"].fillna(0).astype(int)
        datatable_df["Inactive"] = datatable_df["Inactive"].fillna(0).astype(int)

        # ---------------------------
        # Remove duplicate SQL codes (keep first)
        # ---------------------------
        datatable_df = datatable_df.drop_duplicates(subset=["BudgetCode"])

        # ---------------------------
        # Create lookup dictionaries
        # ---------------------------
        shortname_dict = dict(zip(datatable_df["BudgetCode"], datatable_df["BudgetShortName"]))
        inactive_dict = dict(zip(datatable_df["BudgetCode"], datatable_df["Inactive"]))

        # ---------------------------
        # Initialize new columns
        # ---------------------------
        budget_df["BudgetCode"] = ""
        budget_df["FrontLineService"] = ""
        budget_df["FrontLineState"] = ""
        budget_df["ActiveState"] = ""
        budget_df["Recommendation"] = ""

        # ---------------------------
        # Row comparison
        # ---------------------------
        for i, row in budget_df.iterrows():
            code = row["Cost_Code"]

            if code in shortname_dict:
                budget_df.at[i, "BudgetCode"] = code
                budget_df.at[i, "FrontLineService"] = shortname_dict[code]
            else:
                budget_df.at[i, "BudgetCode"] = "Not Found"
                budget_df.at[i, "FrontLineService"] = "Not Found"

            # Compare FrontLine
            if code in shortname_dict and row["FrontLine"] == shortname_dict[code]:
                budget_df.at[i, "FrontLineState"] = "Same"
            else:
                budget_df.at[i, "FrontLineState"] = "Changed"

            # Compare Inactive
            if code in inactive_dict and row["Inactive"] == inactive_dict[code]:
                budget_df.at[i, "ActiveState"] = "Same"
            else:
                budget_df.at[i, "ActiveState"] = "Changed"

            # Recommendation logic
            if (
                budget_df.at[i, "BudgetCode"] == "Not Found"
                or budget_df.at[i, "FrontLineState"] == "Changed"
                or budget_df.at[i, "ActiveState"] == "Changed"
            ):
                budget_df.at[i, "Recommendation"] = "Review"

            if (i + 1) % 1000 == 0:
                logging.info(f"Compared {i + 1} rows")

        logging.info("Comparison complete.")
        return budget_df

    except Exception as e:
        logging.exception(f"Failed during comparison: {e}")
        return None