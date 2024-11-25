import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

def create_hexbin_plot(data, title):
    """Create a single hexbin plot with WBGT lines and dynamic scaling"""
    
    plt.figure(figsize=(16, 16))
    
    ax = plt.axes([0.1, 0.1, 0.75, 0.85])
    
    temp_min = max(20, np.percentile(data['Temperature'], 0.1))
    temp_max = np.percentile(data['Temperature'], 99.9)
    
    nx = 40  # number of hexagons in x direction
    ny = 20  # significantly reduced number of hexagons in y direction
    
    hb = ax.hexbin(data['Temperature'], 
                   data['Humidity'],
                   gridsize=(nx, ny),  # separate x and y bin counts
                   bins='log',
                   cmap='YlOrRd',
                   mincnt=5,
                   reduce_C_function=np.sum,
                   extent=[temp_min, temp_max, 40, 100])
    
    ax.set_box_aspect(ny/nx)
    
    temp_points = np.linspace(temp_min, temp_max, 100)
    wbgt_values = [20, 23, 25, 28, 30, 33]
    
    for wbgt in wbgt_values:
        rh_values = []
        for t in temp_points:
            rh = (wbgt - 0.7 * t) / (0.3 * t) * 100
            rh_values.append(rh)
        ax.plot(temp_points, rh_values, 'k-', alpha=0.5, linewidth=1)
        if rh_values[-1] >= 40 and rh_values[-1] <= 100:
            ax.text(temp_max + 0.2, rh_values[-1], f'{wbgt}', fontsize=8)

    cbar_ax = plt.axes([0.87, 0.1, 0.03, 0.85])
    cbar = plt.colorbar(hb, cax=cbar_ax)
    cbar.set_label('Number of records')

    ax.set_xlabel('Temperature (°C)')
    ax.set_ylabel('Relative Humidity (%)')
    ax.set_title(title, pad=20)
    
    temp_max_rounded = np.ceil(temp_max)
    temp_min_rounded = np.floor(temp_min)
    ax.set_xlim(temp_min_rounded, temp_max_rounded)
    ax.set_ylim(40, 100)
    
    ax.text(temp_min - 1, 98, 'WBGT (°C)', fontsize=10)
    
    print(f"{title} - Temperature range: {temp_min:.1f}°C to {temp_max:.1f}°C")
    print(f"Number of records: {len(data['Temperature'])}")
    
    return plt.gcf()

def process_data_and_create_plots():
    master_df = pd.read_csv('master_dataframe.csv', parse_dates=['DateTime'])
    logger_flags_df = pd.read_csv('logger_flags.csv')
    
    settlements = ['Rainbow Field', 'Sports Complex']
    interventions = ['MEB', 'RBF', 'Control']
    
    plot_data = {}
    all_temp = []
    all_humidity = []
    
    for settlement in settlements:
        for intervention in interventions:
            key = f'{settlement} - {intervention}'
            plot_data[key] = {'temp': [], 'humidity': []}
    
    for _, logger_info in logger_flags_df.iterrows():
        logger = logger_info['Loggers']
        settlement = logger_info['Settlement']
        intervention = logger_info['Intervention']
        
        if intervention == 'CONTROL':
            intervention = 'Control'
        
        try:
            logger_data = pd.read_csv(f'Cleaned Data/{logger}_data.csv')
            
            if logger.startswith('U'):
                temp_col = 'Temperature_Celsius(℃)'
                humid_col = 'Relative_Humidity(%)'
            else:
                temp_col = 'Temperature(C)'
                humid_col = 'Humidity(%RH)'
            
            valid_temp = (logger_data[temp_col] >= 20)
            valid_humid = (logger_data[humid_col] >= 0) & (logger_data[humid_col] <= 100)
            valid_data = valid_temp & valid_humid
            
            temp_data = logger_data.loc[valid_data, temp_col].values
            humid_data = logger_data.loc[valid_data, humid_col].values
            
            all_temp.extend(temp_data)
            all_humidity.extend(humid_data)
            
            category = f'{settlement} - {intervention}'
            plot_data[category]['temp'].extend(temp_data)
            plot_data[category]['humidity'].extend(humid_data)
            
        except FileNotFoundError:
            print(f"Data file not found for logger {logger}")

    plt.ion()
    
    all_data = pd.DataFrame({
        'Temperature': all_temp,
        'Humidity': all_humidity
    })
    fig_all = create_hexbin_plot(all_data, 'All Records')
    plt.show()
    
    for category in plot_data.keys():
        if len(plot_data[category]['temp']) > 0:
            data = pd.DataFrame({
                'Temperature': plot_data[category]['temp'],
                'Humidity': plot_data[category]['humidity']
            })
            fig = create_hexbin_plot(data, category)
            plt.show()

    return plot_data

plot_data = process_data_and_create_plots()

plt.ioff()
plt.show()