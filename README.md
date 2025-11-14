# 🚀 Suraksha Analytics

**Comprehensive District-wise Crime Data Analysis Platform for India (2017-2022)**

This repository provides advanced analytics tools for exploring crime patterns across Indian states and districts. Features include cross-dataset comparisons, interactive visualizations, and comprehensive exploratory data analysis (EDA) capabilities.

## ✨ Key Features

- 📊 **Interactive Crime Analysis** - CLI and Jupyter notebook interfaces
- 🆚 **Cross-Dataset Comparison** - Compare IPC vs Cyber vs Women crimes  
- 🌍 **Multi-State Analysis** - Compare crime patterns across states
- 📈 **Advanced Visualizations** - Seaborn-powered charts and trend analysis
- 🔍 **Flexible Filtering** - By state, district, crime type, and time period
- 🎯 **Hotspot Identification** - Find top crime districts and patterns

## Repository structure (current snapshot)

Top-level files and folders:

- `Data.ipynb` — Jupyter notebook containing exploratory analysis and visualizations.
- `Data.py` — Interactive script to query datasets by state/district and crime type. Loads CSVs from the `Dataset/` folder and prints selected rows.
- `DataSet Merge.py` — Utility script added to merge or transform the missing-persons datasets (added upstream).
- `Dataset/` — Folder with CSV dataset files (see list below).
- `README.md` — This file (project overview and instructions).
- `.cspell.json` — (editor-only) cSpell dictionary used to silence spelling warnings in VS Code for domain words like `districtwise`.
- `LICENSE` — Project license file.


### Files currently in `Dataset/` (examples from repo)
- `crime-by-juveniles-expanded.csv`
- `districtwise_crime_against_women_readable.csv`
- `districtwise_cyber_crimes_readable.csv`
- `districtwise_ipc_crimes_readable.csv`
- `districtwise-missing-persons-20172020-cleaned.csv`
- `districtwise-missing-persons-2021-onwards-cleaned.csv`

If you add or rename files inside `Dataset/`, update the mapping at the top of `Data.py` or the notebook cell that loads CSVs.


## 🛠️ Quick Setup & Installation

### Prerequisites
- **Python 3.7+** (3.8+ recommended)
- **Git** for cloning the repository

### 1. Clone the Repository
```bash
git clone https://github.com/mohvijayjain/Suraksha_Analytics.git
cd Suraksha_Analytics
```

### 2. Install Required Packages

**Option A: Quick Install**
```bash
pip install -r requirements.txt
```

**Option B: Manual Install**
```bash
pip install pandas numpy matplotlib seaborn
```

**Option C: Virtual Environment (Recommended)**
```bash
# Create virtual environment
python -m venv suraksha_env

# Activate it
# Windows:
suraksha_env\Scripts\activate
# Mac/Linux:
source suraksha_env/bin/activate

# Install packages
pip install -r requirements.txt
```

### 3. Verify Setup
Run the setup validator to ensure everything is configured correctly:
```bash
python setup_validator.py
```

This will check:
- ✅ Python version compatibility
- ✅ Required packages installation  
- ✅ Dataset files availability
- ✅ Data loading functionality

### 4. Test Run
If setup validator passes, you're ready to run the analysis:
```bash
python Data.py
```


## 🚀 Usage Guide

### Interactive CLI Analysis (`Data.py`)

The main script provides a comprehensive, step-by-step analysis workflow:

```bash
python Data.py
```

**Analysis Flow:**
1. **📊 Choose Dataset** - Select from IPC, Women crimes, Cyber crimes, Juveniles, Missing persons
2. **🗺️ Choose State** - Pick from available states in selected dataset  
3. **🏘️ Choose District** - Select specific district or "all" for state-level analysis
4. **🔍 Choose Crime Type** - Select from available crime categories
5. **⚙️ Choose Analysis** - Pick from 8 analysis options:

