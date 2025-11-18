import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configure page
st.set_page_config(
    page_title="Crime Analyser",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set seaborn style
sns.set(style="whitegrid", palette="deep")

@st.cache_data
def load_datasets():
    """Load all datasets from Dataset folder with proper cleaning"""
    dataset_dir = Path("Dataset")
    
    if not dataset_dir.exists():
        st.error("Dataset folder not found!")
        return {}
    
    dataset_files = {
        'ipc': 'crime-by-juveniles-expanded.csv',
        'crime_against_women': 'districtwise_crime_against_women_readable.csv',
        'cyber_crimes': 'districtwise_cyber_crimes_readable.csv',
        'juveniles': 'districtwise_ipc_crimes_readable.csv',
        'missing_persons': 'districtwise-missing-persons-merged.csv'
    }
    
    datasets = {}
    
    for name, filename in dataset_files.items():
        file_path = dataset_dir / filename
        if file_path.exists():
            try:
                df = pd.read_csv(file_path)
                
                # Clean dataset like in Data.py
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
                
                datasets[name] = df
            except Exception as e:
                st.warning(f"Could not load {filename}: {e}")
    
    return datasets

def categorize_crimes(crime_columns):
    """Categorize crimes into logical groups for better user experience."""
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

def get_crime_columns(df):
    """Get crime columns from dataset"""
    return [col for col in df.columns if col not in 
            ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]

def plot_trends_streamlit(data, state, district, crime):
    """Create trend plot for Streamlit"""
    if data.empty or crime not in data.columns:
        st.warning(f"No data available for {crime}")
        return
    
    yearly = data.groupby("Year")[crime].sum().reset_index()
    
    if yearly.empty or yearly[crime].sum() == 0:
        st.warning(f"No reported cases of '{crime}' found to plot.")
        return
    
    plot_title = f"{crime} Trend in {district}, {state}"
    if district == 'all':
        plot_title = f"Total {crime} Trend in {state}"
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=yearly, x="Year", y=crime, marker="o", ax=ax, linewidth=3, markersize=8)
    ax.set_title(plot_title, fontsize=16, fontweight='bold')
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Number of Cases", fontsize=12)
    ax.set_xticks(yearly['Year'].astype(int))
    plt.tight_layout()
    st.pyplot(fig)

