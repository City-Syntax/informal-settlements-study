import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

master_df = pd.read_csv('master_dataframe.csv', parse_dates=['DateTime'])

long_df = pd.melt(master_df, id_vars=['DateTime'], var_name='Logger', value_name='Temperature')

long_df['Temperature'].fillna(0, inplace=True)

long_df['Logger_numeric'] = pd.factorize(long_df['Logger'])[0]

long_df['DateTime_numeric'] = long_df['DateTime'].apply(lambda x: x.toordinal())

X = long_df['DateTime_numeric']
Y = long_df['Logger_numeric']
Z = long_df['Temperature']

fig = plt.figure(figsize=(16, 10))
ax = fig.add_subplot(111, projection='3d')

scatter = ax.scatter(X, Y, Z, c=Z, cmap='viridis')

ax.set_xlabel('Time (Ordinal)')
ax.set_ylabel('Logger ID (Numeric)')
ax.set_zlabel('Temperature (°C)')
ax.set_title('3D Plot of Temperatures from All Loggers Over Time')

cbar = fig.colorbar(scatter, ax=ax, orientation='vertical')
cbar.set_label('Temperature (°C)')

ax.view_init(elev=30, azim=120)

plt.show()