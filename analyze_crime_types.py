#!/usr/bin/env python3
"""
Crime Types Analysis Script
Analyzes all available crime types across datasets
"""

import pandas as pd
from pathlib import Path

def analyze_crime_types():
    """Analyze all crime types available in the datasets"""
    
    datasets = {
        'IPC Crimes (Juveniles)': 'Dataset/crime-by-juveniles-expanded.csv',
        'Crime Against Women': 'Dataset/districtwise_crime_against_women_readable.csv', 
        'Cyber Crimes': 'Dataset/districtwise_cyber_crimes_readable.csv',
        'IPC Crimes (General)': 'Dataset/districtwise_ipc_crimes_readable.csv',
        'Missing Persons': 'Dataset/districtwise-missing-persons-merged.csv'
    }

    print('🔍 COMPREHENSIVE CRIME TYPES ANALYSIS')
    print('='*70)

    all_crime_types = []
    dataset_summary = []
    
    for name, file_path in datasets.items():
        try:
            df = pd.read_csv(file_path)
            
            # Get crime columns (exclude metadata)
            metadata_cols = ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']
            crime_cols = [col for col in df.columns if col not in metadata_cols]
            
            all_crime_types.extend(crime_cols)
            dataset_summary.append({
                'dataset': name,
                'crime_count': len(crime_cols),
                'crimes': crime_cols
            })
            
            print(f'\n📊 {name}:')
            print(f'   📁 File: {file_path}')
            print(f'   📈 Total Crime Types: {len(crime_cols)}')
            print(f'   📋 Crime Types:')
            
            # Show all crime types for this dataset
            for i, col in enumerate(crime_cols, 1):
                print(f'      {i:2d}. {col}')
                
        except Exception as e:
            print(f'❌ Error reading {name}: {e}')

    # Summary statistics
    print(f'\n' + '='*70)
    print(f'📊 SUMMARY STATISTICS:')
    print(f'   🎯 Total Datasets: {len(datasets)}')
    print(f'   🎯 Total Crime Types (with duplicates): {len(all_crime_types)}')
    print(f'   🎯 Unique Crime Types: {len(set(all_crime_types))}')
    
    # Show dataset breakdown
    print(f'\n📋 DATASET BREAKDOWN:')
    for item in dataset_summary:
        print(f'   • {item["dataset"]}: {item["crime_count"]} crime types')
    
    # Check for potential missing categories
    print(f'\n🔍 POTENTIAL MISSING CRIME CATEGORIES:')
    common_crime_categories = [
        'Economic Crimes', 'White Collar Crimes', 'Drug Related Crimes',
        'Arms Act Violations', 'Environmental Crimes', 'Railway Crimes',
        'Customs Violations', 'Immigration Violations', 'Excise Violations',
        'Copyright Violations', 'Forest Crimes', 'Railway Property Crimes'
    ]
    
    found_categories = set()
    for crime in all_crime_types:
        crime_lower = crime.lower()
        for category in common_crime_categories:
            if any(keyword in crime_lower for keyword in category.lower().split()):
                found_categories.add(category)
    
    missing_categories = set(common_crime_categories) - found_categories
    
    if missing_categories:
        print("   Categories that might be missing from datasets:")
        for category in sorted(missing_categories):
            print(f"   ❓ {category}")
    else:
        print("   ✅ All major crime categories appear to be covered")
    
    return dataset_summary

if __name__ == "__main__":
    analyze_crime_types()