def compare_multiple_crimes_streamlit(df, crimes, state, district):
    """Compare multiple crimes in Streamlit"""
    if df.empty:
        st.warning("No data available for the selected location.")
        return
    
    existing = [c for c in crimes if c in df.columns]
    if not existing:
        st.warning("None of the requested crime columns exist in this data selection.")
        return
    
    yearly = df.groupby("Year")[existing].sum().reset_index()
    if yearly.empty:
        st.warning("No yearly data to plot.")
        return
    
    plot_title = f"Crime Comparison in {district}, {state}"
    if district == 'all':
        plot_title = f"Total Crime Comparison in {state}"
    
    fig, ax = plt.subplots(figsize=(14, 8))
    for c in existing:
        sns.lineplot(data=yearly, x="Year", y=c, marker="o", label=c, linewidth=3, markersize=6)
    
    ax.set_title(plot_title, fontsize=16, fontweight='bold')
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Cases", fontsize=12)
    ax.legend(title="Crime Type", bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.set_xticks(yearly['Year'].astype(int))
    plt.tight_layout()
    st.pyplot(fig)

def compare_districts_streamlit(dataset, state, districts, crime):
    """Compare districts in Streamlit"""
    existing_districts = []
    for d in districts:
        mask = (dataset['State Name'] == state) & (dataset['District Name'] == d)
        if mask.any():
            existing_districts.append(d)
    
    if not existing_districts:
        st.warning("No valid districts found to compare.")
        return
    
    if crime not in dataset.columns:
        st.warning(f"Crime '{crime}' not in dataset columns.")
        return
    
    fig, ax = plt.subplots(figsize=(14, 8))
    for d in existing_districts:
        df = dataset[(dataset['State Name'] == state) & (dataset['District Name'] == d)]
        yearly = df.groupby("Year")[crime].sum().reset_index()
        if not yearly.empty:
            sns.lineplot(data=yearly, x="Year", y=crime, marker="o", label=d.title(), linewidth=3, markersize=6)
    
    ax.set_title(f"{crime} Comparison across Districts in {state.title()}", fontsize=16, fontweight='bold')
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Cases", fontsize=12)
    ax.legend(title="District", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    st.pyplot(fig)

def plot_all_districts_bar_streamlit(data, state, crime):
    """Create bar plot for all districts in Streamlit"""
    if data.empty or crime not in data.columns:
        st.warning(f"No data available for {crime}")
        return
    
    district_totals = data.groupby("District Name")[crime].sum().reset_index()
    district_totals = district_totals[district_totals[crime] > 0]
    district_totals = district_totals.sort_values(by=crime, ascending=False)
    
    if district_totals.empty:
        st.warning(f"No reported cases of '{crime}' found in {state} to plot.")
        return
    
    num_districts = len(district_totals)
    fig_height = max(8, num_districts * 0.4)
    fig, ax = plt.subplots(figsize=(12, fig_height))
    
    sns.barplot(data=district_totals, y="District Name", x=crime, palette="viridis", ax=ax)
    ax.set_title(f"Total '{crime}' Cases by District in {state.title()}", fontsize=16, fontweight='bold')
    ax.set_xlabel("Total Number of Cases", fontsize=12)
    ax.set_ylabel("District", fontsize=12)
    plt.tight_layout()
    st.pyplot(fig)

def show_descriptive_stats_streamlit(df, crime_cols):
    """Show descriptive statistics in Streamlit"""
    existing = [c for c in crime_cols if c in df.columns]
    if not existing:
        st.warning("None of the requested crime columns exist in this data selection.")
        return
    
    st.subheader("Descriptive Statistics")
    stats = df[existing].describe().T
    stats['median'] = df[existing].median()
    
    # Reorder columns for better readability
    to_show = ['count', 'mean', 'median', 'std', 'min', '25%', '50%', '75%', 'max']
    available_cols = [col for col in to_show if col in stats.columns]
    
    st.dataframe(stats[available_cols].round(3), use_container_width=True)

def compare_dataset_types_streamlit(datasets, state_name, district_name, location_desc):
    """Compare different dataset types in Streamlit"""
    st.subheader(f"Cross-Dataset Comparison for {location_desc}")
    
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
            crime_columns = get_crime_columns(dataset_df)
            
            if crime_columns:
                total_crimes = filtered_data[crime_columns].sum().sum()
                dataset_totals[dataset_name] = total_crimes
                
                yearly_totals = filtered_data.groupby('Year')[crime_columns].sum().sum(axis=1).reset_index()
                yearly_totals.columns = ['Year', dataset_name]
                dataset_yearly[dataset_name] = yearly_totals
    
    if not dataset_totals:
        st.warning(f"No data found for {location_desc} across any datasets.")
        return
    
    # Display summary table
    st.write("**Total Crime Counts by Dataset Type:**")
    sorted_totals = sorted(dataset_totals.items(), key=lambda x: x[1], reverse=True)
    
    summary_data = []
    for dataset_name, total in sorted_totals:
        summary_data.append({
            'Dataset': dataset_name.replace('_', ' ').title(),
            'Total Crimes': f"{total:,}"
        })
    
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
    
    # Create comparison plots
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart of total crimes by dataset
        dataset_names = [name.replace('_', ' ').title() for name, _ in sorted_totals]
        totals = [total for _, total in sorted_totals]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=dataset_names, y=totals, palette="Set2", ax=ax)
        ax.set_title(f"Total Crime Comparison by Dataset Type", fontsize=14, fontweight='bold')
        ax.set_xlabel("Dataset Type")
        ax.set_ylabel("Total Crime Count")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        # Line plot of trends over time
        if len(dataset_yearly) > 1:
            merged_yearly = None
            for dataset_name, yearly_data in dataset_yearly.items():
                if merged_yearly is None:
                    merged_yearly = yearly_data
                else:
                    merged_yearly = merged_yearly.merge(yearly_data, on='Year', how='outer')
            
            if merged_yearly is not None:
                merged_yearly = merged_yearly.fillna(0)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                for dataset_name in dataset_yearly.keys():
                    if dataset_name in merged_yearly.columns:
                        sns.lineplot(data=merged_yearly, x='Year', y=dataset_name, 
                                   marker='o', label=dataset_name.replace('_', ' ').title(), ax=ax)
                
                ax.set_title(f"Crime Trends Comparison by Dataset Type", fontsize=14, fontweight='bold')
                ax.set_xlabel("Year")
                ax.set_ylabel("Total Crime Count")
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                ax.set_xticks(merged_yearly['Year'].astype(int))
                plt.tight_layout()
                st.pyplot(fig)

def enhanced_crime_choice_streamlit(df, context="crime type"):
    """Enhanced crime selection with categorization for single selection"""
    crime_cols = get_crime_columns(df)
    
    if len(crime_cols) > 20:
        st.write(f"**This dataset has {len(crime_cols)} crime types. Choose selection method:**")
        method = st.radio(
            "Selection Method:",
            ["Browse by Category", "Search", "Show All"],
            key=f"method_{context}"
        )
        
        if method == "Browse by Category":
            categories = categorize_crimes(crime_cols)
            
            selected_category = st.selectbox(
                "Choose Category:",
                list(categories.keys()),
                key=f"category_{context}"
            )
            
            crimes_in_category = categories[selected_category]
            selected_crime = st.selectbox(
                f"Choose {context} from {selected_category}:",
                crimes_in_category,
                key=f"crime_from_cat_{context}"
            )
            return selected_crime
            
        elif method == "Search":
            search_term = st.text_input(f"Search for {context}:", key=f"search_{context}")
            
            if search_term:
                matching_crimes = [c for c in crime_cols if search_term.lower() in c.lower()]
                
                if matching_crimes:
                    selected_crime = st.selectbox(
                        f"Choose {context} from search results:",
                        matching_crimes,
                        key=f"crime_from_search_{context}"
                    )
                    return selected_crime
                else:
                    st.warning(f"No crimes found matching '{search_term}'")
                    return None
            return None
        else:
            selected_crime = st.selectbox(f"Choose {context}:", crime_cols, key=f"crime_full_{context}")
            return selected_crime
    else:
        selected_crime = st.selectbox(f"Choose {context}:", crime_cols, key=f"crime_simple_{context}")
        return selected_crime

def enhanced_crime_selection_streamlit(available_crimes, max_select=5, context="crimes"):
    """Enhanced crime selection for Streamlit with categorization"""
    if not available_crimes:
        return []
    
    st.subheader(f"Select {context.title()} ({len(available_crimes)} available)")
    
    # Show different options based on list size
    if len(available_crimes) > 20:
        selection_method = st.radio(
            "Selection Method:",
            ["Browse by Category", "Search & Select", "Show All", "Select Popular Crimes"]
        )
        
        if selection_method == "Browse by Category":
            return select_by_category_streamlit(available_crimes, max_select)
        elif selection_method == "Search & Select":
            return select_by_search_streamlit(available_crimes, max_select)
        elif selection_method == "Select Popular Crimes":
            return select_popular_crimes_streamlit(available_crimes, max_select)
        else:
            return select_from_full_list_streamlit(available_crimes, max_select)
    else:
        return select_from_full_list_streamlit(available_crimes, max_select)

def select_by_category_streamlit(available_crimes, max_select):
    """Select crimes by category in Streamlit"""
    categories = categorize_crimes(available_crimes)
    
    st.write("**Crime Categories:**")
    selected_crimes = []
    
    for category, crimes in categories.items():
        with st.expander(f"{category} ({len(crimes)} crimes)"):
            if st.checkbox(f"Select all {category}", key=f"all_{category}"):
                selected_crimes.extend(crimes[:max_select - len(selected_crimes)])
            else:
                for crime in crimes:
                    if len(selected_crimes) < max_select:
                        if st.checkbox(crime, key=f"crime_{crime}"):
                            if crime not in selected_crimes:
                                selected_crimes.append(crime)
    
    return selected_crimes[:max_select]

def select_by_search_streamlit(available_crimes, max_select):
    """Select crimes by search in Streamlit"""
    search_term = st.text_input("Search for crimes:", key="crime_search")
    
    if search_term:
        matching_crimes = [c for c in available_crimes if search_term.lower() in c.lower()]
        
        if matching_crimes:
            st.write(f"**Found {len(matching_crimes)} matching crimes:**")
            selected_crimes = st.multiselect(
                "Select from search results:",
                matching_crimes,
                key="search_results",
                max_selections=max_select
            )
            return selected_crimes
        else:
            st.warning(f"No crimes found matching '{search_term}'")
            return []
    else:
        st.info("Enter a search term to find crimes")
        return []

def select_popular_crimes_streamlit(available_crimes, max_select):
    """Select from popular crimes in Streamlit"""
    popular_keywords = [
        'murder', 'rape', 'theft', 'burglary', 'robbery', 'kidnapping',
        'cyber', 'fraud', 'dowry', 'acid attack', 'assault', 'domestic violence',
        'drug', 'trafficking', 'extortion', 'cheating'
    ]
    
    popular_crimes = []
    crime_lower = [c.lower() for c in available_crimes]
    
    for keyword in popular_keywords:
        matches = [available_crimes[i] for i, c in enumerate(crime_lower) 
                  if keyword in c and available_crimes[i] not in popular_crimes]
        popular_crimes.extend(matches[:2])  # Max 2 per keyword
        if len(popular_crimes) >= 15:
            break
    
    if popular_crimes:
        st.write("**Popular Crime Types:**")
        selected_crimes = st.multiselect(
            "Select from popular crimes:",
            popular_crimes,
            key="popular_crimes",
            max_selections=max_select
        )
        return selected_crimes
    
    return []

def select_from_full_list_streamlit(available_crimes, max_select):
    """Select from full list in Streamlit"""
    st.write(f"**All Available Crimes ({len(available_crimes)} total):**")
    
    # Add "Select All" option
    if st.checkbox("Select All Crimes", key="select_all_crimes"):
        if len(available_crimes) <= max_select:
            return available_crimes.copy()
        else:
            st.warning(f"Too many crimes to select all. Showing first {max_select}.")
            return available_crimes[:max_select]
    
    selected_crimes = st.multiselect(
        "Choose crimes:",
        available_crimes,
        key="full_list_crimes",
        max_selections=max_select
    )
    
    return selected_crimes

def plot_pie_chart_streamlit(data, state_name, district_name="all", top_n=10):
    """Pie/Donut Charts for Streamlit"""
    if data.empty:
        st.warning("No data available for pie chart.")
        return
    
    crime_columns = get_crime_columns(data)
    if not crime_columns:
        st.warning("No crime data found for pie chart.")
        return
    
    crime_totals = data[crime_columns].sum().sort_values(ascending=False)
    
    if len(crime_totals) > top_n:
        top_crimes = crime_totals.head(top_n)
        other_total = crime_totals.iloc[top_n:].sum()
        if other_total > 0:
            top_crimes['Others'] = other_total
    else:
        top_crimes = crime_totals
    
    top_crimes = top_crimes[top_crimes > 0]
    
    if top_crimes.empty:
        st.warning("No crimes with non-zero values found.")
        return
    
    location_desc = f"{district_name}, {state_name}" if district_name != "all" else f"All Districts in {state_name}"
    
    fig = px.pie(
        values=top_crimes.values,
        names=top_crimes.index,
        title=f'Crime Distribution in {location_desc}<br>Top {min(top_n, len(crime_totals))} Crime Types',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=True, height=600, font=dict(size=12))
    
    st.plotly_chart(fig, use_container_width=True)

def plot_crime_heatmap_streamlit(data, state_name, district_name="all"):
    """Crime correlation heatmap for Streamlit"""
    if data.empty:
        st.warning("No data available for heatmap.")
        return
    
    crime_columns = get_crime_columns(data)
    
    if len(crime_columns) < 2:
        st.warning("Need at least 2 crime types for correlation heatmap.")
        return
    
    crime_data = data[crime_columns]
    location_desc = f"{district_name}, {state_name}" if district_name != "all" else f"All Districts in {state_name}"
    
    corr_matrix = crime_data.corr()
    
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        title=f'Crime Correlation Heatmap - {location_desc}',
        color_continuous_scale='RdYlBu_r',
        zmin=-1, zmax=1
    )
    
    fig.update_layout(height=600, font=dict(size=10))
    st.plotly_chart(fig, use_container_width=True)

