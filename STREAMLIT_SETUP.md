# 🚀 Suraksha Analytics - Streamlit Web Interface

## Quick Start

### Option 1: Windows (Easy)
```bash
# Double-click or run in command prompt
run_streamlit.bat
```

### Option 2: Cross-Platform
```bash
# Run the Python launcher
python run_app.py
```

### Option 3: Manual
```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit
streamlit run streamlit_main.py
```

## Features Synced with Data.py

✅ **All Analysis Types Available:**
- 📈 Single Crime Trend Analysis
- 🔄 Multiple Crimes Comparison  
- 🏙️ Multi-District Comparison
- 📊 Descriptive Statistics
- 🏛️ District Rankings
- 🔥 Crime Hotspots Analysis
- ⚔️ Cross-Dataset Comparison
- 🌍 Cross-State Analysis
- 🎨 Enhanced Visualizations

✅ **Enhanced Features:**
- Professional UI with modern styling
- Interactive Plotly charts
- Smart crime categorization
- Real-time data filtering
- Responsive design
- Error handling and validation

## Access the Application

Once running, open your browser to:
**http://localhost:8501**

## Troubleshooting

**Dependencies Issues:**
```bash
pip install --upgrade streamlit plotly pandas seaborn matplotlib
```

**Dataset Not Found:**
- Ensure `Dataset/` folder exists in the same directory
- Verify all CSV files are present and accessible

**Port Already in Use:**
```bash
streamlit run streamlit_main.py --server.port 8502
```

## File Structure
```
suraksha analytics/
├── streamlit_main.py      # Main Streamlit application
├── Data.py               # Core analysis functions
├── Dataset/              # Crime data CSV files
├── requirements.txt      # Python dependencies
├── run_streamlit.bat     # Windows launcher
├── run_app.py           # Cross-platform launcher
└── STREAMLIT_SETUP.md   # This file
```

## Professional Features

🎯 **Interactive Dashboard** - Point-and-click analysis
📊 **Real-time Charts** - Dynamic Plotly visualizations  
🔍 **Smart Filtering** - Intelligent crime categorization
📱 **Responsive Design** - Works on desktop and mobile
⚡ **Fast Performance** - Cached data loading
🛡️ **Error Handling** - Robust validation and feedback

---
*Powered by Streamlit + Data.py Integration*