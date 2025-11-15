
# Hit 5 Lottery Analysis

## A modular pipeline for cleaning, analyzing, simulating, and modeling 5-number lottery draws
### Project Overview

#### This repository provides Python scripts and Jupyter notebooks for:

1. Cleaning and preparing raw lottery draw data

2. Generating strategic combination candidates (using hot/warm/cold frequency analysis)

3. Running simulations and backtests to evaluate combo strategies

4. Applying machine learning for draw prediction and feature analysis

#### Folder Structure
project_root/
│
├── data/          # Raw, cleaned, and output data files
├── scripts/       # Python scripts for processing, analysis, and simulation
├── notebooks/     # Jupyter notebooks for exploration and reporting
├── README.md      # Project overview and workflow (this file)

#### Workflow Chart
flowchart TD
    A[Raw Data (.txt/.html/.csv)] --> B[Cleaning Scripts (clean_data.py, robust_clean.py, dedup.py)]
    B --> C[Cleaned Data (.csv)]
    C --> D[Analysis & Combo Gen (lottery_main.py, pool.py)]
    D --> E[Simulation/Backtest (backtest.py, final_pool.py)]
    D --> F[Exploration/Reporting (notebooks)]

#### Usage
1. Clean raw data:
python scripts/clean_data.py data/hit5_raw.txt

2. Generate combos and analyze:
python scripts/clean_data.py data/hit5_raw.txt

3. Simulate combos versus history:
python scripts/backtest.py

4. Explore/visualize results:
Open Jupyter notebooks in notebooks/

 #### Requirements
 1. Python 3.x
 2. pandas, numpy, scikit-learn
