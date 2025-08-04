import pandas as pd

def extract_text_from_excel(file_path):
    dfs = pd.read_excel(file_path, sheet_name=None)
    all_text = ""
    for sheet_name, df in dfs.items():
        all_text += f"\nSheet: {sheet_name}\n"
        all_text += df.astype(str).to_string(index=False)
    return all_text

def parse_excel(file_path):
    """Parse Excel file and extract text content"""
    try:
        return extract_text_from_excel(file_path)
    except Exception as e:
        print(f"Error parsing Excel {file_path}: {e}")
        return ""
