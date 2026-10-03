# visualization_functions.py
# All visualization and plotting functions

from config import *
from analysis_functions import categorize_crimes
from user_interface import parse_multiple_selection

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
    
    fig.show()
    print(f"✅ Interactive boxplot generated for {crime_col}.")

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