**Analysis Options:**
- `1` **Single Crime Trend** - Time series analysis for selected crime
- `2` **Multiple Crimes Comparison** - Compare different crimes in same location
- `3` **Multi-District Comparison** - Same crime across different districts  
- `4` **Descriptive Statistics** - Statistical summary of crime data
- `5` **District Bar Chart** - Visual comparison of all districts in state
- `6` **Crime Hotspots** - Identify top N districts by crime count
- `7` **🆚 Cross-Dataset Comparison** - Compare IPC vs Cyber vs Women crimes
- `8` **🌍 Cross-State Analysis** - Same crime type across multiple states

### Jupyter Notebook (`Data.ipynb`)

For interactive analysis and visualization:

```bash
jupyter notebook Data.ipynb
```

**Or in VS Code:**
1. Open `Data.ipynb` in VS Code
2. Select Python kernel
3. Run cells sequentially

**Notebook Features:**
- 📊 Interactive data exploration
- 📈 Customizable visualizations  
- ⚙️ Easy parameter modification
- 📋 Comprehensive dataset summaries


## Git workflow notes (team collaboration)

- To fetch and merge upstream changes safely when you have uncommitted work, use either a stash or a backup branch:

```powershell
# stash
git stash push -m "WIP: my local edits"
git pull origin main
git stash pop

# or create a backup branch
git checkout -b my-work-backup
git add -A
git commit -m "WIP: backup"
git checkout main
git pull origin main
```

- If `git pull` complains that files would be overwritten, either stash or commit your local changes first. Avoid `git reset --hard` unless you are certain you want to discard local edits.

- If you need to revert a single commit safely (create an undo commit):

```powershell
git revert <commit-hash>
```


## Notes about editor warnings

- You may see a VS Code cSpell warning underlining words like `districtwise`. The repository contains `.cspell.json` to whitelist domain vocabulary. This is an editor-only configuration and does not affect runtime.
- On Windows you may see a Git warning about line endings (LF vs CRLF). This is normal; Git will convert as configured by your `core.autocrlf` setting.


## Recent changes (summary)

- Added robust dataset loading and state/district selection logic to `Data.py`.
- Fixed merge artifacts and improved error messages when CSV files or columns are missing.
- Added `DataSet Merge.py` to help merge missing-persons datasets (incoming from contributor).


## Contributing

- When you edit `Data.py` or `Data.ipynb`, please run the script/notebook locally to verify behavior before pushing.
- Communicate breaking changes in the dataset filenames or column names to the team so we can keep `Data.py` and the notebook in sync.


## Questions or next steps

- Want me to run `DataSet Merge.py` and show what it produces? Reply and I will run it locally (no push).
- Want me to open a PR-style diff summarizing the recent teammate changes to `Data.py`? I can generate that for review.

---

## 🔧 Troubleshooting

### Common Issues & Solutions

**❌ "Dataset directory not found" error:**
```bash
# Make sure you're in the project root directory
cd path/to/Suraksha_Analytics
python Data.py
```

**❌ "Module not found" error:**
```bash
# Install missing packages
pip install -r requirements.txt

# Or install individually
pip install pandas numpy matplotlib seaborn
```

**❌ "Permission denied" error:**
```bash
# On Linux/Mac, ensure files are readable
chmod +r Dataset/*.csv

# On Windows, run as administrator or check antivirus settings
```

**❌ Files not loading properly:**
```bash
# Run the setup validator
python setup_validator.py

# This will diagnose and report specific issues
```

### Getting Help

1. **Run Setup Validator**: `python setup_validator.py`
2. **Check File Paths**: Ensure you're in the correct directory
3. **Verify Downloads**: Make sure all files downloaded from Git
4. **Check Permissions**: Ensure read access to Dataset folder
5. **Update Dependencies**: `pip install --upgrade pandas numpy matplotlib seaborn`

---

## 📈 Project Stats

- **5 Datasets** with 20,000+ crime records  
- **6+ Years** of historical data (2017-2022)
- **35+ States/UTs** across India
- **700+ Districts** covered
- **8 Analysis Types** available
- **Cross-Platform** compatible (Windows/Mac/Linux)

---

*Last updated: November 15, 2025*