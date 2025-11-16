import pandas as pd
import numpy as np

def combine_csv_files(file1_path, file2_path, output_path):
    """Combine two CSV files keeping only common columns"""
    
    # Read both CSV files
    df1 = pd.read_csv(file1_path)
    df2 = pd.read_csv(file2_path)
    
    print(f"File 1 columns: {list(df1.columns)}")
    print(f"File 2 columns: {list(df2.columns)}")
    
    # Find common columns
    common_columns = list(set(df1.columns) & set(df2.columns))
    print(f"Common columns: {common_columns}")
    
    # Keep only common columns from both dataframes
    df1_filtered = df1[common_columns]
    df2_filtered = df2[common_columns]
    
    # Combine the dataframes
    combined_df = pd.concat([df1_filtered, df2_filtered], ignore_index=True)
    
    # Sort by year if year column exists
    if 'year' in combined_df.columns:
        combined_df = combined_df.sort_values('year')
    
    print(f"Combined data shape: {combined_df.shape}")
    
    # Save combined data
    combined_df.to_csv(output_path, index=False)
    print(f"Combined file saved as: {output_path}")
    
    return combined_df

# Usage example
if __name__ == "__main__":
    # File paths for missing persons data
    file1 = "e:\\suraksha analytics\\districtwise-missing-persons-20172020.csv"
    file2 = "e:\\suraksha analytics\\districtwise-missing-persons-2021-onwards.csv"
    output = "e:\\suraksha analytics\\missing_person.csv"
    
    combined_data = combine_csv_files(file1, file2, output)