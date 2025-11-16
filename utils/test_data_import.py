#!/usr/bin/env python3
"""
Test script to verify Data.py imports and functions work
"""

print("Testing Data.py import and functions...")

try:
    from Data import load_datasets
    print("[OK] Successfully imported load_datasets")
    
    # Test loading datasets
    print("Testing dataset loading...")
    datasets = load_datasets()
    
    if datasets:
        print(f"[OK] Successfully loaded {len(datasets)} datasets")
        print("Available datasets:")
        for name in datasets.keys():
            print(f"  - {name}")
        
        # Test first dataset
        first_dataset = list(datasets.keys())[0]
        df = datasets[first_dataset]
        print(f"\nFirst dataset '{first_dataset}' info:")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        
        if 'State Name' in df.columns:
            states = df['State Name'].unique()
            print(f"  States available: {len(states)}")
            print(f"  Sample states: {list(states)[:3]}")
        
        print("\n[OK] Data loading test successful!")
        print("[OK] Streamlit app should work with this data")
        
    else:
        print("[ERROR] No datasets loaded - check Dataset folder")
        
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
except Exception as e:
    print(f"[ERROR] Error: {e}")

print("\nTest complete.")