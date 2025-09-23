# Crime Analysis System

Simple interactive crime data analysis tool.

## How to Use

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the main script:**
   ```bash
   python main.py
   ```

3. **Follow the prompts:**
   - Select State
   - Select District/City
   - Select Crime Type
   - Select Graph Type
   - View Analysis

## Available Graph Types

1. **Line Chart** - Year-wise trend line
2. **Bar Chart** - Year-wise bar graph
3. **Interactive Chart** - Plotly interactive chart
4. **Pie Chart** - Distribution by year
5. **Area Chart** - Filled area chart

## Files

- `main.py` - Main interactive script (run this)
- `crime_analyzer.py` - Core analysis functions
- `requirements.txt` - Required packages
- `districtwise-ipc-crimes-2017-onwards.csv` - Data file (required)

## Usage Flow

```
State → District/City → Crime Type → Graph Type → Analysis
```