def plot_stacked_bar_streamlit(data, state_name, district_name="all", top_crimes=8):
    """Stacked bar chart for Streamlit"""
    if data.empty or 'Year' not in data.columns:
        st.warning("No data or Year column available for stacked bar chart.")
        return
    
    crime_columns = get_crime_columns(data)
    crime_totals = data[crime_columns].sum().sort_values(ascending=False)
    top_crime_cols = crime_totals.head(top_crimes).index.tolist()
    
    yearly_data = data.groupby('Year')[top_crime_cols].sum().reset_index()
    location_desc = f"{district_name}, {state_name}" if district_name != "all" else f"All Districts in {state_name}"
    
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
        title=f'Stacked Crime Trends by Year - {location_desc}<br>Top {top_crimes} Crime Types',
        xaxis_title='Year',
        yaxis_title='Number of Cases',
        height=600,
        showlegend=True,
        font=dict(size=12)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def compare_states_streamlit(datasets, selected_dataset_name, selected_crime_type, selected_states):
    """Compare states in Streamlit"""
    selected_dataset = datasets[selected_dataset_name]
    
    if selected_crime_type not in selected_dataset.columns:
        st.warning(f"Crime type '{selected_crime_type}' not found in {selected_dataset_name} dataset.")
        return
    
    # Create comparison data
    state_comparison = []
    state_yearly = {}
    
    for state in selected_states:
        state_data = selected_dataset[selected_dataset['State Name'] == state]
        if not state_data.empty:
            total_crimes = state_data[selected_crime_type].sum()
            state_comparison.append({'State': state.title(), 'Total_Crimes': total_crimes})
            
            yearly = state_data.groupby('Year')[selected_crime_type].sum().reset_index()
            state_yearly[state] = yearly
    
    if not state_comparison:
        st.warning("No data found for selected states.")
        return
    
    # Convert to DataFrame and sort
    comparison_df = pd.DataFrame(state_comparison)
    comparison_df = comparison_df.sort_values('Total_Crimes', ascending=False)
    
    # Display results
    st.subheader(f"{selected_crime_type} Comparison Across States")
    
    # Show summary table
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # Create visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart comparison
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=comparison_df, x='State', y='Total_Crimes', palette='viridis', ax=ax)
        ax.set_title(f'{selected_crime_type} - Total Cases by State', fontsize=14, fontweight='bold')
        ax.set_xlabel('State')
        ax.set_ylabel(f'Total {selected_crime_type} Cases')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        # Trend lines for each state
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for state, yearly_data in state_yearly.items():
            if not yearly_data.empty:
                sns.lineplot(data=yearly_data, x='Year', y=selected_crime_type, 
                            marker='o', label=state.title(), ax=ax)
        
        ax.set_title(f'{selected_crime_type} - Trends Across States', fontsize=14, fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel(f'{selected_crime_type} Cases')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        st.pyplot(fig)

def main():
    st.title("🚀 Crime Analyser")
    st.markdown("**Comprehensive District-wise Crime Data Analysis Platform for India (2017-2022)**")
    
    # Load datasets
    with st.spinner("Loading datasets..."):
        datasets = load_datasets()
    
    if not datasets:
        st.error("No datasets loaded. Check your Dataset folder.")
        st.info("Make sure you have the Dataset folder with CSV files in the same directory as this script.")
        return
    

    
    # Analysis type selection
    st.header("🎯 Analysis Configuration")
    
    analysis_options = {
        "Single Crime Trend": "Plot trend for one crime in selected location",
        "Multiple Crimes Comparison": "Compare different crimes in same location", 
        "Multi-District Comparison": "Compare same crime across different districts",
        "Descriptive Statistics": "Statistical summary of crime data",
        "District Bar Chart": "Visual comparison of all districts in state",
        "Crime Hotspots": "Identify top districts by crime count",
        "Cross-Dataset Comparison": "Compare IPC vs Cyber vs Women crimes",
        "Cross-State Analysis": "Same crime type across multiple states",
        "Enhanced Visualizations": "Interactive pie charts, heatmaps, and advanced plots"
    }
    
    # Use analysis type from home page if available, otherwise use main selection
    if 'analysis_type' in st.session_state and st.session_state.analysis_type:
        # Map the analysis type from home page to match the options
        analysis_mapping = {
            "Single Crime Trend": "Single Crime Trend",
            "Multiple Crimes Comparison": "Multiple Crimes Comparison", 
            "Multi-District Comparison": "Multi-District Comparison",
            "Descriptive Statistics": "Descriptive Statistics",
            "District Bar Chart": "District Bar Chart",
            "Crime Hotspots": "Crime Hotspots",
            "Cross-Dataset Comparison": "Cross-Dataset Comparison",
            "Cross-State Analysis": "Cross-State Analysis",
            "Enhanced Visualizations": "Enhanced Visualizations"
        }
        
        selected_analysis = analysis_mapping.get(st.session_state.analysis_type, "Single Crime Trend")
        
        # Show the selected analysis in main area
        st.write(f"**Selected Analysis:** {selected_analysis}")
        st.write("*Selected from home page*")
        
        # Option to change analysis type
        if st.button("Change Analysis Type"):
            del st.session_state.analysis_type
            st.rerun()
    else:
        selected_analysis = st.selectbox(
            "Choose Analysis Type:",
            list(analysis_options.keys()),
            help="Select the type of analysis you want to perform"
        )
    
    st.write(f"**Description:** {analysis_options[selected_analysis]}")
    
    # Main analysis based on selection
    if selected_analysis == "Single Crime Trend":
        st.header("📈 Single Crime Trend Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dataset_choice = st.selectbox("Choose Dataset:", list(datasets.keys()))
            df = datasets[dataset_choice]
            
            states = sorted(df['State Name'].unique())
            selected_state = st.selectbox("Choose State:", states)
            
        with col2:
            districts = df[df['State Name'] == selected_state]['District Name'].unique()
            district_options = ['all'] + sorted(districts.tolist())
            selected_district = st.selectbox("Choose District:", district_options, 
                                           format_func=lambda x: "All Districts" if x == 'all' else x.title())
            
            crime_cols = get_crime_columns(df)
            selected_crime = st.selectbox("Choose Crime Type:", crime_cols)
        
        if st.button("Generate Trend Analysis", type="primary"):
            if selected_district == 'all':
                filtered_data = df[df['State Name'] == selected_state]
            else:
                filtered_data = df[(df['State Name'] == selected_state) & (df['District Name'] == selected_district)]
            
            plot_trends_streamlit(filtered_data, selected_state, selected_district, selected_crime)
    
    elif selected_analysis == "Multiple Crimes Comparison":
        st.header("🔄 Multiple Crimes Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dataset_choice = st.selectbox("Choose Dataset:", list(datasets.keys()))
            df = datasets[dataset_choice]
            
            states = sorted(df['State Name'].unique())
            selected_state = st.selectbox("Choose State:", states)
            
        with col2:
            districts = df[df['State Name'] == selected_state]['District Name'].unique()
            district_options = ['all'] + sorted(districts.tolist())
            selected_district = st.selectbox("Choose District:", district_options,
                                           format_func=lambda x: "All Districts" if x == 'all' else x.title())
        
        crime_cols = get_crime_columns(df)
        selected_crimes = enhanced_crime_selection_streamlit(crime_cols, max_select=7, context="crimes for comparison")
        
        if st.button("Generate Comparison", type="primary") and selected_crimes:
            if selected_district == 'all':
                filtered_data = df[df['State Name'] == selected_state]
            else:
                filtered_data = df[(df['State Name'] == selected_state) & (df['District Name'] == selected_district)]
            
            compare_multiple_crimes_streamlit(filtered_data, selected_crimes, selected_state, selected_district)
    
    elif selected_analysis == "Multi-District Comparison":
        st.header("🏙️ Multi-District Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dataset_choice = st.selectbox("Choose Dataset:", list(datasets.keys()))
            df = datasets[dataset_choice]
            
            states = sorted(df['State Name'].unique())
            selected_state = st.selectbox("Choose State:", states)
            
        with col2:
            crime_cols = get_crime_columns(df)
            selected_crime = st.selectbox("Choose Crime Type:", crime_cols)
        
        districts = df[df['State Name'] == selected_state]['District Name'].unique()
        selected_districts = st.multiselect("Choose Districts to Compare:", sorted(districts.tolist()), 
                                          default=sorted(districts.tolist())[:5])
        
        if st.button("Generate District Comparison", type="primary") and selected_districts:
            compare_districts_streamlit(df, selected_state, selected_districts, selected_crime)
    
    elif selected_analysis == "Descriptive Statistics":
        st.header("📊 Descriptive Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dataset_choice = st.selectbox("Choose Dataset:", list(datasets.keys()))
            df = datasets[dataset_choice]
            
            states = sorted(df['State Name'].unique())
            selected_state = st.selectbox("Choose State:", states)
            
        with col2:
            districts = df[df['State Name'] == selected_state]['District Name'].unique()
            district_options = ['all'] + sorted(districts.tolist())
            selected_district = st.selectbox("Choose District:", district_options,
                                           format_func=lambda x: "All Districts" if x == 'all' else x.title())
        
        crime_cols = get_crime_columns(df)
        selected_crimes = enhanced_crime_selection_streamlit(crime_cols, max_select=10, context="crimes for statistics")
        
        if st.button("Generate Statistics", type="primary") and selected_crimes:
            if selected_district == 'all':
                filtered_data = df[df['State Name'] == selected_state]
            else:
                filtered_data = df[(df['State Name'] == selected_state) & (df['District Name'] == selected_district)]
            
            show_descriptive_stats_streamlit(filtered_data, selected_crimes)
    
    elif selected_analysis == "District Bar Chart":
        st.header("🏛️ District Bar Chart Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dataset_choice = st.selectbox("Choose Dataset:", list(datasets.keys()))
            df = datasets[dataset_choice]
            
            states = sorted(df['State Name'].unique())
            selected_state = st.selectbox("Choose State:", states)
            
        with col2:
            crime_cols = get_crime_columns(df)
            selected_crime = st.selectbox("Choose Crime Type:", crime_cols)
        
        if st.button("Generate Bar Chart", type="primary"):
            state_data = df[df['State Name'] == selected_state]
            plot_all_districts_bar_streamlit(state_data, selected_state, selected_crime)
    
    elif selected_analysis == "Crime Hotspots":
        st.header("🔥 Crime Hotspots Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dataset_choice = st.selectbox("Choose Dataset:", list(datasets.keys()))
            df = datasets[dataset_choice]
            
            scope = st.radio("Analysis Scope:", ["District hotspots within a state", "State hotspots across country"])
            
        with col2:
            crime_cols = get_crime_columns(df)
            selected_crime = st.selectbox("Choose Crime Type:", crime_cols)
            
            n_hotspots = st.number_input("Number of top hotspots to show:", min_value=1, max_value=20, value=10)
        
        if scope == "District hotspots within a state":
            states = sorted(df['State Name'].unique())
            selected_state = st.selectbox("Choose State for District Analysis:", states)
            
            if st.button("Find District Hotspots", type="primary"):
                state_data = df[df['State Name'] == selected_state]
                
                district_totals = state_data.groupby("District Name")[selected_crime].sum().reset_index()
                district_totals = district_totals[district_totals[selected_crime] > 0]
                district_totals = district_totals.sort_values(by=selected_crime, ascending=False).head(n_hotspots)
                
                if not district_totals.empty:
                    st.subheader(f"Top {n_hotspots} District Hotspots for {selected_crime} in {selected_state.title()}")
                    
                    # Show table
                    display_df = district_totals.copy()
                    display_df['District Name'] = display_df['District Name'].str.title()
                    display_df.columns = ['District', 'Total Cases']
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                    
                    # Show chart
                    fig, ax = plt.subplots(figsize=(12, 8))
                    sns.barplot(data=district_totals, y="District Name", x=selected_crime, palette="Reds_r", ax=ax)
                    ax.set_title(f"Top {n_hotspots} District Hotspots - {selected_crime}", fontsize=16, fontweight='bold')
                    ax.set_xlabel("Total Cases")
                    ax.set_ylabel("District")
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.warning(f"No data found for {selected_crime} in {selected_state}")
        
        else:  # State hotspots
            if st.button("Find State Hotspots", type="primary"):
                state_totals = df.groupby('State Name')[selected_crime].sum().sort_values(ascending=False).head(n_hotspots)
                
                if not state_totals.empty:
                    st.subheader(f"Top {n_hotspots} State Hotspots for {selected_crime}")
                    
                    # Show table
                    hotspot_data = []
                    for i, (state, total) in enumerate(state_totals.items(), 1):
                        hotspot_data.append({'Rank': i, 'State': state.title(), 'Total Cases': f"{total:,}"})
                    
                    st.dataframe(pd.DataFrame(hotspot_data), use_container_width=True, hide_index=True)
                    
                    # Show chart
                    fig, ax = plt.subplots(figsize=(12, 8))
                    sns.barplot(x=state_totals.values, y=state_totals.index, palette="Reds_r", ax=ax)
                    ax.set_title(f"Top {n_hotspots} State Hotspots - {selected_crime}", fontsize=16, fontweight='bold')
                    ax.set_xlabel("Total Cases")
                    ax.set_ylabel("State")
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.warning(f"No data found for {selected_crime}")
    
    elif selected_analysis == "Cross-Dataset Comparison":
        st.header("📊 Cross-Dataset Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Use any dataset to get states (they should be consistent)
            sample_dataset = list(datasets.values())[0]
            states = sorted(sample_dataset['State Name'].unique())
            selected_state = st.selectbox("Choose State:", states)
            
        with col2:
            districts = sample_dataset[sample_dataset['State Name'] == selected_state]['District Name'].unique()
            district_options = ['all'] + sorted(districts.tolist())
            selected_district = st.selectbox("Choose District:", district_options,
                                           format_func=lambda x: "All Districts" if x == 'all' else x.title())
        
        location_desc = f"{selected_district.title()}, {selected_state.title()}" if selected_district != 'all' else f"All Districts in {selected_state.title()}"
        
        st.write(f"**Comparing all available datasets for:** {location_desc}")
        
        available_datasets = list(datasets.keys())
        st.write(f"**Available datasets:** {', '.join([name.replace('_', ' ').title() for name in available_datasets])}")
        
        if st.button("Generate Cross-Dataset Comparison", type="primary"):
            compare_dataset_types_streamlit(datasets, selected_state, selected_district, location_desc)
    
    elif selected_analysis == "Enhanced Visualizations":
        st.header("🎨 Enhanced Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dataset_choice = st.selectbox("Choose Dataset:", list(datasets.keys()))
            df = datasets[dataset_choice]
            
            states = sorted(df['State Name'].unique())
            selected_state = st.selectbox("Choose State:", states)
            
        with col2:
            districts = df[df['State Name'] == selected_state]['District Name'].unique()
            district_options = ['all'] + sorted(districts.tolist())
            selected_district = st.selectbox("Choose District:", district_options,
                                           format_func=lambda x: "All Districts" if x == 'all' else x.title())
        
        # Filter data
        if selected_district == 'all':
            filtered_data = df[df['State Name'] == selected_state]
            location_desc = f"All Districts in {selected_state}"
        else:
            filtered_data = df[(df['State Name'] == selected_state) & (df['District Name'] == selected_district)]
            location_desc = f"{selected_district}, {selected_state}"
        
        st.subheader(f"Visualization Options for {location_desc}")
        
        viz_type = st.selectbox(
            "Choose Visualization Type:",
            ["Pie/Donut Chart", "Correlation Heatmap", "Stacked Bar Chart", "Interactive Line Chart", "All Visualizations"]
        )
        
        if st.button("Generate Visualization", type="primary"):
            if filtered_data.empty:
                st.warning("No data found for the selected filters.")
            else:
                if viz_type == "Pie/Donut Chart":
                    plot_pie_chart_streamlit(filtered_data, selected_state, selected_district)
                elif viz_type == "Correlation Heatmap":
                    plot_crime_heatmap_streamlit(filtered_data, selected_state, selected_district)
                elif viz_type == "Stacked Bar Chart":
                    plot_stacked_bar_streamlit(filtered_data, selected_state, selected_district)
                elif viz_type == "Interactive Line Chart":
                    crime_cols = get_crime_columns(filtered_data)
                    if len(crime_cols) > 0 and 'Year' in filtered_data.columns:
                        # Use top 5 crimes for interactive chart
                        crime_totals = filtered_data[crime_cols].sum().sort_values(ascending=False)
                        top_crimes = crime_totals.head(5).index.tolist()
                        
                        yearly_data = filtered_data.groupby('Year')[top_crimes].sum().reset_index()
                        
                        fig = px.line(
                            yearly_data.melt(id_vars=['Year'], var_name='Crime Type', value_name='Cases'),
                            x='Year',
                            y='Cases',
                            color='Crime Type',
                            title=f'Interactive Crime Trends - {location_desc}',
                            markers=True,
                            line_shape='spline'
                        )
                        
                        fig.update_layout(height=600, hovermode='x unified')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No suitable data for line chart.")
                elif viz_type == "All Visualizations":
                    st.subheader("Generating All Visualizations...")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Pie Chart:**")
                        plot_pie_chart_streamlit(filtered_data, selected_state, selected_district)
                        
                        st.write("**Stacked Bar Chart:**")
                        plot_stacked_bar_streamlit(filtered_data, selected_state, selected_district)
                    
                    with col2:
                        st.write("**Correlation Heatmap:**")
                        plot_crime_heatmap_streamlit(filtered_data, selected_state, selected_district)
                        
                        # Interactive line chart
                        crime_cols = get_crime_columns(filtered_data)
                        if len(crime_cols) > 0 and 'Year' in filtered_data.columns:
                            crime_totals = filtered_data[crime_cols].sum().sort_values(ascending=False)
                            top_crimes = crime_totals.head(3).index.tolist()
                            
                            yearly_data = filtered_data.groupby('Year')[top_crimes].sum().reset_index()
                            
                            fig = px.line(
                                yearly_data.melt(id_vars=['Year'], var_name='Crime Type', value_name='Cases'),
                                x='Year',
                                y='Cases',
                                color='Crime Type',
                                title=f'Top 3 Crime Trends - {location_desc}',
                                markers=True
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
    
    elif selected_analysis == "Cross-State Analysis":
        st.header("🌍 Cross-State Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dataset_choice = st.selectbox("Choose Dataset:", list(datasets.keys()))
            df = datasets[dataset_choice]
            
            crime_cols = get_crime_columns(df)
            selected_crime = st.selectbox("Choose Crime Type:", crime_cols)
            
        with col2:
            states = sorted(df['State Name'].unique())
            
            # Option to select all states or specific ones
            use_all_states = st.checkbox("Use all states (top 10 will be shown)", value=True)
            
            if use_all_states:
                # Get top 10 states by total crime
                state_totals = df.groupby('State Name')[selected_crime].sum().sort_values(ascending=False)
                selected_states = state_totals.head(10).index.tolist()
                st.write(f"**Selected:** Top 10 states by {selected_crime} cases")
            else:
                selected_states = st.multiselect("Choose States to Compare:", states, default=states[:5])
        
        if st.button("Generate Cross-State Analysis", type="primary") and selected_states:
            compare_states_streamlit(datasets, dataset_choice, selected_crime, selected_states)
    
    # Footer
    st.markdown("---")
    st.markdown("**Crime Analyser** - Crime Data Analysis Platform for India | Data: 2017-2022")
    st.markdown("*Enhanced with Smart Crime Selection and Categorization*")
    
    # Additional Analysis Tools
    st.markdown("---")
    st.subheader("🔧 Additional Tools")
    
    if st.button("📊 Analyze All Crime Types"):
        total_crimes = 0
        unique_crimes = set()
        
        for dataset_name, dataset_df in datasets.items():
            crime_cols = get_crime_columns(dataset_df)
            total_crimes += len(crime_cols)
            unique_crimes.update(crime_cols)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Crime Types", total_crimes)
        with col2:
            st.metric("Unique Crime Types", len(unique_crimes))
        with col3:
            st.metric("Total Datasets", len(datasets))

if __name__ == "__main__":
    main()