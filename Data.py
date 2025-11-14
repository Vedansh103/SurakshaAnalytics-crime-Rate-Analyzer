# Data.py
# Upgraded crime analysis tool
# Features:
# - Clean datasets
# - Compare multiple crimes in a district (multiple input allowed)
# - Compare same crime across multiple districts (multiple input allowed)
# - Descriptive statistics (multiple crimes allowed)
# - Seaborn plots (modern styling)
# - Flexible multi-value input: names, comma-separated numbers, or "all"
# - Select 'all' districts to analyze at the state level
# - Bar chart comparison for all districts in a state
# - UPDATED: Using try...except for numeric input validation
# - NEW: Identify top N hotspots (Action 6)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import sys

# Seaborn defaults
sns.set(style="whitegrid", palette="deep")


def clean_dataset(df):
    """
    Applies a standard set of cleaning operations to a loaded dataframe.
    """
    print(f"Cleaning dataframe... Original shape: {df.shape}")
    
    # 1. Standardize Key Text Columns (State/District)
    key_cols = ['State Name', 'District Name']
    for col in key_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().str.strip()
            # add any project-specific replacements here if necessary
    
    # 2. Clean and Standardize 'Year' Column
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df = df.dropna(subset=['Year'])
        df['Year'] = df['Year'].astype(int)
    
    # 3. Clean Crime/Data Columns
    metadata_cols = ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']
    crime_cols = [col for col in df.columns if col not in metadata_cols]
    
    if crime_cols:
        for col in crime_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df[crime_cols] = df[crime_cols].fillna(0)
    
    # 4. Drop duplicates
    id_subset = ['State Name', 'District Name', 'Year']
    existing_id_subset = [c for c in id_subset if c in df.columns]
    if existing_id_subset:
        df = df.drop_duplicates(subset=existing_id_subset, keep='first')

    print(f"Cleaning complete. New shape: {df.shape}")
    return df


def load_datasets():
    """
    Loads AND CLEANS all crime datasets from CSV files into a dictionary.
    Returns dict of cleaned DataFrames or None on error.
    
    NOTE: This function already implements the requested try...except FileNotFoundError.
    """
    dataset_paths = {
        'ipc': 'Dataset/crime-by-juveniles-expanded.csv',
        'crime_against_women': 'Dataset/districtwise_crime_against_women_readable.csv',
        'cyber_crimes': 'Dataset/districtwise_cyber_crimes_readable.csv',
        'juveniles': 'Dataset/districtwise_ipc_crimes_readable.csv',
        'missing_persons': 'Dataset/districtwise-missing-persons-merged.csv'
    }
    
    datasets = {}
    try:
        for name, path in dataset_paths.items():
            print(f"Loading dataset: {name} from {path}")
            df = pd.read_csv(path)
            datasets[name] = clean_dataset(df)
        print("\nAll datasets loaded and cleaned successfully.")
        return datasets
    except FileNotFoundError as e:
        print(f"Error loading dataset: {e}")
        print("Please make sure the 'Dataset' folder and all CSV files are in the correct location.")
        return None
    except Exception as e:
        print(f"An error occurred during loading or cleaning: {e}")
        return None


def get_state_choice(all_states):
    """
    Prompts the user to select a state from the provided list and validates it.
    Returns the chosen cleaned state name (lowercase) or None.
    """
    print("\nAvailable States:")
    for i, state in enumerate(sorted(all_states), 1):
        print(f"{i}. {state}")
    
    state_name = input("\nEnter state name (or part of it): ").lower().strip()
    if not state_name:
        print("No input provided.")
        return None
    
    matching_states = [state for state in all_states if state_name in state]
    if not matching_states:
        print(f"State '{state_name}' not found.")
        return None
    
    chosen_state = matching_states[0]
    if state_name != chosen_state:
        print(f"Found matching state: {chosen_state}")
    return chosen_state


