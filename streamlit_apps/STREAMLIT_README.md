# 🚀 Crime Analyser - Streamlit Web App

**Interactive Web Interface for Crime Data Analysis**

This Streamlit web application provides a comprehensive, user-friendly interface for analyzing district-wise crime data across India (2017-2022). It includes all the functionality from the CLI tool with enhanced interactive visualizations.

## ✨ Features

### 📊 Analysis Types
- **🏛️ Single Location Analysis** - Analyze specific districts or entire states
- **📊 Cross-Dataset Comparison** - Compare IPC vs Cyber vs Women crimes
- **🌍 Cross-State Comparison** - Compare same crime across different states  
- **🔥 Crime Hotspots** - Find top crime districts and states
- **🎨 Enhanced Visualizations** - Interactive charts, heatmaps, and dashboards
- **📈 Statistical Analysis** - Detailed statistics and correlation analysis

### 🎯 Interactive Features
- **Real-time filtering** by state, district, and crime type
- **Multi-select options** for comparing multiple crimes
- **Interactive Plotly charts** with zoom, pan, and hover details
- **Dynamic data tables** with sorting and filtering
- **Responsive design** that works on desktop and mobile

### 📈 Visualization Types
- **Line Charts** - Crime trends over time
- **Bar Charts** - District/state comparisons
- **Pie Charts** - Crime distribution analysis
- **Heatmaps** - Correlation and geographic analysis
- **Scatter Plots** - Crime relationship analysis
- **Area Charts** - Stacked trend analysis

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.7+ (3.8+ recommended)
- All CSV files in the `Dataset/` folder

### 1. Install Dependencies
```bash
# From the streamlit_apps directory
pip install -r requirements_streamlit.txt

# Or install individually
pip install streamlit pandas numpy matplotlib seaborn plotly
```

### 2. Run the Application
```bash
# From the project root directory
streamlit run streamlit_apps/simple_streamlit.py

# Or from streamlit_apps directory
cd streamlit_apps
streamlit run simple_streamlit.py
```

### 3. Access the App
- The app will automatically open in your browser
- Default URL: `http://localhost:8501`
- Use the sidebar to configure your analysis

## 📱 How to Use

### Step 1: Choose Analysis Type
Select from 6 different analysis types in the sidebar:
- Single Location Analysis
- Cross-Dataset Comparison  
- Cross-State Comparison
- Crime Hotspots
- Enhanced Visualizations
- Statistical Analysis

### Step 2: Configure Parameters
- **Dataset**: Choose from IPC, Women crimes, Cyber crimes, etc.
- **State**: Select the state for analysis
- **District**: Choose specific district or "All Districts"
- **Crime Type**: Select crime(s) to analyze

### Step 3: View Results
- Interactive charts and visualizations
- Statistical summaries and data tables
- Export options for charts and data

## 🎨 Analysis Examples

### Single Location Analysis
```
Dataset: Crime Against Women
State: Delhi
District: All Districts
Crime: Dowry Deaths
→ Shows trend analysis, statistics, and comparisons
```

### Cross-State Comparison
```
Dataset: Cyber Crimes  
Crime: Online Financial Fraud
States: Delhi, Maharashtra, Karnataka, Tamil Nadu
→ Compares cyber crime rates across tech hubs
```

### Crime Hotspots
```
Dataset: IPC Crimes
Crime: Murder
Scope: State Hotspots (nationwide)
→ Shows top 10 states with highest murder rates
```

## 📊 Data Sources

The app uses the same datasets as the CLI tool:
- `districtwise_ipc_crimes_readable.csv`
- `districtwise_crime_against_women_readable.csv`
- `districtwise_cyber_crimes_readable.csv`
- `crime-by-juveniles-expanded.csv`
- `districtwise-missing-persons-merged.csv`

## 🔧 Troubleshooting

### Common Issues

**App won't start:**
```bash
# Check if streamlit is installed
streamlit --version

# Reinstall if needed
pip install --upgrade streamlit
```

**Data not loading:**
- Ensure you're running from the correct directory
- Check that `Dataset/` folder exists with CSV files
- Verify file permissions

**Charts not displaying:**
```bash
# Install/update plotly
pip install --upgrade plotly
```

**Performance issues:**
- Large datasets may take time to load
- Use filters to reduce data size
- Close other browser tabs if needed

### Error Messages

**"Could not import Data module"**
- Run from project root directory: `streamlit run streamlit_apps/simple_streamlit.py`

**"Dataset directory not found"**
- Ensure `Dataset/` folder is in project root
- Check that CSV files are present

## 🚀 Advanced Features

### Interactive Dashboard
- Real-time filtering and analysis
- Multiple visualization types
- Export capabilities for charts and data

### Enhanced Visualizations
- **Correlation Heatmaps** - See relationships between crimes
- **Geographic Analysis** - Crime distribution across regions
- **Time Series Analysis** - Trend analysis with statistical insights
- **Distribution Analysis** - Histograms and box plots

### Statistical Analysis
- Descriptive statistics (mean, median, std dev)
- Correlation analysis between crime types
- Year-over-year change calculations
- Trend analysis with percentage changes

## 📈 Performance Tips

1. **Filter Early** - Use state/district filters to reduce data size
2. **Limit Selections** - Don't select too many crimes at once
3. **Use Caching** - Streamlit caches data automatically
4. **Close Tabs** - Close unused browser tabs for better performance

## 🔄 Updates & Maintenance

The Streamlit app automatically syncs with:
- All CLI tool functionality
- Latest dataset updates
- New analysis features
- Enhanced visualizations

## 📞 Support

If you encounter issues:
1. Check this README for solutions
2. Verify your Python and package versions
3. Ensure all CSV files are present and readable
4. Try restarting the Streamlit server

---

**Last Updated**: November 2024
**Version**: 2.0 (Synced with CLI tool)