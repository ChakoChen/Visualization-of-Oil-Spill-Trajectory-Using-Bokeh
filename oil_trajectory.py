# oil_trajectory.py - add hovertoll to oil trajectory

from bokeh.io import output_file, show
from bokeh.plotting import figure, ColumnDataSource
from bokeh.layouts import row, column, gridplot
from bokeh.models import HoverTool
from bokeh.models.widgets import Panel, Tabs
from bokeh.transform import factor_cmap
from bokeh.palettes import Greys256, Magma256, Viridis256, Category20
from bokeh.models import Range1d
import numpy as np
import pandas as pd


def trajactory():
    # Import data
    df = pd.read_csv('../data/SWRX_OIL20181130.csv', delimiter=",")

    # Convert UTC time to Newfoundland time
    df['LocalDateTime'] = pd.to_datetime(df['DateTime']).dt.tz_localize('UTC').dt.tz_convert('America/St_Johns').dt.tz_localize(None).dt.strftime('%Y-%m-%d %H:%M')

    # Specify Series for cicle plot annotations
    df['ScaledRadius'] = df['Radius']/10000.  # cirle size
    df['mass'] = df['Mass'].astype(str)  # circle color

    # Create the figure: p
    p = figure()

    # Define colors according to 'Mass' and legends to 'DateTime' 
    colors = factor_cmap('mass', palette=Category20[13], factors=df['mass'].unique()) 
    legends = factor_cmap('LocalDateTime', palette=Category20[13], factors=df['DateTime'].unique())

    # Add the first circle glyph to the figure p
    p.scatter(source=df, x='Latitude', y='Longitude', marker='circle',radius='ScaledRadius', alpha=0.5, fill_color=colors, legend=legends)

    # Assign the legend to the bottom left: p.legend.location
    p.x_range = Range1d(46.73, 46.92)
    p.legend.location = 'bottom_right'

    # Add a title
    p.title.text = "Oil Spill Trajectory"

    # Create a HoverTool object: hover
    hover = HoverTool(tooltips=[('DateTime','@LocalDateTime'), ('Radius','@Radius{0.0000}'), ('Thickness','@Thickness{0.0000}')])

    # Add the HoverTool object to figure p
    p.add_tools(hover)

    # Specify the name of the output_file and show the result
    output_file('oil_trajectory.html')
    show(p)


def main():
    trajactory()

if __name__ == "__main__":
    main()