def get_district_choice(state_name, master_data):
    """
    Prompts the user to select a district for the given state.
    Returns the chosen district name (cleaned) or 'all' or None.
    """
    state_districts = master_data[master_data['State Name'] == state_name]['District Name'].unique()
    if len(state_districts) == 0:
        print(f"No districts found for state '{state_name}'.")
        return None
    
    print(f"\nAvailable Districts in {state_name}:")
    for i, district in enumerate(sorted(state_districts), 1):
        print(f"{i}. {district}")
    
    # *** CHANGED: Added 'all' option ***
    print(f"Or type 'all' to select all districts in {state_name}.")
    district_name = input("\nEnter district name (or part of it, or 'all'): ").lower().strip()
    
    if not district_name:
        print("No input provided.")
        return None
        
    # *** CHANGED: Handle 'all' input ***
    if district_name == 'all':
        return 'all'
    
    matching_districts = [d for d in state_districts if district_name in d]
    if not matching_districts:
        print(f"District '{district_name}' not found in {state_name}.")
        return None
    
    chosen_district = matching_districts[0]
    if district_name != chosen_district:
        print(f"Found matching district: {chosen_district}")
    return chosen_district


def get_dataset_choice(dataset_names):
    """
    Prompts the user to select a dataset by name or number.
    Returns dataset key or None.
    
    UPDATED: Uses try...except ValueError for numeric input.
    """
    print("\nAvailable datasets:")
    for i, name in enumerate(dataset_names, 1):
        print(f"{i}. {name}")
    
    file_choice = input("\nEnter dataset name (number or name): ").strip()
    if not file_choice:
        print("No input provided.")
        return None
    
    try:
        # Attempt to parse as a number
        idx = int(file_choice) - 1
        if 0 <= idx < len(dataset_names):
            return dataset_names[idx]
        # If it's a number but out of range, it will fall to the 'Invalid' message
    except ValueError:
        # Not a number, treat as a name
        file_choice_normalized = file_choice.replace(' ', '_').lower()
        if file_choice_normalized in dataset_names:
            return file_choice_normalized
    
    # This will be hit if:
    # 1. It was a number but out of range
    # 2. It was a name, but not found
    print(f"Invalid dataset choice '{file_choice}'.")
    return None


