import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# Load datasets
datasets = {
    'ipc': pd.read_csv('Dataset/crime-by-juveniles-expanded.csv'),
    'crime_against_women': pd.read_csv('Dataset/districtwise_crime_against_women_readable.csv'),
    'cyber_crimes': pd.read_csv('Dataset/districtwise_cyber_crimes_readable.csv'),
    'juveniles': pd.read_csv('Dataset/districtwise_ipc_crimes_readable.csv'),
    'missing_persons_2017_2020': pd.read_csv('Dataset/districtwise-missing-persons-20172020-cleaned.csv'),
    'missing_persons_2021_onwards': pd.read_csv('Dataset/districtwise-missing-persons-2021-onwards-cleaned.csv')
}

# Get all unique states
states = datasets['ipc']['State Name'].unique()
print("Available States:")
for i, state in enumerate(sorted(states), 1):
    print(f"{i}. {state}")

# User input
state_name = input("\nEnter state name: ")
print("\nAvailable datasets:")
print("1. ipc")
print("2. crime_against_women")
print("3. cyber_crimes")
print("4. juveniles")
print("5. missing_persons_2017_2020")
print("6. missing_persons_2021_onwards")

file_choice = input("\nEnter dataset name: ")

# Normalize input
file_choice = file_choice.replace(' ', '_').lower()

if file_choice in datasets:
    # Show available crime types
    crime_columns = [col for col in datasets[file_choice].columns if col not in ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
    print(f"\nAvailable crime types in {file_choice} dataset:")
    for i, crime in enumerate(crime_columns, 1):
        print(f"{i}. {crime}")
    
    crime_choice = input("\nEnter crime type: ")
    
    # Case-insensitive matching
    dataset_states = datasets[file_choice]['State Name'].str.lower().values
    if state_name.lower() in dataset_states:
        selected_data = datasets[file_choice][datasets[file_choice]['State Name'].str.lower() == state_name.lower()]
        if crime_choice in crime_columns:
            print(f"\nData for {state_name} - {crime_choice} from {file_choice} dataset:")
            print(selected_data[['State Name', 'District Name', 'Year', crime_choice]])
        else:
            print(f"Crime type '{crime_choice}' not found in {file_choice} dataset.")
    else:
        print(f"State '{state_name}' not found in {file_choice} dataset.")
else:
    print(f"Dataset '{file_choice}' not available. Choose from: {list(datasets.keys())}")