# analysis_functions.py
# Core analysis and statistical functions

from config import *
from user_interface import parse_multiple_selection

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