def get_crime_choice(dataset):
    """
    Prompts the user to select a single crime type from the chosen dataset.
    Returns chosen crime column name or None.
    
    UPDATED: Uses try...except ValueError for numeric input.
    """
    crime_columns = [col for col in dataset.columns if col not in 
                     ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
    if not crime_columns:
        print("No crime-specific columns found in this dataset.")
        return None
    
    print(f"\nAvailable crime types ({len(crime_columns)} total):")
    for i, crime in enumerate(crime_columns, 1):
        print(f"{i}. {crime}")
    
    crime_choice = input("\nEnter crime type (number or name): ").strip()
    if not crime_choice:
        print("No input provided.")
        return None
    
    try:
        # Attempt to parse as a number
        crime_index = int(crime_choice) - 1
        if 0 <= crime_index < len(crime_columns):
            return crime_columns[crime_index]
        else:
            print(f"Invalid number. Choose between 1 and {len(crime_columns)}.")
            return None
    except ValueError:
        # Not a number, treat as a name
        if crime_choice in crime_columns:
            return crime_choice
        else:
            matching_crimes = [c for c in crime_columns if crime_choice.lower() in c.lower()]
            if matching_crimes:
                chosen_crime = matching_crimes[0]
                print(f"Found matching crime: {chosen_crime}")
                return chosen_crime
            
    # If it's not a valid number and not a valid name
    print(f"Crime type '{crime_choice}' not found.")
    return None


def parse_multiple_selection(user_input, available_list, allow_all=True):
    """
    Parse a user_input string for multiple selections.
    - user_input can be comma-separated numbers (1-based), comma-separated names (partial or exact),
      or the word 'all' to select everything (if allow_all True).
    - available_list is a list of available values (strings). Comparison is case-insensitive.
    Returns a list of matched available_list values (exact strings from available_list, in original form).
    
    UPDATED: Uses try...except ValueError for numeric input.
    """
    if not user_input or not user_input.strip():
        return []
    s = user_input.strip()
    lower_avail = [a.lower() for a in available_list]

    # allow "all"
    if allow_all and s.lower() == 'all':
        return list(available_list)

    parts = [p.strip() for p in s.split(',') if p.strip()]
    results = []
    for p in parts:
        try:
            # Attempt numeric selection
            idx = int(p) - 1
            if 0 <= idx < len(available_list):
                results.append(available_list[idx])
            else:
                print(f"Ignored invalid index: {p}")
            # If int() succeeded, we are done with this part
            continue
        except ValueError:
            # Not a number, pass through to name logic
            pass
        
        # --- Name logic (only runs if ValueError occurred) ---
        p_lower = p.lower()
        # try exact case-insensitive match
        if p_lower in lower_avail:
            matched = available_list[lower_avail.index(p_lower)]
            results.append(matched)
            continue
        # try partial match (first match)
        partial_matches = [available_list[i] for i, a in enumerate(lower_avail) if p_lower in a]
        if partial_matches:
            results.append(partial_matches[0])
            continue
        # nothing matched
        print(f"Ignored unknown entry: '{p}'")

    # deduplicate while preserving order
    seen = set()
    final = []
    for r in results:
        if r not in seen:
            final.append(r)
            seen.add(r)
    return final


def show_descriptive_stats(df, crime_cols):
    """
    Shows descriptive statistics (mean, median, std, min, max) for selected crime columns.
    """
    existing = [c for c in crime_cols if c in df.columns]
    if not existing:
        print("None of the requested crime columns exist in this data selection.")
        return
    print("\n=== Descriptive Statistics ===")
    stats = df[existing].describe().T  # mean, std, min, 25%, 50%, 75%, max
    stats['median'] = df[existing].median()
    # show a selection of columns in a readable order
    to_show = ['count', 'mean', 'median', 'std', 'min', '25%', '50%', '75%', 'max']
    for col in to_show:
        if col not in stats.columns:
            # safety: some describe variants might differ
            stats[col] = None
    print(stats[to_show].round(3))


def plot_trends(data, state, district, crime):
    """
    Seaborn line plot for a single crime in a district/state over years.
    If district is 'all', plots the total for the state.
    """
    if data.empty:
        print("No data to plot.")
        return

    if crime not in data.columns:
        print(f"Crime '{crime}' not present in data.")
        return

    yearly = data.groupby("Year")[crime].sum().reset_index()
    
    plot_title = f"{crime} Trend in {district}, {state}"
    if district == 'all':
        plot_title = f"Total {crime} Trend in {state}"
        
    if yearly.empty or yearly[crime].sum() == 0:
        print(f"No reported cases of '{crime}' found in {district}, {state} to plot.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=yearly, x="Year", y=crime, marker="o", ax=ax)
    ax.set_title(plot_title)
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Cases")
    ax.set_xticks(yearly['Year'].astype(int))
    plt.tight_layout()
    plt.show()


def compare_multiple_crimes(df, crimes, state, district):
    """
    Plots multiple crime trends together using seaborn for one district (or state total).
    'crimes' should be a list of column names present in df.
    """
    if df.empty:
        print("No data available for the selected district/state.")
        return

    existing = [c for c in crimes if c in df.columns]
    if not existing:
        print("None of the requested crime columns exist in this data selection.")
        return

    yearly = df.groupby("Year")[existing].sum().reset_index()
    if yearly.empty:
        print("No yearly data to plot.")
        return

    plt.figure(figsize=(12, 6))
    for c in existing:
        sns.lineplot(data=yearly, x="Year", y=c, marker="o", label=c)

    plot_title = f"Crime Comparison in {district}, {state}"
    if district == 'all':
        plot_title = f"Total Crime Comparison in {state}"

    plt.title(plot_title)
    plt.xlabel("Year")
    plt.ylabel("Cases")
    plt.legend(title="Crime Type")
    plt.xticks(yearly['Year'].astype(int))
    plt.tight_layout()
    plt.show()


def compare_districts(dataset, state, districts, crime):
    """
    Compares the same crime across multiple districts in the same state.
    'districts' is a list of district names (cleaned / lowercase).
    """
    existing_districts = []
    for d in districts:
        mask = (dataset['State Name'] == state) & (dataset['District Name'] == d)
        if mask.any():
            existing_districts.append(d)
        else:
            print(f"Warning: district '{d}' not found in state '{state}' or has no records.")
    if not existing_districts:
        print("No valid districts found to compare.")
        return
    if crime not in dataset.columns:
        print(f"Crime '{crime}' not in dataset columns.")
        return

    plt.figure(figsize=(12, 6))
    for d in existing_districts:
        df = dataset[(dataset['State Name'] == state) & (dataset['District Name'] == d)]
        yearly = df.groupby("Year")[crime].sum().reset_index()
        if yearly.empty:
            print(f"No data for '{d}' to plot; skipping.")
            continue
        sns.lineplot(data=yearly, x="Year", y=crime, marker="o", label=d)

    plt.title(f"{crime} Comparison across Districts in {state}")
    plt.xlabel("Year")
    plt.ylabel("Cases")
    plt.legend(title="District")
    plt.tight_layout()
    plt.show()


def plot_all_districts_bar(data, state, crime):
    """
    Seaborn bar plot comparing total of a single crime across all districts in the state.
    'data' is assumed to be already filtered for the state.
    """
    if data.empty:
        print("No data to plot.")
        return

    if crime not in data.columns:
        print(f"Crime '{crime}' not present in data.")
        return

    # Group by district and sum the crime
    district_totals = data.groupby("District Name")[crime].sum().reset_index()
    # Filter out districts with 0 crime for this type
    district_totals = district_totals[district_totals[crime] > 0]
    district_totals = district_totals.sort_values(by=crime, ascending=False)

    if district_totals.empty:
        print(f"No reported cases of '{crime}' found in {state} to plot.")
        return

    # Dynamic figsize
    num_districts = len(district_totals)
    fig_height = max(8, num_districts * 0.4) # Make plot taller for more districts
    fig, ax = plt.subplots(figsize=(12, fig_height))
    
    sns.barplot(data=district_totals, y="District Name", x=crime, palette="viridis", ax=ax)
    ax.set_title(f"Total '{crime}' Cases by District in {state}")
    ax.set_xlabel("Total Number of Cases")
    ax.set_ylabel("District")
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.show()


# *** NEW FUNCTION: Added for Action 6 ***
def show_crime_hotspots(data, state, crime):
    """
    Calculates and prints the top N districts for a specific crime in a state.
    'data' is assumed to be already filtered for the state.
    """
    if data.empty:
        print("No data available to find hotspots.")
        return

    if crime not in data.columns:
        print(f"Crime '{crime}' not present in data.")
        return

    # Group by district and sum the crime
    district_totals = data.groupby("District Name")[crime].sum().reset_index()
    # Filter out districts with 0 crime
    district_totals = district_totals[district_totals[crime] > 0]
    district_totals = district_totals.sort_values(by=crime, ascending=False)

    if district_totals.empty:
        print(f"No reported cases of '{crime}' found in {state} to analyze.")
        return

    # Get N from user
    n_input = input("How many top districts to show? (default: 5): ").strip()
    try:
        n = int(n_input)
        if n <= 0:
            print("Invalid number, defaulting to 5.")
            n = 5
    except ValueError:
        if not n_input: # User just pressed Enter
            n = 5
        else:
            print("Invalid input, defaulting to 5.")
            n = 5
    
    # Get top N
    top_n_districts = district_totals.head(n)

    print(f"\n=== Top {n} Hotspots for '{crime}' in {state} ===")
    print("(Based on total reported cases over the available years)")
    # Reset index for cleaner printing, remove old index
    top_n_districts = top_n_districts[['District Name', crime]].reset_index(drop=True)
    # Make index 1-based for readability
    top_n_districts.index = top_n_districts.index + 1
    print(top_n_districts)


# *** NEW FUNCTIONS: Cross-Dataset Comparison ***
def compare_dataset_types(datasets, state_name, district_name, location_desc):
    """
    Compare different dataset types (IPC vs Cyber vs Women crimes, etc.) for the same location.
    Shows total crime counts across different dataset categories.
    """
    print(f"\n🆚 CROSS-DATASET COMPARISON for {location_desc}")
    print("="*60)
    
    # Get data for each dataset type
    dataset_totals = {}
    dataset_yearly = {}
    
    for dataset_name, dataset_df in datasets.items():
        # Filter data for location
        if district_name == 'all':
            filtered_data = dataset_df[dataset_df['State Name'] == state_name]
        else:
            filtered_data = dataset_df[
                (dataset_df['State Name'] == state_name) & 
                (dataset_df['District Name'] == district_name)
            ]
        
        if not filtered_data.empty:
            # Get crime columns
            crime_columns = [col for col in dataset_df.columns if col not in 
                           ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
            
            if crime_columns:
                # Calculate total crimes for this dataset
                total_crimes = filtered_data[crime_columns].sum().sum()
                dataset_totals[dataset_name] = total_crimes
                
                # Calculate yearly totals for trend comparison
                yearly_totals = filtered_data.groupby('Year')[crime_columns].sum().sum(axis=1).reset_index()
                yearly_totals.columns = ['Year', dataset_name]
                dataset_yearly[dataset_name] = yearly_totals
    
    if not dataset_totals:
        print(f"❌ No data found for {location_desc} across any datasets.")
        return
    
    # Display summary table
    print(f"\n📊 Total Crime Counts by Dataset Type:")
    sorted_totals = sorted(dataset_totals.items(), key=lambda x: x[1], reverse=True)
    for dataset_name, total in sorted_totals:
        print(f"   {dataset_name.replace('_', ' ').title()}: {total:,} total crimes")
    
    # Create comparison plots
    # 1. Bar chart of total crimes by dataset
    plt.figure(figsize=(15, 10))
    
    plt.subplot(2, 1, 1)
    dataset_names = [name.replace('_', ' ').title() for name, _ in sorted_totals]
    totals = [total for _, total in sorted_totals]
    
    sns.barplot(x=dataset_names, y=totals, palette="Set2")
    plt.title(f"Total Crime Comparison by Dataset Type - {location_desc}", fontsize=14, fontweight='bold')
    plt.xlabel("Dataset Type")
    plt.ylabel("Total Crime Count")
    plt.xticks(rotation=45)
    
    # 2. Line plot of trends over time
    plt.subplot(2, 1, 2)
    
    # Merge all yearly data
    if len(dataset_yearly) > 1:
        merged_yearly = None
        for dataset_name, yearly_data in dataset_yearly.items():
            if merged_yearly is None:
                merged_yearly = yearly_data
            else:
                merged_yearly = merged_yearly.merge(yearly_data, on='Year', how='outer')
        
        if merged_yearly is not None:
            merged_yearly = merged_yearly.fillna(0)
            
            for dataset_name in dataset_yearly.keys():
                if dataset_name in merged_yearly.columns:
                    sns.lineplot(data=merged_yearly, x='Year', y=dataset_name, 
                               marker='o', label=dataset_name.replace('_', ' ').title())
            
            plt.title(f"Crime Trends Comparison by Dataset Type - {location_desc}", fontsize=14, fontweight='bold')
            plt.xlabel("Year")
            plt.ylabel("Total Crime Count")
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.xticks(merged_yearly['Year'].astype(int))
    
    plt.tight_layout()
    plt.show()


def compare_states_datasets(datasets, selected_dataset_name, selected_crime_type):
    """
    Compare the same crime type across different states using the selected dataset.
    """
    print(f"\n🌍 CROSS-STATE COMPARISON: {selected_crime_type} from {selected_dataset_name} dataset")
    print("="*80)
    
    selected_dataset = datasets[selected_dataset_name]
    
    if selected_crime_type not in selected_dataset.columns:
        print(f"❌ Crime type '{selected_crime_type}' not found in {selected_dataset_name} dataset.")
        return
    
    # Get user input for states to compare
    available_states = sorted(selected_dataset['State Name'].unique())
    print(f"\nAvailable states in {selected_dataset_name} dataset:")
    for i, state in enumerate(available_states[:15], 1):  # Show first 15 states
        print(f"   {i:2d}. {state.title()}")
    
    if len(available_states) > 15:
        print(f"   ... and {len(available_states) - 15} more states")
    
    states_input = input("\nEnter states to compare (comma-separated numbers or names, or 'all' for top 10): ").strip()
    
    if states_input.lower() == 'all':
        # Get top 10 states by total crime
        state_totals = selected_dataset.groupby('State Name')[selected_crime_type].sum().sort_values(ascending=False)
        chosen_states = state_totals.head(10).index.tolist()
        print(f"\nSelected top 10 states by {selected_crime_type} cases")
    else:
        chosen_states = parse_multiple_selection(states_input, available_states, allow_all=False)
    
    if not chosen_states:
        print("❌ No valid states selected.")
        return
    
    # Create comparison data
    state_comparison = []
    state_yearly = {}
    
    for state in chosen_states:
        state_data = selected_dataset[selected_dataset['State Name'] == state]
        if not state_data.empty:
            total_crimes = state_data[selected_crime_type].sum()
            state_comparison.append({'State': state.title(), 'Total_Crimes': total_crimes})
            
            # Yearly data for trend analysis
            yearly = state_data.groupby('Year')[selected_crime_type].sum().reset_index()
            state_yearly[state] = yearly
    
    if not state_comparison:
        print("❌ No data found for selected states.")
        return
    
    # Convert to DataFrame and sort
    comparison_df = pd.DataFrame(state_comparison)
    comparison_df = comparison_df.sort_values('Total_Crimes', ascending=False)
    
    # Display results
    print(f"\n📊 {selected_crime_type} Comparison Across States:")
    print("="*50)
    for i, (_, row) in enumerate(comparison_df.iterrows(), 1):
        print(f"   {i:2d}. {row['State']}: {row['Total_Crimes']:,} cases")
    
    # Create visualizations
    plt.figure(figsize=(15, 10))
    
    # 1. Bar chart comparison
    plt.subplot(2, 1, 1)
    sns.barplot(data=comparison_df, x='State', y='Total_Crimes', palette='viridis')
    plt.title(f'{selected_crime_type} - Total Cases by State', fontsize=14, fontweight='bold')
    plt.xlabel('State')
    plt.ylabel(f'Total {selected_crime_type} Cases')
    plt.xticks(rotation=45)
    
    # 2. Trend lines for each state
    plt.subplot(2, 1, 2)
    
    for state, yearly_data in state_yearly.items():
        if not yearly_data.empty:
            sns.lineplot(data=yearly_data, x='Year', y=selected_crime_type, 
                        marker='o', label=state.title())
    
    plt.title(f'{selected_crime_type} - Trends Across States', fontsize=14, fontweight='bold')
    plt.xlabel('Year')
    plt.ylabel(f'{selected_crime_type} Cases')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.show()


def safe_input_list(prompt, available_values=None, to_lower=True, allow_all=True):
    """
    Wrapper around parse_multiple_selection that first prints a prompt and optional available_values.
    Returns final validated list (values from available_values) or empty list.
    """
    if available_values is not None:
        print("You may enter comma-separated numbers or names. Enter 'all' to select all available options.")
    raw = input(prompt).strip()
    if available_values is None:
        # just split and return cleaned items
        if not raw:
            return []
        items = [i.strip().lower() if to_lower else i.strip() for i in raw.split(",") if i.strip()]
        return items
    else:
        return parse_multiple_selection(raw, list(available_values), allow_all=allow_all)


def main():
    warnings.filterwarnings('ignore')
    datasets = load_datasets()
    if not datasets:
        return

    print("\n" + "="*60)
    print("🚀 SURAKSHA ANALYTICS - CRIME DATA ANALYSIS TOOL")
    print("="*60)
    print("Please follow the steps in order:")
    print("1️⃣  First: Choose Dataset")
    print("2️⃣  Second: Choose State") 
    print("3️⃣  Third: Choose District")
    print("4️⃣  Fourth: Choose Crime Type")
    print("5️⃣  Finally: Select Analysis Option")
    print("="*60)

    while True:
        # Step 1: Choose dataset first
        file_choice = get_dataset_choice(list(datasets.keys()))
        if not file_choice:
            print("Invalid dataset. Restarting selection...")
            continue

        chosen_dataset_df = datasets[file_choice]
        
        # Step 2: Choose state (using selected dataset)
        dataset_states = chosen_dataset_df['State Name'].unique()
        state_name = get_state_choice(dataset_states)
        if not state_name:
            print("Invalid state. Restarting selection...")
            continue

        # Step 3: Choose district (using selected dataset and state)
        district_name = get_district_choice(state_name, chosen_dataset_df)
        if not district_name:
            print("Invalid district. Restarting selection...")
            continue

        # Step 4: Choose crime type (using selected dataset)
        crime_choice = get_crime_choice(chosen_dataset_df)
        if not crime_choice:
            print("Invalid crime type. Restarting selection...")
            continue

        # *** CHANGED: Conditional filtering ***
        if district_name == 'all':
            # Filter for the state only
            selected_data = chosen_dataset_df[
                (chosen_dataset_df['State Name'] == state_name)
            ]
        else:
            # Original filter for a single district
            selected_data = chosen_dataset_df[
                (chosen_dataset_df['State Name'] == state_name) &
                (chosen_dataset_df['District Name'] == district_name)
            ]

        if selected_data.empty:
            location_desc = f"{district_name}, {state_name}"
            if district_name == 'all':
                location_desc = f"ALL Districts in {state_name}"
            print(f"\nNo data found for {location_desc} in {file_choice} dataset.")
        else:
            display_cols = ['State Name', 'District Name', 'Year']
            if crime_choice in selected_data.columns:
                display_cols.append(crime_choice)
            
            location_desc = f"{district_name}, {state_name}"
            if district_name == 'all':
                location_desc = f"ALL Districts in {state_name}"
            
            print(f"\nData for {location_desc} - {crime_choice} from {file_choice} dataset:")
            print(selected_data[display_cols])

        # *** CHANGED: Dynamic action menu ***
        print("\nChoose an action:")
        if district_name == 'all':
            print(f"1. Plot single crime trend (Total for {state_name})")
            print(f"2. Compare multiple crimes (Total for {state_name})")
        else:
            print(f"1. Plot single crime trend (for {district_name})")
            print(f"2. Compare multiple crimes (for {district_name})")
        print("3. Compare multiple districts (same crime, line plot)")
        print("4. Show descriptive statistics")
        print("5. Compare all districts (Total crime, bar chart)")
        print("6. Identify top N district hotspots")
        print("7. 🆚 Compare different dataset types (IPC vs Cyber vs Women crimes, etc.)")
        print("8. 🌍 Cross-state dataset comparison")
        action = input("Enter choice (1/2/3/4/5/6/7/8): ").strip()

        if action == "1":
            plot_trends(selected_data, state_name, district_name, crime_choice)

        elif action == "2":
            available_crimes = [c for c in chosen_dataset_df.columns if c not in 
                                ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
            print("\nAvailable crime columns (you can use numbers or names; enter 'all' to pick all):")
            for i, c in enumerate(available_crimes, 1):
                print(f"{i}. {c}")
            crimes_input = input("\nEnter crimes (comma-separated numbers or names, or 'all'): ").strip()
            crimes = parse_multiple_selection(crimes_input, available_crimes, allow_all=True)
            if not crimes:
                print("No valid crimes selected. Skipping compare.")
            else:
                compare_multiple_crimes(selected_data, crimes, state_name, district_name)

        elif action == "3":
            state_districts = chosen_dataset_df[chosen_dataset_df['State Name'] == state_name]['District Name'].unique()
            if len(state_districts) == 0:
                print(f"No districts found for state '{state_name}' in this dataset.")
            else:
                print("\nAvailable districts in this dataset (you can use numbers or names; enter 'all' to pick all):")
                for i, d in enumerate(sorted(state_districts), 1):
                    print(f"{i}. {d}")
                districts_input = input("\nEnter districts (comma-separated numbers or names, or 'all'): ").strip()
                chosen_districts = parse_multiple_selection(districts_input, sorted(state_districts), allow_all=True)
                if not chosen_districts:
                    print("No valid districts selected. Skipping compare.")
                else:
                    change_crime = input(f"Compare across districts using which crime? (default: '{crime_choice}'). Enter to accept or type a different crime name/number: ").strip()
                    if change_crime:
                        all_crimes_list = [c for c in chosen_dataset_df.columns if c not in 
                                ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
                        c_list = parse_multiple_selection(change_crime, all_crimes_list, allow_all=False)
                        if c_list:
                            new_crime = c_list[0]
                        else:
                            print("Invalid crime specified; using default.")
                            new_crime = crime_choice
                    else:
                        new_crime = crime_choice
                    compare_districts(chosen_dataset_df, state_name, chosen_districts, new_crime)

        elif action == "4":
            print("\nDo you want statistics for (a) single crime or (b) multiple crimes?")
            sub = input("Enter a or b: ").strip().lower()
            if sub == 'a':
                show_descriptive_stats(selected_data, [crime_choice])
            elif sub == 'b':
                available_crimes = [c for c in chosen_dataset_df.columns if c not in 
                                    ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
                print("\nAvailable crime columns (numbers or names; 'all' also allowed):")
                for i, c in enumerate(available_crimes, 1):
                    print(f"{i}. {c}")
                crimes_input = input("\nEnter crimes (comma-separated numbers or names, or 'all'): ").strip()
                crimes = parse_multiple_selection(crimes_input, available_crimes, allow_all=True)
                if not crimes:
                    print("No valid crimes provided.")
                else:
                    show_descriptive_stats(selected_data, crimes)
            else:
                print("Invalid choice. Returning to main menu.")

        elif action == "5":
            # Get all data for the state, regardless of initial district selection
            state_data = chosen_dataset_df[chosen_dataset_df['State Name'] == state_name]
            
            # Allow user to pick the crime, defaulting to the one already chosen
            change_crime = input(f"Compare all districts using which crime? (default: '{crime_choice}'). Enter to accept or type a different crime name/number: ").strip()
            if change_crime:
                all_crimes_list = [c for c in chosen_dataset_df.columns if c not in 
                                ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
                c_list = parse_multiple_selection(change_crime, all_crimes_list, allow_all=False)
                if c_list:
                    new_crime = c_list[0]
                else:
                    print("Invalid crime specified; using default.")
                    new_crime = crime_choice
            else:
                new_crime = crime_choice
            
            plot_all_districts_bar(state_data, state_name, new_crime)

        # *** NEW ACTION: Added for Action 6 ***
        elif action == "6":
            # Get all data for the state
            state_data = chosen_dataset_df[chosen_dataset_df['State Name'] == state_name]
            
            # Allow user to pick the crime, defaulting to the one already chosen
            change_crime = input(f"Analyze hotspots for which crime? (default: '{crime_choice}'). Enter to accept or type a different crime name/number: ").strip()
            if change_crime:
                all_crimes_list = [c for c in chosen_dataset_df.columns if c not in 
                                ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
                c_list = parse_multiple_selection(change_crime, all_crimes_list, allow_all=False)
                if c_list:
                    new_crime = c_list[0]
                else:
                    print("Invalid crime specified; using default.")
                    new_crime = crime_choice
            else:
                new_crime = crime_choice
            
            # Call the new hotspot function
            show_crime_hotspots(state_data, state_name, new_crime)

        # *** NEW ACTION: Cross-Dataset Comparison (Action 7) ***
        elif action == "7":
            print("\n🆚 CROSS-DATASET COMPARISON")
            print("This will compare different dataset types (IPC vs Cyber vs Women crimes, etc.)")
            print("for the same location you selected.")
            
            confirmation = input(f"\nProceed with cross-dataset comparison for {location_desc}? (y/n): ").strip().lower()
            if confirmation in ['y', 'yes']:
                compare_dataset_types(datasets, state_name, district_name, location_desc)
            else:
                print("Cross-dataset comparison cancelled.")

        # *** NEW ACTION: Cross-State Comparison (Action 8) ***
        elif action == "8":
            print("\n🌍 CROSS-STATE COMPARISON")
            print(f"This will compare the same crime type ({crime_choice}) across different states")
            print(f"using the {file_choice} dataset.")
            
            confirmation = input(f"\nProceed with cross-state comparison of {crime_choice}? (y/n): ").strip().lower()
            if confirmation in ['y', 'yes']:
                compare_states_datasets(datasets, file_choice, crime_choice)
            else:
                print("Cross-state comparison cancelled.")

        else:
            print("Invalid choice. Showing single-plot by default.")
            plot_trends(selected_data, state_name, district_name, crime_choice)

        print("\n" + "-"*60)
        another = input("Perform another analysis? (yes/no): ").strip().lower()
        if another not in ['yes', 'y']:
            print("Exiting analysis tool. Goodbye!")
            break
        else:
            print("\nStarting new analysis...\n")


if __name__ == "__main__":
    main()