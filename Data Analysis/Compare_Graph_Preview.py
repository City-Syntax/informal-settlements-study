import pandas as pd
import numpy.ma as ma
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import seaborn as sns

def create_average_day_comparison_plot(
    settlement, 
    intervention_type='MEB',
    period='Full',
    shaded=True,
    colors=None
):
    """
    Create comparison plot of temperature differences for an average 24-hour day
    
    Parameters:
    -----------
    settlement : str
        Name of the settlement
    intervention_type : str
        Type of intervention (default: 'MEB')
    period : str
        Time period to plot ('Full', 'Day', or 'Night')
    shaded : bool
        Whether to analyze shaded (True) or unshaded (False) structures
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
    temp_diff_df = pd.read_csv('temperature_differences.csv', parse_dates=['DateTime'])
    logger_flags_df = pd.read_csv('logger_flags.csv')
    temp_diff_df['DateTime'] = pd.to_datetime(temp_diff_df['DateTime'])

    # Get loggers with shading condition
    control_loggers = logger_flags_df[
        (logger_flags_df['Settlement'] == settlement) & 
        (logger_flags_df['Intervention'] == 'CONTROL') &
        (logger_flags_df['Shaded'] == shaded)
    ]['Loggers'].tolist()
    
    intervention_loggers = logger_flags_df[
        (logger_flags_df['Settlement'] == settlement) & 
        (logger_flags_df['Intervention'] == intervention_type) &
        (logger_flags_df['Shaded'] == shaded)
    ]['Loggers'].tolist()

    # Get intervention start and end dates
    intervention_start = pd.to_datetime(
        logger_flags_df[
            (logger_flags_df['Settlement'] == settlement) & 
            (logger_flags_df['Intervention'] == intervention_type)
        ]['Intervention_Start'].iloc[0]
    )
    
    intervention_end = pd.to_datetime(
        logger_flags_df[
            (logger_flags_df['Settlement'] == settlement) & 
            (logger_flags_df['Intervention'] == intervention_type)
        ]['Post_Intervention_End'].iloc[0]
    )

    # Filter loggers based on data availability during intervention period
    def filter_active_loggers(loggers, df_pre, df_post):
        active_loggers = []
        for logger in loggers:
            # Check both pre and post intervention periods
            pre_data = df_pre[logger] if logger in df_pre.columns else pd.Series()
            post_data = df_post[logger] if logger in df_post.columns else pd.Series()
            
            if (not pre_data.empty and not pre_data.isna().all()) or \
               (not post_data.empty and not post_data.isna().all()):
                active_loggers.append(logger)
            else:
                print(f"Warning: Logger {logger} has no valid data")
        return active_loggers

    # Filter post-intervention data and active loggers
    pre_intervention_df = temp_diff_df[temp_diff_df['DateTime'] < intervention_start].copy()
    post_intervention_df = temp_diff_df[
        (temp_diff_df['DateTime'] >= intervention_start) & 
        (temp_diff_df['DateTime'] <= intervention_end)
    ].copy()

    active_control_loggers = filter_active_loggers(
        control_loggers, 
        pre_intervention_df,
        post_intervention_df
    )
    
    active_intervention_loggers = filter_active_loggers(
        intervention_loggers,
        pre_intervention_df,
        post_intervention_df
    )

    # Process hour information
    pre_intervention_df['Hour'] = pre_intervention_df['DateTime'].dt.hour
    post_intervention_df['Hour'] = post_intervention_df['DateTime'].dt.hour

    print(f"\nAnalyzing {settlement} - {intervention_type} - {'Shaded' if shaded else 'Unshaded'} - {period}")
    print(f"Active control loggers: {active_control_loggers}")
    print(f"Active intervention loggers: {active_intervention_loggers}")

    # Check if we have enough active loggers for comparison
    if not active_control_loggers or not active_intervention_loggers:
        print(f"Insufficient active loggers for {settlement} - {intervention_type} - "
              f"{'Shaded' if shaded else 'Unshaded'} - {period}")
        return

    # Filter by period
    if period == 'Day':
        pre_intervention_df = pre_intervention_df[
            (pre_intervention_df['Hour'] >= 6) & 
            (pre_intervention_df['Hour'] < 19)
        ]
        post_intervention_df = post_intervention_df[
            (post_intervention_df['Hour'] >= 6) & 
            (post_intervention_df['Hour'] < 19)
        ]
        hours_range = range(6, 19)
    elif period == 'Night':
        pre_intervention_df = pre_intervention_df[
            (pre_intervention_df['Hour'] < 6) | 
            (pre_intervention_df['Hour'] >= 19)
        ]
        post_intervention_df = post_intervention_df[
            (post_intervention_df['Hour'] < 6) | 
            (post_intervention_df['Hour'] >= 19)
        ]
        hours_range = list(range(19, 24)) + list(range(0, 6))
    else:  # Full day
        hours_range = range(24)

    # Combine control data
    all_control_data = []
    
    # Add control logger data
    if active_control_loggers:
        control_data_pre = pre_intervention_df[active_control_loggers]
        control_data_post = post_intervention_df[active_control_loggers]
        all_control_data.extend([control_data_pre, control_data_post])

    # Add pre-intervention data from intervention loggers
    if active_intervention_loggers:
        intervention_pre_data = pre_intervention_df[active_intervention_loggers]
        all_control_data.append(intervention_pre_data)

    # Combine all control data
    combined_control_df = pd.concat(all_control_data) if all_control_data else pd.DataFrame()
    
    # Get post-intervention data for intervention loggers
    intervention_post_df = post_intervention_df[active_intervention_loggers]

    def calculate_hourly_stats(loggers, df):
        """
        Modified function to handle single logger cases by creating an artificial range
        """
        hourly_stats = []
        
        if not loggers:
            print("No loggers provided for analysis")
            return pd.DataFrame()

        print(f"Processing {len(loggers)} loggers: {loggers}")
        
        for hour in hours_range:
            hour_data = df[df['Hour'] == hour][loggers]
            hour_data = hour_data.replace(0, np.nan)
            hour_data = hour_data.dropna(how='all')
            
            if not hour_data.empty:
                try:
                    if len(loggers) == 1:
                        # For single logger, calculate mean and create artificial range
                        mean_val = hour_data.mean(axis=1).mean()
                        std_val = hour_data.mean(axis=1).std()
                        
                        # Create range as mean ± standard deviation
                        # If std is too small or nan, use a minimum range
                        if pd.isna(std_val) or std_val < 0.1:
                            range_margin = abs(mean_val) * 0.1 if mean_val != 0 else 0.1
                        else:
                            range_margin = std_val
                        
                        max_val = mean_val + range_margin
                        min_val = mean_val - range_margin
                    else:
                        max_val = hour_data.max(axis=1).mean()
                        min_val = hour_data.min(axis=1).mean()
                        mean_val = hour_data.mean(axis=1).mean()
                        std_val = hour_data.mean(axis=1).std()

                    if pd.isna([max_val, min_val, mean_val]).any():
                        print(f"Warning: NaN values found for hour {hour}")
                        continue
                        
                    stats = {
                        'Hour': hour,
                        'max': max_val,
                        'min': min_val,
                        'mean': mean_val,
                        'std': std_val if not pd.isna(std_val) else 0,
                        'values': hour_data.mean(axis=1).values
                    }
                    hourly_stats.append(stats)
                except Exception as e:
                    print(f"Error processing hour {hour}: {str(e)}")
                    continue
        
        if not hourly_stats:
            print("No valid statistics could be calculated")
            return pd.DataFrame()
            
        return pd.DataFrame(hourly_stats)

    control_stats = calculate_hourly_stats(
        active_control_loggers + active_intervention_loggers, 
        combined_control_df
    )
    
    intervention_stats = calculate_hourly_stats(
        active_intervention_loggers,
        intervention_post_df
    )

    if control_stats.empty or intervention_stats.empty:
        print("No valid statistics available for plotting")
        return

    print("\nControl Statistics Summary:")
    print(control_stats[['Hour', 'max', 'min', 'mean']].describe())
    print("\nIntervention Statistics Summary:")
    print(intervention_stats[['Hour', 'max', 'min', 'mean']].describe())

    fig, ax = plt.subplots(figsize=(15, 10))

    x_values = control_stats['plot_hour'] if period == 'Night' else control_stats['Hour']

    try:
        if not control_stats.empty and not np.isnan(control_stats['max']).all():
            control_range = ax.fill_between(control_stats['Hour'],
                                          control_stats['max'],
                                          control_stats['min'],
                                          alpha=0.3,
                                          color=default_colors['control_range'],
                                          label='Control Range')
        else:
            print("Warning: Invalid control range data")

        x_values = intervention_stats['plot_hour'] if period == 'Night' else intervention_stats['Hour']

        if not intervention_stats.empty and not np.isnan(intervention_stats['max']).all():
            intervention_range = ax.fill_between(intervention_stats['Hour'],
                                               intervention_stats['max'],
                                               intervention_stats['min'],
                                               alpha=0.5,
                                               color=default_colors['intervention_range'],
                                               label='Intervention Range')
        else:
            print("Warning: Invalid intervention range data")

    except Exception as e:
        print(f"Error during plotting: {str(e)}")
        return

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

    ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
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

    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Temperature Difference (°C)')
    shading_str = "Shaded" if shaded else "Unshaded"
    period_str = f" ({period}time)" if period != 'Full' else ""
    ax.set_title(f'Average Daily Temperature Difference{period_str}: {shading_str} Control vs {intervention_type} in {settlement}')

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
periods = ['Full']
shading_conditions = [True, False]

custom_colors = {
    'control_range': '#E0E0E0',
    'intervention_range': '#ADD8E6',
    'control_mean': '#FF6961',
    'intervention_mean': '#6495ED',
    'control_box': '#D3D3D3',
    'intervention_box': '#87CEFA'
}

for settlement in settlements:
    for intervention_type in intervention_types:
        for period in periods:
            for shaded in shading_conditions:
                try:
                    create_average_day_comparison_plot(
                        settlement, 
                        intervention_type,
                        period,
                        shaded,
                        colors=custom_colors
                    )
                except Exception as e:
                    print(f"Error creating plot for {settlement} - {intervention_type} - "
                          f"{'Shaded' if shaded else 'Unshaded'} - {period}: {str(e)}")