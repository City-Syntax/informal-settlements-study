import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import LabelEncoder

# Load the data
temp_diff_df = pd.read_csv('temperature_differences.csv', parse_dates=['DateTime'])
logger_flags_df = pd.read_csv('logger_flags.csv')
env_data_df = pd.read_csv('Environmental Data.csv', parse_dates=[['Date', 'Time']])

# Merge the dataframes
merged_df = temp_diff_df.melt(id_vars=['DateTime'], var_name='Logger', value_name='TempDifference')
merged_df = merged_df.merge(logger_flags_df, left_on='Logger', right_on='Loggers')
merged_df = merged_df.merge(env_data_df, left_on='DateTime', right_on='Date_Time', how='left')

# Create a 'Time of Day' column
merged_df['TimeOfDay'] = pd.cut(merged_df['DateTime'].dt.hour, 
                                bins=[-1, 5, 11, 17, 23],
                                labels=['Night', 'Morning', 'Afternoon', 'Evening'])

# Label encode categorical variables
le = LabelEncoder()
merged_df['Settlement_encoded'] = le.fit_transform(merged_df['Settlement'])
merged_df['Intervention_encoded'] = le.fit_transform(merged_df['Intervention'])
merged_df['Shaded_encoded'] = le.fit_transform(merged_df['Shaded'])
merged_df['TimeOfDay_encoded'] = le.fit_transform(merged_df['TimeOfDay'])

# Calculate days since intervention start
merged_df['DaysSinceIntervention'] = (merged_df['DateTime'] - pd.to_datetime(merged_df['Intervention_Start'])).dt.days

# Function to create scatter plots
def plot_scatter(x, y, hue, data, title):
    plt.figure(figsize=(12, 8))
    sns.scatterplot(x=x, y=y, hue=hue, data=data, alpha=0.5)
    plt.title(title)
    plt.show()

# Function to create box plots
def plot_box(x, y, data, title):
    plt.figure(figsize=(12, 8))
    sns.boxplot(x=x, y=y, data=data)
    plt.title(title)
    plt.xticks(rotation=45)
    plt.show()

# Scatter plots
plot_scatter('temp', 'TempDifference', 'Intervention', merged_df, 'Temperature Difference vs Environmental Temperature')
plot_scatter('humidity', 'TempDifference', 'Intervention', merged_df, 'Temperature Difference vs Humidity')
plot_scatter('windspeed', 'TempDifference', 'Intervention', merged_df, 'Temperature Difference vs Wind Speed')
plot_scatter('DaysSinceIntervention', 'TempDifference', 'Intervention', merged_df, 'Temperature Difference vs Days Since Intervention')

# Box plots
plot_box('Intervention', 'TempDifference', merged_df, 'Temperature Difference by Intervention Type')
plot_box('Settlement', 'TempDifference', merged_df, 'Temperature Difference by Settlement')
plot_box('Shaded', 'TempDifference', merged_df, 'Temperature Difference by Shading Condition')
plot_box('TimeOfDay', 'TempDifference', merged_df, 'Temperature Difference by Time of Day')

# Correlation analysis
correlation_vars = ['TempDifference', 'temp', 'humidity', 'windspeed', 'DaysSinceIntervention', 
                    'Settlement_encoded', 'Intervention_encoded', 'Shaded_encoded', 'TimeOfDay_encoded']
correlation_matrix = merged_df[correlation_vars].corr()

plt.figure(figsize=(12, 10))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0)
plt.title('Correlation Matrix of Variables')
plt.show()

# Print summary statistics
print(merged_df.groupby('Intervention')['TempDifference'].describe())
print(merged_df.groupby('Settlement')['TempDifference'].describe())
print(merged_df.groupby('Shaded')['TempDifference'].describe())
print(merged_df.groupby('TimeOfDay')['TempDifference'].describe())

# Perform t-tests
def perform_ttest(group1, group2):
    t_stat, p_value = stats.ttest_ind(group1, group2)
    print(f"T-statistic: {t_stat}, p-value: {p_value}")

print("T-test for RBF vs Control:")
perform_ttest(merged_df[merged_df['Intervention'] == 'RBF']['TempDifference'],
              merged_df[merged_df['Intervention'] == 'CONTROL']['TempDifference'])

print("T-test for MEB vs Control:")
perform_ttest(merged_df[merged_df['Intervention'] == 'MEB']['TempDifference'],
              merged_df[merged_df['Intervention'] == 'CONTROL']['TempDifference'])

print("T-test for Shaded vs Unshaded:")
perform_ttest(merged_df[merged_df['Shaded'] == True]['TempDifference'],
              merged_df[merged_df['Shaded'] == False]['TempDifference'])