# main.py
import os
import logging
from datetime import datetime
import xml.etree.ElementTree as ET

from excel_loader import load_chargecentres, transform_chargecentres
from sql_connector import load_db_config, create_sqlalchemy_engine, load_datatable
from comparator import compare_chargecentres_to_datatable
from preview_generator import generate_preview


def load_config(config_path):
    """Load paths and filenames from config XML."""
    tree = ET.parse(config_path)
    root = tree.getroot()
    config = {
        "inputExcel": root.find("paths/inputExcel").text,
        "sheetName": root.find("paths/sheetName").text,
        "outputFolder": root.find("paths/outputFolder").text,
        "outputFile": root.find("paths/outputFileName").text,
        "logBaseName": root.find("paths/logFileName").text
    }
    return config


def setup_logging(output_folder, base_log_name):
    """Configure logging with daily log filename."""
    os.makedirs(output_folder, exist_ok=True)
    day_prefix = datetime.now().strftime("%d")
    log_file = os.path.join(output_folder, f"{day_prefix}-{base_log_name}")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="a"
    )
    logging.info("========== BudgetCentres Job Started ==========")


def main():
    start_time = datetime.now()  # Capture start time
    try:
        base_dir = r"C:\Projects\MBU"
        config_path = os.path.join(base_dir, "Input", "config.xml")
        config = load_config(config_path)

        setup_logging(config["outputFolder"], config["logBaseName"])

        # --- Load Excel ---
        charge_df = load_chargecentres(config["inputExcel"], config["sheetName"])
        if charge_df is None:
            raise Exception("ChargeCentres Excel load failed.")

        budget_df = transform_chargecentres(charge_df)
        if budget_df is None:
            raise Exception("ChargeCentres transform failed.")

        # --- Load SQL DataTable using SQLAlchemy ---
        db_config = load_db_config(config_path)
        engine = create_sqlalchemy_engine(db_config)
        if engine is None:
            raise Exception("Failed to create SQLAlchemy engine.")

        datatable_df = load_datatable(engine, db_config["table"])
        if datatable_df is None:
            raise Exception("DataTable load failed.")

        # --- Compare BudgetCentres with DataTable ---
        budget_df = compare_chargecentres_to_datatable(budget_df, datatable_df)
        if budget_df is None:
            raise Exception("Comparison failed.")

        # --- Generate Preview of Proposed Changes ---
        preview_df = generate_preview(datatable_df, budget_df, config["outputFolder"])

        # --- Save final BudgetCentres Excel safely ---
        output_file = os.path.join(config["outputFolder"], config["outputFile"])
        try:
            budget_df.to_excel(output_file, index=False)
            logging.info(f"BudgetCentres output saved: {output_file}")
        except Exception as e:
            logging.exception(f"Failed to save BudgetCentres Excel: {e}")
            raise
        
        # --- Capture end time and calculate runtime ---
        end_time = datetime.now()
        runtime = end_time - start_time
        logging.info(f"Program completed successfully at {end_time}")
        logging.info(f"Total runtime: {runtime}")
        print(f"SUCCESS: {len(budget_df)} rows processed. Preview saved: {preview_df.shape[0]} rows.")
        print(f"Program runtime: {runtime}")

        #--logging.info("========== Job Completed Successfully ==========")
        #--print(f"SUCCESS: {len(budget_df)} rows processed. Preview saved: {preview_df.shape[0]} rows.")

    except Exception as e:
        end_time = datetime.now()
        runtime = end_time - start_time
        logging.exception(f"FATAL ERROR: {e}")
        logging.info(f"Program terminated at {end_time}, runtime: {runtime}")
        print("FATAL ERROR occurred. Check log for details.")
        print(f"Program runtime until failure: {runtime}")

        #--logging.exception(f"FATAL ERROR: {e}")
        #--print("FATAL ERROR occurred. Check log for details.")


if __name__ == "__main__":
    main()