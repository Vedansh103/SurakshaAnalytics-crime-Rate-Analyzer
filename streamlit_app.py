import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from Data import (
    load_datasets, plot_trends, compare_multiple_crimes, compare_districts,
    show_descriptive_stats, plot_all_districts_bar, show_crime_hotspots,
    compare_dataset_types, compare_states_datasets, verify_setup
)

# Configure Streamlit page
st.set_page_config(
    page_title="Suraksha Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'datasets' not in st.session_state:
        st.session_state.datasets = None
    if 'selected_dataset' not in st.session_state:
        st.session_state.selected_dataset = None
    if 'selected_state' not in st.session_state:
        st.session_state.selected_state = None
    if 'selected_district' not in st.session_state:
        st.session_state.selected_district = None
    if 'selected_crime' not in st.session_state:
        st.session_state.selected_crime = None

def load_data():
    """Load datasets with caching"""
    if st.session_state.datasets is None:
        with st.spinner("Loading datasets..."):
            st.session_state.datasets = load_datasets()
    return st.session_state.datasets

def get_crime_columns(df):
    """Get crime columns from dataset"""
    return [col for col in df.columns if col not in 
            ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]

def main():
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">Suraksha Analytics</h1>', unsafe_allow_html=True)
    st.markdown("**Comprehensive District-wise Crime Data Analysis Platform for India (2017-2022)**")
    
    # Load datasets
    datasets = load_data()
    
    if not datasets:
        st.error("Failed to load datasets. Please check your Dataset folder and CSV files.")
        st.info("Make sure you have all required CSV files in the Dataset folder.")
        return
    
    st.success(f"Successfully loaded {len(datasets)} datasets!")
    
    # Sidebar for selections
    st.sidebar.markdown("## Analysis Configuration")
    
    # Step 1: Dataset Selection
    st.sidebar.markdown('<div class="step-header">1. Choose Dataset</div>', unsafe_allow_html=True)
    dataset_names = list(datasets.keys())
    dataset_display_names = [name.replace('_', ' ').title() for name in dataset_names]
    
    selected_dataset_idx = st.sidebar.selectbox(
        "Select Dataset:",
        range(len(dataset_names)),
        format_func=lambda x: dataset_display_names[x],
        key="dataset_select"
    )
    
    selected_dataset_name = dataset_names[selected_dataset_idx]
    chosen_dataset_df = datasets[selected_dataset_name]
    
    # Step 2: State Selection
    st.sidebar.markdown('<div class="step-header">2. Choose State</div>', unsafe_allow_html=True)
    available_states = sorted(chosen_dataset_df['State Name'].unique())
    
    selected_state = st.sidebar.selectbox(
        "Select State:",
        available_states,
        key="state_select"
    )
    
    # Step 3: District Selection
    st.sidebar.markdown('<div class="step-header">3. Choose District</div>', unsafe_allow_html=True)
    state_districts = chosen_dataset_df[chosen_dataset_df['State Name'] == selected_state]['District Name'].unique()
    district_options = ['all'] + sorted(state_districts.tolist())
    
    selected_district = st.sidebar.selectbox(
        "Select District:",
        district_options,
        format_func=lambda x: "All Districts" if x == 'all' else x.title(),
        key="district_select"
    )
    
    # Step 4: Crime Type Selection
    st.sidebar.markdown('<div class="step-header">4. Choose Crime Type</div>', unsafe_allow_html=True)
    crime_columns = get_crime_columns(chosen_dataset_df)
    
    selected_crime = st.sidebar.selectbox(
        "Select Crime Type:",
        crime_columns,
        key="crime_select"
    )
    
    # Filter data based on selections
    if selected_district == 'all':
        selected_data = chosen_dataset_df[chosen_dataset_df['State Name'] == selected_state]
        location_desc = f"ALL Districts in {selected_state}"
    else:
        selected_data = chosen_dataset_df[
            (chosen_dataset_df['State Name'] == selected_state) &
            (chosen_dataset_df['District Name'] == selected_district)
        ]
        location_desc = f"{selected_district}, {selected_state}"
    
    # Main content area
    st.markdown("---")
    st.markdown(f"### Analysis for: {location_desc}")
    st.markdown(f"**Dataset:** {selected_dataset_name.replace('_', ' ').title()}")
    st.markdown(f"**Crime Type:** {selected_crime}")
    
    if selected_data.empty:
        st.warning(f"No data found for {location_desc} in {selected_dataset_name} dataset.")
        return
    
    # Display data preview
    with st.expander("Data Preview", expanded=False):
        display_cols = ['State Name', 'District Name', 'Year', selected_crime]
        st.dataframe(selected_data[display_cols].head(10))
    
    # Analysis Options
    st.markdown("---")
    st.markdown("### Analysis Options")
    
    # Create tabs for different analysis types
    tab1, tab2, tab3, tab4 = st.tabs([
        "Basic Analysis", 
        "Comparative Analysis", 
        "Advanced Analysis", 
        "Cross Analysis"
    ])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Plot Crime Trend", use_container_width=True):
                st.markdown("#### Crime Trend Analysis")
                fig = plot_trends_streamlit(selected_data, selected_state, selected_district, selected_crime)
                if fig:
                    st.pyplot(fig)
        
        with col2:
            if st.button("Show Statistics", use_container_width=True):
                st.markdown("#### Descriptive Statistics")
                stats_df = show_descriptive_stats_streamlit(selected_data, [selected_crime])
                if stats_df is not None:
                    st.dataframe(stats_df)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Compare Multiple Crimes")
            selected_crimes = st.multiselect(
                "Select crimes to compare:",
                crime_columns,
                default=[selected_crime]
            )
            
            if st.button("Compare Crimes", use_container_width=True) and selected_crimes:
                fig = compare_multiple_crimes_streamlit(selected_data, selected_crimes, selected_state, selected_district)
                if fig:
                    st.pyplot(fig)
        
        with col2:
            st.markdown("#### Compare Districts")
            if selected_district != 'all':
                available_districts = sorted(state_districts.tolist())
                selected_districts = st.multiselect(
                    "Select districts to compare:",
                    available_districts,
                    default=[selected_district] if selected_district in available_districts else []
                )
                
                if st.button("Compare Districts", use_container_width=True) and selected_districts:
                    fig = compare_districts_streamlit(chosen_dataset_df, selected_state, selected_districts, selected_crime)
                    if fig:
                        st.pyplot(fig)
            else:
                st.info("District comparison not available when 'All Districts' is selected.")
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("All Districts Bar Chart", use_container_width=True):
                st.markdown("#### District Comparison Bar Chart")
                state_data = chosen_dataset_df[chosen_dataset_df['State Name'] == selected_state]
                fig = plot_all_districts_bar_streamlit(state_data, selected_state, selected_crime)
                if fig:
                    st.pyplot(fig)
        
        with col2:
            st.markdown("#### Crime Hotspots")
            n_hotspots = st.number_input("Number of top districts:", min_value=1, max_value=20, value=5)
            
            if st.button("Find Hotspots", use_container_width=True):
                state_data = chosen_dataset_df[chosen_dataset_df['State Name'] == selected_state]
                hotspots_df = show_crime_hotspots_streamlit(state_data, selected_state, selected_crime, n_hotspots)
                if hotspots_df is not None:
                    st.dataframe(hotspots_df)
    
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Cross-Dataset Comparison", use_container_width=True):
                st.markdown("#### Cross-Dataset Analysis")
                fig = compare_dataset_types_streamlit(datasets, selected_state, selected_district, location_desc)
                if fig:
                    st.pyplot(fig)
        
        with col2:
            st.markdown("#### Cross-State Analysis")
            available_states_for_comparison = sorted(chosen_dataset_df['State Name'].unique())
            selected_states = st.multiselect(
                "Select states to compare:",
                available_states_for_comparison,
                default=[selected_state]
            )
            
            if st.button("Compare States", use_container_width=True) and selected_states:
                fig = compare_states_datasets_streamlit(datasets, selected_dataset_name, selected_crime, selected_states)
                if fig:
                    st.pyplot(fig)

# Streamlit wrapper functions that return figures instead of showing them
def plot_trends_streamlit(data, state, district, crime):
    """Streamlit version of plot_trends that returns figure"""
    if data.empty or crime not in data.columns:
        st.error("No data available to plot.")
        return None
    
    yearly = data.groupby("Year")[crime].sum().reset_index()
    
    if yearly.empty or yearly[crime].sum() == 0:
        st.warning(f"No reported cases of '{crime}' found to plot.")
        return None
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=yearly, x="Year", y=crime, marker="o", ax=ax)
    
    plot_title = f"{crime} Trend in {district}, {state}"
    if district == 'all':
        plot_title = f"Total {crime} Trend in {state}"
    
    ax.set_title(plot_title)
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Cases")
    ax.set_xticks(yearly['Year'].astype(int))
    plt.tight_layout()
    return fig

