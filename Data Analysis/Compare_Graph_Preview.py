import pandas as pd
import numpy.ma as ma
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import seaborn as sns

def create_hourly_comparison_plot(settlement, intervention_type='MEB'):
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

    box_width = 12
    for day in range(int(max(control_stats['Hours_After_Intervention']) / 24)):
        hour = day * 24
        
        control_day = control_stats[
            (control_stats['Hours_After_Intervention'] >= hour) & 
            (control_stats['Hours_After_Intervention'] < hour + 24)
        ]
        intervention_day = intervention_stats[
            (intervention_stats['Hours_After_Intervention'] >= hour) & 
            (intervention_stats['Hours_After_Intervention'] < hour + 24)
        ]

        if len(control_day) > 0:
            control_box = ax.boxplot(control_day['mean'],
                                   positions=[hour + 12],
                                   widths=box_width,
                                   patch_artist=True,
                                   boxprops=dict(facecolor='lightgray', color='gray'),
                                   medianprops=dict(color='red'),
                                   showfliers=False)
            control_boxes.append(control_box)
            
        if len(intervention_day) > 0:
            intervention_box = ax.boxplot(intervention_day['mean'],
                                        positions=[hour + 12],
                                        widths=box_width,
                                        patch_artist=True,
                                        boxprops=dict(facecolor='lightblue', color='blue'),
                                        medianprops=dict(color='blue'),
                                        showfliers=False)
            intervention_boxes.append(intervention_box)

    legend_elements = [
        (Patch(facecolor='lightgray', alpha=0.3), control_range, control_boxes, 'Control Range'),
        (Patch(facecolor='lightblue', alpha=0.5), intervention_range, intervention_boxes, 'Intervention Range'),
        (Patch(facecolor='red'), control_mean, [], 'Control Mean'),
        (Patch(facecolor='blue'), intervention_mean, [], 'Intervention Mean')
    ]

    leg = ax.legend([item[0] for item in legend_elements],
                   [item[3] for item in legend_elements],
                   loc='upper right')

    lined = {}
    for legpatch, fill_between, boxes, label in legend_elements:
        legline = leg.get_patches()[legend_elements.index((legpatch, fill_between, boxes, label))]
        lined[legline] = [fill_between]
        
        if isinstance(fill_between, plt.Line2D):
            lined[legline] = [fill_between]
            
        if boxes:
            for box in boxes:
                lined[legline].extend(box['boxes'])
                lined[legline].extend(box['medians'])
                lined[legline].extend(box['whiskers'])
                lined[legline].extend(box['caps'])

    def on_pick(event):
        legline = event.artist
        if legline in lined:
            elements = lined[legline]
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
    ax.set_title(f'Temperature Comparison: Control vs {intervention_type} in {settlement}')

    xticks = np.arange(0, max(control_stats['Hours_After_Intervention']), 24)
    ax.set_xticks(xticks)
    ax.set_xticklabels([f'Day {int(x/24)}' for x in xticks])

    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

settlements = ['Rainbow Field', 'Sports Complex']
intervention_types = ['MEB', 'RBF']

for settlement in settlements:
    for intervention_type in intervention_types:
        create_hourly_comparison_plot(settlement, intervention_type)