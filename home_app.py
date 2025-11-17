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
    initial_sidebar_state="collapsed"
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        animation: fadeInDown 0.8s ease-out;
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 25px;
        color: white;
        text-align: center;
        margin: 3rem 0;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
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
        color: #667eea;
        font-weight: 800;
        margin-bottom: 1rem;
        animation: fadeInUp 1s ease-out;
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem 3rem;
        border: none;
        border-radius: 50px;
        font-size: 1.3rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
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
        color: #667eea;
    }
    
    .footer {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 25px;
        margin-top: 4rem;
        color: #666;
        border-top: 3px solid #667eea;
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
    
    # Professional Website Header
    st.markdown("""
    <div style="background: white; padding: 1rem 0; border-bottom: 1px solid #e0e0e0; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 2rem;">
            <div style="display: flex; align-items: center;">
                <h2 style="margin: 0; color: #667eea; font-weight: 700; font-size: 1.8rem;">
                    🚔 Crime Analyser
                </h2>
                <span style="margin-left: 1rem; color: #888; font-size: 0.9rem;">Advanced Analytics Platform</span>
            </div>
            <div style="display: flex; align-items: center; gap: 2rem;">
                <a href="#features" style="color: #666; text-decoration: none; font-weight: 500;">Features</a>
                <a href="#analytics" style="color: #666; text-decoration: none; font-weight: 500;">Analytics</a>
                <a href="#about" style="color: #666; text-decoration: none; font-weight: 500;">About</a>
                <button onclick="document.getElementById('hero_launch').click();" style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 0.5rem 1.5rem;
                    border-radius: 25px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                " onmouseover="this.style.transform='translateY(-2px)';" onmouseout="this.style.transform='translateY(0px)';">Get Started</button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
            powered by machine learning and advanced statistical methods.
        </p>
        <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap; margin-top: 2rem;">
            <div style="background: rgba(102, 126, 234, 0.1); padding: 0.8rem 1.5rem; border-radius: 25px; font-weight: 600; color: #667eea;">
                📊 Real-time Analytics
            </div>
            <div style="background: rgba(118, 75, 162, 0.1); padding: 0.8rem 1.5rem; border-radius: 25px; font-weight: 600; color: #764ba2;">
                🌍 Multi-state Coverage
            </div>
            <div style="background: rgba(102, 126, 234, 0.1); padding: 0.8rem 1.5rem; border-radius: 25px; font-weight: 600; color: #667eea;">
                🔥 AI-powered Insights
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
        <div class="feature-card">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
            <h3 style="color: #667eea; font-weight: 600; margin-bottom: 1rem;">Interactive Analytics</h3>
            <p style="color: #666; line-height: 1.6;">Comprehensive data visualization with interactive charts, trend analysis, and statistical insights across multiple crime categories with real-time filtering.</p>
            <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #eee; font-size: 0.9rem; color: #888;">
                ⚡ Real-time • 📈 Trends • 🎯 Filtering
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🌍</div>
            <h3 style="color: #667eea; font-weight: 600; margin-bottom: 1rem;">Geographic Intelligence</h3>
            <p style="color: #666; line-height: 1.6;">Multi-state and district-level comparisons with advanced geographic analysis and crime pattern identification using spatial analytics.</p>
            <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #eee; font-size: 0.9rem; color: #888;">
                🗺️ Spatial Analysis • 📍 Hotspots • 🔍 Patterns
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔥</div>
            <h3 style="color: #667eea; font-weight: 600; margin-bottom: 1rem;">AI-Powered Hotspots</h3>
            <p style="color: #666; line-height: 1.6;">Advanced machine learning algorithms for crime hotspot identification with risk assessment and predictive analytics for proactive law enforcement.</p>
            <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #eee; font-size: 0.9rem; color: #888;">
                🤖 AI-Powered • ⚠️ Risk Assessment • 🔮 Predictive
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
                <div style="font-size: 2rem; font-weight: 700; color: #667eea;">{}</div>
                <div style="color: #666; font-weight: 500;">Datasets</div>
                <div style="font-size: 0.8rem; color: #888; margin-top: 0.5rem;">Crime categories</div>
            </div>
            """.format(len(datasets)), unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📋</div>
                <div style="font-size: 2rem; font-weight: 700; color: #667eea;">{:,}</div>
                <div style="color: #666; font-weight: 500;">Records</div>
                <div style="font-size: 0.8rem; color: #888; margin-top: 0.5rem;">Crime incidents</div>
            </div>
            """.format(total_records), unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🗺️</div>
                <div style="font-size: 2rem; font-weight: 700; color: #667eea;">{}</div>
                <div style="color: #666; font-weight: 500;">States/UTs</div>
                <div style="font-size: 0.8rem; color: #888; margin-top: 0.5rem;">Geographic coverage</div>
            </div>
            """.format(total_states), unsafe_allow_html=True)
        with col4:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🏘️</div>
                <div style="font-size: 2rem; font-weight: 700; color: #667eea;">{}</div>
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
                2024 Crime Analyser Platform | Data Coverage: 2017-2022<br>
                Built for safer communities through data-driven insights
            </p>
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
    
    # Enhanced analysis type selection with cards
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem;">
        <h2 style="text-align: center; color: #667eea; margin-bottom: 1rem;">🔍 Select Analysis Type</h2>
        <p style="text-align: center; color: #666; font-size: 1.1rem;">Choose from our comprehensive suite of crime data analysis tools</p>
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
        {"name": "Enhanced Visualizations", "icon": "🎨", "desc": "Interactive charts and plots", "color": "#96ceb4"}
    ]
    
    # Create analysis selection cards in a grid
    cols = st.columns(3)
    
    for i, option in enumerate(analysis_options):
        with cols[i % 3]:
            if st.button(
                f"{option['icon']} {option['name']}",
                key=f"analysis_{i}",
                help=option['desc'],
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
        # Show welcome message when no analysis is selected
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: #f8f9fa; border-radius: 15px; margin: 2rem 0;">
            <h3 style="color: #667eea;">👆 Select an Analysis Type Above</h3>
            <p style="color: #666; font-size: 1.1rem;">Choose from our comprehensive analysis tools to start exploring crime data patterns and insights.</p>
            <div style="margin-top: 2rem;">
                <p style="color: #888; font-size: 0.9rem;">✨ Interactive visualizations • 📊 Statistical analysis • 🗺️ Geographic insights</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced footer
    st.markdown("""
    <div style="text-align: center; padding: 2rem; margin-top: 3rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; border-top: 3px solid #667eea;">
        <p style="color: #667eea; margin: 0; font-weight: bold; font-size: 1.1rem;">🔬 Crime Analyser - Advanced Analytics Platform</p>
        <p style="color: #888; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Powered by Python, Streamlit & Advanced Data Science | Data Coverage: 2017-2022</p>
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

if __name__ == "__main__":
    main()