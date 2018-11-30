# oil_trajectory_slider.py -- highlight the trajectory of oil blobs with a slider of date and time

from bokeh.io import curdoc, output_file, show
from bokeh.plotting import figure
from bokeh.models import HoverTool,ColumnDataSource,CategoricalColorMapper,Slider,Select
from bokeh.layouts import widgetbox, row, column
from bokeh.palettes import Spectral6
from datetime import datetime, date, time, timedelta
import pandas as pd

# Specify data file name
filename = '../data/SWRX_OIL20181130.csv'

def prepare_data(filename):
    """
    Prepare the data by converting UTC time to local time, and add new Series for plot
    """
    # Import data
    data = pd.read_csv(filename, delimiter=",")

    # Convert UTC time to Newfoundland time
    data['LocalDateTime'] = pd.to_datetime(data['DateTime']).dt.tz_localize('UTC').dt.tz_convert('America/St_Johns').dt.tz_localize(None).dt.strftime('%Y-%m-%d %H:%M:%S')

    # Define a scaled radius for circle plots
    data['ScaledRadius'] = data['Radius']/15000.  # cirle size

    # Set index to DateTime
    data = data.set_index(pd.DatetimeIndex(data['LocalDateTime']))
     
    return data 

def myapp():
    """
    Build the oil trajectory visulization app
    """
    ####################################
    # (0) Construct a ColumnDataSource #
    ####################################

    # Read data
    data = prepare_data(filename)
   
    # Get the beginning time of oil spill
    StartDateTime = str(data['LocalDateTime'][0]) 

    # Make a ColumnDataSource for background plot
    BackgroundSource = ColumnDataSource(data={
        'x'         : data.loc[:,'Longitude'],
        'y'         : data.loc[:,'Latitude'],
        'radius'    : data.loc[:,'ScaledRadius'],
        'thickness' : data.loc[:,'Thickness'],
        'Radius'    : data.loc[:,'Radius']
    })

    # Make a ColumnDataSource for line plot
    LineSource = ColumnDataSource(data={
        'x' : data.loc[:,'Longitude'].resample('2H').mean(),
        'y' : data.loc[:,'Latitude'].resample('2H').mean(),
        'thickness' : data.loc[:,'Thickness'].resample('2H').mean(),
        'Radius' : data.loc[:,'Radius'].resample('2H').mean()
    })

    # Make an initial ColumnDataSource: source
    source = ColumnDataSource(data={
        'x'         : data.loc[StartDateTime,'Longitude'],
        'y'         : data.loc[StartDateTime,'Latitude'],
        'radius'    : data.loc[StartDateTime,'ScaledRadius'],
        'thickness' : data.loc[StartDateTime,'Thickness'],
        'Radius'    : data.loc[StartDateTime,'Radius']
    })

    # Save the minimum and maximum values of the longitude column: xmin, xmax
    xmin, xmax = min(data.Longitude)-0.02, max(data.Longitude)+0.02

    # Save the minimum and maximum values of the latitude column: ymin, ymax
    ymin, ymax = min(data.Latitude)-0.02, max(data.Latitude)+0.02

    ################################
    # (1) Make an interactive plot # 
    ################################

    # Create the figure: plot
    plot = figure(title='Oil distribution at '+StartDateTime, x_axis_label='Longitude', y_axis_label='Latitude', x_range=(xmin, xmax), y_range=(ymin, ymax))

    #------------------------#
    # THE CALLBACK FUNCTION! #
    #------------------------#
    # Define the callback function for the slider and title: update_plot
    def update_plot(attr, old, new):
        # Read the current value off the slider
        hour = slider.value

        # Update datetime corresponding to passed hours
        delta = timedelta(hour/24.)
        NewDateTime = datetime.strptime(StartDateTime, '%Y-%m-%d %H:%M:%S') + delta 
 
        # Set new_data
        new_data = {
            'x'         : data.loc[str(NewDateTime),'Longitude'],
            'y'         : data.loc[str(NewDateTime),'Latitude'],
            'radius'    : data.loc[str(NewDateTime),'ScaledRadius'],
            'thickness' : data.loc[str(NewDateTime),'Thickness'],
            'Radius'    : data.loc[str(NewDateTime),'Radius']
        }
        
        # Assign new_data to source.data
        source.data = new_data
 
        # Set the range of all axes to the original range
        plot.x_range.start = xmin
        plot.x_range.end = xmax
        plot.y_range.start = ymin
        plot.y_range.end = ymax   

        # Add title to figure: plot.title.text
        plot.title.text = 'Oil distribution at %s' % str(NewDateTime)
    
    #--------------------#
    # (1.1) Add a slider #
    #--------------------#
    # Make a slider object: slider
    slider = Slider(title='Hour', start=0, end=24, step=2, value=0)

    # Attach the callback to the 'value' property of slider
    slider.on_change('value', update_plot)

    #-----------------------#
    # (1.2) Add a HoverTool #
    #-----------------------#
    # Create a HoverTool: hover
    hover = HoverTool(tooltips=[('Longitude','@x'),('Latitude','@y'),('Radius','@Radius{0.0000}'),('Thickness','@thickness{0.0000}')])

    #------------------------------------------------#
    # (1.3) Add the initial circle glyph to the plot #
    #------------------------------------------------#
    # Plot a circle glyph as a background
    plot.scatter(source=BackgroundSource, x='x', y='y', radius='radius', marker='circle', alpha=0.5, fill_color='grey', line_color='white')

    # Add an average path by resamping the DataFrame
    plot.line(source=LineSource, x='x', y='y', color='grey', line_width=1.5, alpha=0.8)

    # Add circle glyphs to the plot
    plot.scatter(source=source, x='x', y='y', radius='radius', marker='circle', alpha=1, fill_color='black', line_color='grey', hover_fill_color='firebrick', hover_alpha=0.5, hover_line_color='white')

    # Add the HoverTool to the plot
    plot.add_tools(hover)

    #-------------------------------#
    # (1.6) Put everything together #
    #-------------------------------#
    # Create layout and add to current document
    layout = column(slider, plot)
    curdoc().add_root(layout)

myapp()
