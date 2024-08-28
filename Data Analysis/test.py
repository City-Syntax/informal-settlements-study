import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

# Load the data
temperature_differences_df = pd.read_csv('temperature_differences.csv', parse_dates=['DateTime'])
logger_flags_df = pd.read_csv('logger_flags.csv')

# Define base colors
shaded_base_color = mcolors.CSS4_COLORS['darkblue']
unshaded_base_color = mcolors.CSS4_COLORS['lightblue']

# Function to generate different shades of a base color
def get_shades(base_color, num_shades):
    return [mcolors.to_rgba(base_color, alpha) for alpha in np.linspace(0.3, 1, num_shades)]

# Function to plot temperature differences using shades of two colors
def plot_temperature_differences(settlement, intervention_type, title, multi_label=False):
    # Filter loggers for the specified settlement and intervention type
    loggers_subset = logger_flags_df[(logger_flags_df['Settlement'] == settlement) & 
                                     (logger_flags_df['Intervention'] == intervention_type)]
    
    num_loggers = len(loggers_subset)
    shaded_loggers = loggers_subset[loggers_subset['Shaded']]
    unshaded_loggers = loggers_subset[~loggers_subset['Shaded']]

    shaded_colors = get_shades(shaded_base_color, len(shaded_loggers))
    unshaded_colors = get_shades(unshaded_base_color, len(unshaded_loggers))
    
    fig, ax = plt.subplots(figsize=(14, 8))
    lines = []
    
    # Plot shaded loggers
    for idx, (_, row) in enumerate(shaded_loggers.iterrows()):
        logger = row['Loggers']
        intervention_start = pd.to_datetime(row['Intervention_Start'])
        post_intervention_end = pd.to_datetime(row['Post_Intervention_End'])
        
        line, = ax.plot(temperature_differences_df['DateTime'], temperature_differences_df[logger], 
                        label=f"{logger} (Shaded)", color=shaded_colors[idx], linewidth=2)
        lines.append(line)

    # Plot unshaded loggers
    for idx, (_, row) in enumerate(unshaded_loggers.iterrows()):
        logger = row['Loggers']
        intervention_start = pd.to_datetime(row['Intervention_Start'])
        post_intervention_end = pd.to_datetime(row['Post_Intervention_End'])
        
        line, = ax.plot(temperature_differences_df['DateTime'], temperature_differences_df[logger], 
                        label=f"{logger} (Unshaded)", color=unshaded_colors[idx], linewidth=2)
        lines.append(line)

    # Mark the intervention period
    ax.axvline(x=intervention_start, color='red', linestyle='--', linewidth=1)
    ax.text(intervention_start, ax.get_ylim()[1], 'Intervention Start', color='red', verticalalignment='top')

    if multi_label:
        intervention_mid = intervention_start + pd.Timedelta(days=2)
        ax.axvline(x=intervention_mid, color='orange', linestyle='--', linewidth=1)
        ax.text(intervention_mid, ax.get_ylim()[1], 'Intervention Implemented', color='orange', verticalalignment='top')
        
        ax.axvline(x=post_intervention_end, color='green', linestyle='--', linewidth=1)
        ax.text(post_intervention_end, ax.get_ylim()[1], 'Intervention End', color='green', verticalalignment='top')
    
    ax.set_title(title)
    ax.set_xlabel('DateTime')
    ax.set_ylabel('Temperature Difference (°C)')
    leg = ax.legend(loc='upper right', fancybox=True, shadow=True)
    leg.get_frame().set_alpha(0.4)

    # Set up interactive legend
    lined = dict()
    for legline, origline in zip(leg.get_lines(), lines):
        legline.set_picker(5)  # 5 pts tolerance
        lined[legline] = origline

    def onpick(event):
        legline = event.artist
        origline = lined[legline]
        vis = not origline.get_visible()
        origline.set_visible(vis)
        legline.set_alpha(1.0 if vis else 0.2)
        fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', onpick)

    plt.grid(True)
    plt.show()

# Plot for Rainbow Field RBF
plot_temperature_differences('Rainbow Field', 'RBF', 'Rainbow Field - RBF Intervention')

# Plot for Rainbow Field MEB
plot_temperature_differences('Rainbow Field', 'MEB', 'Rainbow Field - MEB Intervention')

# Plot for Rainbow Field Control
plot_temperature_differences('Rainbow Field', 'CONTROL', 'Rainbow Field - Control Loggers')

# Plot for Sports Complex RBF
plot_temperature_differences('Sports Complex', 'RBF', 'Sports Complex - RBF Intervention', multi_label=True)

# Plot for Sports Complex MEB
plot_temperature_differences('Sports Complex', 'MEB', 'Sports Complex - MEB Intervention', multi_label=True)

# Plot for Sports Complex Control
plot_temperature_differences('Sports Complex', 'CONTROL', 'Sports Complex - Control Loggers', multi_label=True)
