{
 "cells": [],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
<<<<<<< HEAD

# Get all unique states
states = datasets['ipc']['State Name'].unique()
print("Available States:")
for i, state in enumerate(sorted(states), 1):
    print(f"{i}. {state}")

# User input
state_name = input("\nEnter state name: ")

# Show available districts for the selected state
state_districts = datasets['ipc'][datasets['ipc']['State Name'].str.lower() == state_name.lower()]['District Name'].unique()
if len(state_districts) > 0:
    print(f"\nAvailable Districts in {state_name}:")
    for i, district in enumerate(sorted(state_districts), 1):
        print(f"{i}. {district}")
    district_name = input("\nEnter district name: ")
else:
    print(f"State '{state_name}' not found.")
    district_name = None

if district_name:
    print("\nAvailable datasets:")
    print("1. ipc")
    print("2. crime_against_women")
    print("3. cyber_crimes")
    print("4. juveniles")
    print("5. missing_persons_2017_2020")
    print("6. missing_persons_2021_onwards")
    
    file_choice = input("\nEnter dataset name: ")
else:
    file_choice = None

# Normalize input
file_choice = file_choice.replace(' ', '_').lower()

if file_choice and file_choice in datasets:
    # Show available crime types
    crime_columns = [col for col in datasets[file_choice].columns if col not in ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
    print(f"\nAvailable crime types in {file_choice} dataset ({len(crime_columns)} total):")
    for i, crime in enumerate(crime_columns, 1):
        print(f"{i}. {crime}")
    
    crime_choice = input("\nEnter crime type (number or name): ")
    
    # Handle number or name input
    if crime_choice.isdigit():
        crime_index = int(crime_choice) - 1
        if 0 <= crime_index < len(crime_columns):
            crime_choice = crime_columns[crime_index]
        else:
            print(f"Invalid number. Choose between 1 and {len(crime_columns)}.")
            print(f"You entered: {crime_choice}")
            crime_choice = None
    elif crime_choice not in crime_columns:
        print(f"Crime type '{crime_choice}' not found in {file_choice} dataset.")
        crime_choice = None
    
    # Case-insensitive matching
    dataset_states = datasets[file_choice]['State Name'].str.lower().values
    dataset_districts = datasets[file_choice]['District Name'].str.lower().values
    
    if (state_name.lower() in dataset_states and 
        district_name.lower() in dataset_districts and 
        crime_choice):
        
        selected_data = datasets[file_choice][
            (datasets[file_choice]['State Name'].str.lower() == state_name.lower()) &
            (datasets[file_choice]['District Name'].str.lower() == district_name.lower())
        ]
        
        if len(selected_data) > 0:
            print(f"\nData for {district_name}, {state_name} - {crime_choice} from {file_choice} dataset:")
            print(selected_data[['State Name', 'District Name', 'Year', crime_choice]])
            
            # Create graphs
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Line graph - Yearly trend for the district
            yearly_data = selected_data.groupby('Year')[crime_choice].sum()
            ax1.plot(yearly_data.index, yearly_data.values, marker='o', linewidth=2)
            ax1.set_title(f'{crime_choice} - Yearly Trend in {district_name}, {state_name}')
            ax1.set_xlabel('Year')
            ax1.set_ylabel('Number of Cases')
            ax1.grid(True)
            
            # Bar graph - Yearly comparison for the district
            ax2.bar(yearly_data.index, yearly_data.values)
            ax2.set_title(f'{crime_choice} - Year-wise Cases in {district_name}, {state_name}')
            ax2.set_xlabel('Year')
            ax2.set_ylabel('Number of Cases')
            ax2.set_xticks(yearly_data.index)
            
            plt.tight_layout()
            plt.show()
        else:
            print(f"No data found for {district_name}, {state_name} in {file_choice} dataset.")
        
    elif not crime_choice:
        pass  # Error already printed above
    else:
        print(f"State '{state_name}' or District '{district_name}' not found in {file_choice} dataset.")
else:
    if file_choice:
        print(f"Dataset '{file_choice}' not available. Choose from: {list(datasets.keys())}")
=======
>>>>>>> 8b4dbc313721a90458b2ca71fdf5834748ee1b9c
