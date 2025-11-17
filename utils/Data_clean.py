# Data_clean.py - Unicode-free version for Streamlit compatibility
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import sys
import os
from pathlib import Path

# Seaborn defaults
sns.set(style="whitegrid", palette="deep")

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()
# Dataset is in the parent directory (project root)
DATASET_DIR = SCRIPT_DIR.parent / "Dataset"

def check_dataset_directory():
    if not DATASET_DIR.exists():
        print("[ERROR] Dataset directory not found!")
        print(f"   Expected location: {DATASET_DIR}")
        return False
    return True

def get_dataset_path(filename):
    full_path = DATASET_DIR / filename
    if not full_path.exists():
        print(f"[ERROR] File not found: {filename}")
        return None
    return str(full_path)

def clean_dataset(df):
    print(f"Cleaning dataframe... Original shape: {df.shape}")
    
    # Standardize Key Text Columns
    key_cols = ['State Name', 'District Name']
    for col in key_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().str.strip()
    
    # Clean Year Column
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df = df.dropna(subset=['Year'])
        df['Year'] = df['Year'].astype(int)
    
    # Clean Crime Columns
    metadata_cols = ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']
    crime_cols = [col for col in df.columns if col not in metadata_cols]
    
    if crime_cols:
        for col in crime_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df[crime_cols] = df[crime_cols].fillna(0)
    
    # Drop duplicates
    id_subset = ['State Name', 'District Name', 'Year']
    existing_id_subset = [c for c in id_subset if c in df.columns]
    if existing_id_subset:
        df = df.drop_duplicates(subset=existing_id_subset, keep='first')

    print(f"Cleaning complete. New shape: {df.shape}")
    return df

def load_datasets():
    if not check_dataset_directory():
        return None
    
    dataset_files = {
        'ipc': 'crime-by-juveniles-expanded.csv',
        'crime_against_women': 'districtwise_crime_against_women_readable.csv',
        'cyber_crimes': 'districtwise_cyber_crimes_readable.csv',
        'juveniles': 'districtwise_ipc_crimes_readable.csv',
        'missing_persons': 'districtwise-missing-persons-merged.csv'
    }
    
    datasets = {}
    missing_files = []
    
    print("Checking for required dataset files...")
    
    for name, filename in dataset_files.items():
        file_path = get_dataset_path(filename)
        if file_path is None:
            missing_files.append(filename)
        else:
            print(f"   [OK] Found: {filename}")
    
    if missing_files:
        print(f"\n[ERROR] Missing {len(missing_files)} required files:")
        for file in missing_files:
            print(f"   - {file}")
        return None
    
    print(f"\nLoading {len(dataset_files)} datasets...")
    
    try:
        for name, filename in dataset_files.items():
            file_path = get_dataset_path(filename)
            print(f"Loading dataset: {name} from {filename}")
            df = pd.read_csv(file_path)
            datasets[name] = clean_dataset(df)
        
        print("\n[OK] All datasets loaded successfully!")
        return datasets
        
    except Exception as e:
        print(f"[ERROR] Error during loading: {e}")
        return None

def get_crime_columns(df):
    return [col for col in df.columns if col not in 
            ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]

# Export main functions for Streamlit
__all__ = ['load_datasets', 'get_crime_columns', 'clean_dataset']