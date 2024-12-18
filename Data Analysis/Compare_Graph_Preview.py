import pandas as pd
import numpy.ma as ma
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import seaborn as sns

def create_average_day_comparison_plot(
    settlement, 
    intervention_type='MEB',
    period='Full',  # 'Full', 'Day', or 'Night'
    colors=None
):
    """
    Create comparison plot of temperatures for an average 24-hour day
    
    Parameters:
    -----------
    settlement : str
        Name of the settlement
    intervention_type : str
        Type of intervention (default: 'MEB')
    period : str
        Time period to plot ('Full', 'Day', or 'Night')
    colors : dict, optional
        Dictionary to customize plot colors
    """
    default_colors = {
        'control_range': '#E0E0E0',
        'intervention_range': '#ADD8E6',
        'control_mean': '#FF6961',
        'intervention_mean': '#6495ED',
        'control_box': '#D3D3D3',
        'intervention_box': '#87CEFA'
    }
    
    if colors is not None:
        default_colors.update(colors)
    
    # Load data
    master_df = pd.read_csv('master_dataframe.csv', parse_dates=['DateTime'])
    logger_flags_df = pd.read_csv('logger_flags.csv')
    
    # Get loggers
    control_loggers = logger_flags_df[
        (logger_flags_df['Settlement'] == settlement) & 
        (logger_flags_df['Intervention'] == 'CONTROL')
    ]['Loggers'].tolist()
    
    intervention_loggers = logger_flags_df[
        (logger_flags_df['Settlement'] == settlement) & 
        (logger_flags_df['Intervention'] == intervention_type)
    ]['Loggers'].tolist()
    
    intervention_start = pd.to_datetime(
        logger_flags_df[
            (logger_flags_df['Settlement'] == settlement) & 
            (logger_flags_df['Intervention'] == intervention_type)
        ]['Intervention_Start'].iloc[0]
    )
    
    # Process data
    master_df['DateTime'] = pd.to_datetime(master_df['DateTime'])
    post_intervention_df = master_df[master_df['DateTime'] >= intervention_start].copy()
    post_intervention_df['Hour'] = post_intervention_df['DateTime'].dt.hour
    
    # Define hours range based on period
    if period == 'Day':
        post_intervention_df = post_intervention_df[
            (post_intervention_df['Hour'] >= 6) & 
            (post_intervention_df['Hour'] < 19)
        ]
        hours_range = range(6, 19)
    elif period == 'Night':
        post_intervention_df = post_intervention_df[
            (post_intervention_df['Hour'] < 6) | 
            (post_intervention_df['Hour'] >= 19)
        ]
        evening_hours = list(range(19, 24))
        morning_hours = list(range(0, 6))
        hours_range = evening_hours + morning_hours
    else:  # Full day
        hours_range = range(24)
    
    def calculate_hourly_stats(loggers, df):
        hourly_stats = []
        
        for hour in hours_range:
            hour_data = df[df['Hour'] == hour][loggers]
            hour_data = hour_data.replace(0, np.nan)
            hour_data = hour_data.dropna(how='all')
            
            if not hour_data.empty:
                stats = {
                    'Hour': hour,
                    'plot_hour': hour if period != 'Night' else (hour if hour >= 19 else hour + 24),
                    'max': hour_data.max(axis=1).mean(),
                    'min': hour_data.min(axis=1).mean(),
                    'mean': hour_data.mean(axis=1).mean(),
                    'std': hour_data.mean(axis=1).std(),
                    'values': hour_data.mean(axis=1).values
                }
                hourly_stats.append(stats)
        
        return pd.DataFrame(hourly_stats)
    
    control_stats = calculate_hourly_stats(control_loggers, post_intervention_df)
    intervention_stats = calculate_hourly_stats(intervention_loggers, post_intervention_df)
    
    fig, ax = plt.subplots(figsize=(15, 10))
    
    # Plot ranges using plot_hour instead of Hour for night period
    x_values = control_stats['plot_hour'] if period == 'Night' else control_stats['Hour']
    
    control_range = ax.fill_between(x_values,
                                  control_stats['max'],
                                  control_stats['min'],
                                  alpha=0.3,
                                  color=default_colors['control_range'],
                                  label='Control Range')
    
    x_values = intervention_stats['plot_hour'] if period == 'Night' else intervention_stats['Hour']
    
    intervention_range = ax.fill_between(x_values,
                                       intervention_stats['max'],
                                       intervention_stats['min'],
                                       alpha=0.5,
                                       color=default_colors['intervention_range'],
                                       label='Intervention Range')
    
    # Plot mean lines
    x_values = control_stats['plot_hour'] if period == 'Night' else control_stats['Hour']
    control_mean, = ax.plot(x_values,
                          control_stats['mean'],
                          color=default_colors['control_mean'],
                          label='Control Mean',
                          linewidth=2)
    
    x_values = intervention_stats['plot_hour'] if period == 'Night' else intervention_stats['Hour']
    intervention_mean, = ax.plot(x_values,
                               intervention_stats['mean'],
                               color=default_colors['intervention_mean'],
                               label='Intervention Mean',
                               linewidth=2)
    
    # Create box plots
    control_boxes = []
    intervention_boxes = []
    
    for _, row in control_stats.iterrows():
        x_pos = row['plot_hour'] if period == 'Night' else row['Hour']
        control_box = ax.boxplot(row['values'],
                               positions=[x_pos],
                               widths=0.5,
                               patch_artist=True,
                               boxprops=dict(facecolor=default_colors['control_box'], color='gray'),
                               medianprops=dict(color=default_colors['control_mean']),
                               showfliers=False)
        control_boxes.append(control_box)
    
    for _, row in intervention_stats.iterrows():
        x_pos = row['plot_hour'] if period == 'Night' else row['Hour']
        intervention_box = ax.boxplot(row['values'],
                                    positions=[x_pos],
                                    widths=0.5,
                                    patch_artist=True,
                                    boxprops=dict(facecolor=default_colors['intervention_box'], color='blue'),
                                    medianprops=dict(color=default_colors['intervention_mean']),
                                    showfliers=False)
        intervention_boxes.append(intervention_box)
    
    # Create legend
    legend_elements = [
        (Patch(facecolor=default_colors['control_range'], alpha=0.3), [control_range], 'Control Range'),
        (Patch(facecolor=default_colors['intervention_range'], alpha=0.5), [intervention_range], 'Intervention Range'),
        (Patch(facecolor=default_colors['control_mean']), [control_mean], 'Control Mean'),
        (Patch(facecolor=default_colors['intervention_mean']), [intervention_mean], 'Intervention Mean'),
        (Patch(facecolor=default_colors['control_box'], alpha=1.0), 
         control_boxes, 
         'Control Hourly Distribution'),
        (Patch(facecolor=default_colors['intervention_box'], alpha=1.0), 
         intervention_boxes, 
         'Intervention Hourly Distribution')
    ]
    
    leg = ax.legend([item[0] for item in legend_elements],
                   [item[2] for item in legend_elements],
                   loc='upper right')
    
    # Interactive legend
    lined = {}
    for legpatch, elements, label in legend_elements:
        legline = leg.get_patches()[legend_elements.index((legpatch, elements, label))]
        if 'Distribution' in label:
            lined[legline] = elements
        else:
            lined[legline] = elements
    
    def on_pick(event):
        legline = event.artist
        if legline in lined:
            elements = lined[legline]
            
            if isinstance(elements[0], dict): 
                visible = not any(box['boxes'][0].get_visible() for box in elements)
                for box in elements:
                    for component in box.values():
                        for artist in component:
                            artist.set_visible(visible)
            else:
                visible = not elements[0].get_visible()
                for element in elements:
                    element.set_visible(visible)
            
            legline.set_alpha(1.0 if visible else 0.2)
            fig.canvas.draw()
    
    for legline in leg.get_patches():
        legline.set_picker(True)
    fig.canvas.mpl_connect('pick_event', on_pick)
    
    # Set labels and title
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Temperature (°C)')
    period_str = f" ({period}time)" if period != 'Full' else ""
    ax.set_title(f'Average Daily Temperature{period_str}: Control vs {intervention_type} in {settlement}')
    
    # Set x-axis ticks and limits based on period
    if period == 'Night':
        plot_hours = list(range(19, 24)) + list(range(24, 30))  # 19-23 and 24-29 (0-5)
        ax.set_xticks(plot_hours)
        hour_labels = [f'{h:02d}:00' if h < 24 else f'{h-24:02d}:00' for h in plot_hours]
        ax.set_xticklabels(hour_labels)
        ax.set_xlim(18.5, 29.5)
    elif period == 'Day':
        ax.set_xticks(list(hours_range))
        ax.set_xticklabels([f'{hour:02d}:00' for hour in hours_range])
        ax.set_xlim(5.5, 19.5)
    else:  # Full day
        ax.set_xticks(list(hours_range))
        ax.set_xticklabels([f'{hour:02d}:00' for hour in hours_range])
        ax.set_xlim(-0.5, 23.5)
    
    # Add grid
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

# Settings
settlements = ['Rainbow Field', 'Sports Complex']
intervention_types = ['MEB', 'RBF']
periods = ['Full', 'Day', 'Night']
custom_colors = {
    'control_range': '#E0E0E0',  # Light gray
    'intervention_range': '#ADD8E6',  # Light blue
    'control_mean': '#FF6961',  # Soft red
    'intervention_mean': '#6495ED',  # Cornflower blue
    'control_box': '#D3D3D3',  # Light gray
    'intervention_box': '#87CEFA'  # Light sky blue
}

# Generate all plots
for settlement in settlements:
    for intervention_type in intervention_types:
        for period in periods:
            create_average_day_comparison_plot(
                settlement, 
                intervention_type,
                period,
                colors=custom_colors
            )