def show_descriptive_stats_streamlit(df, crime_cols):
    """Streamlit version that returns DataFrame"""
    existing = [c for c in crime_cols if c in df.columns]
    if not existing:
        st.error("No valid crime columns found.")
        return None
    
    stats = df[existing].describe().T
    stats['median'] = df[existing].median()
    to_show = ['count', 'mean', 'median', 'std', 'min', '25%', '50%', '75%', 'max']
    
    for col in to_show:
        if col not in stats.columns:
            stats[col] = None
    
    return stats[to_show].round(3)

def compare_multiple_crimes_streamlit(df, crimes, state, district):
    """Streamlit version of compare_multiple_crimes"""
    if df.empty:
        st.error("No data available.")
        return None
    
    existing = [c for c in crimes if c in df.columns]
    if not existing:
        st.error("No valid crime columns found.")
        return None
    
    yearly = df.groupby("Year")[existing].sum().reset_index()
    if yearly.empty:
        st.error("No yearly data available.")
        return None
    
    fig, ax = plt.subplots(figsize=(12, 6))
    for c in existing:
        sns.lineplot(data=yearly, x="Year", y=c, marker="o", label=c, ax=ax)
    
    plot_title = f"Crime Comparison in {district}, {state}"
    if district == 'all':
        plot_title = f"Total Crime Comparison in {state}"
    
    ax.set_title(plot_title)
    ax.set_xlabel("Year")
    ax.set_ylabel("Cases")
    ax.legend(title="Crime Type")
    ax.set_xticks(yearly['Year'].astype(int))
    plt.tight_layout()
    return fig

