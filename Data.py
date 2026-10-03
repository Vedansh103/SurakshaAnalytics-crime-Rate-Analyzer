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
# - NEW: Advanced Plotly visualizations (Pie, Heatmap, Interactive)
# - NEW: Outlier Detection (Z-score, IQR, Boxplot) in Option 4

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import sys
import os
from pathlib import Path

# Import plotly and scipy (required packages)
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
from scipy.stats import pearsonr

# Seaborn defaults
sns.set(style="whitegrid", palette="deep")

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()
DATASET_DIR = SCRIPT_DIR / "Dataset"

# Crime Categories Definition
CRIME_CATEGORIES = {
    'Violent Crimes': [
        'murder', 'culpable homicide not amounting to murder', 'attempt to murder',
        'causing death by negligence', 'rape', 'attempt to commit rape', 'custodial rape',
        'other rape', 'kidnapping and abduction', 'kidnapping and abduction of women and girls',
        'kidnapping and abduction of others', 'dacoity', 'preparation and assembly for dacoity',
        'robbery', 'riots', 'criminal intimidation', 'assault on women with intent to outrage her modesty',
        'insult to modesty of women', 'cruelty by husband or his relatives', 'importation of girls from foreign countries',
        'causing hurt', 'grievous hurt', 'dowry deaths', 'assault on public servant to deter him from duty',
        'voluntarily causing hurt to deter public servant from duty'
    ],
    'Property Crimes': [
        'theft', 'auto theft', 'burglary', 'criminal breach of trust', 'cheating',
        'counterfeiting', 'arson', 'mischief', 'criminal trespass', 'house-breaking',
        'house trespass', 'theft by servant', 'dishonest misappropriation of property',
        'receiving stolen property', 'criminal misappropriation', 'breach of trust by public servant',
        'breach of trust by banker, merchant or agent'
    ],
    'Economic Crimes': [
        'criminal breach of trust', 'cheating', 'counterfeiting', 'forgery',
        'forgery of valuable security, will, etc', 'forgery for purpose of cheating',
        'using as genuine a forged document', 'currency offences', 'breach of trust by public servant',
        'breach of trust by banker, merchant or agent', 'dishonest misappropriation of property',
        'criminal misappropriation', 'preparing false evidence'
    ],
    'Public Order Crimes': [
        'riots', 'unlawful assembly', 'promoting enmity between different groups',
        'imputations, assertions prejudicial to national-integration', 'public nuisance',
        'negligent conduct with respect to machinery', 'negligent conduct with respect to fire or combustible matter',
        'disobedience to order duly promulgated by public servant', 'threat of injury to public servant',
        'public servant disobeying direction of law', 'public servant framing an incorrect document'
    ],
    'Cyber Crimes': [
        'cyber crimes', 'cybercrime', 'online fraud', 'identity theft', 'hacking',
        'cyber stalking', 'cyber bullying', 'online harassment', 'data theft',
        'credit card fraud', 'internet fraud', 'phishing', 'malware'
    ],
    'Women & Children Crimes': [
        'rape', 'attempt to commit rape', 'custodial rape', 'other rape',
        'assault on women with intent to outrage her modesty', 'insult to modesty of women',
        'cruelty by husband or his relatives', 'dowry deaths', 'importation of girls from foreign countries',
        'kidnapping and abduction of women and girls', 'selling of girls for prostitution',
        'buying of girls for prostitution', 'trafficking', 'immoral traffic (prevention) act',
        'protection of children from sexual offences act', 'child marriage', 'juvenile crimes'
    ]
}

# Risk Score Weights for different crime categories
RISK_WEIGHTS = {
    'Violent Crimes': 3.0,      # Highest weight - most serious
    'Women & Children Crimes': 2.8,
    'Cyber Crimes': 2.0,
    'Property Crimes': 1.5,
    'Economic Crimes': 1.3,
    'Public Order Crimes': 1.2,
    'Drug & Substance': 1.8,
    'Traffic & Vehicle': 1.0    # Lowest weight
}

def calculate_district_risk_score(district_data, crime_columns):
    """
    Calculate comprehensive risk score for a district based on multiple factors.
    Returns a dictionary with overall score and component scores.
    """
    if district_data.empty:
        return None
    
    risk_components = {}
    
    # 1. Total Crime Volume Score (0-30 points)
    total_crimes = district_data[crime_columns].sum().sum()
    volume_score = min(30, (total_crimes / 1000) * 10)  # Normalize to 30 points
    risk_components['volume'] = volume_score
    
    # 2. Crime Severity Score (0-40 points) - weighted by crime category
    severity_score = 0
    for category, crimes in CRIME_CATEGORIES.items():
        weight = RISK_WEIGHTS.get(category, 1.0)
        category_total = 0
        
        for col in crime_columns:
            col_lower = col.lower()
            for crime_keyword in crimes:
                if crime_keyword.lower() in col_lower:
                    category_total += district_data[col].sum()
                    break
        
        severity_score += (category_total / max(1, total_crimes)) * weight * 40
    
    risk_components['severity'] = min(40, severity_score)
    
    # 3. Growth Trend Score (0-20 points) - increasing trends are riskier
    if 'Year' in district_data.columns and len(district_data['Year'].unique()) >= 2:
        yearly_totals = district_data.groupby('Year')[crime_columns].sum().sum(axis=1)
        if len(yearly_totals) >= 2:
            recent_year = yearly_totals.iloc[-1]
            previous_year = yearly_totals.iloc[-2]
            
            if previous_year > 0:
                growth_rate = ((recent_year - previous_year) / previous_year) * 100
                trend_score = min(20, max(0, growth_rate * 2))  # Positive growth = higher risk
            else:
                trend_score = 10  # Neutral if no previous data
        else:
            trend_score = 10
    else:
        trend_score = 10  # Neutral score if no year data
    
    risk_components['trend'] = trend_score
    
    # 4. Crime Diversity Score (0-10 points) - more crime types = higher risk
    non_zero_crimes = sum(1 for col in crime_columns if district_data[col].sum() > 0)
    diversity_score = min(10, (non_zero_crimes / len(crime_columns)) * 10)
    risk_components['diversity'] = diversity_score
    
    # Calculate overall risk score (0-100)
    overall_score = sum(risk_components.values())
    
    # Determine risk level
    if overall_score >= 75:
        risk_level = "🔴 EXTREME RISK"
        color = "red"
    elif overall_score >= 60:
        risk_level = "🟠 HIGH RISK"
        color = "orange"
    elif overall_score >= 40:
        risk_level = "🟡 MODERATE RISK"
        color = "yellow"
    elif overall_score >= 20:
        risk_level = "🟢 LOW RISK"
        color = "green"
    else:
        risk_level = "⚪ MINIMAL RISK"
        color = "gray"
    
    return {
        'overall_score': round(overall_score, 2),
        'risk_level': risk_level,
        'color': color,
        'components': {
            'volume': round(volume_score, 2),
            'severity': round(severity_score, 2),
            'trend': round(trend_score, 2),
            'diversity': round(diversity_score, 2)
        },
        'total_crimes': int(total_crimes),
        'crime_types_active': non_zero_crimes
    }

def calculate_all_districts_risk_scores(dataset, state_name=None):
    """
    Calculate risk scores for all districts in a dataset or specific state.
    Returns a sorted DataFrame with risk scores.
    """
    # Get crime columns
    crime_columns = [col for col in dataset.columns if col not in 
                    ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
    
    if not crime_columns:
        print("❌ No crime data found in dataset.")
        return None
    
    # Filter by state if specified
    if state_name:
        dataset = dataset[dataset['State Name'] == state_name]
    
    if dataset.empty:
        print(f"❌ No data found for state: {state_name}")
        return None
    
    # Calculate risk scores for each district
    risk_scores = []
    
    for (state, district), group in dataset.groupby(['State Name', 'District Name']):
        score_data = calculate_district_risk_score(group, crime_columns)
        
        if score_data:
            risk_scores.append({
                'State': state.title(),
                'District': district.title(),
                'Risk_Score': score_data['overall_score'],
                'Risk_Level': score_data['risk_level'],
                'Total_Crimes': score_data['total_crimes'],
                'Volume_Score': score_data['components']['volume'],
                'Severity_Score': score_data['components']['severity'],
                'Trend_Score': score_data['components']['trend'],
                'Diversity_Score': score_data['components']['diversity'],
                'Active_Crime_Types': score_data['crime_types_active']
            })
    
    if not risk_scores:
        print("❌ Could not calculate risk scores for any district.")
        return None
    
    # Convert to DataFrame and sort by risk score
    risk_df = pd.DataFrame(risk_scores)
    risk_df = risk_df.sort_values('Risk_Score', ascending=False)
    risk_df = risk_df.reset_index(drop=True)
    risk_df.index = risk_df.index + 1  # 1-based index
    
    return risk_df

def display_risk_score_table(risk_df, top_n=None, title="District Risk Scores"):
    """
    Display risk scores in a formatted table.
    """
    if risk_df is None or risk_df.empty:
        print("❌ No risk score data to display.")
        return
    
    display_df = risk_df.head(top_n) if top_n else risk_df
    
    print(f"\n{'='*120}")
    print(f"📊 {title}")
    print(f"{'='*120}")
    
    # Create formatted table
    print(f"\n{'Rank':<6} {'District':<25} {'State':<20} {'Risk Level':<18} {'Score':<8} {'Crimes':<10} {'Vol':<7} {'Sev':<7} {'Trend':<7} {'Div':<7}")
    print(f"{'-'*120}")
    
    for idx, row in display_df.iterrows():
        # Truncate long names
        district = row['District'][:23] + '..' if len(row['District']) > 25 else row['District']
        state = row['State'][:18] + '..' if len(row['State']) > 20 else row['State']
        
        print(f"{idx:<6} {district:<25} {state:<20} {row['Risk_Level']:<18} {row['Risk_Score']:<8.2f} {row['Total_Crimes']:<10,} "
              f"{row['Volume_Score']:<7.1f} {row['Severity_Score']:<7.1f} {row['Trend_Score']:<7.1f} {row['Diversity_Score']:<7.1f}")
    
    print(f"\n{'-'*120}")
    print(f"Legend: Vol=Volume(/30), Sev=Severity(/40), Trend=Growth(/20), Div=Diversity(/10)")
    print(f"Risk Levels: 🔴 EXTREME (75+) | 🟠 HIGH (60+) | 🟡 MODERATE (40+) | 🟢 LOW (20+) | ⚪ MINIMAL (<20)")
    print(f"{'='*120}\n")

def plot_risk_score_visualizations(risk_df, state_name=None):
    """
    Create comprehensive visualizations for risk scores.
    """
    if risk_df is None or risk_df.empty:
        print("❌ No data to visualize.")
        return
    
    # Limit to top 20 for better visualization
    top_districts = risk_df.head(20)
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Horizontal bar chart of overall risk scores
    ax1 = plt.subplot(2, 2, 1)
    colors = top_districts.apply(lambda row: 
        'red' if row['Risk_Score'] >= 75 else
        'orange' if row['Risk_Score'] >= 60 else
        'gold' if row['Risk_Score'] >= 40 else
        'green', axis=1)
    
    ax1.barh(range(len(top_districts)), top_districts['Risk_Score'], color=colors)
    ax1.set_yticks(range(len(top_districts)))
    ax1.set_yticklabels(top_districts['District'].str[:20], fontsize=9)
    ax1.set_xlabel('Risk Score (0-100)', fontweight='bold')
    ax1.set_title('🎯 Top 20 Districts by Risk Score', fontweight='bold', fontsize=12)
    ax1.invert_yaxis()
    ax1.axvline(x=75, color='red', linestyle='--', alpha=0.3, label='Extreme Risk')
    ax1.axvline(x=60, color='orange', linestyle='--', alpha=0.3, label='High Risk')
    ax1.axvline(x=40, color='gold', linestyle='--', alpha=0.3, label='Moderate Risk')
    ax1.legend(fontsize=8)
    
    # 2. Component scores comparison (stacked bar)
    ax2 = plt.subplot(2, 2, 2)
    components = top_districts[['District', 'Volume_Score', 'Severity_Score', 'Trend_Score', 'Diversity_Score']].head(10)
    
    x = range(len(components))
    width = 0.8
    
    ax2.bar(x, components['Volume_Score'], width, label='Volume (30)', color='#FF6B6B')
    ax2.bar(x, components['Severity_Score'], width, bottom=components['Volume_Score'], 
            label='Severity (40)', color='#FFA07A')
    ax2.bar(x, components['Trend_Score'], width, 
            bottom=components['Volume_Score'] + components['Severity_Score'],
            label='Trend (20)', color='#FFD93D')
    ax2.bar(x, components['Diversity_Score'], width,
            bottom=components['Volume_Score'] + components['Severity_Score'] + components['Trend_Score'],
            label='Diversity (10)', color='#6BCF7F')
    
    ax2.set_xticks(x)
    ax2.set_xticklabels(components['District'].str[:15], rotation=45, ha='right', fontsize=8)
    ax2.set_ylabel('Score', fontweight='bold')
    ax2.set_title('📊 Risk Components Breakdown (Top 10)', fontweight='bold', fontsize=12)
    ax2.legend(fontsize=8)
    
    # 3. Risk level distribution (pie chart)
    ax3 = plt.subplot(2, 2, 3)
    risk_counts = risk_df['Risk_Level'].value_counts()
    colors_pie = ['red', 'orange', 'gold', 'green', 'gray']
    ax3.pie(risk_counts.values, labels=risk_counts.index, autopct='%1.1f%%',
            colors=colors_pie[:len(risk_counts)], startangle=90)
    ax3.set_title('🥧 Risk Level Distribution', fontweight='bold', fontsize=12)
    
    # 4. Scatter plot: Total Crimes vs Risk Score
    ax4 = plt.subplot(2, 2, 4)
    scatter_data = risk_df.head(30)
    scatter = ax4.scatter(scatter_data['Total_Crimes'], scatter_data['Risk_Score'],
                         c=scatter_data['Risk_Score'], cmap='RdYlGn_r', s=100, alpha=0.6)
    
    # Add labels for top 5
    for idx, row in scatter_data.head(5).iterrows():
        ax4.annotate(row['District'][:10], (row['Total_Crimes'], row['Risk_Score']),
                    fontsize=8, alpha=0.7)
    
    ax4.set_xlabel('Total Crimes', fontweight='bold')
    ax4.set_ylabel('Risk Score', fontweight='bold')
    ax4.set_title('📈 Crime Volume vs Risk Score', fontweight='bold', fontsize=12)
    plt.colorbar(scatter, ax=ax4, label='Risk Score')
    
    title = f"Risk Score Analysis - {state_name.title()}" if state_name else "Risk Score Analysis - All Districts"
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.995)
    
    plt.tight_layout()
    plt.show()

