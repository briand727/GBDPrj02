=================================================================
                     BudgetCentres Python Suite
                       Developer’s Manual
                       (README2.txt)
=================================================================

1. Project Overview
-------------------
The BudgetCentres project is a Python ETL workflow that:

- Reads ChargeCentres.xlsx from a configurable input folder.
- Loads a SQL Server DataTable with existing budget data.
- Compares Excel and database entries to detect changes.
- Generates a transformed BudgetCentres.xlsx and a preview of proposed changes.
- Logs runtime, errors, and processing progress.

Future Expansion:
The ultimate goal is to load ChargeCentres into a tiered database structure representing organizational hierarchy. The design will include multiple tiers:

1. Tier #1: Frontline Service linked to a Budget Number.
2. Tier #2: The supervisory or managerial unit that Tier #1 reports to.
3. Tier #3: Higher-level organizational structure that Tier #2 units report to.
4. Tier #4 (optional): Additional executive or corporate-level aggregation.

This structure reflects a many-to-one relationship, where multiple lower-tier units report to a single upper-tier entity, allowing for clear hierarchical reporting and consolidated budget tracking across the organization.

Key features of the current system remain fully functional, while this future design will support more sophisticated reporting and organizational analysis.

-----------------------------------------------------------------
2. Folder Structure
-----------------------------------------------------------------
C:\Projects\MBU
¦
+- Input\
¦   +- config.xml                 # Configuration file
+- Output\
¦   +- BudgetCentres.xlsx         # Final output
¦   +- PreviewChanges.xlsx        # Preview of proposed changes
¦   +- DD-BudgetCentres.log       # Daily log files
+- main.py                        # Main orchestrator
+- excel_loader.py                # Excel reading and transformation
+- sql_connector.py               # SQL Server connection and DataTable load
+- comparator.py                  # Comparison logic
+- preview_generator.py           # Generate preview Excel
+- requirements.txt               # Python dependencies

-----------------------------------------------------------------
3. Configuration (config.xml)
-----------------------------------------------------------------
<configuration>
    <paths>
        <inputExcel>C:\Projects\MBU\Input\ChargeCentres.xlsx</inputExcel>
        <sheetName>Sheet1</sheetName>
        <outputFolder>C:\Projects\MBU\Output</outputFolder>
        <outputFileName>BudgetCentres.xlsx</outputFileName>
        <logFileName>BudgetCentres.log</logFileName>
    </paths>
    <database>
        <server>YOUR_SERVER_NAME</server>
        <databaseName>YOUR_DB_NAME</databaseName>
        <tableName>BudgetData</tableName>
        <username>optional_user</username>
        <password>optional_password</password>
    </database>
</configuration>

-----------------------------------------------------------------
4. Python Scripts Overview
-----------------------------------------------------------------

4.1 main.py
- Orchestrates the entire workflow.
- Loads Excel and SQL DataTable, transforms and compares data.
- Generates preview and final output.
- Tracks runtime and logs all major events.

4.2 excel_loader.py
- Reads ChargeCentres.xlsx from the configured path.
- Transforms data into BudgetCentres format:
  - Cost_Code ? 6-digit string
  - Inactive flag based on Budget_Holder = "NOT USED"
  - Adds ModifiedDate column with current datetime

4.3 sql_connector.py
- Connects to SQL Server using SQLAlchemy engine.
- Loads DataTable safely into a Pandas DataFrame.
- Normalizes columns: BudgetCode, BudgetShortName, Inactive
- Avoids PyODBC warnings.

4.4 comparator.py
- Compares Excel BudgetCentres to SQL DataTable.
- Adds columns: BudgetCode, FrontLineService, FrontLineState, ActiveState, Recommendation
- Logic:
  - If Cost_Code not in DataTable ? BudgetCode = "Not Found"
  - If FrontLine changed ? FrontLineState = "Changed"
  - If Inactive changed ? ActiveState = "Changed"
  - Any "Not Found" or "Changed" ? Recommendation = "Review"

4.5 preview_generator.py
- Generates a PreviewChanges.xlsx showing proposed updates to SQL DataTable.
- Useful for review before applying changes.
- Ensures no duplicate Cost_Code + Description combinations.

-----------------------------------------------------------------
5. Dependencies (requirements.txt)
-----------------------------------------------------------------
pandas==2.1.2
numpy==1.26.0
openpyxl==3.1.2
SQLAlchemy==2.0.20
pyodbc==4.0.40

Install with:
> pip install -r requirements.txt

-----------------------------------------------------------------
6. Logging
-----------------------------------------------------------------
- Logs to daily files with DD-BudgetCentres.log format.
- Captures:
  - Program start/end times
  - Runtime
  - Number of rows processed
  - Errors and stack traces

-----------------------------------------------------------------
7. Runtime Tracking
-----------------------------------------------------------------
- Shows HH:mm:ss format in log and console.
- Example:
Program runtime: 00:03:25 (HH:mm:ss)

-----------------------------------------------------------------
8. Recommended Workflow for Developers
-----------------------------------------------------------------
1. Update config.xml with correct paths and database credentials.
2. Install Python dependencies: pip install -r requirements.txt
3. Run main.py to execute full workflow.
4. Check Output folder for:
   - BudgetCentres.xlsx ? final output
   - PreviewChanges.xlsx ? proposed changes
   - Daily log file ? runtime and debug info
5. Review preview before applying changes to the database.

-----------------------------------------------------------------
9. Extending or Modifying
-----------------------------------------------------------------
- Add columns: Update excel_loader.py and comparator.py
- Change inactive logic: Adjust in transform_chargecentres()
- Add database checks: Enhance sql_connector.py
- Email alerts / automation: Wrap main.py in a scheduler and add notifications

=================================================================
End of Developer’s Manual
=================================================================