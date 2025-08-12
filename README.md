## Cooling Interventions for Informal Settlements: A Study in Bihar, India

### Overview
This repository contains data, analysis code, and figures for a study evaluating low-cost passive cooling interventions for informal housing in Bihar, India. We study Radiant Barrier Foils (RBF) and Mylar Emergency Blankets (MEB) against controls using minute-level indoor temperatures from 42 loggers across two settlements. Using a difference-in-differences design with over 2.28 million 
temperature observations from 42 data loggers across two settlement locations, 
we find that both interventions provide significant cooling effects, with RBF 
reducing indoor temperatures by 1.1-1.2°C and MEB by 1.0-1.3°C relative to 
control structures.

### Quickstart
- Create and activate a virtual environment (Windows PowerShell):
  - `python -m venv .venv`
  - `.\.venv\Scripts\Activate.ps1`
- Install dependencies: `pip install -r requirements.txt`
- Open the notebooks in `Data Analysis/` to reproduce the analysis, or run the plotting scripts below to regenerate figures.
- Important: The plotting scripts expect the working directory to be `Data Analysis/`. See the commands below.

### Repository Structure (key items)
```
├── Data Analysis/
│   ├── data_analysis.ipynb              # Primary data processing and descriptive analysis
│   ├── did_analysis.ipynb               # Difference-in-differences models (main results)
│   ├── did_analysis (new|old).ipynb     # Updated and archival DID analyses
│   ├── Compare_Graph_Preview.py         # Average daily comparison plots
│   ├── graph.py                         # EDA: scatter/box plots, correlations, t-tests
│   ├── hexbin_plots.py                  # Temperature–humidity hexbin plots with WBGT guides
│   ├── master_dataframe.csv             # Minute-by-minute, analysis-ready panel
│   ├── did_df.csv                       # Processed dataset for DID models
│   ├── did_regression_results.txt       # Model outputs
│   ├── Extended_Data_Table_1.html       # Publication-ready table
│   ├── Cleaned Data/                    # Processed logger files per device
│   └── Loggers Data/                    # Raw logger exports
├── Environmental Data.csv               # Hourly weather data (joined in analysis)
├── download_weather.py                  # Weather.com scraper (optional; not required to reproduce)
└── requirements.txt                     # Python dependencies
```

### Experimental Setting
- **Location**: Informal settlements in Bihar, India
- **Study Period**: June 4 - August 6, 2024
- **Sample**: 42 households across two settlement clusters
  - Rainbow Field Settlement: 17 structures
  - Sports Complex Settlement: 25 structures

### Interventions
1. **Radiant Barrier Foils (RBF)**: Reflective aluminum foil barriers installed on roof structures
2. **Mylar Emergency Blankets (MEB)**: Reflective emergency blankets applied to roofing materials  
3. **Control**: No intervention

### Data Overview
- Logger network: 42 indoor temperature/humidity devices across two settlements (Rainbow Field, Sports Complex); 1-minute sampling.
- Intervention periods per device are specified in `Data Analysis/logger_flags.csv`:
  - Columns include `Loggers`, `Settlement`, `Intervention` (`RBF`, `MEB`, `CONTROL`), `Shaded` (boolean), `Intervention_Start`, `Post_Intervention_End`.
- `Data Analysis/temperature_differences.csv`:
  - Wide format with `DateTime` and one column per logger of indoor–outdoor temperature differences (°C).
- `Environmental Data.csv`:
  - Hourly weather time series joined to logger data in notebooks/scripts.

### Key Findings (from DID models)
| Model Specification | RBF Effect (°C) | MEB Effect (°C) | p-value |
|---------------------|-----------------|-----------------|---------|
| Basic DiD | -1.122*** | -1.122*** | <0.01 |
| Separate Technologies | -1.241*** | -0.972*** | <0.01 |
| + Environmental Controls | -0.861* | -0.683 | 0.078 |
| + Heterogeneous Effects | -1.109** | -1.298** | <0.05 |

Negative coefficients indicate cooling. Standard errors clustered at the logger level.

### Method Summary
We estimate difference-in-differences models comparing treated and control structures before and after intervention deployment, with settlement fixed effects, and time controls. Outcome is indoor–outdoor temperature (°C).

### Software Requirements
- Python 3.8+
- Dependencies in `requirements.txt` (includes `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `statsmodels`, `scikit-learn`, `requests`, `beautifulsoup4`, `jupyter`).

### Weather Scraper (optional)
`download_weather.py` scrapes current conditions from Weather.com at fixed intervals and appends to monthly CSVs (`weather_data_YYYYMM.csv`). It is not required to reproduce the paper figures and may break if the site layout changes.
- Run: `python download_weather.py`
- Stop with Ctrl+C. Logs are written to `weather_scraper.log` with rotation.

### Ethical Considerations
- Community consent obtained; identifiers anonymized; materials left with participants.

### License
MIT License. See `LICENSE`.

### Effectiveness
- **Significant cooling benefits**: 1-1.3°C temperature reduction
- **Easy implementation**: Suitable for community-led deployment

Keywords: informal settlements, passive cooling, difference-in-differences, urban heat, Bihar, India
