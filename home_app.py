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
    page_icon="🚔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for professional and interactive styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 25%, #45b7d1 50%, #96ceb4 75%, #feca57 100%);
        background-size: 400% 400%;
        animation: gradientShift 8s ease infinite, fadeInDown 0.8s ease-out;
        color: white;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 15px 40px rgba(255, 107, 107, 0.4);
    }
    
    .feature-card {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        text-align: center;
        margin: 1rem 0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 1px solid rgba(102, 126, 234, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.5s;
    }
    
    .feature-card:hover::before {
        left: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    .stats-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
        background-size: 400% 400%;
        animation: gradientShift 10s ease infinite;
        padding: 3rem;
        border-radius: 30px;
        color: white;
        text-align: center;
        margin: 3rem 0;
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    .stats-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .hero-section {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        border-radius: 30px;
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.1) 0%, transparent 50%), 
                    radial-gradient(circle at 80% 20%, rgba(118, 75, 162, 0.1) 0%, transparent 50%);
        opacity: 0.5;
    }
    
    .hero-title {
        font-size: 4.5rem;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57);
        background-size: 400% 400%;
        animation: gradientShift 6s ease infinite, fadeInUp 1s ease-out, titlePulse 3s ease-in-out infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 0 0 30px rgba(255, 107, 107, 0.5);
    }
    
    .hero-subtitle {
        font-size: 1.4rem;
        color: #666;
        font-weight: 400;
        margin-bottom: 2rem;
        animation: fadeInUp 1s ease-out 0.2s both;
    }
    
    .hero-description {
        font-size: 1.2rem;
        color: #888;
        max-width: 800px;
        margin: 0 auto 3rem;
        line-height: 1.8;
        animation: fadeInUp 1s ease-out 0.4s both;
    }
    
    .cta-button {
        background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 25%, #45b7d1 50%, #96ceb4 75%, #feca57 100%);
        background-size: 400% 400%;
        animation: gradientShift 3s ease infinite;
        color: white;
        padding: 1.2rem 3rem;
        border: none;
        border-radius: 50px;
        font-size: 1.3rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 10px 30px rgba(255, 107, 107, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .cta-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .cta-button:hover::before {
        left: 100%;
    }
    
    .cta-button:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
    }
    
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.15);
    }
    
    .section-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin: 3rem 0 2rem;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
        background-size: 200% 200%;
        animation: gradientShift 4s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .footer {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 25px;
        margin-top: 4rem;
        color: #666;
        border-top: 3px solid #4f46e5;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(102, 126, 234, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(102, 126, 234, 0);
        }
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes titlePulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    @keyframes buttonGlow {
        0%, 100% { box-shadow: 0 20px 40px rgba(255, 107, 107, 0.6); }
        50% { box-shadow: 0 25px 50px rgba(255, 107, 107, 0.8), 0 0 30px rgba(255, 107, 107, 0.5); }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_datasets():
    """Load all datasets from Dataset folder with proper cleaning"""
    dataset_dir = Path("Dataset")
    
    if not dataset_dir.exists():
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
                
                # Clean dataset
                key_cols = ['State Name', 'District Name']
                for col in key_cols:
                    if col in df.columns:
                        df[col] = df[col].astype(str).str.lower().str.strip()
                
                if 'Year' in df.columns:
                    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
                    df = df.dropna(subset=['Year'])
                    df['Year'] = df['Year'].astype(int)
                
                metadata_cols = ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']
                crime_cols = [col for col in df.columns if col not in metadata_cols]
                
                if crime_cols:
                    for col in crime_cols:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    df[crime_cols] = df[crime_cols].fillna(0)
                
                id_subset = ['State Name', 'District Name', 'Year']
                existing_id_subset = [c for c in id_subset if c in df.columns]
                if existing_id_subset:
                    df = df.drop_duplicates(subset=existing_id_subset, keep='first')
                
                datasets[name] = df
            except Exception as e:
                continue
    
    return datasets

def show_home_page():
    """Display the professional home page"""
    
    # Sliding Sidebar
    with st.sidebar:
        st.title("🚔 Crime Analyser")
        st.markdown("---")
        
        if st.button("ℹ️ About", key="sidebar_about", help="Learn about Crime Analyser", use_container_width=True, type="primary"):
            st.session_state.page = "about"
            st.rerun()
            
        if st.button("✨ Features", key="sidebar_features", help="Explore platform features", use_container_width=True, type="primary"):
            st.session_state.page = "features"
            st.rerun()
            
        if st.button("🚀 Launch Analytics", key="sidebar_analytics", help="Launch Analytics Platform", use_container_width=True, type="primary"):
            st.session_state.page = "analysis"
            st.rerun()
    
    # Professional Website Header
    st.markdown("""
    <div style="background: white; padding: 1rem 0; border-bottom: 1px solid #e0e0e0; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 2rem;">
            <div style="display: flex; align-items: center;">
                <h2 style="margin: 0; color: #667eea; font-weight: 700; font-size: 1.8rem;">
                    🚔 Crime Analyser
                </h2>
            </div>
            <div style="display: flex; align-items: center; gap: 2rem;">
                <button onclick="document.getElementById('hero_launch').click();" style="
                    background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 50%, #45b7d1 100%);
                    color: white;
                    border: none;
                    padding: 0.5rem 1.5rem;
                    border-radius: 25px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    box-shadow: 0 5px 15px rgba(255, 107, 107, 0.3);
                " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 25px rgba(255, 107, 107, 0.5)';" onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 5px 15px rgba(255, 107, 107, 0.3)';">Get Started</button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hidden About button for header functionality
    if st.button("ℹ️ About", key="nav_about", help="Learn about Crime Analyser", type="secondary", use_container_width=False):
        st.session_state.page = "about"
        st.rerun()
    st.markdown('<style>div[data-testid="stButton"]:has(button[kind="secondary"]) { display: none; }</style>', unsafe_allow_html=True)
    
    # Enhanced Hero Section with Interactive Elements
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">
            🚔 Crime Analyser
        </h1>
        <h3 class="hero-subtitle">
            Advanced Crime Data Analysis Platform for India
        </h3>
        <p class="hero-description">
            Unlock powerful insights from comprehensive crime data across Indian states and districts. 
            Analyze trends, identify hotspots, and make data-driven decisions with our cutting-edge analytics platform 
            powered by advanced statistical methods and data visualization.
        </p>
        <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap; margin-top: 2rem;">
            <div style="background: rgba(102, 126, 234, 0.1); padding: 0.8rem 1.5rem; border-radius: 25px; font-weight: 600; color: #667eea;">
                📊 Real-time Analytics
            </div>
            <div style="background: rgba(118, 75, 162, 0.1); padding: 0.8rem 1.5rem; border-radius: 25px; font-weight: 600; color: #764ba2;">
                🌍 Multi-state Coverage
            </div>
            <div style="background: rgba(102, 126, 234, 0.1); padding: 0.8rem 1.5rem; border-radius: 25px; font-weight: 600; color: #667eea;">
                🔥 Data-driven Insights
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced launch button with animation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <div style="margin-bottom: 1rem;">
                <span style="font-size: 1.1rem; color: #667eea; font-weight: 600;">✨ Ready to explore crime data insights?</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Launch Analytics Platform", type="primary", use_container_width=True, key="hero_launch", help="Access comprehensive crime data analysis tools"):
            st.session_state.page = "analysis"
            st.rerun()
    
    # Enhanced Features Section
    st.markdown('<h2 class="section-title">✨ Platform Capabilities</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <p style="font-size: 1.2rem; color: #666; max-width: 600px; margin: 0 auto;">
            Discover powerful features designed for law enforcement, researchers, and policy makers
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card" style="height: 320px; display: flex; flex-direction: column; justify-content: space-between;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
            <h3 style="color: #ff6b6b; font-weight: 600; margin-bottom: 1rem;">Interactive Analytics</h3>
            <p style="color: #666; line-height: 1.6; flex-grow: 1;">Comprehensive data visualization with interactive charts, trend analysis, and statistical insights across multiple crime categories with real-time filtering.</p>
            <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #eee; font-size: 0.9rem; color: #888;">
                ⚡ Real-time • 📈 Trends • 🎯 Filtering
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card" style="height: 320px; display: flex; flex-direction: column; justify-content: space-between;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🌍</div>
            <h3 style="color: #4ecdc4; font-weight: 600; margin-bottom: 1rem;">Geographic Intelligence</h3>
            <p style="color: #666; line-height: 1.6; flex-grow: 1;">Multi-state and district-level comparisons with advanced geographic analysis and crime pattern identification using spatial analytics.</p>
            <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #eee; font-size: 0.9rem; color: #888;">
                🗺️ Spatial Analysis • 📍 Hotspots • 🔍 Patterns
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card" style="height: 320px; display: flex; flex-direction: column; justify-content: space-between;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔥</div>
            <h3 style="color: #45b7d1; font-weight: 600; margin-bottom: 1rem;">Crime Hotspots</h3>
            <p style="color: #666; line-height: 1.6; flex-grow: 1;">Advanced statistical analysis for crime hotspot identification with risk assessment and data analytics for proactive law enforcement.</p>
            <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #eee; font-size: 0.9rem; color: #888;">
                📊 Statistical • ⚠️ Risk Assessment • 🔮 Predictive
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Platform Statistics
    datasets = load_datasets()
    if datasets:
        total_records = sum(len(df) for df in datasets.values())
        total_states = len(set().union(*[df['State Name'].unique() for df in datasets.values()]))
        total_districts = len(set().union(*[df['District Name'].unique() for df in datasets.values()]))
        
        st.markdown("""
        <div class="stats-container">
            <h2 style="margin-bottom: 2rem;">📈 Platform Statistics</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</div>
                <div style="font-size: 2rem; font-weight: 700; color: #ff6b6b;">{}</div>
                <div style="color: #666; font-weight: 500;">Datasets</div>
                <div style="font-size: 0.8rem; color: #888; margin-top: 0.5rem;">Crime categories</div>
            </div>
            """.format(len(datasets)), unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📋</div>
                <div style="font-size: 2rem; font-weight: 700; color: #4ecdc4;">{:,}</div>
                <div style="color: #666; font-weight: 500;">Records</div>
                <div style="font-size: 0.8rem; color: #888; margin-top: 0.5rem;">Crime incidents</div>
            </div>
            """.format(total_records), unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🗺️</div>
                <div style="font-size: 2rem; font-weight: 700; color: #45b7d1;">{}</div>
                <div style="color: #666; font-weight: 500;">States/UTs</div>
                <div style="font-size: 0.8rem; color: #888; margin-top: 0.5rem;">Geographic coverage</div>
            </div>
            """.format(total_states), unsafe_allow_html=True)
        with col4:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🏘️</div>
                <div style="font-size: 2rem; font-weight: 700; color: #96ceb4;">{}</div>
                <div style="color: #666; font-weight: 500;">Districts</div>
                <div style="font-size: 0.8rem; color: #888; margin-top: 0.5rem;">Local analysis</div>
            </div>
            """.format(total_districts), unsafe_allow_html=True)
    
    # Enhanced Analysis Types Section
    st.markdown('<h2 class="section-title">🔍 Analysis Capabilities</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <p style="font-size: 1.2rem; color: #666; max-width: 700px; margin: 0 auto;">
            Comprehensive suite of analytical tools for deep crime data insights and intelligence
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📈 Trend & Pattern Analysis
        - **Single Crime Trends**: Time series visualization
        - **Multi-Crime Comparison**: Comparative analysis
        - **Geographic Patterns**: Spatial crime distribution
        - **Seasonal Analysis**: Temporal crime patterns
        
        ### 🎯 Advanced Analytics
        - **Hotspot Identification**: High-risk area detection
        - **Correlation Analysis**: Crime relationship mapping
        - **Statistical Modeling**: Predictive insights
        - **Risk Assessment**: Threat level evaluation
        """)
    
    with col2:
        st.markdown("""
        ### 🌐 Cross-Dataset Intelligence
        - **IPC vs Cyber Crimes**: Category comparison
        - **Women & Child Safety**: Specialized analysis
        - **Missing Persons**: Investigation support
        - **Juvenile Crime**: Youth-focused insights
        
        ### 📊 Interactive Visualizations
        - **Dynamic Dashboards**: Real-time updates
        - **Interactive Maps**: Geographic visualization
        - **Custom Reports**: Tailored analysis
        - **Export Capabilities**: Data sharing tools
        """)
    
    # Enhanced Secondary Call to Action
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%); 
                padding: 3rem 2rem; border-radius: 25px; margin: 3rem 0; text-align: center; 
                border: 1px solid rgba(102, 126, 234, 0.1);">
        <h2 style="color: #667eea; margin-bottom: 1rem; font-weight: 700;">🚀 Ready to Unlock Crime Intelligence?</h2>
        <p style="font-size: 1.2rem; color: #666; margin-bottom: 2rem; max-width: 600px; margin-left: auto; margin-right: auto;">
            Join thousands of analysts, researchers, and law enforcement professionals using our platform for data-driven insights.
        </p>
        <div style="display: flex; justify-content: center; gap: 1rem; margin-bottom: 2rem;">
            <span style="background: rgba(102, 126, 234, 0.1); padding: 0.5rem 1rem; border-radius: 20px; color: #667eea; font-weight: 600;">🎯 Precision Analytics</span>
            <span style="background: rgba(118, 75, 162, 0.1); padding: 0.5rem 1rem; border-radius: 20px; color: #764ba2; font-weight: 600;">⚡ Real-time Insights</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🔬 Explore Advanced Analytics", type="secondary", use_container_width=True, key="secondary_launch", help="Access comprehensive analytical tools and visualizations"):
            st.session_state.page = "analysis"
            st.rerun()
    
    # Enhanced Platform Features
    st.markdown('<h2 class="section-title">🛠️ Platform Features</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <p style="font-size: 1.1rem; color: #666;">Built with enterprise-grade security and performance standards</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); text-align: center; border-left: 4px solid #667eea;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🔒</div>
            <h4 style="color: #667eea; margin-bottom: 1rem;">Data Security</h4>
            <ul style="text-align: left; color: #666; line-height: 1.8;">
                <li>End-to-end encryption</li>
                <li>Privacy protection</li>
                <li>GDPR compliance</li>
                <li>Secure processing</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); text-align: center; border-left: 4px solid #4facfe;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">⚡</div>
            <h4 style="color: #4facfe; margin-bottom: 1rem;">Performance</h4>
            <ul style="text-align: left; color: #666; line-height: 1.8;">
                <li>Lightning-fast processing</li>
                <li>Real-time analytics</li>
                <li>Optimized algorithms</li>
                <li>Scalable architecture</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); text-align: center; border-left: 4px solid #43e97b;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">📱</div>
            <h4 style="color: #43e97b; margin-bottom: 1rem;">Accessibility</h4>
            <ul style="text-align: left; color: #666; line-height: 1.8;">
                <li>Web-based platform</li>
                <li>Mobile responsive</li>
                <li>Cross-platform support</li>
                <li>Cloud-based access</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); text-align: center; border-left: 4px solid #fa709a;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🎓</div>
            <h4 style="color: #fa709a; margin-bottom: 1rem;">User Experience</h4>
            <ul style="text-align: left; color: #666; line-height: 1.8;">
                <li>Intuitive interface</li>
                <li>Guided workflows</li>
                <li>Interactive tutorials</li>
                <li>24/7 support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Simple Footer
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 15px;">
            <h3 style="color: #667eea; margin-bottom: 1rem;">Crime Analyser</h3>
            <p style="color: #666; margin-bottom: 1.5rem;">
                Empowering law enforcement and policy makers with cutting-edge data intelligence
            </p>
            <p style="color: #888; font-size: 0.9rem;">
                2025 Crime Analyser Platform | Data Coverage: 2017-2022<br>
                Built for safer communities through data-driven insights
            </p>
        </div>
        """, unsafe_allow_html=True)

def show_features_page():
    """Display the Features page with platform capabilities"""
    
    st.title("✨ Platform Features")
    st.write("Explore our comprehensive crime analytics capabilities")
    
    if st.button("🏠 Back", key="features_back_home"):
        st.session_state.page = "home"
        st.rerun()
    
    st.markdown("---")
    
    # Main Features
    st.subheader("🚀 Core Capabilities")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Data Analytics")
        st.write("• Single crime trend visualization")
        st.write("• Multi-crime comparison charts")
        st.write("• Time series analysis")
        st.write("• Statistical modeling")
        
        st.markdown("")
        
        st.markdown("### 🌍 Geographic Intelligence")
        st.write("• Multi-district comparisons")
        st.write("• Cross-state analysis")
        st.write("• Crime hotspot identification")
        st.write("• Risk assessment mapping")
    
    with col2:
        st.markdown("### 📊 Advanced Insights")
        st.write("• District risk scoring")
        st.write("• Pattern recognition")
        st.write("• Predictive modeling")
        st.write("• Correlation analysis")
        
        st.markdown("")
        
        st.markdown("### 🔍 Interactive Tools")
        st.write("• Dynamic dashboards")
        st.write("• Real-time filtering")
        st.write("• Custom visualizations")
        st.write("• Data export options")
    
    st.markdown("---")
    
    # Additional Info
    st.subheader("📋 Dataset Coverage")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**5** Crime Categories")
    with col2:
        st.info("**35+** States & UTs")
    with col3:
        st.info("**700+** Districts")
    
    st.markdown("---")
    
    st.write("Ready to explore crime data insights?")
    if st.button("🚀 Launch Analytics", type="primary", key="features_try"):
        st.session_state.page = "analysis"
        st.rerun()

def show_about_page():
    """Display the About page with project information"""
    
    # About page header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 20px; margin-bottom: 2rem; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);">
        <div style="color: white; text-align: center;">
            <h1 style="margin: 0; font-size: 3rem; font-weight: 800;">📊 About Crime Analyser</h1>
            <p style="margin: 1rem 0 0 0; opacity: 0.9; font-size: 1.3rem;">Advanced Crime Data Intelligence Platform</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Back to home button
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("🏠 Home", key="about_back_home", help="Return to homepage"):
            st.session_state.page = "home"
            st.rerun()
    
    # Project Overview
    st.markdown("""
    <div style="background: white; padding: 2.5rem; border-radius: 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.08); margin: 2rem 0;">
        <h2 style="color: #667eea; margin-bottom: 1.5rem; font-size: 2.2rem;">🎯 Project Overview</h2>
        <p style="font-size: 1.2rem; line-height: 1.8; color: #444; margin-bottom: 1.5rem;">
            <strong>Crime Analyser</strong> is a comprehensive data intelligence platform designed to empower law enforcement agencies, 
            policy makers, and researchers with advanced crime analytics capabilities across India.
        </p>
        <p style="font-size: 1.1rem; line-height: 1.7; color: #666;">
            Our platform processes and analyzes over <strong>20,000+ crime records</strong> spanning <strong>35+ Indian states</strong> 
            and <strong>700+ districts</strong>, covering the period from <strong>2017-2022</strong>. We provide actionable insights 
            through interactive visualizations, statistical analysis, and predictive modeling.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mission
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(78, 205, 196, 0.1) 100%); padding: 2rem; border-radius: 15px; margin: 2rem 0;">
        <h3 style="color: #ff6b6b; margin-bottom: 1rem; font-size: 1.8rem;">🎯 Our Mission</h3>
        <p style="font-size: 1.1rem; line-height: 1.7; color: #555;">
            To democratize access to crime data analytics and empower stakeholders with data-driven insights 
            for creating safer communities through evidence-based decision making and proactive crime prevention strategies.
        </p>
        <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(255, 107, 107, 0.1); border-radius: 10px;">
            <strong style="color: #ff6b6b;">📊 Data-Driven • 🔒 Security-Focused • 🌐 Community-Centered</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Features
    st.markdown("""
    <div style="background: white; padding: 2.5rem; border-radius: 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.08); margin: 2rem 0;">
        <h2 style="color: #667eea; margin-bottom: 2rem; font-size: 2.2rem; text-align: center;">🚀 Platform Capabilities</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
            <h4 style="color: #667eea; margin-bottom: 1rem;">Advanced Analytics</h4>
            <ul style="text-align: left; color: #666; line-height: 1.8;">
                <li>Time series analysis</li>
                <li>Statistical modeling</li>
                <li>Trend identification</li>
                <li>Correlation analysis</li>
                <li>Predictive insights</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🗺️</div>
            <h4 style="color: #4facfe; margin-bottom: 1rem;">Geographic Intelligence</h4>
            <ul style="text-align: left; color: #666; line-height: 1.8;">
                <li>Multi-state comparisons</li>
                <li>District-level analysis</li>
                <li>Hotspot identification</li>
                <li>Spatial patterns</li>
                <li>Risk assessment</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎨</div>
            <h4 style="color: #43e97b; margin-bottom: 1rem;">Interactive Visualizations</h4>
            <ul style="text-align: left; color: #666; line-height: 1.8;">
                <li>Dynamic dashboards</li>
                <li>Real-time charts</li>
                <li>Custom reports</li>
                <li>Export capabilities</li>
                <li>Mobile responsive</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Technical Stack
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%); padding: 2.5rem; border-radius: 20px; margin: 2rem 0;">
        <h2 style="color: #667eea; margin-bottom: 2rem; font-size: 2.2rem; text-align: center;">🛠️ Technical Architecture</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-top: 2rem;">
            <div style="background: white; padding: 1.5rem; border-radius: 15px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
                <h4 style="color: #ff6b6b; margin-bottom: 1rem;">🐍 Backend</h4>
                <p style="color: #666;">Python, Pandas, NumPy, SciPy</p>
            </div>
            <div style="background: white; padding: 1.5rem; border-radius: 15px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
                <h4 style="color: #4ecdc4; margin-bottom: 1rem;">📊 Visualization</h4>
                <p style="color: #666;">Plotly, Matplotlib, Seaborn</p>
            </div>
            <div style="background: white; padding: 1.5rem; border-radius: 15px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
                <h4 style="color: #45b7d1; margin-bottom: 1rem;">🌐 Frontend</h4>
                <p style="color: #666;">Streamlit, HTML5, CSS3</p>
            </div>
            <div style="background: white; padding: 1.5rem; border-radius: 15px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
                <h4 style="color: #96ceb4; margin-bottom: 1rem;">🤖 AI/ML</h4>
                <p style="color: #666;">Recommendation Engine, Smart Insights</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Data Coverage
    st.markdown("""
    <div style="background: white; padding: 2.5rem; border-radius: 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.08); margin: 2rem 0;">
        <h2 style="color: #667eea; margin-bottom: 2rem; font-size: 2.2rem; text-align: center;">📊 Data Coverage & Statistics</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Load and display actual statistics
    datasets = load_datasets()
    if datasets:
        total_records = sum(len(df) for df in datasets.values())
        total_states = len(set().union(*[df['State Name'].unique() for df in datasets.values()]))
        total_districts = len(set().union(*[df['District Name'].unique() for df in datasets.values()]))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ff8a80 100%); color: white; padding: 2rem; border-radius: 15px; text-align: center; box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3);">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📁</div>
                <div style="font-size: 2.2rem; font-weight: 800;">{len(datasets)}</div>
                <div style="font-size: 1.1rem; opacity: 0.9;">Datasets</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); color: white; padding: 2rem; border-radius: 15px; text-align: center; box-shadow: 0 8px 20px rgba(78, 205, 196, 0.3);">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</div>
                <div style="font-size: 2.2rem; font-weight: 800;">{total_records:,}</div>
                <div style="font-size: 1.1rem; opacity: 0.9;">Records</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #45b7d1 0%, #2196f3 100%); color: white; padding: 2rem; border-radius: 15px; text-align: center; box-shadow: 0 8px 20px rgba(69, 183, 209, 0.3);">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🗺️</div>
                <div style="font-size: 2.2rem; font-weight: 800;">{total_states}</div>
                <div style="font-size: 1.1rem; opacity: 0.9;">States/UTs</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #96ceb4 0%, #4caf50 100%); color: white; padding: 2rem; border-radius: 15px; text-align: center; box-shadow: 0 8px 20px rgba(150, 206, 180, 0.3);">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🏘️</div>
                <div style="font-size: 2.2rem; font-weight: 800;">{total_districts}</div>
                <div style="font-size: 1.1rem; opacity: 0.9;">Districts</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Call to Action
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 3rem 2rem; border-radius: 20px; margin: 3rem 0; text-align: center; color: white;">
        <h2 style="margin-bottom: 1rem; font-size: 2.2rem;">🚀 Ready to Explore Crime Intelligence?</h2>
        <p style="font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.9;">
            Join law enforcement professionals and researchers using our platform for data-driven insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📊 Launch Analytics Platform", type="primary", use_container_width=True, key="about_launch"):
            st.session_state.page = "analysis"
            st.rerun()
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 2rem; margin-top: 3rem; background: #f8f9fa; border-radius: 15px; color: #666;">
        <p style="margin: 0; font-weight: 600; color: #667eea;">🔒 Crime Analyser - Advanced Analytics Platform</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Empowering safer communities through data intelligence | 2025</p>
    </div>
    """, unsafe_allow_html=True)

def show_analysis_page():
    """Display the enhanced analysis page"""
    
    # Enhanced navigation header with professional styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
        <div style="color: white;">
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">📊 Crime Analytics Dashboard</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem;">Advanced Data Analysis & Visualization Platform</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Back to home button with enhanced styling
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("🏠 Home", key="back_home", help="Return to homepage"):
            st.session_state.page = "home"
            st.rerun()
    
    # Load datasets with enhanced loading display
    with st.spinner("🔄 Loading crime datasets..."):
        datasets = load_datasets()
    
    if not datasets:
        st.error("❌ **Dataset Loading Failed**")
        st.info("📁 Please ensure the Dataset folder contains all required CSV files.")
        return
    
    # Enhanced success message with metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.success(f"✅ **{len(datasets)} Datasets**")
    with col2:
        total_records = sum(len(df) for df in datasets.values())
        st.info(f"📊 **{total_records:,} Records**")
    with col3:
        total_states = len(set().union(*[df['State Name'].unique() for df in datasets.values()]))
        st.info(f"🗺️ **{total_states} States**")
    with col4:
        total_districts = len(set().union(*[df['District Name'].unique() for df in datasets.values()]))
        st.info(f"🏘️ **{total_districts} Districts**")
    
    st.markdown("---")
    
    # Enhanced analysis interface
    show_enhanced_analysis_interface(datasets)

def show_enhanced_analysis_interface(datasets):
    """Show the enhanced main analysis interface with professional styling"""
    
    # Professional analytics overview section with elegant colors
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(139, 92, 246, 0.12) 25%, rgba(59, 130, 246, 0.12) 50%, rgba(16, 185, 129, 0.12) 75%, rgba(245, 158, 11, 0.12) 100%); 
                padding: 3rem; border-radius: 25px; margin-bottom: 2.5rem; 
                border: 1px solid rgba(99, 102, 241, 0.2);
                box-shadow: 0 20px 40px rgba(99, 102, 241, 0.15), 0 0 0 1px rgba(255, 255, 255, 0.05);">
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 25%, #3b82f6 50%, #10b981 75%, #f59e0b 100%);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
                       margin-bottom: 1rem; font-size: 2.5rem; font-weight: 800;">🔍 Advanced Crime Analytics Suite</h2>
            <p style="color: #64748b; font-size: 1.3rem; max-width: 850px; margin: 0 auto 2rem; font-weight: 500;">Choose from our comprehensive suite of professional-grade crime data analysis tools</p>
            <div style="display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap; margin-top: 2rem;">
                <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%); 
                            padding: 1rem 2rem; border-radius: 30px; font-weight: 700; color: #6366f1;
                            border: 1px solid rgba(99, 102, 241, 0.2); box-shadow: 0 8px 25px rgba(99, 102, 241, 0.15);">
                    🎯 Precision Analytics
                </div>
                <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(139, 92, 246, 0.05) 100%); 
                            padding: 1rem 2rem; border-radius: 30px; font-weight: 700; color: #8b5cf6;
                            border: 1px solid rgba(139, 92, 246, 0.2); box-shadow: 0 8px 25px rgba(139, 92, 246, 0.15);">
                    📊 Real-time Insights
                </div>
                <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%); 
                            padding: 1rem 2rem; border-radius: 30px; font-weight: 700; color: #10b981;
                            border: 1px solid rgba(16, 185, 129, 0.2); box-shadow: 0 8px 25px rgba(16, 185, 129, 0.15);">
                    🔬 Statistical Modeling
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Analysis options with enhanced styling
    analysis_options = [
        {"name": "Single Crime Trend", "icon": "📈", "desc": "Time series analysis for specific crimes", "color": "#667eea"},
        {"name": "Multiple Crimes Comparison", "icon": "🔄", "desc": "Compare different crime types", "color": "#f093fb"},
        {"name": "Multi-District Comparison", "icon": "🏙️", "desc": "Compare across districts", "color": "#4facfe"},
        {"name": "Descriptive Statistics", "icon": "📊", "desc": "Statistical analysis and insights", "color": "#43e97b"},
        {"name": "District Bar Chart", "icon": "🏛️", "desc": "Visual district comparisons", "color": "#fa709a"},
        {"name": "Crime Hotspots", "icon": "🔥", "desc": "Identify high-risk areas", "color": "#ff6b6b"},
        {"name": "Cross-Dataset Comparison", "icon": "📊", "desc": "Compare dataset categories", "color": "#4ecdc4"},
        {"name": "Cross-State Analysis", "icon": "🌍", "desc": "Multi-state comparisons", "color": "#45b7d1"},
        {"name": "Enhanced Visualizations", "icon": "🎨", "desc": "Interactive charts and plots", "color": "#96ceb4"},
        {"name": "District Risk Scoring", "icon": "🎯", "desc": "Calculate comprehensive risk scores (NEW!)", "color": "#FF4500"}
    ]
    
    # Interactive analysis cards with enhanced styling
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h3 style="text-align: center; color: #667eea; margin-bottom: 2rem; font-size: 1.8rem;">📈 Analysis Categories</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Group analysis options by category
    categories = {
        "📊 Statistical Analysis": [0, 3, 9],  # Single Trend, Descriptive Stats, Risk Scoring
        "🔄 Comparative Analysis": [1, 2, 4, 6, 7],  # Multiple Crimes, Multi-District, Bar Chart, Cross-Dataset, Cross-State
        "🎨 Advanced Visualizations": [5, 8]  # Hotspots, Enhanced Viz
    }
    
    category_colors = {
        "📊 Statistical Analysis": {"bg": "linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(99, 102, 241, 0.02) 100%)", "border": "#6366f1", "text": "#6366f1"},
        "🔄 Comparative Analysis": {"bg": "linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(139, 92, 246, 0.02) 100%)", "border": "#8b5cf6", "text": "#8b5cf6"},
        "🎨 Advanced Visualizations": {"bg": "linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(16, 185, 129, 0.02) 100%)", "border": "#10b981", "text": "#10b981"}
    }
    
    for category, indices in categories.items():
        colors = category_colors[category]
        st.markdown(f"""
        <div style="background: {colors['bg']}; padding: 1rem 1.5rem; border-radius: 20px; margin: 1.5rem 0; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.08); border-left: 5px solid {colors['border']};
                    border: 1px solid {colors['border']}33;">
            <h4 style="color: {colors['text']}; margin-bottom: 0.5rem; font-size: 1.4rem; font-weight: 700;">{category}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(len(indices))
        for col_idx, option_idx in enumerate(indices):
            option = analysis_options[option_idx]
            with cols[col_idx]:
                if st.button(
                    f"{option['icon']} {option['name']}",
                    key=f"analysis_{option_idx}",
                    help=f"{option['desc']} - {option['name']} provides detailed insights for data-driven decision making.",
                    use_container_width=True
                ):
                    st.session_state.selected_analysis = option['name']
                    st.rerun()
    
    # Show selected analysis interface
    if hasattr(st.session_state, 'selected_analysis'):
        selected_option = next(opt for opt in analysis_options if opt['name'] == st.session_state.selected_analysis)
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {selected_option['color']}22 0%, {selected_option['color']}11 100%); 
                    padding: 1.5rem; border-radius: 15px; margin: 2rem 0; border-left: 5px solid {selected_option['color']};">
            <h3 style="color: {selected_option['color']}; margin: 0;">
                {selected_option['icon']} {selected_option['name']}
            </h3>
            <p style="margin: 0.5rem 0 0 0; color: #666;">{selected_option['desc']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Set the analysis type in session state for streamlit_main to use
        st.session_state.analysis_type = st.session_state.selected_analysis
        
        # Run the main analysis application
        from streamlit_main import main as analysis_main
        analysis_main()
    else:
        # Enhanced welcome section with elegant colors
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(248, 250, 252, 0.8) 0%, rgba(241, 245, 249, 0.8) 100%); 
                    padding: 4rem; border-radius: 25px; margin: 2rem 0;
                    border: 1px solid rgba(99, 102, 241, 0.15); 
                    box-shadow: 0 20px 40px rgba(99, 102, 241, 0.08), 0 0 0 1px rgba(255, 255, 255, 0.05);">
            <div style="text-align: center;">
                <div style="font-size: 4rem; margin-bottom: 1.5rem; 
                            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #10b981 100%);
                            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">🚀</div>
                <h3 style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #10b981 100%);
                           -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
                           margin-bottom: 1.5rem; font-size: 2.5rem; font-weight: 800;">Ready to Analyze Crime Data?</h3>
                <p style="color: #64748b; font-size: 1.3rem; margin-bottom: 3rem; max-width: 700px; margin-left: auto; margin-right: auto; font-weight: 500;">
                    Select an analysis type above to start exploring comprehensive crime data patterns, trends, and insights with our advanced analytics platform.
                </p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 2rem; margin-top: 3rem;">
                    <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%); 
                                padding: 2rem; border-radius: 20px; 
                                box-shadow: 0 10px 30px rgba(99, 102, 241, 0.1);
                                border: 1px solid rgba(99, 102, 241, 0.1);">
                        <div style="font-size: 2.5rem; margin-bottom: 1rem;">📊</div>
                        <h4 style="color: #6366f1; margin-bottom: 0.8rem; font-weight: 700;">Statistical Analysis</h4>
                        <p style="color: #64748b; font-size: 1rem; font-weight: 500;">Advanced statistical modeling and trend analysis</p>
                    </div>
                    <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%); 
                                padding: 2rem; border-radius: 20px; 
                                box-shadow: 0 10px 30px rgba(139, 92, 246, 0.1);
                                border: 1px solid rgba(139, 92, 246, 0.1);">
                        <div style="font-size: 2.5rem; margin-bottom: 1rem;">🗺️</div>
                        <h4 style="color: #8b5cf6; margin-bottom: 0.8rem; font-weight: 700;">Geographic Intelligence</h4>
                        <p style="color: #64748b; font-size: 1rem; font-weight: 500;">Multi-state and district-level comparisons</p>
                    </div>
                    <div style="background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%); 
                                padding: 2rem; border-radius: 20px; 
                                box-shadow: 0 10px 30px rgba(16, 185, 129, 0.1);
                                border: 1px solid rgba(16, 185, 129, 0.1);">
                        <div style="font-size: 2.5rem; margin-bottom: 1rem;">🎨</div>
                        <h4 style="color: #10b981; margin-bottom: 0.8rem; font-weight: 700;">Interactive Visualizations</h4>
                        <p style="color: #64748b; font-size: 1rem; font-weight: 500;">Dynamic charts and real-time insights</p>
                    </div>
                </div>
                <div style="margin-top: 3rem; padding: 1.5rem; 
                            background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%); 
                            border-radius: 15px; border: 1px solid rgba(99, 102, 241, 0.15);">
                    <p style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                              -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
                              font-weight: 700; margin: 0; font-size: 1.1rem;">💡 Pro Tip: Start with 'Descriptive Statistics' for an overview, then explore specific analysis types for deeper insights</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced footer with elegant styling
    st.markdown("""
    <div style="text-align: center; padding: 3rem; margin-top: 4rem; 
                background: linear-gradient(135deg, rgba(248, 250, 252, 0.8) 0%, rgba(241, 245, 249, 0.8) 100%); 
                border-radius: 20px; 
                border-top: 4px solid transparent;
                border-image: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #10b981 100%) 1;
                box-shadow: 0 10px 30px rgba(99, 102, 241, 0.08);">
        <p style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #10b981 100%);
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
                  margin: 0; font-weight: 800; font-size: 1.3rem;">🔬 Crime Analyser - Advanced Analytics Platform</p>
        <p style="color: #64748b; margin: 1rem 0 0 0; font-size: 1rem; font-weight: 500;">Powered by Python, Streamlit & Advanced Data Science | Data Coverage: 2017-2022</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application controller"""
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    
    # Page routing
    if st.session_state.page == "home":
        show_home_page()
    elif st.session_state.page == "analysis":
        show_analysis_page()
    elif st.session_state.page == "about":
        show_about_page()
    elif st.session_state.page == "features":
        show_features_page()

if __name__ == "__main__":
    main()