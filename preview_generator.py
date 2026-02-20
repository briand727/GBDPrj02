# preview_generator.py
import pandas as pd
import os
import logging

def generate_preview(existing_df, budget_df, output_folder):
    """
    Generate a preview Excel file showing proposed changes to the datatable.
    ChangeType: 'Update', 'Swap', 'Insert'
    """
    preview_rows = []

    # Create mappings for fast lookup
    # Map SQL descriptions to SQL codes
    existing_desc_to_code = dict(zip(existing_df["BudgetShortName"], existing_df["BudgetCode"]))

    # Map SQL codes to SQL descriptions
    existing_code_to_desc = dict(zip(existing_df["BudgetCode"], existing_df["BudgetShortName"]))

    for _, row in budget_df.iterrows():
        code = row["Cost_Code"]
        desc = row["FrontLine"]

        if code in existing_code_to_desc:
            old_desc = existing_code_to_desc[code]
            if old_desc != desc:
                # Check if new description exists elsewhere
                if desc in existing_desc_to_code:
                    other_code = existing_desc_to_code[desc]
                    # Swap entries
                    preview_rows.append({
                        "ChangeType": "Swap",
                        "OldCostCode": other_code,
                        "OldDescription": desc,
                        "NewCostCode": code,
                        "NewDescription": desc
                    })
                    preview_rows.append({
                        "ChangeType": "Swap",
                        "OldCostCode": code,
                        "OldDescription": old_desc,
                        "NewCostCode": other_code,
                        "NewDescription": old_desc
                    })
                else:
                    # Simple update of description
                    preview_rows.append({
                        "ChangeType": "Update",
                        "OldCostCode": code,
                        "OldDescription": old_desc,
                        "NewCostCode": code,
                        "NewDescription": desc
                    })
        else:
            # New insertion
            preview_rows.append({
                "ChangeType": "Insert",
                "OldCostCode": "",
                "OldDescription": "",
                "NewCostCode": code,
                "NewDescription": desc
            })

    # Convert to DataFrame
    preview_df = pd.DataFrame(preview_rows)

    # Write to Excel
    os.makedirs(output_folder, exist_ok=True)
    preview_file = os.path.join(output_folder, "PreviewChanges.xlsx")
    preview_df.to_excel(preview_file, index=False)
    logging.info(f"Preview of proposed changes saved: {preview_file}")
    print(f"Preview saved: {preview_file}")
    return preview_df