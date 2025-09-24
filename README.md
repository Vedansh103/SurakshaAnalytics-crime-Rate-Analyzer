# Suraksha_Analytics

District-wise Crime Data Analysis (2017 onwards).

This repository contains data and analysis code for district-level crime statistics in India. It focuses on multiple crime datasets (IPC, crimes against women, cyber crimes, juvenile crimes, and missing-persons datasets) prepared for analysis and visualization.

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


## Quickstart — prerequisites

You need Python 3.8+ and the following pip packages (minimum):

- pandas
- numpy
- matplotlib
- seaborn

Install them with:

```powershell
pip install pandas numpy matplotlib seaborn
```

Optionally create a virtual environment first.


## How to run `Data.py` (interactive script)

1. Open a terminal in the repository root (e.g., `e:\Surakshya Analytics`).
2. Run the script:

```powershell
python "e:\Surakshya Analytics\Data.py"
```

3. Follow the interactive prompts:
- Enter a state (you can enter a name or the number from the printed list).
- Choose a dataset by typing the dataset name or the number shown.
- Choose a crime type by name or number.

Notes:
- The script will attempt to load the CSV files listed at the top of `Data.py`. If a file is missing, the script prints a warning and that dataset is unavailable.
- The script normalizes column names (trims whitespace) and tries to detect the state column automatically (common column names: `State Name`, `State`, `state_name`). If the column name is different in your CSV, either rename the CSV columns or update the detection logic in `Data.py`.


## How to run the notebook

Open `Data.ipynb` in Jupyter or VS Code Jupyter and run cells interactively. The notebook contains exploratory analysis and visualizations. If you change dataset filenames, update the CSV paths in the notebook cells before running.


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

Last updated: September 24, 2025