def compare_districts_streamlit(dataset, state, districts, crime):
    """Streamlit version of compare_districts"""
    if crime not in dataset.columns:
        st.error(f"Crime '{crime}' not found in dataset.")
        return None
    
    fig, ax = plt.subplots(figsize=(12, 6))
    plotted = False
    
    for d in districts:
        df = dataset[(dataset['State Name'] == state) & (dataset['District Name'] == d)]
        yearly = df.groupby("Year")[crime].sum().reset_index()
        if not yearly.empty:
            sns.lineplot(data=yearly, x="Year", y=crime, marker="o", label=d, ax=ax)
            plotted = True
    
    if not plotted:
        st.error("No data found for selected districts.")
        return None
    
    ax.set_title(f"{crime} Comparison across Districts in {state}")
    ax.set_xlabel("Year")
    ax.set_ylabel("Cases")
    ax.legend(title="District")
    plt.tight_layout()
    return fig

def plot_all_districts_bar_streamlit(data, state, crime):
    """Streamlit version of plot_all_districts_bar"""
    if data.empty or crime not in data.columns:
        st.error("No data available to plot.")
        return None
    
    district_totals = data.groupby("District Name")[crime].sum().reset_index()
    district_totals = district_totals[district_totals[crime] > 0]
    district_totals = district_totals.sort_values(by=crime, ascending=False)
    
    if district_totals.empty:
        st.warning(f"No reported cases of '{crime}' found in {state}.")
        return None
    
    num_districts = len(district_totals)
    fig_height = max(8, num_districts * 0.4)
    fig, ax = plt.subplots(figsize=(12, fig_height))
    
    sns.barplot(data=district_totals, y="District Name", x=crime, palette="viridis", ax=ax)
    ax.set_title(f"Total '{crime}' Cases by District in {state}")
    ax.set_xlabel("Total Number of Cases")
    ax.set_ylabel("District")
    plt.tight_layout()
    return fig

