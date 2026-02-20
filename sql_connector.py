# sql_connector.py
import xml.etree.ElementTree as ET
import pandas as pd
import logging
from sqlalchemy import create_engine
import urllib


def load_db_config(config_path):
    """Load database configuration from XML file."""
    tree = ET.parse(config_path)
    root = tree.getroot()
    db_config = {
        "server": root.find("database/server").text,
        "database": root.find("database/databaseName").text,
        "table": root.find("database/tableName").text,
        "username": root.find("database/username").text if root.find("database/username") is not None else None,
        "password": root.find("database/password").text if root.find("database/password") is not None else None
    }
    return db_config


def create_sqlalchemy_engine(db_config):
    """Create a SQLAlchemy engine for SQL Server."""
    try:
        if db_config["username"] and db_config["password"]:
            params = urllib.parse.quote_plus(
                f"DRIVER={{SQL Server}};"
                f"SERVER={db_config['server']};"
                f"DATABASE={db_config['database']};"
                f"UID={db_config['username']};"
                f"PWD={db_config['password']};"
                "Encrypt=no;"
            )
        else:
            params = urllib.parse.quote_plus(
                f"DRIVER={{SQL Server}};"
                f"SERVER={db_config['server']};"
                f"DATABASE={db_config['database']};"
                "Trusted_Connection=yes;"
                "Encrypt=no;"
            )

        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
        logging.info(f"Created SQLAlchemy engine for database '{db_config['database']}' on server '{db_config['server']}'")
        return engine
    except Exception as e:
        logging.exception(f"Failed to create SQLAlchemy engine: {e}")
        return None


def load_datatable(engine, table_name):
    """Load the SQL table into a Pandas DataFrame with type normalization."""
    try:
        if not table_name.isidentifier():
            raise ValueError(f"Invalid table name: {table_name}")

        query = f"SELECT * FROM [{table_name}]"
        df = pd.read_sql(query, engine)

        # Check required columns
        required_cols = ["BudgetCode", "BudgetShortName", "Inactive"]
        for col in required_cols:
            if col not in df.columns:
                raise KeyError(f"Required column '{col}' not found in SQL table.")

        # Normalize types
        df["BudgetCode"] = df["BudgetCode"].astype(str).str.zfill(6).str.strip()
        df["BudgetShortName"] = df["BudgetShortName"].astype(str).str.strip()
        df["Inactive"] = df["Inactive"].fillna(0).astype(int)

        #Debug Lines, lists out the database columns avaiable
        #--logging.info(f"Loaded {len(df)} records from DataTable '{table_name}'")
        #--logging.info(f"Columns: {df.columns.tolist()}")

        return df

    except Exception as e:
        logging.exception(f"Failed to load DataTable '{table_name}': {e}")
        return None