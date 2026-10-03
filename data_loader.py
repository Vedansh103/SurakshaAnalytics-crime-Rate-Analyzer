# data_loader.py
# Data loading and cleaning functions

from config import *

def check_dataset_directory():
    """
    Check if Dataset directory exists and create helpful error messages if not.
    """
    if not DATASET_DIR.exists():
        print("❌ ERROR: Dataset directory not found!")
        print(f"   Expected location: {DATASET_DIR}")
        print("   Please ensure you have:")
        print("   1. Cloned the complete repository")
        print("   2. The 'Dataset' folder is in the same directory as Data.py")
        print("   3. All CSV files are present in the Dataset folder")
        return False
    return True

def get_dataset_path(filename):
    """
    Get the full path to a dataset file, with proper error handling.
    """
    full_path = DATASET_DIR / filename
    if not full_path.exists():
        print(f"❌ ERROR: File not found: {filename}")
        print(f"   Expected location: {full_path}")
        print("   Please check if the file exists in the Dataset folder")
        return None
    return str(full_path)

def clean_dataset(df):
    """
    Applies a standard set of cleaning operations to a loaded dataframe.
    """
    print(f"Cleaning dataframe... Original shape: {df.shape}")
    
    # 1. Standardize Key Text Columns (State/District)
    key_cols = ['State Name', 'District Name']
    for col in key_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().str.strip()
            # add any project-specific replacements here if necessary
    
    # 2. Clean and Standardize 'Year' Column
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df = df.dropna(subset=['Year'])
        df['Year'] = df['Year'].astype(int)
    
    # 3. Clean Crime/Data Columns
    metadata_cols = ['ID', 'Year', 'State Name', 'State Code', 'District Name', 'District Code', 'Registration Circles']
    crime_cols = [col for col in df.columns if col not in metadata_cols]
    
    if crime_cols:
        for col in crime_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df[crime_cols] = df[crime_cols].fillna(0)
    
    # 4. Drop duplicates
    id_subset = ['State Name', 'District Name', 'Year']
    existing_id_subset = [c for c in id_subset if c in df.columns]
    if existing_id_subset:
        df = df.drop_duplicates(subset=existing_id_subset, keep='first')

    print(f"Cleaning complete. New shape: {df.shape}")
    return df

def load_datasets():
    """
    Loads AND CLEANS all crime datasets from CSV files into a dictionary.
    Returns dict of cleaned DataFrames or None on error.
    Uses robust path handling that works on any system.
    """
    # Check if Dataset directory exists
    if not check_dataset_directory():
        return None
    
    dataset_files = {
        'ipc': 'crime-by-juveniles-expanded.csv',
        'crime_against_women': 'districtwise_crime_against_women_readable.csv',
        'cyber_crimes': 'districtwise_cyber_crimes_readable.csv',
        'juveniles': 'districtwise_ipc_crimes_readable.csv',
        'missing_persons': 'districtwise-missing-persons-merged.csv'
    }
    
    datasets = {}
    missing_files = []
    
    print("🔍 Checking for required dataset files...")
    
    # First, check if all files exist
    for name, filename in dataset_files.items():
        file_path = get_dataset_path(filename)
        if file_path is None:
            missing_files.append(filename)
        else:
            print(f"   ✅ Found: {filename}")
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} required files:")
        for file in missing_files:
            print(f"   - {file}")
        print(f"\n📁 Expected location: {DATASET_DIR}")
        print("🔧 Please ensure all CSV files are present before running the analysis.")
        return None
    
    print(f"\n📊 Loading {len(dataset_files)} datasets...")
    
    try:
        for name, filename in dataset_files.items():
            file_path = get_dataset_path(filename)
            print(f"Loading dataset: {name} from {filename}")
            df = pd.read_csv(file_path)
            datasets[name] = clean_dataset(df)
        
        print("\n✅ All datasets loaded and cleaned successfully!")
        print(f"📍 Working directory: {SCRIPT_DIR}")
        return datasets
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("🔧 Please ensure all CSV files are in the Dataset folder.")
        return None
    except pd.errors.EmptyDataError as e:
        print(f"❌ Empty or corrupted file: {e}")
        print("🔧 Please check the CSV file integrity.")
        return None
    except Exception as e:
        print(f"❌ Unexpected error during loading: {e}")
        print("🔧 Please check file permissions and CSV format.")
        return None

def verify_setup():
    """
    Verify that the setup is correct for running the analysis.
    Provides helpful information about the current environment.
    """
    print("🔧 SETUP VERIFICATION")
    print("="*50)
    print(f"📍 Script location: {SCRIPT_DIR}")
    print(f"📁 Dataset directory: {DATASET_DIR}")
    print(f"🐍 Python version: {sys.version.split()[0]}")
    
    # Check required packages
    required_packages = ['pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 'scipy']
    print(f"\n📦 Package versions:")
    for package in required_packages:
        try:
            if package == 'pandas':
                print(f"   {package}: {pd.__version__}")
            elif package == 'numpy':
                print(f"   {package}: {np.__version__}")
            elif package == 'matplotlib':
                import matplotlib
                print(f"   {package}: {matplotlib.__version__}")
            elif package == 'seaborn':
                print(f"   {package}: {sns.__version__}")
            elif package == 'plotly':
                import plotly
                print(f"   {package}: {plotly.__version__}")
            elif package == 'scipy':
                import scipy
                print(f"   {package}: {scipy.__version__}")
        except Exception:
            print(f"   {package}: ❌ Not installed")
    
    print("="*50)