def show_crime_hotspots_streamlit(data, state, crime, n=5):
    """Streamlit version that returns DataFrame"""
    if data.empty or crime not in data.columns:
        st.error("No data available.")
        return None
    
    district_totals = data.groupby("District Name")[crime].sum().reset_index()
    district_totals = district_totals[district_totals[crime] > 0]
    district_totals = district_totals.sort_values(by=crime, ascending=False)
    
    if district_totals.empty:
        st.warning(f"No reported cases of '{crime}' found in {state}.")
        return None
    
    top_n_districts = district_totals.head(n)
    top_n_districts = top_n_districts[['District Name', crime]].reset_index(drop=True)
    top_n_districts.index = top_n_districts.index + 1
    return top_n_districts

def compare_dataset_types_streamlit(datasets, state_name, district_name, location_desc):
    """Streamlit version of compare_dataset_types"""
    dataset_totals = {}
    dataset_yearly = {}
    
    for dataset_name, dataset_df in datasets.items():
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
        st.error(f"No data found for {location_desc}.")
        return None
    
    # Display summary
    st.write("**Total Crime Counts by Dataset Type:**")
    for dataset_name, total in sorted(dataset_totals.items(), key=lambda x: x[1], reverse=True):
        st.write(f"- {dataset_name.replace('_', ' ').title()}: {total:,} total crimes")
    
    # Create plots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
    
    # Bar chart
    sorted_totals = sorted(dataset_totals.items(), key=lambda x: x[1], reverse=True)
    dataset_names = [name.replace('_', ' ').title() for name, _ in sorted_totals]
    totals = [total for _, total in sorted_totals]
    
    sns.barplot(x=dataset_names, y=totals, palette="Set2", ax=ax1)
    ax1.set_title(f"Total Crime Comparison by Dataset Type - {location_desc}")
    ax1.set_xlabel("Dataset Type")
    ax1.set_ylabel("Total Crime Count")
    ax1.tick_params(axis='x', rotation=45)
    
    # Line plot
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
                               marker='o', label=dataset_name.replace('_', ' ').title(), ax=ax2)
            
            ax2.set_title(f"Crime Trends Comparison by Dataset Type - {location_desc}")
            ax2.set_xlabel("Year")
            ax2.set_ylabel("Total Crime Count")
            ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    return fig

def compare_states_datasets_streamlit(datasets, selected_dataset_name, selected_crime_type, chosen_states):
    """Streamlit version of compare_states_datasets"""
    selected_dataset = datasets[selected_dataset_name]
    
    if selected_crime_type not in selected_dataset.columns:
        st.error(f"Crime type '{selected_crime_type}' not found in dataset.")
        return None
    
    state_comparison = []
    state_yearly = {}
    
    for state in chosen_states:
        state_data = selected_dataset[selected_dataset['State Name'] == state]
        if not state_data.empty:
            total_crimes = state_data[selected_crime_type].sum()
            state_comparison.append({'State': state.title(), 'Total_Crimes': total_crimes})
            
            yearly = state_data.groupby('Year')[selected_crime_type].sum().reset_index()
            state_yearly[state] = yearly
    
    if not state_comparison:
        st.error("No data found for selected states.")
        return None
    
    comparison_df = pd.DataFrame(state_comparison)
    comparison_df = comparison_df.sort_values('Total_Crimes', ascending=False)
    
    # Display results
    st.write(f"**{selected_crime_type} Comparison Across States:**")
    for i, (_, row) in enumerate(comparison_df.iterrows(), 1):
        st.write(f"{i}. {row['State']}: {row['Total_Crimes']:,} cases")
    
    # Create plots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
    
    sns.barplot(data=comparison_df, x='State', y='Total_Crimes', palette='viridis', ax=ax1)
    ax1.set_title(f'{selected_crime_type} - Total Cases by State')
    ax1.set_xlabel('State')
    ax1.set_ylabel(f'Total {selected_crime_type} Cases')
    ax1.tick_params(axis='x', rotation=45)
    
    for state, yearly_data in state_yearly.items():
        if not yearly_data.empty:
            sns.lineplot(data=yearly_data, x='Year', y=selected_crime_type, 
                        marker='o', label=state.title(), ax=ax2)
    
    ax2.set_title(f'{selected_crime_type} - Trends Across States')
    ax2.set_xlabel('Year')
    ax2.set_ylabel(f'{selected_crime_type} Cases')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    main()