def check_dataset_directory():
    """
    Check if Dataset directory exists and create helpful error messages if not.
    """
    if not DATASET_DIR.exists():
        print("❌ ERROR: Dataset directory not found!")
        print(f"   Expected location: {DATASET_DIR}")
        print("   Please ensure you have:")
        print("   1. Cloned the complete repository")
        print("   2. The 'Dataset' folder is in the same directory as Data.py")
        print("   3. All CSV files are present in the Dataset folder")
        return False
    return True

def get_dataset_path(filename):
    """
    Get the full path to a dataset file, with proper error handling.
    """
    full_path = DATASET_DIR / filename
    if not full_path.exists():
        print(f"❌ ERROR: File not found: {filename}")
        print(f"   Expected location: {full_path}")
        print("   Please check if the file exists in the Dataset folder")
        return None
    return str(full_path)


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
    Uses robust path handling that works on any system.
    """
    # Check if Dataset directory exists
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
    
    print("🔍 Checking for required dataset files...")
    
    # First, check if all files exist
    for name, filename in dataset_files.items():
        file_path = get_dataset_path(filename)
        if file_path is None:
            missing_files.append(filename)
        else:
            print(f"   ✅ Found: {filename}")
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} required files:")
        for file in missing_files:
            print(f"   - {file}")
        print(f"\n📁 Expected location: {DATASET_DIR}")
        print("🔧 Please ensure all CSV files are present before running the analysis.")
        return None
    
    print(f"\n📊 Loading {len(dataset_files)} datasets...")
    
    try:
        for name, filename in dataset_files.items():
            file_path = get_dataset_path(filename)
            print(f"Loading dataset: {name} from {filename}")
            df = pd.read_csv(file_path)
            datasets[name] = clean_dataset(df)
        
        print("\n✅ All datasets loaded and cleaned successfully!")
        print(f"📍 Working directory: {SCRIPT_DIR}")
        return datasets
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("🔧 Please ensure all CSV files are in the Dataset folder.")
        return None
    except pd.errors.EmptyDataError as e:
        print(f"❌ Empty or corrupted file: {e}")
        print("🔧 Please check the CSV file integrity.")
        return None
    except Exception as e:
        print(f"❌ Unexpected error during loading: {e}")
        print("🔧 Please check file permissions and CSV format.")
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


def categorize_crimes(crime_columns):
    """
    Categorize crimes into logical groups for better user experience.
    """
    categories = {
        'Violent Crimes': [],
        'Property Crimes': [],
        'Cyber Crimes': [],
        'Women & Children': [],
        'Drug & Substance': [],
        'Economic Crimes': [],
        'Public Order': [],
        'Traffic & Vehicle': [],
        'Other Crimes': []
    }
    
    # Define keywords for each category
    violent_keywords = ['murder', 'homicide', 'assault', 'hurt', 'rape', 'acid', 'attack', 'violence', 'kidnapping', 'abduction']
    property_keywords = ['theft', 'burglary', 'robbery', 'dacoity', 'extortion', 'trespass', 'mischief', 'arson']
    cyber_keywords = ['cyber', 'computer', 'electronic', 'online', 'internet', 'digital', 'atm', 'credit card', 'debit card']
    women_children_keywords = ['women', 'child', 'minor', 'girl', 'dowry', 'modesty', 'sexual', 'trafficking', 'prostitution', 'pocso']
    drug_keywords = ['drug', 'narcotic', 'substance', 'ndps', 'alcohol', 'liquor']
    economic_keywords = ['fraud', 'cheating', 'forgery', 'counterfeit', 'bank', 'financial', 'money', 'corruption']
    public_order_keywords = ['rioting', 'unlawful', 'assembly', 'sedition', 'public', 'tranquility', 'enmity']
    traffic_keywords = ['vehicle', 'driving', 'traffic', 'rash', 'negligent', 'hit and run', 'motor']
    
    for crime in crime_columns:
        crime_lower = crime.lower()
        categorized = False
        
        # Check each category
        if any(keyword in crime_lower for keyword in violent_keywords):
            categories['Violent Crimes'].append(crime)
            categorized = True
        elif any(keyword in crime_lower for keyword in property_keywords):
            categories['Property Crimes'].append(crime)
            categorized = True
        elif any(keyword in crime_lower for keyword in cyber_keywords):
            categories['Cyber Crimes'].append(crime)
            categorized = True
        elif any(keyword in crime_lower for keyword in women_children_keywords):
            categories['Women & Children'].append(crime)
            categorized = True
        elif any(keyword in crime_lower for keyword in drug_keywords):
            categories['Drug & Substance'].append(crime)
            categorized = True
        elif any(keyword in crime_lower for keyword in economic_keywords):
            categories['Economic Crimes'].append(crime)
            categorized = True
        elif any(keyword in crime_lower for keyword in public_order_keywords):
            categories['Public Order'].append(crime)
            categorized = True
        elif any(keyword in crime_lower for keyword in traffic_keywords):
            categories['Traffic & Vehicle'].append(crime)
            categorized = True
        
        if not categorized:
            categories['Other Crimes'].append(crime)
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


def get_crime_choice(dataset):
    """
    Enhanced crime selection with categorization for better user experience.
    Returns chosen crime column name or None.
    """
    crime_columns = [col for col in dataset.columns if col not in 
                    ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
    if not crime_columns:
        print("No crime-specific columns found in this dataset.")
        return None
    
    # Handle datasets with many crimes using categories
    if len(crime_columns) > 20:
        print(f"\n📊 This dataset has {len(crime_columns)} crime types. Choose selection method:")
        print("1. Browse by Category (Recommended)")
        print("2. Search by Name")
        print("3. Show All (Full List)")
        
        method = input("Enter choice (1/2/3): ").strip()
        
        if method == "1":
            return get_crime_by_category(crime_columns)
        elif method == "2":
            return get_crime_by_search(crime_columns)
        elif method == "3":
            return get_crime_from_full_list(crime_columns)
        else:
            print("Invalid choice, using category browsing...")
            return get_crime_by_category(crime_columns)
    else:
        # For smaller datasets, show full list
        return get_crime_from_full_list(crime_columns)


def get_crime_by_category(crime_columns):
    """Select crime by browsing categories."""
    categories = categorize_crimes(crime_columns)
    
    print(f"\n🗂️ CRIME CATEGORIES ({len(crime_columns)} total crimes):")
    category_list = list(categories.keys())
    
    for i, (category, crimes) in enumerate(categories.items(), 1):
        print(f"{i}. {category} ({len(crimes)} crimes)")
    
    while True:
        cat_choice = input(f"\nChoose category (1-{len(category_list)}): ").strip()
        try:
            cat_index = int(cat_choice) - 1
            if 0 <= cat_index < len(category_list):
                selected_category = category_list[cat_index]
                crimes_in_category = categories[selected_category]
                
                print(f"\n📋 {selected_category} ({len(crimes_in_category)} crimes):")
                for i, crime in enumerate(crimes_in_category, 1):
                    print(f"{i:2d}. {crime}")
                
                crime_choice = input(f"\nEnter crime number (1-{len(crimes_in_category)}): ").strip()
                try:
                    crime_index = int(crime_choice) - 1
                    if 0 <= crime_index < len(crimes_in_category):
                        return crimes_in_category[crime_index]
                    else:
                        print(f"Invalid number. Choose between 1 and {len(crimes_in_category)}.")
                except ValueError:
                    print("Please enter a valid number.")
            else:
                print(f"Invalid category. Choose between 1 and {len(category_list)}.")
        except ValueError:
            print("Please enter a valid number.")


def get_crime_by_search(crime_columns):
    """Select crime by searching."""
    while True:
        search_term = input("\n🔍 Enter search term (crime name or keyword): ").strip().lower()
        if not search_term:
            print("Please enter a search term.")
            continue
        
        matching_crimes = [c for c in crime_columns if search_term in c.lower()]
        
        if not matching_crimes:
            print(f"No crimes found matching '{search_term}'. Try different keywords.")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                return None
            continue
        
        print(f"\n📋 Found {len(matching_crimes)} matching crimes:")
        for i, crime in enumerate(matching_crimes, 1):
            print(f"{i:2d}. {crime}")
        
        if len(matching_crimes) == 1:
            confirm = input(f"Select '{matching_crimes[0]}'? (y/n): ").strip().lower()
            if confirm == 'y':
                return matching_crimes[0]
        else:
            choice = input(f"Enter number (1-{len(matching_crimes)}) or search again (s): ").strip()
            if choice.lower() == 's':
                continue
            
            try:
                crime_index = int(choice) - 1
                if 0 <= crime_index < len(matching_crimes):
                    return matching_crimes[crime_index]
                else:
                    print(f"Invalid number. Choose between 1 and {len(matching_crimes)}.")
            except ValueError:
                print("Invalid input. Enter a number or 's' to search again.")


def get_crime_from_full_list(crime_columns):
    """Select from full list (for smaller datasets or user preference)."""
    print(f"\nAvailable crime types ({len(crime_columns)} total):")
    for i, crime in enumerate(crime_columns, 1):
        print(f"{i:2d}. {crime}")
    
    crime_choice = input(f"\nEnter crime type (1-{len(crime_columns)} or name): ").strip()
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


def get_crime_suggestions(available_crimes, category=None):
    """Get smart crime suggestions based on category or popularity."""
    if category:
        categories = categorize_crimes(available_crimes)
        if category in categories:
            return categories[category][:10]  # Top 10 from category
    
    # Popular crime suggestions
    popular_keywords = [
        'murder', 'rape', 'theft', 'burglary', 'robbery', 'kidnapping',
        'cyber', 'fraud', 'dowry', 'acid attack', 'assault', 'domestic violence',
        'drug', 'trafficking', 'extortion', 'cheating'
    ]
    
    suggestions = []
    crime_lower = [c.lower() for c in available_crimes]
    
    for keyword in popular_keywords:
        matches = [available_crimes[i] for i, c in enumerate(crime_lower) 
                  if keyword in c and available_crimes[i] not in suggestions]
        suggestions.extend(matches[:2])  # Max 2 per keyword
        if len(suggestions) >= 15:
            break
    
    return suggestions


def enhanced_crime_selection_prompt(available_crimes, max_select=5, context="crimes"):
    """Enhanced helper for crime selection with smart features."""
    if not available_crimes:
        return []
    
    print(f"\n🎯 SELECT {context.upper()} ({len(available_crimes)} available)")
    
    # Show different options based on list size
    if len(available_crimes) > 20:
        print(f"\n📚 This dataset has many crime types. Choose selection method:")
        print("1. 🔥 Quick picks (popular crimes)")
        print("2. 📂 Browse by category") 
        print("3. 🔍 Search & select")
        print("4. 📋 Show full list")
        print("5. ✅ Select ALL crimes")
        
        method = input("Choose method (1-5): ").strip()
        
        if method == "1":
            suggestions = get_crime_suggestions(available_crimes)
            if suggestions:
                print(f"\n⭐ POPULAR {context.upper()}:")
                for i, crime in enumerate(suggestions, 1):
                    print(f"{i:2d}. {crime}")
                
                print(f"\n💡 Select up to {max_select} (examples: '1,3,5' or '1-3' or 'murder,theft' or 'all')")
                selection = input("Your selection: ").strip()
                if selection.lower() in ['all', '*']:
                    print(f"✅ Selected ALL {len(suggestions)} popular crimes!")
                    return suggestions.copy()
                return parse_multiple_selection(selection, suggestions, False)
        
        elif method == "2":
            return select_by_category_method(available_crimes, max_select)
        
        elif method == "3":
            return select_by_search_method(available_crimes, max_select)
        
        elif method == "5":
            confirm = input(f"🚨 Select ALL {len(available_crimes)} crimes? This may create a very busy plot! (y/n): ").strip().lower()
            if confirm == 'y':
                print(f"✅ Selected ALL {len(available_crimes)} crimes!")
                return available_crimes.copy()
            else:
                print("❌ Selection cancelled.")
                return []
    
    # Default: show full list for smaller datasets
    return show_full_list_selection(available_crimes, max_select, context)


def select_by_category_method(available_crimes, max_select):
    """Select crimes by browsing categories."""
    categories = categorize_crimes(available_crimes)
    
    print(f"\n🗂️ CRIME CATEGORIES:")
    cat_list = list(categories.keys())
    for i, (cat, crimes) in enumerate(categories.items(), 1):
        print(f"{i}. {cat} ({len(crimes)} crimes)")
    print(f"{len(cat_list)+1}. ✅ SELECT ALL CRIMES ({len(available_crimes)} total)")
    
    selected = []
    while len(selected) < max_select:
        try:
            cat_choice = input(f"\nChoose category (1-{len(cat_list)+1}) or 'done': ").strip()
            if cat_choice.lower() == 'done':
                break
            
            cat_idx = int(cat_choice) - 1
            
            # Handle "Select All" option
            if cat_idx == len(cat_list):
                confirm = input(f"🚨 Select ALL {len(available_crimes)} crimes? (y/n): ").strip().lower()
                if confirm == 'y':
                    print(f"✅ Selected ALL {len(available_crimes)} crimes!")
                    return available_crimes.copy()
                else:
                    continue
                    
            if 0 <= cat_idx < len(cat_list):
                cat_name = cat_list[cat_idx]
                crimes_in_cat = categories[cat_name]
                
                print(f"\n📋 {cat_name} ({len(crimes_in_cat)} crimes):")
                for i, crime in enumerate(crimes_in_cat, 1):
                    print(f"{i:2d}. {crime}")
                
                remaining = max_select - len(selected)
                print(f"\nSelect up to {remaining} crimes (e.g., '1,3' or '1-3'):")
                selection = input("Selection: ").strip()
                new_crimes = parse_multiple_selection(selection, crimes_in_cat, False)
                
                for crime in new_crimes:
                    if crime not in selected and len(selected) < max_select:
                        selected.append(crime)
                        print(f"✅ Added: {crime}")
                
                if len(selected) >= max_select:
                    break
            else:
                print("Invalid category number.")
        except (ValueError, KeyboardInterrupt):
            break
    
    return selected


def select_by_search_method(available_crimes, max_select):
    """Select crimes by searching."""
    selected = []
    
    print(f"\n🔍 SEARCH & SELECT (up to {max_select} crimes)")
    
    while len(selected) < max_select:
        search_term = input(f"\nSearch term (or 'done'): ").strip()
        if search_term.lower() == 'done':
            break
        
        matches = [c for c in available_crimes if search_term.lower() in c.lower() and c not in selected]
        
        if not matches:
            print(f"❌ No matches for '{search_term}'")
            continue
        
        print(f"\n📋 Found {len(matches)} matches:")
        display_matches = matches[:15]  # Show top 15
        for i, crime in enumerate(display_matches, 1):
            print(f"{i:2d}. {crime}")
        
        if len(matches) > 15:
            print(f"... and {len(matches)-15} more (refine search to see all)")
        
        remaining = max_select - len(selected)
        selection = input(f"Select up to {remaining} (numbers or names): ").strip()
        new_crimes = parse_multiple_selection(selection, display_matches, False)
        
        for crime in new_crimes:
            if crime not in selected and len(selected) < max_select:
                selected.append(crime)
                print(f"✅ Added: {crime}")
        
        if len(selected) >= max_select:
            break
    
    return selected


def show_full_list_selection(available_crimes, max_select, context):
    """Show full list for selection (optimized display)."""
    print(f"\n📋 ALL AVAILABLE {context.upper()} ({len(available_crimes)} total):")
    
    # Display in organized format
    if len(available_crimes) > 30:
        # Two columns for large lists
        for i in range(0, len(available_crimes), 2):
            left = f"{i+1:2d}. {available_crimes[i]}"
            right = f"{i+2:2d}. {available_crimes[i+1]}" if i+1 < len(available_crimes) else ""
            print(f"{left:<45} {right}")
    else:
        # Single column for smaller lists
        for i, crime in enumerate(available_crimes, 1):
            print(f"{i:2d}. {crime}")
    
    print(f"\n💡 SELECTION TIPS:")
    print(f"✓ Single: '1' or '{available_crimes[0][:25]}...'")
    print(f"✓ Multiple: '1,3,5' or '1-3,8'")
    print(f"✓ Names: 'murder,theft' (partial matching works)")
    print(f"✓ All crimes: 'all' or '*'")
    if max_select > 1:
        print(f"✓ Max {max_select} selections (or 'all' for everything)")
    
    selection = input(f"\nYour selection: ").strip()
    
    # Handle "all" selection specially
    if selection.lower() in ['all', '*']:
        if len(available_crimes) <= max_select:
            print(f"✅ Selected ALL {len(available_crimes)} crimes!")
            return available_crimes.copy()
        else:
            confirm = input(f"⚠️  This will select ALL {len(available_crimes)} crimes (exceeds max {max_select}). Continue? (y/n): ").strip().lower()
            if confirm == 'y':
                print(f"✅ Selected ALL {len(available_crimes)} crimes!")
                return available_crimes.copy()
            else:
                print("❌ Selection cancelled. Please choose specific crimes.")
                return []
    
    return parse_multiple_selection(selection, available_crimes, max_select >= len(available_crimes))


def show_descriptive_stats(df, crime_cols):
    """
    Shows descriptive statistics (mean, median, std, min, max) 
    AND textual outlier analysis for selected crime columns.
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

    # === NEW OUTLIER SECTION ===
    print("\n=== Textual Outlier Detection ===")
    print("(Based on non-zero values; '0' cases are not considered outliers)")
    
    for col in existing:
        print(f"\n--- Outliers for '{col}' ---")
        
        # Filter out zeros for meaningful outlier analysis
        series = df[df[col] > 0][col]
        
        if series.empty:
            print("  No non-zero data available for outlier analysis.")
            continue
        
        # 1. Z-Score Method
        mean = series.mean()
        std = series.std()
        if std > 0:
            z_scores = np.abs((series - mean) / std)
            outliers_z = series[z_scores > 3] # Using threshold=3
            if not outliers_z.empty:
                print(f"  Z-Score (threshold=3) outliers: {sorted(list(outliers_z.values))}")
            else:
                print("  No Z-Score (threshold=3) outliers found.")
        else:
            print("  Z-Score: Not applicable (data has no variance).")

        # 2. IQR Rule
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        if IQR > 0:
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers_iqr = series[(series < lower_bound) | (series > upper_bound)]
            if not outliers_iqr.empty:
                print(f"  IQR (multiplier=1.5) outliers: {sorted(list(outliers_iqr.values))}")
            else:
                print("  No IQR (multiplier=1.5) outliers found.")
        else:
            print("  IQR: Not applicable (data has no variance).")
    # === END NEW SECTION ===


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


