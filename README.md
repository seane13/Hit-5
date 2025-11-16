
# Hit 5 Lottery Analysis

## A modular pipeline for cleaning, analyzing, simulating, and modeling 5-number lottery draws

### Project Overview

#### This repository provides Python scripts and Jupyter notebooks for:

1. Cleaning and preparing raw lottery draw data

2. Generating strategic combination candidates (using hot/warm/cold frequency analysis)

3. Running simulations and backtests to evaluate both pool and machine-learning strategies

4. Hybrid backtesting: combining pool selection and ML scoring
5. Feature engineering and performance benchmarking

### Data Source and Attribution
The historical lottery data analyzed in this project originates from:

Washington's Lottery - Official Results
https://www.walottery.com/WinningNumbers/

#### Methods of Extraction and Processing
Raw Data Collection: Draw results were manually downloaded and/or programmatically extracted from Washington's Lottery official winning numbers pages, using standard web browsers and custom Python scripts (see html2hit5.py for examples).

Cleaning & Preprocessing: All draw records were reformatted, deduplicated, and cleaned to normalize date formats and number columns using scripts in the scripts/ and utils/ folders.

Data Files: Intermediate and results data (e.g., data/hit5_clean_deduped.csv) are derived solely from the aforementioned public lottery data.

Intellectual Property and Open Source Notice
This repository is an open-source, non-commercial project for educational, statistical, and research purposes only.
Washington's Lottery retains all copyrights and ownership of the original draw result data.
Use, redistribution, or publication of the data should comply with the terms outlined by the Washington State Lottery and any additional applicable regulations.

No affiliation or endorsement: This project is not affiliated with, endorsed by, or associated with Washington's Lottery, the Washington State Lottery Commission, or any related entity.
Official game results should always be verified via the primary source.

If utilizing or redistributing this dataset, please cite both this repository and the official Washington Lottery site as the original source for the underlying game results.

#### Folder Structure
```
project_root/
│
├── data/       # Raw, cleaned, and output data files
├── scripts/    # Python scripts for processing, analysis, simulation, and backtest
├── notebooks/  # Jupyter notebooks for exploration and reporting
├── archive/    # Deprecated scripts for reference
├── utils/      # Shared utilities (lottery_stats, pool_select, combo_filters, etc.)
├── README.md   # This project overview
```

#### Workflow Chart
```
flowchart TD
    A[Raw Data (.txt/.html/.csv)] --> B[Cleaning Scripts (clean_data.py, robust_clean.py, dedup.py)]
    B --> C[Cleaned Data (.csv)]
    C --> D[Analysis & Pool/Combo Gen (analysis.py, pool.py, combos.py)]
    D --> E[Simulation/Backtest (backtest_pool.py, backtest.py, hybrid_backtest.py)]
    D --> F[Exploration/Reporting (notebooks)]
    E --> F
```
#### Key Scripts
* scripts/pool.py, combos.py, backtest_pool.py: Strategic pool generation & historical coverage analysis
* scripts/backtest.py: ML modeling and feature analysis for prediction
* scripts/hybrid_backtest.py: Combines pool selection and ML probabilities to build/test hybrid strategies

#### Requirements
 1. Python 3.x
 2. pandas, numpy, scikit-learn
 3. Optional: Mermaid support in VS Code for flowcharts

#### Set up
 ##### Option 1: Using Conda
conda env create -f environment.yml
conda activate hit5-lottery-env

##### Option 2: Using PIP
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

#### Usage
1. Clean raw data:
python scripts/clean_data.py data/hit5_raw.txt

2. Generate pools/ combos:
python scripts/combos.py

3. Pool-based backtest:
python scripts/backtest_pool.py

4. Machine learning backtest:
python scripts/backtest.py

5. Hybrid pool + ML backtest:
python scripts/hybrid_backtest.py

6. Explore/visualize results:
Open Jupyter notebooks in notebooks/
