#!/usr/bin/env python3
"""
Setup Validator for Crime Analyser
This script checks if your environment is properly configured to run the analysis tools.
"""

import sys
from pathlib import Path
import importlib

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"🐍 Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7 or higher is required!")
        return False
    else:
        print("✅ Python version is compatible")
        return True

def check_packages():
    """Check if required packages are installed"""
    required_packages = {
        'pandas': 'Data manipulation and analysis',
        'numpy': 'Numerical computing',
        'matplotlib': 'Plotting and visualization',
        'seaborn': 'Statistical data visualization',
        'pathlib': 'Path handling (built-in)'
    }
    
    print(f"\n📦 Checking Required Packages:")
    missing_packages = []
    
    for package, description in required_packages.items():
        try:
            if package == 'pathlib':
                # pathlib is built-in since Python 3.4
                print(f"   ✅ {package}: Built-in module")
            else:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', 'Unknown')
                print(f"   ✅ {package} ({version}): {description}")
        except ImportError:
            print(f"   ❌ {package}: Missing - {description}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🔧 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_files():
    """Check if all required files and directories exist"""
    script_dir = Path(__file__).parent.absolute()
    dataset_dir = script_dir / "Dataset"
    
    print(f"\n📁 Checking File Structure:")
    print(f"   Project Directory: {script_dir}")
    
    # Check main files
    main_files = ['Data.py']
    for file in main_files:
        file_path = script_dir / file
        if file_path.exists():
            print(f"   ✅ {file}: Found")
        else:
            print(f"   ❌ {file}: Missing")
    
    # Check Dataset directory
    if dataset_dir.exists():
        print(f"   ✅ Dataset directory: Found")
        
        # Check dataset files
        required_datasets = [
            'crime-by-juveniles-expanded.csv',
            'districtwise_crime_against_women_readable.csv',
            'districtwise_cyber_crimes_readable.csv',
            'districtwise_ipc_crimes_readable.csv',
            'districtwise-missing-persons-merged.csv'
        ]
        
        missing_datasets = []
        for dataset in required_datasets:
            dataset_path = dataset_dir / dataset
            if dataset_path.exists():
                size_mb = dataset_path.stat().st_size / (1024 * 1024)
                print(f"   ✅ {dataset}: Found ({size_mb:.1f} MB)")
            else:
                print(f"   ❌ {dataset}: Missing")
                missing_datasets.append(dataset)
        
        if missing_datasets:
            print(f"\n🚨 Missing {len(missing_datasets)} dataset files!")
            return False
        else:
            print(f"\n✅ All {len(required_datasets)} dataset files found!")
            return True
    else:
        print(f"   ❌ Dataset directory: Missing")
        print(f"      Expected location: {dataset_dir}")
        return False

def test_data_loading():
    """Test if data can be loaded successfully"""
    try:
        import pandas as pd
        script_dir = Path(__file__).parent.absolute()
        dataset_dir = script_dir / "Dataset"
        
        print(f"\n🧪 Testing Data Loading:")
        
        # Test loading one dataset
        test_file = dataset_dir / "districtwise_ipc_crimes_readable.csv"
        if test_file.exists():
            df = pd.read_csv(test_file)
            print(f"   ✅ Successfully loaded test dataset")
            print(f"      Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            print(f"      Memory usage: {df.memory_usage(deep=True).sum() / (1024*1024):.1f} MB")
            return True
        else:
            print(f"   ❌ Test file not found: {test_file}")
            return False
    except Exception as e:
        print(f"   ❌ Data loading failed: {e}")
        return False

def main():
    """Run all setup checks"""
    print("🔍 CRIME ANALYSER - SETUP VALIDATOR")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_packages), 
        ("File Structure", check_files),
        ("Data Loading", test_data_loading)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            passed = check_func()
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Your system is ready to run Crime Analyser")
        print("🚀 You can now run:")
        print("   • python Data.py        (comprehensive crime data analysis tool)")
    else:
        print("❌ SOME CHECKS FAILED!")
        print("🔧 Please fix the issues above before running the analysis tools")
        print("\n💡 COMMON SOLUTIONS:")
        print("   • Install missing packages: pip install pandas numpy matplotlib seaborn")
        print("   • Ensure you're in the correct directory (where Data.py is located)")
        print("   • If cloning from Git, make sure all files downloaded properly")
        print("   • Check file permissions (especially on Linux/Mac)")
    
    print("=" * 50)

if __name__ == "__main__":
    main()