# *** ENHANCED VISUALIZATION FUNCTIONS ***

def plot_pie_chart_crime_distribution(data, state_name, district_name="all", top_n=10):
    """
    3. Pie/Donut Charts (Crime Type Distribution)
    Shows the percentage share of different crime categories.
    """
    if data.empty:
        print("No data available for pie chart.")
        return
    
    # Get crime columns
    crime_columns = [col for col in data.columns if col not in 
                    ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
    
    if not crime_columns:
        print("No crime data found for pie chart.")
        return
    
    # Calculate totals for each crime type
    crime_totals = data[crime_columns].sum().sort_values(ascending=False)
    
    # Get top N crimes to avoid overcrowding
    if len(crime_totals) > top_n:
        top_crimes = crime_totals.head(top_n)
        other_total = crime_totals.iloc[top_n:].sum()
        if other_total > 0:
            top_crimes['Others'] = other_total
    else:
        top_crimes = crime_totals
    
    # Remove zero values
    top_crimes = top_crimes[top_crimes > 0]
    
    if top_crimes.empty:
        print("No crimes with non-zero values found.")
        return
    
    # Create pie chart
    location_desc = f"{district_name}, {state_name}" if district_name != "all" else f"All Districts in {state_name}"
    
    fig = px.pie(
        values=top_crimes.values,
        names=top_crimes.index,
        title=f'🥧 Crime Distribution in {location_desc}<br>Top {min(top_n, len(crime_totals))} Crime Types',
        hole=0.4,  # Creates donut chart
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        showlegend=True,
        height=600,
        font=dict(size=12)
    )
    
    fig.show()
    print(f"✅ Pie chart generated for {location_desc}")


def plot_crime_heatmap(data, state_name, district_name="all", method='geographic'):
    """
    4. Geographic Heatmaps (Crime Distribution Across Locations)
    Shows crime intensity across states, districts, and years for geographic analysis.
    """
    try:
        if data.empty:
            print("❌ No data available for heatmap.")
            return False
        
        print(f"📊 Generating geographic heatmap for {len(data)} records...")
        
        # Get crime columns
        crime_columns = [col for col in data.columns if col not in 
                        ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
        
        print(f"📋 Found {len(crime_columns)} crime types for analysis")
        
        if len(crime_columns) < 1:
            print("❌ No crime data found for heatmap.")
            print(f"Available columns: {list(data.columns)}")
            return False
        
        location_desc = f"{district_name}, {state_name}" if district_name != "all" else f"Multiple Locations"
        
        if method == 'geographic':
            # Geographic heatmap - Crime intensity across states/districts
            return create_geographic_heatmap(data, crime_columns, location_desc)
        
        elif method == 'state_comparison':
            # State-wise crime comparison heatmap
            return create_state_comparison_heatmap(data, crime_columns)
        
        elif method == 'district_comparison':
            # District-wise crime comparison within a state
            return create_district_comparison_heatmap(data, crime_columns, state_name)
        
        elif method == 'year_location':
            # Year vs Location heatmap
            return create_year_location_heatmap(data, crime_columns, state_name, district_name)
        
        else:
            print("❌ Invalid heatmap method. Choose: geographic, state_comparison, district_comparison, or year_location")
            return False
    
    except Exception as e:
        print(f"❌ Error generating heatmap: {str(e)}")
        print("🔍 Debug info:")
        print(f"   - Data shape: {data.shape}")
        print(f"   - Available columns: {list(data.columns)}")
        print(f"   - Method: {method}")
        return False


def create_geographic_heatmap(data, crime_columns, location_desc):
    """
    Create a geographic heatmap showing crime distribution across locations.
    """
    try:
        print("🗺️ Creating geographic crime distribution heatmap...")
        
        # Choose a representative crime or allow user selection
        if len(crime_columns) > 1:
            print(f"📋 Available crime types ({len(crime_columns)} total):")
            for i, crime in enumerate(crime_columns[:10], 1):
                print(f"{i:2d}. {crime}")
            if len(crime_columns) > 10:
                print(f"    ... and {len(crime_columns)-10} more")
            
            crime_choice = input("Enter crime number or name (or press Enter for total): ").strip()
            
            if crime_choice.isdigit() and 1 <= int(crime_choice) <= min(10, len(crime_columns)):
                selected_crime = crime_columns[int(crime_choice) - 1]
            elif crime_choice in crime_columns:
                selected_crime = crime_choice
            else:
                # Use total of all crimes
                selected_crime = None
        else:
            selected_crime = crime_columns[0]
        
        # Create location-wise aggregation
        if 'State Name' in data.columns and 'District Name' in data.columns:
            if selected_crime:
                # Single crime analysis
                location_data = data.groupby(['State Name', 'District Name'])[selected_crime].sum().reset_index()
                location_data = location_data[location_data[selected_crime] > 0]
                
                if location_data.empty:
                    print(f"❌ No data for {selected_crime}")
                    return False
                
                # Create pivot table for heatmap
                pivot_data = location_data.pivot(index='State Name', columns='District Name', values=selected_crime)
                title = f'🗺️ Geographic Distribution: {selected_crime}<br>{location_desc}'
                
            else:
                # Total crimes analysis
                numeric_crimes = []
                for col in crime_columns:
                    temp_col = pd.to_numeric(data[col], errors='coerce').fillna(0)
                    numeric_crimes.append(temp_col)
                
                data['Total_Crimes'] = sum(numeric_crimes)
                location_data = data.groupby(['State Name', 'District Name'])['Total_Crimes'].sum().reset_index()
                location_data = location_data[location_data['Total_Crimes'] > 0]
                
                if location_data.empty:
                    print("❌ No crime data found")
                    return False
                
                # Create pivot table
                pivot_data = location_data.pivot(index='State Name', columns='District Name', values='Total_Crimes')
                title = f'🗺️ Geographic Distribution: All Crimes Combined<br>{location_desc}'
            
            # Fill NaN with 0 for visualization
            pivot_data = pivot_data.fillna(0)
            
            # Limit size for readability
            if pivot_data.shape[0] > 20 or pivot_data.shape[1] > 30:
                # Show top states and districts
                state_totals = pivot_data.sum(axis=1).sort_values(ascending=False)
                top_states = state_totals.head(15).index
                
                district_totals = pivot_data.sum(axis=0).sort_values(ascending=False)  
                top_districts = district_totals.head(20).index
                
                pivot_data = pivot_data.loc[top_states, top_districts]
                title += f'<br>Top {len(top_states)} States × Top {len(top_districts)} Districts'
            
            # Create interactive heatmap
            try:
                fig = px.imshow(
                    pivot_data.values,
                    x=pivot_data.columns,
                    y=pivot_data.index,
                    color_continuous_scale='Reds',
                    title=title,
                    labels=dict(x="District", y="State", color="Cases")
                )
                
                fig.update_layout(
                    height=max(500, len(pivot_data.index) * 25),
                    width=max(800, len(pivot_data.columns) * 20),
                    font=dict(size=10),
                    xaxis_title="Districts",
                    yaxis_title="States"
                )
                
                # Rotate x-axis labels for readability
                fig.update_xaxes(tickangle=45)
                
                fig.show()
                print(f"✅ Geographic heatmap generated!")
                return True
                
            except Exception as e:
                print(f"⚠️ Plotly failed: {e}")
                return create_fallback_geographic_heatmap(pivot_data, title)
        
        else:
            print("❌ Missing State Name or District Name columns")
            return False
            
    except Exception as e:
        print(f"❌ Error creating geographic heatmap: {e}")
        return False


def create_state_comparison_heatmap(data, crime_columns):
    """
    Create heatmap comparing crime types across states.
    """
    try:
        print("🏛️ Creating state comparison heatmap...")
        
        if 'State Name' not in data.columns:
            print("❌ No State Name column found")
            return False
        
        # Select top crimes and states for manageable visualization
        crime_data = data[['State Name'] + crime_columns].copy()
        
        # Convert crime columns to numeric
        for col in crime_columns:
            crime_data[col] = pd.to_numeric(crime_data[col], errors='coerce').fillna(0)
        
        # Aggregate by state
        state_crimes = crime_data.groupby('State Name')[crime_columns].sum()
        
        # Get top crimes by total volume
        crime_totals = state_crimes.sum().sort_values(ascending=False)
        top_crimes = crime_totals.head(15).index.tolist()  # Top 15 crimes
        
        # Get top states by total crime
        state_totals = state_crimes[top_crimes].sum(axis=1).sort_values(ascending=False)
        top_states = state_totals.head(20).index.tolist()  # Top 20 states
        
        # Create filtered dataset
        heatmap_data = state_crimes.loc[top_states, top_crimes]
        
        try:
            fig = px.imshow(
                heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                color_continuous_scale='Reds',
                title=f'🏛️ State vs Crime Type Heatmap<br>Top {len(top_states)} States × Top {len(top_crimes)} Crimes',
                labels=dict(x="Crime Type", y="State", color="Cases")
            )
            
            fig.update_layout(
                height=max(600, len(top_states) * 25),
                width=max(1000, len(top_crimes) * 50),
                font=dict(size=10),
                xaxis_title="Crime Types",
                yaxis_title="States"
            )
            
            fig.update_xaxes(tickangle=45)
            fig.show()
            print(f"✅ State comparison heatmap generated!")
            return True
            
        except Exception as e:
            print(f"⚠️ Plotly failed: {e}")
            return create_fallback_state_heatmap(heatmap_data)
            
    except Exception as e:
        print(f"❌ Error creating state comparison heatmap: {e}")
        return False


def create_district_comparison_heatmap(data, crime_columns, state_name):
    """
    Create heatmap comparing crime types across districts within a state.
    """
    try:
        print(f"🏘️ Creating district comparison heatmap for {state_name}...")
        
        if 'District Name' not in data.columns:
            print("❌ No District Name column found")
            return False
        
        # Filter to specific state
        state_data = data[data['State Name'] == state_name].copy()
        
        if state_data.empty:
            print(f"❌ No data found for {state_name}")
            return False
        
        # Select crime data
        district_crime_data = state_data[['District Name'] + crime_columns].copy()
        
        # Convert to numeric
        for col in crime_columns:
            district_crime_data[col] = pd.to_numeric(district_crime_data[col], errors='coerce').fillna(0)
        
        # Aggregate by district
        district_crimes = district_crime_data.groupby('District Name')[crime_columns].sum()
        
        # Get top crimes and districts
        crime_totals = district_crimes.sum().sort_values(ascending=False)
        top_crimes = crime_totals.head(12).index.tolist()
        
        district_totals = district_crimes[top_crimes].sum(axis=1).sort_values(ascending=False)
        top_districts = district_totals.head(25).index.tolist()
        
        heatmap_data = district_crimes.loc[top_districts, top_crimes]
        
        try:
            fig = px.imshow(
                heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                color_continuous_scale='Reds',
                title=f'🏘️ District vs Crime Type Heatmap - {state_name}<br>Top {len(top_districts)} Districts × Top {len(top_crimes)} Crimes',
                labels=dict(x="Crime Type", y="District", color="Cases")
            )
            
            fig.update_layout(
                height=max(600, len(top_districts) * 20),
                width=max(900, len(top_crimes) * 60),
                font=dict(size=10)
            )
            
            fig.update_xaxes(tickangle=45)
            fig.show()
            print(f"✅ District comparison heatmap generated for {state_name}!")
            return True
            
        except Exception as e:
            print(f"⚠️ Plotly failed: {e}")
            return create_fallback_district_heatmap(heatmap_data, state_name)
            
    except Exception as e:
        print(f"❌ Error creating district comparison heatmap: {e}")
        return False


def create_year_location_heatmap(data, crime_columns, state_name, district_name):
    """
    Create heatmap showing crime trends over years across locations.
    """
    try:
        print(f"📅 Creating year vs location heatmap...")
        
        if 'Year' not in data.columns:
            print("❌ No Year column found")
            return False
        
        # Choose single crime for year analysis
        if len(crime_columns) > 1:
            print("Select crime type for year analysis:")
            for i, crime in enumerate(crime_columns[:10], 1):
                print(f"{i:2d}. {crime}")
            
            choice = input("Enter number: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= min(10, len(crime_columns)):
                selected_crime = crime_columns[int(choice) - 1]
            else:
                selected_crime = crime_columns[0]
        elif crime_columns:
            selected_crime = crime_columns[0]
        else:
            print("❌ No crime columns to analyze.")
            return False
        
        # Aggregate by year and location
        if district_name != 'all':
            # Single district, show Crime vs Year
            year_crime_data = data.groupby('Year')[crime_columns].sum().reset_index()
            # Select top crimes
            crime_totals = year_crime_data[crime_columns].sum().sort_values(ascending=False)
            top_crimes = crime_totals.head(15).index.tolist()
            
            pivot_data = year_crime_data.set_index('Year')[top_crimes].T # Transpose: Crimes on Y-axis, Year on X-axis
            title = f'📅 Crime vs. Year Heatmap - {district_name}, {state_name}<br>Top {len(top_crimes)} Crimes'
            y_label = "Crime Type"

        elif state_name != "Multiple Locations":
            # All districts for a specific state, show District vs Year
            year_location_data = data.groupby(['Year', 'District Name'])[selected_crime].sum().reset_index()
            year_location_data[selected_crime] = pd.to_numeric(year_location_data[selected_crime], errors='coerce').fillna(0)
            
            pivot_data = year_location_data.pivot(index='District Name', columns='Year', values=selected_crime).fillna(0)
            title = f'📅 {selected_crime} Over Years - {state_name} Districts'
            y_label = "District"
            
        else:
            # All states, show State vs Year
            year_location_data = data.groupby(['Year', 'State Name'])[selected_crime].sum().reset_index()
            year_location_data[selected_crime] = pd.to_numeric(year_location_data[selected_crime], errors='coerce').fillna(0)
            
            pivot_data = year_location_data.pivot(index='State Name', columns='Year', values=selected_crime).fillna(0)
            title = f'📅 {selected_crime} Over Years - All States'
            y_label = "State"
        
        # Limit data for readability
        if len(pivot_data.index) > 25:
            location_totals = pivot_data.sum(axis=1).sort_values(ascending=False)
            top_locations = location_totals.head(25).index
            pivot_data = pivot_data.loc[top_locations]
            title += f'<br>Showing Top {len(top_locations)} {y_label}s'
        
        try:
            fig = px.imshow(
                pivot_data.values,
                x=pivot_data.columns,
                y=pivot_data.index,
                color_continuous_scale='Reds',
                title=title,
                labels=dict(x="Year", y=y_label, color="Cases")
            )
            
            fig.update_layout(
                height=max(500, len(pivot_data.index) * 20),
                width=max(700, len(pivot_data.columns) * 60),
                font=dict(size=10)
            )
            
            fig.show()
            print(f"✅ Year vs location heatmap generated!")
            return True
            
        except Exception as e:
            print(f"⚠️ Plotly failed: {e}")
            # Fallback to seaborn
            plt.figure(figsize=(max(10, len(pivot_data.columns)*0.8), max(8, len(pivot_data.index)*0.4)))
            sns.heatmap(pivot_data, cmap='Reds', annot=False, cbar_kws={'label': 'Cases'})
            plt.title(title)
            plt.xlabel('Year')
            plt.ylabel(y_label)
            plt.tight_layout()
            plt.show()
            return True
            
    except Exception as e:
        print(f"❌ Error creating year vs location heatmap: {e}")
        return False


def create_fallback_geographic_heatmap(pivot_data, title):
    """Fallback matplotlib heatmap for geographic data."""
    try:
        plt.figure(figsize=(max(12, len(pivot_data.columns)*0.5), max(8, len(pivot_data.index)*0.4)))
        sns.heatmap(pivot_data, cmap='Reds', annot=False, cbar_kws={'label': 'Cases'})
        plt.title(title.replace('<br>', '\n'))
        plt.xlabel('Districts')
        plt.ylabel('States')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
        print("✅ Fallback geographic heatmap generated!")
        return True
    except Exception as e:
        print(f"❌ Fallback heatmap failed: {e}")
        return False


def create_fallback_state_heatmap(heatmap_data):
    """Fallback matplotlib heatmap for state comparison."""
    try:
        plt.figure(figsize=(15, 10))
        sns.heatmap(heatmap_data, cmap='Reds', annot=False, cbar_kws={'label': 'Cases'})
        plt.title('State vs Crime Type Comparison')
        plt.xlabel('Crime Types')
        plt.ylabel('States')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
        print("✅ Fallback state heatmap generated!")
        return True
    except Exception as e:
        print(f"❌ Fallback failed: {e}")
        return False


def create_fallback_district_heatmap(heatmap_data, state_name):
    """Fallback matplotlib heatmap for district comparison."""
    try:
        plt.figure(figsize=(12, 8))
        sns.heatmap(heatmap_data, cmap='Reds', annot=False, cbar_kws={'label': 'Cases'})
        plt.title(f'District vs Crime Type Comparison - {state_name}')
        plt.xlabel('Crime Types')
        plt.ylabel('Districts')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
        print(f"✅ Fallback district heatmap generated for {state_name}!")
        return True
    except Exception as e:
        print(f"❌ Fallback failed: {e}")
        return False


def test_heatmap_data(data):
    """
    Test function to diagnose heatmap data issues.
    """
    print("\n🔍 HEATMAP DATA DIAGNOSIS:")
    print(f"📊 Data shape: {data.shape}")
    
    crime_columns = [col for col in data.columns if col not in 
                    ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
    
    print(f"📋 Crime columns found: {len(crime_columns)}")
    
    if len(crime_columns) > 0:
        print(f"📈 Sample crime columns: {crime_columns[:5]}")
        
        crime_data = data[crime_columns]
        print(f"🔢 Crime data shape: {crime_data.shape}")
        print(f"🚫 Columns with all zeros: {(crime_data == 0).all().sum()}")
        print(f"❓ Columns with NaN: {crime_data.isnull().all().sum()}")
        
        # Show sample statistics
        non_zero_data = crime_data.loc[:, (crime_data != 0).any(axis=0)]
        print(f"✅ Non-zero columns: {len(non_zero_data.columns)}")
        
        if len(non_zero_data.columns) >= 2:
            corr_sample = non_zero_data.iloc[:, :5].corr() if len(non_zero_data.columns) >= 5 else non_zero_data.corr()
            print(f"🔗 Sample correlation matrix shape: {corr_sample.shape}")
            print("💡 Heatmap should work with this data!")
        else:
            print("❌ Not enough non-zero columns for correlation heatmap")
    else:
        print("❌ No crime columns found!")


def plot_stacked_bar_chart(data, state_name, district_name="all", top_crimes=8):
    """
    5. Stacked Bar Charts (Year vs Crime Category)
    Shows how different crime types contribute each year.
    """
    if data.empty or 'Year' not in data.columns:
        print("No data or Year column available for stacked bar chart.")
        return
    
    # Get crime columns
    crime_columns = [col for col in data.columns if col not in 
                    ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
    
    # Get top crimes by total volume
    crime_totals = data[crime_columns].sum().sort_values(ascending=False)
    top_crime_cols = crime_totals.head(top_crimes).index.tolist()
    
    # Group by year and sum
    yearly_data = data.groupby('Year')[top_crime_cols].sum().reset_index()
    
    location_desc = f"{district_name}, {state_name}" if district_name != "all" else f"All Districts in {state_name}"
    
    # Create stacked bar chart
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set3
    
    for i, crime in enumerate(top_crime_cols):
        fig.add_trace(go.Bar(
            x=yearly_data['Year'],
            y=yearly_data[crime],
            name=crime[:30] + "..." if len(crime) > 30 else crime,
            marker_color=colors[i % len(colors)]
        ))
    
    fig.update_layout(
        barmode='stack',
        title=f'📊 Stacked Crime Trends by Year - {location_desc}<br>Top {top_crimes} Crime Types',
        xaxis_title='Year',
        yaxis_title='Number of Cases',
        height=600,
        showlegend=True,
        font=dict(size=12)
    )
    
    fig.show()
    print(f"✅ Stacked bar chart generated for {location_desc}")


def plot_interactive_crime_dashboard(datasets, selected_dataset_key):
    """
    7. Interactive Dashboards with filters
    Allows users to explore the data dynamically.
    """
    if selected_dataset_key not in datasets:
        print("Invalid dataset selected.")
        return
    
    data = datasets[selected_dataset_key]
    
    # Get available options
    states = sorted(data['State Name'].unique()) if 'State Name' in data.columns else []
    years = sorted(data['Year'].unique()) if 'Year' in data.columns else []
    crime_columns = [col for col in data.columns if col not in 
                    ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
    
    print(f"\n🎛️ INTERACTIVE DASHBOARD - {selected_dataset_key}")
    print("="*60)
    print("Available filters:")
    print(f"📍 States: {len(states)} available")
    print(f"📅 Years: {min(years) if years else 'N/A'} - {max(years) if years else 'N/A'}")
    print(f"🚨 Crime Types: {len(crime_columns)} available")
    
    # Simple interactive selection
    print("\n🎯 Create your custom analysis:")
    
    # State filter
    print(f"\nAvailable states: {', '.join(states[:10])}{'...' if len(states) > 10 else ''}")
    selected_state = input("Enter state name (or press Enter for all): ").strip().lower() # Make lowercase
    
    # Find matching state
    matching_states = [s for s in states if selected_state in s]
    if selected_state and matching_states:
        selected_state = matching_states[0] # Use the full, correct-cased name
        filtered_data = data[data['State Name'] == selected_state]
        print(f"✅ Filtered to: {selected_state}")
    else:
        filtered_data = data
        selected_state = "All States"
        print("✅ Using all states")
    
    # Year filter
    if years:
        year_choice = input(f"Enter year range (e.g., '{min(years)}-{max(years)}') or press Enter for all: ").strip()
        if year_choice and '-' in year_choice:
            try:
                start_year, end_year = map(int, year_choice.split('-'))
                filtered_data = filtered_data[
                    (filtered_data['Year'] >= start_year) & 
                    (filtered_data['Year'] <= end_year)
                ]
                print(f"✅ Filtered to years: {start_year}-{end_year}")
            except:
                print("Invalid range, using all years.")
                print("✅ Using all years")
        else:
            print("✅ Using all years")
    
    # Crime type filter
    print(f"\nTop 10 crime types: {', '.join(crime_columns[:10])}")
    crime_choice = input("Enter crime types (comma-separated) or press Enter for top 5: ").strip()
    
    if crime_choice:
        selected_crimes = parse_multiple_selection(crime_choice, crime_columns, allow_all=False)
    else:
        # Default to top 5 by total volume
        crime_totals = filtered_data[crime_columns].sum().sort_values(ascending=False)
        selected_crimes = crime_totals.head(5).index.tolist()
    
    if not selected_crimes:
        print("❌ No valid crimes selected. Defaulting to top 5.")
        crime_totals = filtered_data[crime_columns].sum().sort_values(ascending=False)
        selected_crimes = crime_totals.head(5).index.tolist()

    print(f"✅ Selected crimes: {selected_crimes}")
    
    # Generate visualization
    print("\n📊 Choose visualization type:")
    print("1. Line trends")
    print("2. Pie distribution") 
    print("3. Correlation heatmap")
    print("4. Stacked bars")
    
    viz_choice = input("Enter choice (1-4): ").strip()
    
    if viz_choice == "1":
        # Line trends
        if 'Year' not in filtered_data.columns:
            print("❌ 'Year' column not found for trend analysis.")
            return

        yearly_data = filtered_data.groupby('Year')[selected_crimes].sum().reset_index()
        
        fig = px.line(
            yearly_data.melt(id_vars=['Year'], var_name='Crime Type', value_name='Cases'),
            x='Year',
            y='Cases',
            color='Crime Type',
            title=f'📈 Interactive Crime Trends - {selected_state}',
            markers=True
        )
        fig.show()
        
    elif viz_choice == "2":
        plot_pie_chart_crime_distribution(filtered_data, selected_state, "Dashboard")
        
    elif viz_choice == "3":
        # Use 'district_comparison' if a state is selected, 'state_comparison' if all states
        if selected_state == "All States":
            plot_crime_heatmap(filtered_data, selected_state, "all", method='state_comparison')
        else:
             plot_crime_heatmap(filtered_data, selected_state, "all", method='district_comparison')

    elif viz_choice == "4":
        plot_stacked_bar_chart(filtered_data, selected_state, "Dashboard")
    
    print("✅ Interactive dashboard completed!")


def plot_india_crime_map(data, crime_type, title_suffix=""):
    """
    6. Crime Hotspot Map of India (Optional but Powerful)
    A geographical map showing crime density across states.
    """
    if data.empty:
        print("No data available for map visualization.")
        return
    
    # Aggregate by state
    if 'State Name' not in data.columns or crime_type not in data.columns:
        print("Required columns not found for map visualization.")
        return
    
    state_data = data.groupby('State Name')[crime_type].sum().reset_index()
    state_data = state_data[state_data[crime_type] > 0].sort_values(crime_type, ascending=False)
    
    if state_data.empty:
        print("No crime data found for mapping.")
        return
    
    # Create choropleth map (simplified version)
    fig = px.bar(
        state_data.head(15),  # Top 15 states
        x=crime_type,
        y='State Name',
        orientation='h',
        title=f'🗺️ Crime Hotspot Map: {crime_type}{title_suffix}<br>Top 15 States by Total Cases',
        color=crime_type,
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        height=600,
        yaxis={'categoryorder':'total ascending'}
    )
    
    fig.show()
    print(f"✅ Crime hotspot map generated for {crime_type}")


# *** NEW FUNCTION: Added for Boxplot ***
def plot_boxplot_outliers(data, crime_col, location_desc):
    """
    Generates an interactive boxplot using Plotly to visually identify outliers.
    'data' is the filtered DataFrame (e.g., for a specific district).
    'crime_col' is the single crime to plot.
    'location_desc' is for the title.
    """
    if data.empty or crime_col not in data.columns:
        print("No data to plot for boxplot.")
        return
        
    # Filter out zero values to make the boxplot more meaningful
    # (Often, crime data has many zeros which are not 'outliers' but just 'no crime')
    plot_data = data[data[crime_col] > 0]
    
    if plot_data.empty:
        print(f"No non-zero data for '{crime_col}' to plot (all values are 0).")
        return

    fig = px.box(
        plot_data,
        y=crime_col,
        title=f"📦 Outlier Analysis (Boxplot) for '{crime_col}'<br>Location: {location_desc} (showing non-zero values)",
        points="all",  # Show all individual data points
        hover_data=data.columns  # Show all data on hover
    )
    
    fig.update_layout(
        yaxis_title="Number of Cases",
        xaxis_title=f"{crime_col}",
    )
    
    # 


    fig.show()
    print(f"✅ Interactive boxplot generated for {crime_col}.")


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
                if 'Year' in filtered_data.columns:
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
            if 'Year' in merged_yearly.columns and not merged_yearly['Year'].empty:
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
            if 'Year' in state_data.columns:
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
    
    all_years = []
    for state, yearly_data in state_yearly.items():
        if not yearly_data.empty:
            sns.lineplot(data=yearly_data, x='Year', y=selected_crime_type, 
                        marker='o', label=state.title())
            all_years.extend(yearly_data['Year'].unique())
    
    plt.title(f'{selected_crime_type} - Trends Across States', fontsize=14, fontweight='bold')
    plt.xlabel('Year')
    plt.ylabel(f'{selected_crime_type} Cases')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    if all_years:
        plt.xticks(sorted(list(set(all_years))))
    
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


def verify_setup():
    """
    Verify that the setup is correct for running the analysis.
    Provides helpful information about the current environment.
    """
    print("🔧 SETUP VERIFICATION")
    print("="*50)
    print(f"📍 Script location: {SCRIPT_DIR}")
    print(f"📁 Dataset directory: {DATASET_DIR}")
    print(f"🐍 Python version: {sys.version.split()[0]}")
    
    # Check required packages
    required_packages = ['pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 'scipy']
    print(f"\n📦 Package versions:")
    for package in required_packages:
        try:
            if package == 'pandas':
                print(f"   {package}: {pd.__version__}")
            elif package == 'numpy':
                print(f"   {package}: {np.__version__}")
            elif package == 'matplotlib':
                import matplotlib
                print(f"   {package}: {matplotlib.__version__}")
            elif package == 'seaborn':
                print(f"   {package}: {sns.__version__}")
            elif package == 'plotly':
                import plotly
                print(f"   {package}: {plotly.__version__}")
            elif package == 'scipy':
                import scipy
                print(f"   {package}: {scipy.__version__}")
        except Exception:
            print(f"   {package}: ❌ Not installed")
    
    print("="*50)


def get_analysis_type():
    """
    Ask user to choose the type of analysis they want to perform.
    Returns the selected analysis type.
    """
    print("\n" + "="*70)
    print("🎯 SELECT ANALYSIS TYPE")
    print("="*70)
    print("What type of crime analysis do you want to perform?")
    print()
    
    analysis_options = {
        '1': {
            'name': '🏛️  Single Location Analysis',
            'description': 'Analyze crime trends in a specific district or entire state',
            'examples': ['Crime trends in Delhi NCR', 'Statistics for Mumbai district']
        },
        '2': {
            'name': '⚔️  District vs District Comparison', 
            'description': 'Compare same crime type across multiple districts within a state',
            'examples': ['Delhi vs Mumbai vs Kolkata for cyber crimes', 'Top 5 districts in Maharashtra']
        },
        '3': {
            'name': '🌍 State vs State Comparison',
            'description': 'Compare same crime type across different states',
            'examples': ['Cyber crimes: Delhi vs Maharashtra vs Karnataka', 'Women crimes across states']
        },
        '4': {
            'name': '📊 Dataset vs Dataset Comparison',
            'description': 'Compare different crime categories in same location',
            'examples': ['IPC vs Cyber vs Women crimes in Delhi', 'Crime category comparison']
        },
        '5': {
            'name': '🔥 Crime Hotspot Analysis',
            'description': 'Find top districts/states with highest crime rates',
            'examples': ['Top 10 cyber crime districts', 'Most dangerous districts for women']
        },
        '6': {
            'name': '📈 Statistical Analysis',
            'description': 'Detailed statistics and descriptive analysis',
            'examples': ['Mean, median, trends', 'Correlation analysis']
        }
    }
    
    for key, option in analysis_options.items():
        print(f"{key}. {option['name']}")
        print(f"   📝 {option['description']}")
        print(f"   💡 Examples: {', '.join(option['examples'])}")
        print()
    
    while True:
        choice = input("Enter your choice (1-6): ").strip()
        if choice in analysis_options:
            selected = analysis_options[choice]
            print(f"\n✅ Selected: {selected['name']}")
            print(f"📋 {selected['description']}")
            return choice
        else:
            print("❌ Invalid choice. Please enter 1-6.")


def handle_single_location_analysis(datasets):
    """Handle single location analysis (district or state level)"""
    print("\n🏛️ SINGLE LOCATION ANALYSIS")
    print("="*50)
    
    # Step 1: Choose dataset
    file_choice = get_dataset_choice(list(datasets.keys()))
    if not file_choice:
        return False
    
    chosen_dataset_df = datasets[file_choice]
    
    # Step 2: Choose state
    dataset_states = chosen_dataset_df['State Name'].unique()
    state_name = get_state_choice(dataset_states)
    if not state_name:
        return False
    
    # Step 3: Choose district or entire state
    district_name = get_district_choice(state_name, chosen_dataset_df)
    if not district_name:
        return False
    
    # Step 4: Choose crime type
    crime_choice = get_crime_choice(chosen_dataset_df)
    if not crime_choice:
        return False
    
    # Filter data based on selection
    if district_name == 'all':
        selected_data = chosen_dataset_df[chosen_dataset_df['State Name'] == state_name]
        location_desc = f"ALL Districts in {state_name}"
    else:
        selected_data = chosen_dataset_df[
            (chosen_dataset_df['State Name'] == state_name) &
            (chosen_dataset_df['District Name'] == district_name)
        ]
        location_desc = f"{district_name}, {state_name}"
    
    if selected_data.empty:
        print(f"❌ No data found for {location_desc}")
        return False
    
    # Show analysis options for single location
    print(f"\n📊 Analysis Options for {location_desc}:")
    print("1. Plot crime trend over time")
    print("2. Compare multiple crimes in this location")
    print("3. Descriptive statistics")
    if district_name == 'all':
        print("4. Bar chart of all districts in state")
    
    action = input("\nChoose analysis (1-4): ").strip()
    
    if action == "1":
        plot_trends(selected_data, state_name, district_name, crime_choice)
    elif action == "2":
        available_crimes = [c for c in chosen_dataset_df.columns if c not in 
                           ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
        crimes = enhanced_crime_selection_prompt(available_crimes, max_select=5, context="crimes for comparison")
        if crimes:
            compare_multiple_crimes(selected_data, crimes, state_name, district_name)
    elif action == "3":
        show_descriptive_stats(selected_data, [crime_choice])
    elif action == "4" and district_name == 'all':
        plot_all_districts_bar(selected_data, state_name, crime_choice)
    else:
        print("Invalid choice or option not available")
    
    return True


def handle_district_comparison_analysis(datasets):
    """Handle district vs district comparison within a state"""
    print("\n⚔️ DISTRICT vs DISTRICT COMPARISON")
    print("="*50)
    
    # Step 1: Choose dataset
    file_choice = get_dataset_choice(list(datasets.keys()))
    if not file_choice:
        return False
    
    chosen_dataset_df = datasets[file_choice]
    
    # Step 2: Choose state
    dataset_states = chosen_dataset_df['State Name'].unique()
    state_name = get_state_choice(dataset_states)
    if not state_name:
        return False
    
    # Step 3: Choose crime type
    crime_choice = get_crime_choice(chosen_dataset_df)
    if not crime_choice:
        return False
    
    # Step 4: Choose districts to compare
    state_districts = chosen_dataset_df[chosen_dataset_df['State Name'] == state_name]['District Name'].unique()
    print(f"\n🏙️ Available districts in {state_name}:")
    for i, d in enumerate(sorted(state_districts), 1):
        print(f"{i}. {d}")
    
    districts_input = input("\nEnter districts to compare (comma-separated numbers/names, or 'all' for all districts): ").strip()
    chosen_districts = parse_multiple_selection(districts_input, sorted(state_districts), allow_all=True)
    
    if not chosen_districts:
        print("❌ No valid districts selected")
        return False
    
    print(f"\n📊 Comparing {crime_choice} across {len(chosen_districts)} districts in {state_name}")
    
    # Show comparison options
    print("\nComparison Options:")
    print("1. Line chart - Trends over time")
    print("2. Bar chart - Total comparison")
    
    action = input("Choose visualization (1-2): ").strip()
    
    if action == "1":
        compare_districts(chosen_dataset_df, state_name, chosen_districts, crime_choice)
    elif action == "2":
        state_data = chosen_dataset_df[chosen_dataset_df['State Name'] == state_name]
        plot_all_districts_bar(state_data, state_name, crime_choice)
    else:
        print("Invalid choice")
    
    return True


def handle_state_comparison_analysis(datasets):
    """Handle state vs state comparison"""
    print("\n🌍 STATE vs STATE COMPARISON")
    print("="*50)
    
    # Step 1: Choose dataset
    file_choice = get_dataset_choice(list(datasets.keys()))
    if not file_choice:
        return False
    
    # Step 2: Choose crime type
    crime_choice = get_crime_choice(datasets[file_choice])
    if not crime_choice:
        return False
    
    # Step 3: Use existing cross-state analysis
    compare_states_datasets(datasets, file_choice, crime_choice)
    return True


def handle_dataset_comparison_analysis(datasets):
    """Handle dataset vs dataset comparison (IPC vs Cyber vs Women crimes etc.)"""
    print("\n📊 DATASET vs DATASET COMPARISON")
    print("="*50)
    
    # Step 1: Choose location first
    # Use any dataset to get states (they should be consistent)
    sample_dataset = list(datasets.values())[0]
    dataset_states = sample_dataset['State Name'].unique()
    state_name = get_state_choice(dataset_states)
    if not state_name:
        return False
    
    # Step 2: Choose district
    district_name = get_district_choice(state_name, sample_dataset)
    if not district_name:
        return False
    
    location_desc = f"{district_name}, {state_name}" if district_name != 'all' else f"ALL Districts in {state_name}"
    
    # Step 3: Use existing cross-dataset comparison
    compare_dataset_types(datasets, state_name, district_name, location_desc)
    return True


def handle_hotspot_analysis(datasets):
    """Handle crime hotspot identification"""
    print("\n🔥 CRIME HOTSPOT ANALYSIS")
    print("="*50)
    
    # Step 1: Choose dataset
    file_choice = get_dataset_choice(list(datasets.keys()))
    if not file_choice:
        return False
    
    chosen_dataset_df = datasets[file_choice]
    
    # Step 2: Choose analysis scope
    print("\nHotspot Analysis Scope:")
    print("1. Within a specific state (district hotspots)")
    print("2. Across all states (state hotspots)")
    
    scope = input("Choose scope (1-2): ").strip()
    
    # Step 3: Choose crime type
    crime_choice = get_crime_choice(chosen_dataset_df)
    if not crime_choice:
        return False
    
    if scope == "1":
        # District hotspots within a state
        dataset_states = chosen_dataset_df['State Name'].unique()
        state_name = get_state_choice(dataset_states)
        if not state_name:
            return False
        
        state_data = chosen_dataset_df[chosen_dataset_df['State Name'] == state_name]
        show_crime_hotspots(state_data, state_name, crime_choice)
        
    elif scope == "2":
        # State hotspots across country
        print(f"\n🌍 Top States for {crime_choice}:")
        state_totals = chosen_dataset_df.groupby('State Name')[crime_choice].sum().sort_values(ascending=False)
        
        n_input = input("How many top states to show? (default: 10): ").strip()
        try:
            n = int(n_input) if n_input else 10
        except ValueError:
            n = 10
        
        top_states = state_totals.head(n)
        print(f"\n🏆 Top {n} States for {crime_choice}:")
        for i, (state, total) in enumerate(top_states.items(), 1):
            print(f"{i:2d}. {state.title()}: {total:,} cases")
        
        # Visualize
        plt.figure(figsize=(12, 8))
        sns.barplot(x=top_states.values, y=top_states.index, palette="viridis")
        plt.title(f"Top {n} States - {crime_choice} Cases", fontsize=14, fontweight='bold')
        plt.xlabel("Total Cases")
        plt.ylabel("State")
        plt.tight_layout()
        plt.show()
    
    return True


def categorize_crimes(df):
    """
    Categorize crimes in a dataset based on predefined crime categories.
    Returns a dictionary with category totals.
    """
    # Get all crime columns (exclude metadata columns)
    metadata_cols = ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']
    crime_cols = [col for col in df.columns if col not in metadata_cols]
    
    category_totals = {}
    
    for category, crime_keywords in CRIME_CATEGORIES.items():
        total = 0
        matched_columns = []
        
        for col in crime_cols:
            col_lower = col.lower().replace('_', ' ')
            # Check if any crime keyword matches the column name
            for keyword in crime_keywords:
                if keyword.lower() in col_lower or col_lower in keyword.lower():
                    if col not in matched_columns:  # Avoid double counting
                        total += df[col].sum()
                        matched_columns.append(col)
                    break
        
        if total > 0:
            category_totals[category] = {
                'total': total,
                'columns': matched_columns
            }
    
    return category_totals

def get_location_crime_categories(df, state_name=None, district_name=None):
    """
    Get crime category totals for a specific location (state or district).
    """
    filtered_df = df.copy()
    
    if state_name:
        filtered_df = filtered_df[filtered_df['State Name'] == state_name.lower()]
    
    if district_name:
        filtered_df = filtered_df[filtered_df['District Name'] == district_name.lower()]
    
    if filtered_df.empty:
        return {}
    
    return categorize_crimes(filtered_df)

def plot_category_pie_chart(category_data, location_name, title_suffix=""):
    """
    Create a pie chart showing crime category distribution.
    """
    if not category_data:
        print("❌ No data available for pie chart.")
        return False
    
    categories = list(category_data.keys())
    totals = [data['total'] for data in category_data.values()]
    
    # Create pie chart
    plt.figure(figsize=(10, 8))
    colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
    
    wedges, texts, autotexts = plt.pie(totals, labels=categories, autopct='%1.1f%%', 
                                       colors=colors, startangle=90, textprops={'fontsize': 10})
    
    plt.title(f"Crime Category Distribution - {location_name}{title_suffix}", 
              fontsize=14, fontweight='bold', pad=20)
    
    # Make percentage text more readable
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    plt.axis('equal')
    plt.tight_layout()
    plt.show()
    
    return True

def plot_category_bar_chart(category_data, location_name, title_suffix=""):
    """
    Create a bar chart showing crime category totals.
    """
    if not category_data:
        print("❌ No data available for bar chart.")
        return False
    
    categories = list(category_data.keys())
    totals = [data['total'] for data in category_data.values()]
    
    # Sort by total (descending)
    sorted_data = sorted(zip(categories, totals), key=lambda x: x[1], reverse=True)
    categories, totals = zip(*sorted_data)
    
    # Create bar chart
    plt.figure(figsize=(12, 8))
    bars = plt.bar(categories, totals, color=plt.cm.viridis(np.linspace(0, 1, len(categories))))
    
    plt.title(f"Crime Category Totals - {location_name}{title_suffix}", 
              fontsize=14, fontweight='bold')
    plt.xlabel("Crime Categories", fontsize=12)
    plt.ylabel("Total Cases", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on bars
    for bar, total in zip(bars, totals):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{int(total):,}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.show()
    
    return True

def handle_statistical_analysis(datasets):
    """Handle detailed statistical analysis"""
    print("\n📈 STATISTICAL ANALYSIS")
    print("="*50)
    
    # Step 1: Choose dataset
    file_choice = get_dataset_choice(list(datasets.keys()))
    if not file_choice:
        return False
    
    chosen_dataset_df = datasets[file_choice]
    
    # Step 2: Choose location
    dataset_states = chosen_dataset_df['State Name'].unique()
    state_name = get_state_choice(dataset_states)
    if not state_name:
        return False
    
    district_name = get_district_choice(state_name, chosen_dataset_df)
    if not district_name:
        return False
    
    # Filter data
    if district_name == 'all':
        selected_data = chosen_dataset_df[chosen_dataset_df['State Name'] == state_name]
        location_desc = f"ALL Districts in {state_name}"
    else:
        selected_data = chosen_dataset_df[
            (chosen_dataset_df['State Name'] == state_name) &
            (chosen_dataset_df['District Name'] == district_name)
        ]
        location_desc = f"{district_name}, {state_name}"
    
    if selected_data.empty:
        print(f"❌ No data found for {location_desc}")
        return False
    
    # Step 3: Choose crimes for analysis
    available_crimes = [c for c in chosen_dataset_df.columns if c not in 
                       ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
    
    print(f"\n📊 Statistical Analysis for {location_desc}")
    print("Available crimes:")
    for i, c in enumerate(available_crimes, 1):
        print(f"{i}. {c}")
    
    crimes = enhanced_crime_selection_prompt(available_crimes, max_select=10, context="crimes for statistics")
    
    if not crimes:
        print("❌ No valid crimes selected")
        return False
    
    show_descriptive_stats(selected_data, crimes)
    return True


def get_main_analysis_choice():
    """
    Show the main analysis options and get user choice.
    """
    print("\n" + "="*60)
    print("🎯 CHOOSE YOUR ANALYSIS TYPE")
    print("="*60)
    
    print("1. Plot single crime trend")
    print("2. Compare multiple crimes")  
    print("3. Compare districts")
    print("4. Descriptive stats & Outliers")
    print("5. Compare all districts")
    print("6. Top hotspots")
    print("7. Compare dataset types")
    print("8. Cross-state comparison")
    print("9. 🎨 Enhanced Visualizations (Pie, Heatmap, Interactive)")
    print("10. 📊 Crime Category Analysis (Pie & Bar Charts)")
    print("11. 🎯 District Risk Score Calculator (NEW!)")
    
    while True:
        choice = input("\nEnter your choice (1-11): ").strip()
        if choice in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']:
            return choice
        else:
            print("❌ Invalid choice. Please enter 1-11.")


def handle_option_1_single_trend(datasets):
    """Option 1: Plot single crime trend"""
    print("\n📈 SINGLE CRIME TREND ANALYSIS")
    print("="*40)
    
    # 1️⃣ Which dataset?
    print("1️⃣ Which dataset do you want to use?")
    file_choice = get_dataset_choice(list(datasets.keys()))
    if not file_choice:
        return False
    
    chosen_dataset_df = datasets[file_choice]
    
    # 2️⃣ Which district?
    print("2️⃣ Which district?")
    dataset_states = chosen_dataset_df['State Name'].unique()
    state_name = get_state_choice(dataset_states)
    if not state_name:
        return False
    
    district_name = get_district_choice(state_name, chosen_dataset_df)
    if not district_name:
        return False
    
    # 3️⃣ Which crime type?
    print("3️⃣ Which crime type?")
    crime_choice = get_crime_choice(chosen_dataset_df)
    if not crime_choice:
        return False
    
    # Filter data
    if district_name == 'all':
        selected_data = chosen_dataset_df[chosen_dataset_df['State Name'] == state_name]
    else:
        selected_data = chosen_dataset_df[
            (chosen_dataset_df['State Name'] == state_name) &
            (chosen_dataset_df['District Name'] == district_name)
        ]
    
    # 4️⃣ Show plot
    print("4️⃣ Generating trend plot...")
    plot_trends(selected_data, state_name, district_name, crime_choice)
    return True


def handle_option_2_multiple_crimes(datasets):
    """Option 2: Compare multiple crimes"""
    print("\n📊 MULTIPLE CRIMES COMPARISON")
    print("="*40)
    
    # 1️⃣ Which dataset?
    print("1️⃣ Which dataset?")
    file_choice = get_dataset_choice(list(datasets.keys()))
    if not file_choice:
        return False
    
    chosen_dataset_df = datasets[file_choice]
    
    # 2️⃣ Which district?
    print("2️⃣ Which district?")
    dataset_states = chosen_dataset_df['State Name'].unique()
    state_name = get_state_choice(dataset_states)
    if not state_name:
        return False
    
    district_name = get_district_choice(state_name, chosen_dataset_df)
    if not district_name:
        return False
    
    # 3️⃣ Which crime types? (multi-select)
    print("3️⃣ Which crime types do you want to compare? (multi-select)")
    available_crimes = [c for c in chosen_dataset_df.columns if c not in 
                       ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
    
    crimes = enhanced_crime_selection_prompt(available_crimes, max_select=7, context="crimes for comparison")
    if not crimes:
        print("❌ No valid crimes selected")
        return False
    
    # Filter data
    if district_name == 'all':
        selected_data = chosen_dataset_df[chosen_dataset_df['State Name'] == state_name]
    else:
        selected_data = chosen_dataset_df[
            (chosen_dataset_df['State Name'] == state_name) &
            (chosen_dataset_df['District Name'] == district_name)
        ]
    
    # 4️⃣ Show line plot
    print("4️⃣ Generating comparison plot...")
    compare_multiple_crimes(selected_data, crimes, state_name, district_name)
    return True


def handle_option_3_compare_districts(datasets):
    """Option 3: Compare multiple districts"""
    print("\n🏙️ DISTRICTS COMPARISON")
    print("="*40)
    
    # 1️⃣ Which dataset?
    print("1️⃣ Which dataset?")
    file_choice = get_dataset_choice(list(datasets.keys()))
    if not file_choice:
        return False
    
    chosen_dataset_df = datasets[file_choice]
    
    # 2️⃣ Which state?
    print("2️⃣ Which state?")
    dataset_states = chosen_dataset_df['State Name'].unique()
    state_name = get_state_choice(dataset_states)
    if not state_name:
        return False
    
    # 3️⃣ Which crime type?
    print("3️⃣ Which crime type?")
    crime_choice = get_crime_choice(chosen_dataset_df)
    if not crime_choice:
        return False
    
    # 4️⃣ Which districts?
    print("4️⃣ Which districts do you want to compare?")
    state_districts = chosen_dataset_df[chosen_dataset_df['State Name'] == state_name]['District Name'].unique()
    print("Available districts:")
    for i, d in enumerate(sorted(state_districts), 1):
        print(f"{i}. {d}")
    
    districts_input = input("Enter districts (comma-separated numbers/names, or 'all'): ").strip()
    chosen_districts = parse_multiple_selection(districts_input, sorted(state_districts), allow_all=True)
    if not chosen_districts:
        print("❌ No valid districts selected")
        return False
    
    # 5️⃣ Show comparison
    print("5️⃣ Generating districts comparison...")
    compare_districts(chosen_dataset_df, state_name, chosen_districts, crime_choice)
    return True


def handle_option_7_compare_datasets(datasets):
    """Option 7: Compare dataset types"""
    print("\n📊 DATASET TYPES COMPARISON")
    print("="*40)
    
    # 1️⃣ Which district or state?
    print("1️⃣ Which district or state?")
    # Use any dataset to get states (they should be consistent)
    sample_dataset = list(datasets.values())[0]
    dataset_states = sample_dataset['State Name'].unique()
    state_name = get_state_choice(dataset_states)
    if not state_name:
        return False
    
    district_name = get_district_choice(state_name, sample_dataset)
    if not district_name:
        return False
    
    location_desc = f"{district_name}, {state_name}" if district_name != 'all' else f"ALL Districts in {state_name}"
    
    # 2️⃣ Which datasets? (automatically use all available)
    print("2️⃣ Using all available datasets for comparison:")
    for name in datasets.keys():
        print(f"   • {name.replace('_', ' ').title()}")
    
    # 3️⃣ Show VS comparison
    print("3️⃣ Generating dataset comparison...")
    compare_dataset_types(datasets, state_name, district_name, location_desc)
    return True


def handle_option_4_descriptive_stats(datasets):
    """Option 4: Descriptive statistics & Outliers"""
    print("\n📊 DESCRIPTIVE STATISTICS & OUTLIERS")
    print("="*40)
    
    # 1️⃣ Which dataset?
    print("1️⃣ Which dataset?")
    file_choice = get_dataset_choice(list(datasets.keys()))
    if not file_choice:
        return False
    
    chosen_dataset_df = datasets[file_choice]
    
    # 2️⃣ Which district/state?
    print("2️⃣ Which location?")
    dataset_states = chosen_dataset_df['State Name'].unique()
    state_name = get_state_choice(dataset_states)
    if not state_name:
        return False
    
    district_name = get_district_choice(state_name, chosen_dataset_df)
    if not district_name:
        return False
    
    # 3️⃣ Which crime types?
    print("3️⃣ Which crime types for statistics?")
    available_crimes = [c for c in chosen_dataset_df.columns if c not in 
                       ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
    
    crimes = enhanced_crime_selection_prompt(available_crimes, max_select=10, context="crimes for statistics")
    if not crimes:
        print("❌ No valid crimes selected")
        return False
    
    # Filter data
    if district_name == 'all':
        selected_data = chosen_dataset_df[chosen_dataset_df['State Name'] == state_name]
    else:
        selected_data = chosen_dataset_df[
            (chosen_dataset_df['State Name'] == state_name) &
            (chosen_dataset_df['District Name'] == district_name)
        ]
    
    # 4️⃣ Show statistics (which now includes Z-score and IQR)
    print("4️⃣ Generating descriptive statistics & textual outlier analysis...")
    show_descriptive_stats(selected_data, crimes)

    # === NEW BOXPLOT SECTION ===
    print("\n" + "-"*30)
    print("📦 VISUAL OUTLIER ANALYSIS")
    plot_choice = input("Do you want to see a boxplot for visual outliers? (yes/no): ").strip().lower()
    if plot_choice in ['yes', 'y']:
        
        # Re-create location_desc for the plot title
        if district_name == 'all':
            location_desc = f"ALL Districts in {state_name}"
        else:
            location_desc = f"{district_name}, {state_name}"

        # If multiple crimes were analyzed, ask which one to plot
        crime_to_plot = None
        if len(crimes) > 1:
            print("Which crime do you want to plot?")
            for i, c in enumerate(crimes, 1):
                print(f"{i}. {c}")
            
            try:
                choice = int(input(f"Enter number (1-{len(crimes)}): ").strip()) - 1
                if 0 <= choice < len(crimes):
                    crime_to_plot = crimes[choice]
                else:
                    print(f"Invalid choice, plotting the first crime: {crimes[0]}")
                    crime_to_plot = crimes[0]
            except ValueError:
                print(f"Invalid input, plotting the first crime: {crimes[0]}")
                crime_to_plot = crimes[0]
        elif len(crimes) == 1:
            crime_to_plot = crimes[0]
        
        if crime_to_plot:
            # Call the new function
            plot_boxplot_outliers(selected_data, crime_to_plot, location_desc)
        else:
            print("No crimes were selected for statistical analysis.")
    # === END NEW SECTION ===
    
    return True


def handle_option_5_compare_all_districts(datasets):
    """Option 5: Compare all districts in a state (bar chart)"""
    print("\n🏛️ COMPARE ALL DISTRICTS")
    print("="*40)
    
    # 1️⃣ Which dataset?
    print("1️⃣ Which dataset?")
    file_choice = get_dataset_choice(list(datasets.keys()))
    if not file_choice:
        return False
    
    chosen_dataset_df = datasets[file_choice]
    
    # 2️⃣ Which state?
    print("2️⃣ Which state?")
    dataset_states = chosen_dataset_df['State Name'].unique()
    state_name = get_state_choice(dataset_states)
    if not state_name:
        return False
    
    # 3️⃣ Which crime type?
    print("3️⃣ Which crime type?")
    crime_choice = get_crime_choice(chosen_dataset_df)
    if not crime_choice:
        return False
    
    # Get state data
    state_data = chosen_dataset_df[chosen_dataset_df['State Name'] == state_name]
    
    # 4️⃣ Show bar chart
    print("4️⃣ Generating districts comparison bar chart...")
    plot_all_districts_bar(state_data, state_name, crime_choice)
    return True


def handle_option_6_top_hotspots(datasets):
    """Option 6: Top crime hotspots"""
    print("\n🔥 TOP CRIME HOTSPOTS")
    print("="*40)
    
    # 1️⃣ Which dataset?
    print("1️⃣ Which dataset?")
    file_choice = get_dataset_choice(list(datasets.keys()))
    if not file_choice:
        return False
    
    chosen_dataset_df = datasets[file_choice]
    
    # 2️⃣ Which scope?
    print("2️⃣ Analysis scope:")
    print("1. District hotspots within a state")
    print("2. State hotspots across country")
    
    scope = input("Choose scope (1-2): ").strip()
    
    # 3️⃣ Which crime type?
    print("3️⃣ Which crime type?")
    crime_choice = get_crime_choice(chosen_dataset_df)
    if not crime_choice:
        return False
    
    if scope == "1":
        # District hotspots within a state
        print("4️⃣ Which state for district analysis?")
        dataset_states = chosen_dataset_df['State Name'].unique()
        state_name = get_state_choice(dataset_states)
        if not state_name:
            return False
        
        state_data = chosen_dataset_df[chosen_dataset_df['State Name'] == state_name]
        print("5️⃣ Generating district hotspots...")
        show_crime_hotspots(state_data, state_name, crime_choice)
        
    elif scope == "2":
        # State hotspots across country
        print("4️⃣ Generating state hotspots...")
        state_totals = chosen_dataset_df.groupby('State Name')[crime_choice].sum().sort_values(ascending=False)
        
        n_input = input("How many top states to show? (default: 10): ").strip()
        try:
            n = int(n_input) if n_input else 10
        except ValueError:
            n = 10
        
        top_states = state_totals.head(n)
        print(f"\n🏆 Top {n} States for {crime_choice}:")
        for i, (state, total) in enumerate(top_states.items(), 1):
            print(f"{i:2d}. {state.title()}: {total:,} cases")
        
        # Visualize
        plt.figure(figsize=(12, 8))
        sns.barplot(x=top_states.values, y=top_states.index, palette="viridis")
        plt.title(f"Top {n} States - {crime_choice} Cases", fontsize=14, fontweight='bold')
        plt.xlabel("Total Cases")
        plt.ylabel("State")
        plt.tight_layout()
        plt.show()
    else:
        print("❌ Invalid scope choice")
        return False
    
    return True


def handle_option_8_cross_state(datasets):
    """Option 8: Cross-state comparison"""
    print("\n🌍 CROSS-STATE COMPARISON")
    print("="*40)
    
    # 1️⃣ Which dataset?
    print("1️⃣ Which dataset?")
    file_choice = get_dataset_choice(list(datasets.keys()))
    if not file_choice:
        return False
    
    # 2️⃣ Which crime type?
    print("2️⃣ Which crime type?")
    crime_choice = get_crime_choice(datasets[file_choice])
    if not crime_choice:
        return False
    
    # 3️⃣ & 4️⃣ States selection and results handled in existing function
    print("3️⃣ Selecting states and generating results...")
    compare_states_datasets(datasets, file_choice, crime_choice)
    return True


def handle_option_9_enhanced_visualizations(datasets):
    """Option 9: Enhanced Visualizations (Pie, Heatmap, Interactive, etc.)"""
    print("\n🎨 ENHANCED VISUALIZATIONS")
    print("="*50)
    
    # 1️⃣ Choose dataset
    print("1️⃣ Which dataset do you want to visualize?")
    file_choice = get_dataset_choice(list(datasets.keys()))
    if not file_choice:
        return False
    
    chosen_dataset_df = datasets[file_choice]
    
    # 2️⃣ Choose location
    print("2️⃣ Select location for analysis:")
    state_name = get_state_choice(chosen_dataset_df['State Name'].unique())
    if not state_name:
        return False
    
    # Get districts in the state
    state_data = chosen_dataset_df[chosen_dataset_df['State Name'] == state_name]
    district_name = get_district_choice(state_name, chosen_dataset_df)
    if not district_name:
        return False
    
    # Filter data
    if district_name == 'all':
        selected_data = state_data
        location_desc = f"All Districts in {state_name}"
    else:
        selected_data = state_data[state_data['District Name'] == district_name]
        location_desc = f"{district_name}, {state_name}"
    
    # 3️⃣ Choose visualization type
    print(f"\n3️⃣ Choose visualization type for {location_desc}:")
    print("1. 🥧 Pie/Donut Chart (Crime Distribution)")
    print("2. 🔥 Heatmap (Crime Correlations)")
    print("3. 📊 Stacked Bar Chart (Year vs Crime)")
    print("4. 🗺️ Hotspot Map (Top States)")
    print("5. 🎛️ Interactive Dashboard")
    print("6. 📈 Enhanced Line Chart (Plotly)")
    print("7. 🎯 All Visualizations")
    
    viz_choice = input("Enter choice (1-7): ").strip()
    
    try:
        if viz_choice == "1":
            plot_pie_chart_crime_distribution(selected_data, state_name, district_name)
        
        elif viz_choice == "2":
            # NEW: User-friendly heatmap menu
            print(f"\n🔥 HEATMAP ANALYSIS")
            print(f"Your current location context: {location_desc}")
            print("="*50)
            print("Which type of heatmap would you like to see?")

            # Option 1: Relevant to the user's selected STATE
            print(f"\n1. 🏘️ District vs. Crime Heatmap")
            print(f"   (Compares all districts within {state_name.title()})")

            # Option 2: Relevant to the user's selected LOCATION (state or district)
            print(f"\n2. 📅 Crime vs. Year Heatmap")
            print(f"   (Shows crime trends over time for {location_desc})")
            
            # Option 3: Broader context, ignores user's location selection
            print(f"\n3. 🏛️ State vs. Crime Heatmap (National)")
            print(f"   (Note: This shows ALL states, ignoring your current selection)")

            # Option 4: The 'geographic' one. This is State vs District.
            print(f"\n4. 🗺️ State vs. District Heatmap (National)")
            print(f"   (Note: This shows ALL states and districts, ignoring your current selection)")

            heatmap_choice = input("\nChoose heatmap type (1-4): ").strip()
            
            if heatmap_choice == "1":
                # This needs data for the WHOLE STATE, even if user picked one district.
                print(f"Generating heatmap for all districts in {state_name}...")
                state_data = chosen_dataset_df[chosen_dataset_df['State Name'] == state_name]
                plot_crime_heatmap(state_data, state_name, "all", method='district_comparison')

            elif heatmap_choice == "2":
                # This uses the user's EXACT selection (selected_data)
                print(f"Generating heatmap for {location_desc}...")
                plot_crime_heatmap(selected_data, state_name, district_name, method='year_location')
                
            elif heatmap_choice == "3":
                # This uses the FULL dataset, ignoring location context
                print("Generating national state vs. crime heatmap...")
                plot_crime_heatmap(chosen_dataset_df, "All States", "all", method='state_comparison')

            elif heatmap_choice == "4":
                # This also uses the FULL dataset, ignoring location context
                print("Generating national state vs. district heatmap...")
                plot_crime_heatmap(chosen_dataset_df, "All States", "all", method='geographic')
                
            else:
                print("❌ Invalid choice. Returning to menu.")

        elif viz_choice == "3":
            plot_stacked_bar_chart(selected_data, state_name, district_name)
        
        elif viz_choice == "4":
            # For hotspot map, use full dataset
            crime_columns = [col for col in chosen_dataset_df.columns if col not in 
                           ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
            if crime_columns:
                print("Available crime types for mapping:")
                for i, crime in enumerate(crime_columns[:10], 1):
                    print(f"{i}. {crime}")
                crime_choice = input("Enter crime number or name: ").strip()
                
                selected_crime = None
                try:
                    # Try number
                    idx = int(crime_choice) - 1
                    if 0 <= idx < len(crime_columns):
                         selected_crime = crime_columns[idx]
                except ValueError:
                    # Try name
                    if crime_choice in crime_columns:
                        selected_crime = crime_choice
                
                if not selected_crime:
                    print(f"Defaulting to first crime: {crime_columns[0]}")
                    selected_crime = crime_columns[0]  # Default to first
                
                plot_india_crime_map(chosen_dataset_df, selected_crime)
            else:
                print("No crime data available for mapping.")
        
        elif viz_choice == "5":
            plot_interactive_crime_dashboard(datasets, file_choice)
        
        elif viz_choice == "6":
            # Enhanced line chart
            crime_columns = [col for col in selected_data.columns if col not in 
                        ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
            
            crimes = enhanced_crime_selection_prompt(crime_columns, max_select=5, context="crimes for trend analysis")
            if crimes and 'Year' in selected_data.columns:
                yearly_data = selected_data.groupby('Year')[crimes].sum().reset_index()
                
                fig = px.line(
                    yearly_data.melt(id_vars=['Year'], var_name='Crime Type', value_name='Cases'),
                    x='Year',
                    y='Cases',
                    color='Crime Type',
                    title=f'📈 Enhanced Crime Trends - {location_desc}',
                    markers=True,
                    line_shape='spline'
                )
                
                fig.update_layout(
                    height=600,
                    hovermode='x unified'
                )
                
                fig.show()
                print("✅ Enhanced line chart generated!")
            else:
                print("No crimes selected or Year column not available.")
        
        elif viz_choice == "7":
            # All visualizations
            print(f"\n🎨 Generating all visualizations for {location_desc}...")
            
            print("\n--- 1. Pie Chart (Crime Distribution) ---")
            plot_pie_chart_crime_distribution(selected_data, state_name, district_name)
            
            print(f"\n--- 2. Heatmap (Districts in {state_name}) ---")
            # Use the whole state's data for a meaningful heatmap
            state_data = chosen_dataset_df[chosen_dataset_df['State Name'] == state_name]
            plot_crime_heatmap(state_data, state_name, "all", method='district_comparison')
            
            print("\n--- 3. Stacked Bar Chart (Trends over Time) ---")
            plot_stacked_bar_chart(selected_data, state_name, district_name)
            
            # Simple enhanced line chart
            crime_columns = [col for col in selected_data.columns if col not in 
                        ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]
            
            if crime_columns and 'Year' in selected_data.columns:
                print("\n--- 4. Line Chart (Top 3 Crime Trends) ---")
                # Use top 3 crimes for the line chart
                crime_totals = selected_data[crime_columns].sum().sort_values(ascending=False)
                top_crimes = crime_totals.head(3).index.tolist()
                
                if top_crimes:
                    yearly_data = selected_data.groupby('Year')[top_crimes].sum().reset_index()
                    
                    fig = px.line(
                        yearly_data.melt(id_vars=['Year'], var_name='Crime Type', value_name='Cases'),
                        x='Year',
                        y='Cases',
                        color='Crime Type',
                        title=f'📈 Top 3 Crime Trends - {location_desc}',
                        markers=True
                    )
                    
                    fig.show()
                else:
                    print("No crime data to plot for line chart.")
            
            print("\n✅ All visualizations completed!")
        
        else:
            print("❌ Invalid choice. Please select 1-7.")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating visualization: {str(e)}")
        print("This might be due to missing data or Plotly not being installed.")
        print("Install Plotly with: pip install plotly")
        return False


def handle_option_11_risk_scoring(datasets):
    """Option 11: Calculate and analyze district risk scores"""
    print("\n🎯 DISTRICT RISK SCORING SYSTEM")
    print("="*70)
    print("This analysis calculates comprehensive risk scores for districts based on:")
    print("  • Crime Volume (30 points) - Total number of crimes")
    print("  • Crime Severity (40 points) - Weighted by crime type seriousness")
    print("  • Growth Trend (20 points) - Year-over-year crime increase")
    print("  • Crime Diversity (10 points) - Variety of crime types")
    print("\nRisk Levels: 🔴 Extreme (75+) | 🟠 High (60+) | 🟡 Moderate (40+) | 🟢 Low (20+) | ⚪ Minimal (<20)")
    print("="*70)
    
    # 1️⃣ Choose dataset
    print("\n1️⃣ Select dataset for risk analysis:")
    file_choice = get_dataset_choice(list(datasets.keys()))
    if not file_choice:
        return False
    
    chosen_dataset_df = datasets[file_choice]
    
    # 2️⃣ Choose scope
    print("\n2️⃣ Choose analysis scope:")
    print("1. 🏛️  Specific State (all districts in one state)")
    print("2. 🌍 National (all districts across all states)")
    print("3. 🏆 Top Risk Districts (highest risk scores nationwide)")
    
    scope_choice = input("\nEnter scope (1-3): ").strip()
    
    if scope_choice == "1":
        # State-specific analysis
        print("\n3️⃣ Select state:")
        state_name = get_state_choice(chosen_dataset_df['State Name'].unique())
        if not state_name:
            return False
        
        print(f"\n📊 Calculating risk scores for all districts in {state_name.title()}...")
        risk_df = calculate_all_districts_risk_scores(chosen_dataset_df, state_name)
        
        if risk_df is None:
            return False
        
        # Display results
        print(f"\n✅ Analyzed {len(risk_df)} districts in {state_name.title()}")
        
        # Show summary statistics
        print(f"\n📈 RISK SCORE SUMMARY:")
        print(f"   Average Risk Score: {risk_df['Risk_Score'].mean():.2f}")
        print(f"   Highest Risk: {risk_df['Risk_Score'].max():.2f} ({risk_df.iloc[0]['District']})")
        print(f"   Lowest Risk: {risk_df['Risk_Score'].min():.2f}")
        
        # Risk level distribution
        print(f"\n🎯 RISK LEVEL BREAKDOWN:")
        for level, count in risk_df['Risk_Level'].value_counts().items():
            percentage = (count / len(risk_df)) * 100
            print(f"   {level}: {count} districts ({percentage:.1f}%)")
        
        # Display top districts
        top_n = min(15, len(risk_df))
        display_risk_score_table(risk_df, top_n, f"Top {top_n} Highest Risk Districts in {state_name.title()}")
        
        # Ask for visualizations
        viz_choice = input("\n🎨 Generate visualizations? (yes/no): ").strip().lower()
        if viz_choice in ['yes', 'y']:
            plot_risk_score_visualizations(risk_df, state_name)
        
        # Export option
        export_choice = input("\n💾 Export full risk scores to CSV? (yes/no): ").strip().lower()
        if export_choice in ['yes', 'y']:
            filename = f"risk_scores_{state_name}_{file_choice}.csv"
            risk_df.to_csv(filename, index=False)
            print(f"✅ Exported to {filename}")
    
    elif scope_choice == "2":
        # National analysis
        print(f"\n📊 Calculating risk scores for ALL districts nationwide...")
        print("⚠️  This may take a moment for large datasets...")
        
        risk_df = calculate_all_districts_risk_scores(chosen_dataset_df)
        
        if risk_df is None:
            return False
        
        print(f"\n✅ Analyzed {len(risk_df)} districts across {risk_df['State'].nunique()} states")
        
        # Show national statistics
        print(f"\n📈 NATIONAL RISK SCORE SUMMARY:")
        print(f"   Average Risk Score: {risk_df['Risk_Score'].mean():.2f}")
        print(f"   Highest Risk: {risk_df['Risk_Score'].max():.2f} ({risk_df.iloc[0]['District']}, {risk_df.iloc[0]['State']})")
        print(f"   Lowest Risk: {risk_df['Risk_Score'].min():.2f}")
        
        # Risk level distribution
        print(f"\n🎯 NATIONAL RISK LEVEL BREAKDOWN:")
        for level, count in risk_df['Risk_Level'].value_counts().items():
            percentage = (count / len(risk_df)) * 100
            print(f"   {level}: {count} districts ({percentage:.1f}%)")
        
        # Top states by average risk
        print(f"\n🏛️  STATES BY AVERAGE RISK SCORE:")
        state_avg_risk = risk_df.groupby('State')['Risk_Score'].mean().sort_values(ascending=False).head(10)
        for i, (state, avg_score) in enumerate(state_avg_risk.items(), 1):
            print(f"   {i:2d}. {state}: {avg_score:.2f}")
        
        # Display top districts
        top_n = min(25, len(risk_df))
        display_risk_score_table(risk_df, top_n, f"Top {top_n} Highest Risk Districts Nationwide")
        
        # Ask for visualizations
        viz_choice = input("\n🎨 Generate visualizations? (yes/no): ").strip().lower()
        if viz_choice in ['yes', 'y']:
            plot_risk_score_visualizations(risk_df)
        
        # Export option
        export_choice = input("\n💾 Export full risk scores to CSV? (yes/no): ").strip().lower()
        if export_choice in ['yes', 'y']:
            filename = f"risk_scores_national_{file_choice}.csv"
            risk_df.to_csv(filename, index=False)
            print(f"✅ Exported to {filename}")
    
    elif scope_choice == "3":
        # Top risk districts
        print(f"\n📊 Calculating risk scores to find highest risk districts nationwide...")
        
        risk_df = calculate_all_districts_risk_scores(chosen_dataset_df)
        
        if risk_df is None:
            return False
        
        # Get top N
        n_input = input("\nHow many top risk districts to show? (default: 20): ").strip()
        try:
            n = int(n_input) if n_input else 20
            n = min(n, len(risk_df))  # Cap at available districts
        except ValueError:
            n = 20
        
        top_districts = risk_df.head(n)
        
        print(f"\n🔴 TOP {n} HIGHEST RISK DISTRICTS IN INDIA")
        print(f"Based on {file_choice.replace('_', ' ').title()} dataset")
        
        display_risk_score_table(top_districts, n, f"Top {n} Highest Risk Districts")
        
        # Show which states appear most
        print(f"\n🏛️  STATES WITH MOST HIGH-RISK DISTRICTS (in top {n}):")
        state_counts = top_districts['State'].value_counts().head(10)
        for state, count in state_counts.items():
            print(f"   • {state}: {count} districts")
        
        # Visualizations
        viz_choice = input("\n🎨 Generate visualizations? (yes/no): ").strip().lower()
        if viz_choice in ['yes', 'y']:
            plot_risk_score_visualizations(top_districts)
        
        # Export option
        export_choice = input("\n💾 Export full risk scores to CSV? (yes/no): ").strip().lower()
        if export_choice in ['yes', 'y']:
            filename = f"risk_scores_top_{n}_{file_choice}.csv"
            top_districts.to_csv(filename, index=False)
            print(f"✅ Exported to {filename}")
    
    else:
        print("❌ Invalid scope choice.")
        return False
    
    print("\n✅ Risk scoring analysis completed!")
    return True

def handle_option_10_crime_categories(datasets):
    """Option 10: Crime Category Analysis with Pie & Bar Charts"""
    print("\n📊 CRIME CATEGORY ANALYSIS")
    print("="*50)
    
    # 1️⃣ Choose dataset
    print("1️⃣ Which dataset do you want to analyze?")
    file_choice = get_dataset_choice(list(datasets.keys()))
    if not file_choice:
        return False
    
    chosen_dataset_df = datasets[file_choice]
    
    # 2️⃣ Choose analysis scope
    print("\n2️⃣ Choose analysis scope:")
    print("1. 🏛️  State-level analysis (all districts in a state)")
    print("2. 🏘️  District-level analysis (specific district)")
    print("3. 🌍 National comparison (all states)")
    
    scope_choice = input("Enter scope (1-3): ").strip()
    
    if scope_choice == "1":
        # State-level analysis
        print("\n3️⃣ Select state:")
        state_name = get_state_choice(chosen_dataset_df['State Name'].unique())
        if not state_name:
            return False
        
        # Get category data for the state
        category_data = get_location_crime_categories(chosen_dataset_df, state_name=state_name)
        location_name = f"{state_name.title()} State"
        
    elif scope_choice == "2":
        # District-level analysis
        print("\n3️⃣ Select state:")
        state_name = get_state_choice(chosen_dataset_df['State Name'].unique())
        if not state_name:
            return False
        
        print("\n4️⃣ Select district:")
        district_name = get_district_choice(state_name, chosen_dataset_df)
        if not district_name or district_name == 'all':
            print("Please select a specific district for district-level analysis.")
            return False
        
        # Get category data for the district
        category_data = get_location_crime_categories(chosen_dataset_df, state_name=state_name, district_name=district_name)
        location_name = f"{district_name.title()}, {state_name.title()}"
        
    elif scope_choice == "3":
        # National comparison - compare categories across all states
        print("\n📊 Generating national crime category analysis...")
        category_data = categorize_crimes(chosen_dataset_df)
        location_name = "All India"
        
    else:
        print("❌ Invalid scope choice.")
        return False
    
    if not category_data:
        print(f"❌ No categorized crime data found for {location_name}")
        print("This might be because:")
        print("• The crime column names don't match our category keywords")
        print("• There's no data for the selected location")
        print("• The dataset doesn't contain recognizable crime types")
        return False
    
    # Show category summary
    print(f"\n📋 Crime Category Summary for {location_name}:")
    print("="*60)
    
    total_crimes = sum(data['total'] for data in category_data.values())
    
    for i, (category, data) in enumerate(sorted(category_data.items(), 
                                               key=lambda x: x[1]['total'], reverse=True), 1):
        percentage = (data['total'] / total_crimes) * 100
        print(f"{i:2d}. {category:25} | {data['total']:8,} cases | {percentage:5.1f}%")
        print(f"    Matched columns: {', '.join(data['columns'][:3])}{'...' if len(data['columns']) > 3 else ''}")
    
    print(f"\n📈 Total Categorized Crimes: {total_crimes:,}")
    
    # 4️⃣ Choose visualization type
    print(f"\n🎨 Choose visualization for {location_name}:")
    print("1. 🥧 Pie Chart (Category Distribution)")
    print("2. 📊 Bar Chart (Category Totals)")  
    print("3. 🎯 Both Charts")
    
    viz_choice = input("Enter choice (1-3): ").strip()
    
    try:
        if viz_choice == "1":
            plot_category_pie_chart(category_data, location_name)
            
        elif viz_choice == "2":
            plot_category_bar_chart(category_data, location_name)
            
        elif viz_choice == "3":
            print(f"\n🥧 Generating pie chart for {location_name}...")
            plot_category_pie_chart(category_data, location_name)
            
            print(f"\n📊 Generating bar chart for {location_name}...")
            plot_category_bar_chart(category_data, location_name)
            
        else:
            print("❌ Invalid choice. Please select 1-3.")
            return False
        
        # Show insights
        if len(category_data) >= 2:
            sorted_categories = sorted(category_data.items(), key=lambda x: x[1]['total'], reverse=True)
            top_category = sorted_categories[0]
            second_category = sorted_categories[1]
            
            print(f"\n💡 Key Insights for {location_name}:")
            print(f"   🥇 Most prevalent: {top_category[0]} ({top_category[1]['total']:,} cases)")
            print(f"   🥈 Second highest: {second_category[0]} ({second_category[1]['total']:,} cases)")
            
            ratio = top_category[1]['total'] / second_category[1]['total']
            print(f"   📊 {top_category[0]} is {ratio:.1f}x more common than {second_category[0]}")
        
        print(f"\n✅ Crime category analysis completed for {location_name}!")
        return True
        
    except Exception as e:
        print(f"❌ Error generating category analysis: {str(e)}")
        return False


def main():
    warnings.filterwarnings('ignore')
    
    # Show setup information
    verify_setup()
    
    # Load datasets
    datasets = load_datasets()
    if not datasets:
        print("\n🚨 SETUP INSTRUCTIONS:")
        print("1. Ensure you're running this script from the project root directory")
        print("2. Verify the 'Dataset' folder exists in the same directory as Data.py")
        print("3. Check that all required CSV files are present in the Dataset folder")
        print("4. Make sure you have read permissions for the files")
        print("\n💡 TIP: If you cloned from Git, make sure you pulled all files including the Dataset folder")
        return

    print("\n" + "="*60)
    print("🚀 SURAKSHA ANALYTICS - CRIME DATA ANALYSIS TOOL")
    print("="*60)

    while True:
        # Show main analysis options
        choice = get_main_analysis_choice()
        
        # Route to appropriate handler
        result = False
        if choice == '1':
            result = handle_option_1_single_trend(datasets)
        elif choice == '2':
            result = handle_option_2_multiple_crimes(datasets)
        elif choice == '3':
            result = handle_option_3_compare_districts(datasets)
        elif choice == '4':
            result = handle_option_4_descriptive_stats(datasets)
        elif choice == '5':
            result = handle_option_5_compare_all_districts(datasets)
        elif choice == '6':
            result = handle_option_6_top_hotspots(datasets)
        elif choice == '7':
            result = handle_option_7_compare_datasets(datasets)
        elif choice == '8':
            result = handle_option_8_cross_state(datasets)
        elif choice == '9':
            result = handle_option_9_enhanced_visualizations(datasets)
        elif choice == '10':
            result = handle_option_10_crime_categories(datasets)
        elif choice == '11':
            result = handle_option_11_risk_scoring(datasets)
        elif choice == '11':
            result = handle_option_11_risk_scoring(datasets)
        
        if not result:
            print("\n❌ Analysis failed or was cancelled. Please try again.")
            continue

        print("\n" + "-"*60)
        another = input("Perform another analysis? (yes/no): ").strip().lower()
        if another not in ['yes', 'y']:
            print("Exiting analysis tool. Goodbye!")
            break
        else:
            print("\nStarting new analysis...\n")


if __name__ == "__main__":
    main()