import pandas as pd
import numpy.ma as ma
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import seaborn as sns

def create_hourly_comparison_plot(settlement, intervention_type='MEB', hour_distribution=2):
    """
    Create comparison plot with configurable hour distribution for box plots
    
    Parameters:
    -----------
    settlement : str
        Name of the settlement
    intervention_type : str
        Type of intervention (default: 'MEB')
    hour_distribution : int
        Number of hours to group for each box plot (default: 2)
        Examples: 2 for 2-hour distribution, 6 for 6-hour, 24 for daily
    """
    
    master_df = pd.read_csv('master_dataframe.csv', parse_dates=['DateTime'])
    logger_flags_df = pd.read_csv('logger_flags.csv')

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

    master_df['DateTime'] = pd.to_datetime(master_df['DateTime'])
    post_intervention_df = master_df[master_df['DateTime'] >= intervention_start].copy()
    post_intervention_df['Hours_After_Intervention'] = (
        post_intervention_df['DateTime'] - intervention_start
    ).dt.total_seconds() / 3600

    def calculate_hourly_stats(loggers, df):
        hourly_stats = pd.DataFrame()
        logger_data = df[loggers]
        hourly_stats['max'] = logger_data.max(axis=1)
        hourly_stats['min'] = logger_data.min(axis=1)
        hourly_stats['mean'] = logger_data.mean(axis=1)
        hourly_stats['std'] = logger_data.std(axis=1)
        hourly_stats['Hours_After_Intervention'] = df['Hours_After_Intervention']
        return hourly_stats

    control_stats = calculate_hourly_stats(control_loggers, post_intervention_df)
    intervention_stats = calculate_hourly_stats(intervention_loggers, post_intervention_df)

    fig, ax = plt.subplots(figsize=(15, 10))

    control_range = ax.fill_between(control_stats['Hours_After_Intervention'],
                                  control_stats['max'],
                                  control_stats['min'],
                                  alpha=0.3,
                                  color='lightgray',
                                  label='Control Range')

    intervention_range = ax.fill_between(intervention_stats['Hours_After_Intervention'],
                                       intervention_stats['max'],
                                       intervention_stats['min'],
                                       alpha=0.5,
                                       color='lightblue',
                                       label='Intervention Range')

    control_mean, = ax.plot(control_stats['Hours_After_Intervention'],
                          control_stats['mean'],
                          color='red',
                          label='Control Mean',
                          linewidth=2)
    
    intervention_mean, = ax.plot(intervention_stats['Hours_After_Intervention'],
                               intervention_stats['mean'],
                               color='blue',
                               label='Intervention Mean',
                               linewidth=2)

    control_boxes = []
    intervention_boxes = []

    box_width = hour_distribution * 0.8
    max_hours = max(control_stats['Hours_After_Intervention'])
    
    for hour in np.arange(0, max_hours, hour_distribution):
        control_period = control_stats[
            (control_stats['Hours_After_Intervention'] >= hour) & 
            (control_stats['Hours_After_Intervention'] < hour + hour_distribution)
        ]
        intervention_period = intervention_stats[
            (intervention_stats['Hours_After_Intervention'] >= hour) & 
            (intervention_stats['Hours_After_Intervention'] < hour + hour_distribution)
        ]

        if len(control_period) > 0:
            control_box = ax.boxplot(control_period['mean'],
                                   positions=[hour + hour_distribution/2],
                                   widths=box_width,
                                   patch_artist=True,
                                   boxprops=dict(facecolor='lightgray', color='gray'),
                                   medianprops=dict(color='red'),
                                   showfliers=False)
            control_boxes.append(control_box)
            
        if len(intervention_period) > 0:
            intervention_box = ax.boxplot(intervention_period['mean'],
                                        positions=[hour + hour_distribution/2],
                                        widths=box_width,
                                        patch_artist=True,
                                        boxprops=dict(facecolor='lightblue', color='blue'),
                                        medianprops=dict(color='blue'),
                                        showfliers=False)
            intervention_boxes.append(intervention_box)

    distribution_label = f'{hour_distribution}-Hour Distribution'
    legend_elements = [
        (Patch(facecolor='lightgray', alpha=0.3), [control_range], 'Control Range'),
        (Patch(facecolor='lightblue', alpha=0.5), [intervention_range], 'Intervention Range'),
        (Patch(facecolor='red'), [control_mean], 'Control Mean'),
        (Patch(facecolor='blue'), [intervention_mean], 'Intervention Mean'),
        (Patch(facecolor='lightgray', alpha=1.0), 
         control_boxes, 
         f'Control {distribution_label}'),
        (Patch(facecolor='lightblue', alpha=1.0), 
         intervention_boxes, 
         f'Intervention {distribution_label}')
    ]

    leg = ax.legend([item[0] for item in legend_elements],
                   [item[2] for item in legend_elements],
                   loc='upper right')

    lined = {}
    for legpatch, elements, label in legend_elements:
        legline = leg.get_patches()[legend_elements.index((legpatch, elements, label))]
        if distribution_label in label:
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

    ax.set_xlabel('Hours After Intervention')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title(f'Temperature Comparison: Control vs {intervention_type} in {settlement}\n')

    # Set x-axis ticks
    xticks = np.arange(0, max_hours, 24)
    ax.set_xticks(xticks)
    ax.set_xticklabels([f'Day {int(x/24)}' for x in xticks])
    
    # Add minor ticks
    minor_xticks = np.arange(0, max_hours, hour_distribution)
    ax.set_xticks(minor_xticks, minor=True)

    ax.grid(True, alpha=0.3)
    ax.grid(True, which='minor', alpha=0.1)
    plt.tight_layout()
    plt.show()

settlements = ['Rainbow Field', 'Sports Complex']
intervention_types = ['MEB', 'RBF']

# Change this value to adjust hour distribution like 2, 6, 24, etc.
hour_distribution = 24 

for settlement in settlements:
    for intervention_type in intervention_types:
        create_hourly_comparison_plot(settlement, intervention_type, hour_distribution)