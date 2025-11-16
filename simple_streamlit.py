import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
from pathlib import Path

# Add current directory to path to import Data module
sys.path.append(str(Path(__file__).parent))

try:
    from Data_clean import load_datasets, get_crime_columns
except ImportError:
    st.error("Could not import Data module. Make sure Data_clean.py is in the same directory.")
    st.stop()

# Configure page
st.set_page_config(
    page_title="Suraksha Analytics",
    layout="wide"
)

def main():
    st.title("Suraksha Analytics")
    st.write("Crime Data Analysis Platform for India")
    
    # Load datasets
    with st.spinner("Loading datasets..."):
        try:
            datasets = load_datasets()
        except Exception as e:
            st.error(f"Error loading datasets: {str(e)}")
            st.info("Make sure you have the Dataset folder with CSV files in the same directory as this script.")
            return
    
    if not datasets:
        st.error("No datasets loaded. Check your Dataset folder.")
        return
    
    st.success(f"Loaded {len(datasets)} datasets successfully!")
    
    # Sidebar selections
    st.sidebar.header("Configuration")
    
    # Dataset selection
    st.sidebar.subheader("1. Choose Dataset")
    dataset_names = list(datasets.keys())
    selected_dataset = st.sidebar.selectbox("Dataset:", dataset_names)
    
    df = datasets[selected_dataset]
    
    # State selection
    st.sidebar.subheader("2. Choose State")
    states = sorted(df['State Name'].unique())
    selected_state = st.sidebar.selectbox("State:", states)
    
    # District selection
    st.sidebar.subheader("3. Choose District")
    districts = df[df['State Name'] == selected_state]['District Name'].unique()
    district_options = ['All Districts'] + sorted(districts.tolist())
    selected_district = st.sidebar.selectbox("District:", district_options)
    
    # Crime selection
    st.sidebar.subheader("4. Choose Crime Type")
    crime_cols = [col for col in df.columns if col not in 
                  ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code']]
    selected_crime = st.sidebar.selectbox("Crime Type:", crime_cols)
    
    # Filter data
    if selected_district == 'All Districts':
        filtered_data = df[df['State Name'] == selected_state]
        location = f"All Districts in {selected_state}"
    else:
        filtered_data = df[
            (df['State Name'] == selected_state) & 
            (df['District Name'] == selected_district)
        ]
        location = f"{selected_district}, {selected_state}"
    
    # Main content
    st.header(f"Analysis for: {location}")
    st.write(f"Dataset: {selected_dataset}")
    st.write(f"Crime Type: {selected_crime}")
    
    if filtered_data.empty:
        st.warning("No data found for the selected filters.")
        return
    
    # Show data preview
    with st.expander("Data Preview"):
        cols_to_show = ['State Name', 'District Name', 'Year', selected_crime]
        st.dataframe(filtered_data[cols_to_show].head())
    
    # Analysis tabs
    tab1, tab2, tab3 = st.tabs(["Basic Analysis", "Comparisons", "Statistics"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Plot Crime Trend"):
                yearly_data = filtered_data.groupby('Year')[selected_crime].sum().reset_index()
                
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(yearly_data['Year'], yearly_data[selected_crime], marker='o')
                ax.set_title(f"{selected_crime} Trend - {location}")
                ax.set_xlabel("Year")
                ax.set_ylabel("Number of Cases")
                st.pyplot(fig)
        
        with col2:
            if st.button("Show Summary Stats"):
                stats = filtered_data[selected_crime].describe()
                st.write("Summary Statistics:")
                st.write(stats)
    
    with tab2:
        st.subheader("Compare Multiple Crimes")
        selected_crimes = st.multiselect("Select crimes to compare:", crime_cols, default=[selected_crime])
        
        if st.button("Compare Crimes") and selected_crimes:
            yearly_comparison = filtered_data.groupby('Year')[selected_crimes].sum().reset_index()
            
            fig, ax = plt.subplots(figsize=(12, 6))
            for crime in selected_crimes:
                ax.plot(yearly_comparison['Year'], yearly_comparison[crime], marker='o', label=crime)
            
            ax.set_title(f"Crime Comparison - {location}")
            ax.set_xlabel("Year")
            ax.set_ylabel("Number of Cases")
            ax.legend()
            st.pyplot(fig)
    
    with tab3:
        if st.button("Generate Full Statistics"):
            st.subheader("Detailed Statistics")
            
            # Basic stats
            total_cases = filtered_data[selected_crime].sum()
            avg_cases = filtered_data[selected_crime].mean()
            max_year = filtered_data.loc[filtered_data[selected_crime].idxmax(), 'Year'] if not filtered_data.empty else "N/A"
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Cases", f"{total_cases:,}")
            col2.metric("Average per Year", f"{avg_cases:.1f}")
            col3.metric("Peak Year", max_year)
            
            # Yearly breakdown
            st.subheader("Yearly Breakdown")
            yearly_stats = filtered_data.groupby('Year')[selected_crime].sum().reset_index()
            st.bar_chart(yearly_stats.set_index('Year')[selected_crime])

if __name__ == "__main__":
    main()