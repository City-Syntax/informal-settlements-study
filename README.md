# Low Cost Interventions for Informal Settlements - A Study in Bihar, India

## Abstract

This repository contains the complete dataset, analysis code, and supplementary materials evaluating the effectiveness of low-cost cooling interventions in informal settlements in Bihar, India. We examine two passive cooling technologies: Radiant Barrier Foils (RBF) and Mylar Emergency Blankets (MEB) applied to informal housing structures constructed from scrap materials. Using a difference-in-differences design with over 2.28 million temperature observations from 42 data loggers across two settlement locations, we find that both interventions provide significant cooling effects, with RBF reducing indoor temperatures by 1.1-1.2°C and MEB by 1.0-1.3°C relative to control structures.

## Repository Structure

```
├── Data Analysis/
│   ├── data_analysis.ipynb              # Primary data processing and analysis
│   ├── did_analysis.ipynb               # Difference-in-differences models
│   ├── did_analysis (new).ipynb         # Updated DID analysis
│   ├── did_analysis (old).ipynb         # Previous version for reference
│   ├── master_dataframe.csv             # Consolidated minute-by-minute data
│   ├── did_df.csv                       # Processed data for DID analysis
│   ├── did_regression_results.txt       # Statistical model outputs
│   ├── Extended_Data_Table_1.html       # Publication-ready results table
│   ├── Cleaned Data/                    # Processed logger data files
│   ├── Loggers Data/                    # Raw temperature logger data
│   └── [Additional analysis files and visualizations]
├── Environmental Data.csv               # Hourly weather station data
└── download_weather.py                  # Weather data collection script
```

## Study Design

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

### Randomization and Treatment Assignment
- **Stratified randomization** by settlement location and shade status
- **Treatment groups**:
  - RBF: 17 structures (9 shaded, 8 unshaded)
  - MEB: 12 structures (7 shaded, 5 unshaded)
  - Control: 13 structures (7 shaded, 6 unshaded)

### Data Collection
- **High-frequency temperature monitoring**: Minute-by-minute recordings using U-series and R-series data loggers
- **Environmental controls**: Hourly weather station data with minute-level interpolation
- **Baseline period**: 15 days pre-intervention
- **Treatment period**: Implementation on July 15-20, 2024
- **Follow-up period**: 2-3 weeks post-intervention

## Key Findings

### Primary Results (Difference-in-Differences Analysis)

| Model Specification | RBF Effect (°C) | MEB Effect (°C) | p-value |
|---------------------|-----------------|-----------------|---------|
| Basic DiD | -1.122*** | -1.122*** | <0.01 |
| Separate Technologies | -1.241*** | -0.972*** | <0.01 |
| + Environmental Controls | -0.861* | -0.683 | 0.078 |
| + Heterogeneous Effects | -1.109** | -1.298** | <0.05 |

**Note**: Negative coefficients indicate cooling effects. Standard errors clustered at logger level.

### Heterogeneous Treatment Effects
- **Shade interactions**: Both interventions show enhanced effectiveness (reduced cooling) in shaded structures
- **Time-of-day effects**: Cooling benefits most pronounced during daytime hours
- **Settlement differences**: Sports Complex settlement shows different baseline temperature patterns

### Robustness
- Results robust across multiple model specifications
- Large sample size (N = 2,279,880 observations)
- Controls for environmental variation, settlement fixed effects, and time trends

## Methodology

### Statistical Approach
We employ a difference-in-differences design comparing treated and control structures before and after intervention implementation:

```
Y_it = α + β₁(Post_t) + β₂(Treatment_i) + β₃(Post_t × Treatment_i) + X_it'γ + ε_it
```

Where:
- `Y_it` = Temperature difference (indoor - outdoor) for structure i at time t
- `Post_t` = Indicator for post-intervention period
- `Treatment_i` = Indicator for treatment assignment
- `X_it` = Environmental and structural controls

### Key Variables
- **Outcome**: Indoor temperature minus outdoor temperature (°C)
- **Treatment**: RBF vs. MEB vs. Control
- **Controls**: Settlement location, shade status, time of day, weather conditions

## Data Description

### Logger Network
- **42 temperature/humidity loggers** deployed across structures
- **U-series loggers**: Higher precision sensors (29 units)
- **R-series loggers**: Standard temperature sensors (13 units)
- **Sampling frequency**: 1-minute intervals
- **Data quality**: Missing data handling and outlier detection implemented

### Environmental Data
- **Weather station**: Kankarbagh, Patna (nearest available)
- **Variables**: Temperature, humidity, wind speed, solar radiation, precipitation
- **Temporal resolution**: Hourly observations with minute-level interpolation

## Reproducibility

### Software Requirements
- Python 3.8+
- Required packages: `pandas`, `numpy`, `matplotlib`, `seaborn`, `statsmodels`, `scipy`
- Jupyter Notebook environment

### Key Analysis Files
1. **`data_analysis.ipynb`**: Data preprocessing, cleaning, and descriptive analysis
2. **`did_analysis.ipynb`**: Main difference-in-differences estimation
3. **`master_dataframe.csv`**: Analysis-ready dataset

### Replication Instructions
1. Clone this repository
2. Install required Python packages: `pip install -r requirements.txt`
3. Run notebooks in the following order:
   - `data_analysis.ipynb` (data preprocessing)
   - `did_analysis.ipynb` (main analysis)

## Policy Implications

### Cost-Effectiveness
- **Low-cost interventions**: Materials cost <$10 USD per structure
- **Significant cooling benefits**: 1-1.3°C temperature reduction
- **Easy implementation**: Suitable for community-led deployment

### Scalability
- Applicable to similar informal settlement contexts
- Minimal technical expertise required for installation
- Potential for integration with existing housing improvement programs

## Ethical Considerations

- **Community consent**: Obtained from all participating households
- **Participant welfare**: No adverse effects documented
- **Data privacy**: All location and household identifiers anonymized
- **Benefit sharing**: Intervention materials left with participating households


## Data Availability

All data and code are made available under the MIT License. The complete dataset includes:
- Raw temperature logger data (`/Data Analysis/Loggers Data/`)
- Processed analysis datasets (`master_dataframe.csv`, `did_df.csv`)
- Environmental data (`Environmental Data.csv`)
- Complete analysis code (Jupyter notebooks)

## Contact

For questions about the data or methodology, please contact:
- **Corresponding Author**: Yu Qian Ang
- **Data Inquiries**: yuqian@nus.edu.sg
- **GitHub Issues**: Use the Issues tab for technical questions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Keywords**: Informal settlements, passive cooling, climate adaptation, randomized controlled trial, difference-in-differences, urban heat, housing interventions, Bihar, India 
