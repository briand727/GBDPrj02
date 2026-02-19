import pandas as pd
import xml.etree.ElementTree as ET
import os

def read_excel_from_config(config_path):
    try:
        # Load the XML config file
        tree = ET.parse(config_path)
        root = tree.getroot()

        # Get Excel file path
        excel_file = root.find('excel_file').text
        if not os.path.exists(excel_file):
            raise FileNotFoundError(f'Excel file not found: {excel_file}')  

        # Read the Excel file
        df = pd.read_excel(excel_file)
        return df
    except Exception as e:
        print(f'Error occurred while reading the Excel file: {e}')  
        return None

def main():
    config_path = 'Input/config.xml'
    output_folder = 'Output'

    # Read data from Excel file using the config
    dataframe = read_excel_from_config(config_path)
    if dataframe is not None:
        # Ensure output directory exists
        os.makedirs(output_folder, exist_ok=True)
        # Output results (you can modify this as needed)
        output_file = os.path.join(output_folder, 'output_results.csv')
        dataframe.to_csv(output_file, index=False)
        print(f'Results saved to: {output_file}') 
    else:
        print('Failed to read data from Excel. No results saved.')

if __name__ == '__main__':
    main()