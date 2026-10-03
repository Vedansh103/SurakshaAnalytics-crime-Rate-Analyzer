import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="Suraksha Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import Data.py functions
try:
    from Data import (
        load_datasets, 
        categorize_crimes,
        plot_trends,
        compare_multiple_crimes,
        compare_districts,
        show_descriptive_stats,
        plot_all_districts_bar,
        show_crime_hotspots,
        compare_dataset_types,
        compare_states_datasets,
        plot_pie_chart_crime_distribution,
        plot_crime_heatmap,
        plot_stacked_bar_chart,
        enhanced_crime_selection_prompt
    )
except ImportError as e:
    st.error(f"Could not import from Data.py: {e}")
    st.stop()

def get_crime_columns(df):
    """Get crime columns from dataset"""
    return [col for col in df.columns if col not in 
            ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']]

@st.cache_data
def load_datasets_cached():
    """Cached version of dataset loading"""
    return load_datasets()

def streamlit_crime_selection(available_crimes, max_select=5, context="crimes"):
    """Streamlit version of crime selection"""
    if not available_crimes:
        return []
    
    st.write(f"**Select {context.title()} ({len(available_crimes)} available)**")
    
    if len(available_crimes) > 20:
        method = st.radio(
            "Selection Method:",
            ["Quick Select (Popular)", "Browse by Category", "Search", "Show All"],
            key=f"method_{context}"
        )
        
        if method == "Quick Select (Popular)":
            popular_keywords = ['murder', 'rape', 'theft', 'burglary', 'robbery', 'kidnapping', 'cyber', 'fraud']
            popular_crimes = []
            for keyword in popular_keywords:
                matches = [c for c in available_crimes if keyword in c.lower()]
                popular_crimes.extend(matches[:2])
                if len(popular_crimes) >= 15:
                    break
            
            if popular_crimes:
                return st.multiselect(
                    f"Select from popular {context}:",
                    popular_crimes,
                    key=f"popular_{context}",
                    max_selections=max_select
                )
        
        elif method == "Browse by Category":
            categories = categorize_crimes(available_crimes)
            selected_crimes = []
            
            for category, crimes in categories.items():
                with st.expander(f"{category} ({len(crimes)} crimes)"):
                    for crime in crimes[:10]:  # Limit to prevent UI overflow
                        if len(selected_crimes) < max_select:
                            if st.checkbox(crime, key=f"crime_{crime}_{context}"):
                                if crime not in selected_crimes:
                                    selected_crimes.append(crime)
            
            return selected_crimes
        
        elif method == "Search":
            search_term = st.text_input(f"Search {context}:", key=f"search_{context}")
            if search_term:
                matches = [c for c in available_crimes if search_term.lower() in c.lower()]
                if matches:
                    return st.multiselect(
                        f"Select from search results:",
                        matches,
                        key=f"search_results_{context}",
                        max_selections=max_select
                    )
            return []
    
    # Default: show multiselect for smaller lists
    return st.multiselect(
        f"Choose {context}:",
        available_crimes,
        key=f"full_list_{context}",
        max_selections=max_select
    )

def plot_trends_streamlit(data, state, district, crime):
    """Streamlit version of trend plotting"""
    if data.empty or crime not in data.columns:
        st.warning(f"No data available for {crime}")
        return
    
    yearly = data.groupby("Year")[crime].sum().reset_index()
    
    if yearly.empty or yearly[crime].sum() == 0:
        st.warning(f"No reported cases of '{crime}' found to plot.")
        return
    
    location_desc = f"{district.title()}, {state.title()}" if district != 'all' else f"All Districts in {state.title()}"
    
    # Create interactive plot
    fig = px.line(
        yearly, x="Year", y=crime,
        title=f"{crime} Trend in {location_desc}",
        markers=True,
        line_shape='spline'
    )
    
    fig.update_layout(
        height=500,
        xaxis_title="Year",
        yaxis_title="Number of Cases",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def compare_multiple_crimes_streamlit(df, crimes, state, district):
    """Streamlit version of multiple crime comparison"""
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
    
    location_desc = f"{district.title()}, {state.title()}" if district != 'all' else f"All Districts in {state.title()}"
    
    # Melt data for plotly
    melted_data = yearly.melt(id_vars=['Year'], var_name='Crime Type', value_name='Cases')
    
    fig = px.line(
        melted_data, x='Year', y='Cases', color='Crime Type',
        title=f"Crime Comparison in {location_desc}",
        markers=True
    )
    
    fig.update_layout(height=500, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

def show_descriptive_stats_streamlit(df, crime_cols):
    """Streamlit version of descriptive statistics"""
    existing = [c for c in crime_cols if c in df.columns]
    if not existing:
        st.warning("None of the requested crime columns exist in this data selection.")
        return
    
    st.subheader("Descriptive Statistics")
    
    stats = df[existing].describe().T
    stats['median'] = df[existing].median()
    
    # Format for better display
    display_stats = stats[['count', 'mean', 'median', 'std', 'min', 'max']].round(2)
    st.dataframe(display_stats, use_container_width=True)
    
    # Additional insights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Crimes Analyzed", len(existing))
    
    with col2:
        total_cases = df[existing].sum().sum()
        st.metric("Total Cases", f"{total_cases:,}")
    
    with col3:
        avg_per_crime = total_cases / len(existing) if existing else 0
        st.metric("Average per Crime Type", f"{avg_per_crime:,.0f}")

def main():
    """Main Streamlit application"""
    
    # Professional header
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2.5rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;'>
        <h1>SURAKSHA ANALYTICS v2.0</h1>
        <h3>Advanced Crime Data Analysis Platform for India</h3>
        <p>Interactive Web Interface • Real-time Analytics • Professional Visualizations</p>
        <p><strong>Data Coverage:</strong> 2017-2022 | <strong>Scope:</strong> All Indian States & Districts</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load datasets
    with st.spinner("Loading crime datasets..."):
        datasets = load_datasets_cached()
    
    if not datasets:
        st.error("No datasets loaded. Check your Dataset folder.")
        st.markdown("""
        **Setup Instructions:**
        1. Ensure Dataset folder exists in the same directory
        2. Verify all CSV files are present and accessible
        3. Check file permissions (read access required)
        """)
        return
    
    # Success metrics
    st.markdown("### System Status Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Datasets Loaded", len(datasets))
    with col2:
        total_records = sum(len(df) for df in datasets.values())
        st.metric("Total Records", f"{total_records:,}")
    with col3:
        total_crimes = sum(len(get_crime_columns(df)) for df in datasets.values())
        st.metric("Crime Categories", total_crimes)
    with col4:
        st.metric("Data Period", "2017-2022")
    
    # Sidebar
    st.sidebar.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1.5rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 1rem;'>
        <h3>ANALYSIS CONTROL PANEL</h3>
        <p>Professional Crime Analytics Suite</p>
    </div>
    """, unsafe_allow_html=True)
    
    analysis_options = {
        "Single Crime Trend": "Analyze trend for one crime type in selected location",
        "Multiple Crimes Comparison": "Compare different crimes in same location", 
        "Multi-District Comparison": "Compare same crime across different districts",
        "Descriptive Statistics": "Statistical summary of crime data",
        "District Rankings": "Visual comparison of all districts in state",
        "Crime Hotspots": "Identify top districts/states by crime count",
        "Cross-Dataset Comparison": "Compare IPC vs Cyber vs Women crimes",
        "Cross-State Analysis": "Same crime type across multiple states",
        "Enhanced Visualizations": "Interactive charts, heatmaps, and advanced plots"
    }
    
    selected_analysis = st.sidebar.selectbox(
        "Choose Analysis Type:",
        list(analysis_options.keys())
    )
    
    st.sidebar.write(f"**Description:** {analysis_options[selected_analysis]}")
    
    # Main analysis area
    st.markdown("""
    <div style='background: white; padding: 2rem; border-radius: 15px; 
                box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin: 1rem 0;'>
    """, unsafe_allow_html=True)
    
    if selected_analysis == "Single Crime Trend":
        st.header("Single Crime Trend Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dataset_choice = st.selectbox("Choose Dataset:", list(datasets.keys()))
            df = datasets[dataset_choice]
            
            states = sorted(df['State Name'].unique())
            selected_state = st.selectbox("Choose State:", states)
        
        with col2:
            districts = df[df['State Name'] == selected_state]['District Name'].unique()
            district_options = ['all'] + sorted(districts.tolist())
            selected_district = st.selectbox(
                "Choose District:", 
                district_options,
                format_func=lambda x: "All Districts" if x == 'all' else x.title()
            )
            
            crime_cols = get_crime_columns(df)
            selected_crime = st.selectbox("Choose Crime Type:", crime_cols)
        
        if st.button("Generate Analysis", type="primary"):
            # Filter data
            if selected_district == 'all':
                filtered_data = df[df['State Name'] == selected_state]
            else:
                filtered_data = df[
                    (df['State Name'] == selected_state) & 
                    (df['District Name'] == selected_district)
                ]
            
            plot_trends_streamlit(filtered_data, selected_state, selected_district, selected_crime)
    
    elif selected_analysis == "Multiple Crimes Comparison":
        st.header("Multiple Crimes Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dataset_choice = st.selectbox("Choose Dataset:", list(datasets.keys()))
            df = datasets[dataset_choice]
            
            states = sorted(df['State Name'].unique())
            selected_state = st.selectbox("Choose State:", states)
        
        with col2:
            districts = df[df['State Name'] == selected_state]['District Name'].unique()
            district_options = ['all'] + sorted(districts.tolist())
            selected_district = st.selectbox(
                "Choose District:",
                district_options,
                format_func=lambda x: "All Districts" if x == 'all' else x.title()
            )
        
        # Crime selection
        crime_cols = get_crime_columns(df)
        selected_crimes = streamlit_crime_selection(crime_cols, max_select=7, context="crimes for comparison")
        
        if st.button("Generate Comparison", type="primary") and selected_crimes:
            # Filter data
            if selected_district == 'all':
                filtered_data = df[df['State Name'] == selected_state]
            else:
                filtered_data = df[
                    (df['State Name'] == selected_state) & 
                    (df['District Name'] == selected_district)
                ]
            
            compare_multiple_crimes_streamlit(filtered_data, selected_crimes, selected_state, selected_district)
    
    elif selected_analysis == "Descriptive Statistics":
        st.header("Descriptive Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dataset_choice = st.selectbox("Choose Dataset:", list(datasets.keys()))
            df = datasets[dataset_choice]
            
            states = sorted(df['State Name'].unique())
            selected_state = st.selectbox("Choose State:", states)
        
        with col2:
            districts = df[df['State Name'] == selected_state]['District Name'].unique()
            district_options = ['all'] + sorted(districts.tolist())
            selected_district = st.selectbox(
                "Choose District:",
                district_options,
                format_func=lambda x: "All Districts" if x == 'all' else x.title()
            )
        
        # Crime selection
        crime_cols = get_crime_columns(df)
        selected_crimes = streamlit_crime_selection(crime_cols, max_select=10, context="crimes for statistics")
        
        if st.button("Generate Statistics", type="primary") and selected_crimes:
            # Filter data
            if selected_district == 'all':
                filtered_data = df[df['State Name'] == selected_state]
            else:
                filtered_data = df[
                    (df['State Name'] == selected_state) & 
                    (df['District Name'] == selected_district)
                ]
            
            show_descriptive_stats_streamlit(filtered_data, selected_crimes)
    
    elif selected_analysis == "Crime Hotspots":
        st.header("Crime Hotspots Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dataset_choice = st.selectbox("Choose Dataset:", list(datasets.keys()))
            df = datasets[dataset_choice]
            
            scope = st.radio(
                "Analysis Scope:",
                ["District hotspots within a state", "State hotspots across country"]
            )
        
        with col2:
            crime_cols = get_crime_columns(df)
            selected_crime = st.selectbox("Choose Crime Type:", crime_cols)
            
            n_hotspots = st.number_input(
                "Number of hotspots:",
                min_value=1, max_value=25, value=10
            )
        
        if scope == "District hotspots within a state":
            states = sorted(df['State Name'].unique())
            selected_state = st.selectbox("Choose State:", states)
            
            if st.button("Find District Hotspots", type="primary"):
                state_data = df[df['State Name'] == selected_state]
                
                district_totals = state_data.groupby("District Name")[selected_crime].sum().reset_index()
                district_totals = district_totals[district_totals[selected_crime] > 0]
                district_totals = district_totals.sort_values(by=selected_crime, ascending=False).head(n_hotspots)
                
                if not district_totals.empty:
                    st.success(f"Top {n_hotspots} District Hotspots for {selected_crime} in {selected_state.title()}")
                    
                    # Display results
                    display_df = district_totals.copy()
                    display_df['District Name'] = display_df['District Name'].str.title()
                    display_df.columns = ['District', 'Total Cases']
                    display_df.index = range(1, len(display_df) + 1)
                    
                    st.dataframe(display_df, use_container_width=True)
                    
                    # Visualization
                    fig = px.bar(
                        district_totals, 
                        x=selected_crime, 
                        y='District Name',
                        orientation='h',
                        title=f"Top {n_hotspots} District Hotspots - {selected_crime}",
                        color=selected_crime,
                        color_continuous_scale='Reds'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No data found for {selected_crime} in {selected_state}")
        
        else:  # State hotspots
            if st.button("Find State Hotspots", type="primary"):
                state_totals = df.groupby('State Name')[selected_crime].sum().sort_values(ascending=False).head(n_hotspots)
                
                if not state_totals.empty:
                    st.success(f"Top {n_hotspots} State Hotspots for {selected_crime}")
                    
                    # Display results
                    hotspot_data = []
                    for i, (state, total) in enumerate(state_totals.items(), 1):
                        hotspot_data.append({
                            'Rank': i, 
                            'State': state.title(), 
                            'Total Cases': f"{total:,}"
                        })
                    
                    st.dataframe(pd.DataFrame(hotspot_data), use_container_width=True, hide_index=True)
                    
                    # Visualization
                    fig = px.bar(
                        x=state_totals.values,
                        y=[s.title() for s in state_totals.index],
                        orientation='h',
                        title=f"Top {n_hotspots} State Hotspots - {selected_crime}",
                        color=state_totals.values,
                        color_continuous_scale='Reds'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No data found for {selected_crime}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p><strong>SURAKSHA ANALYTICS</strong> - Professional Crime Data Analysis Platform</p>
        <p>Data Period: 2017-2022 | Coverage: All Indian States & Districts</p>
        <p>Powered by Streamlit • Enhanced with Data.py Integration</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()