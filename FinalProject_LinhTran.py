"""
Name:       Linh Tran
CS230:      Fall 2020
Data:       ridesharesample.csv
URL:        https://ridesharing-cs230.streamlit.app/

Description:
This program summarizes the statistics of ridesharing data, graphs bar charts
to display the change in number of rides by day or hour. It also displays
pickups and destinations on the map, and graphs a scatterplot that shows the
relationship between demand, hour, and outside temperature.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk


MENU_1 = {0: "Rides Summary",
          1: "Pickups and Destinations",
          2: "Ridesharing Demand"}

MENU_2 = {0: "Uber",
          1: "Lyft",
          2: "Both apps"}

MENU_3 = {'By day': 'day',
          'By hour': 'hour'}

LOCATIONS = {'Back Bay': [42.3503,-71.0810], 'Beacon Hill': [42.3588,-71.0707],
             'Boston University': [42.3505,-71.1054], 'Fenway': [42.3429,-71.1003],
             'Financial District': [42.3559,-71.0550], 'Haymarket Square': [42.3634,-71.0586],
             'Northeastern University': [42.3398,-71.0892], 'North End': [42.3647,-71.0542],
             'North Station': [42.3661,-71.0631], 'South Station': [42.3519,-71.0551],
             'Theatre District': [42.3519,-71.0643], 'West End': [42.3644,-71.0661]}

MAPKEY = "pk.eyJ1IjoiY2hlY2ttYXJrIiwiYSI6ImNrOTI0NzU3YTA0azYzZ21rZHRtM2tuYTcifQ.6aQ9nlBpGbomhySWPF98DApk.eyJ1IjoiY2hlY2ttYXJrIiwiYSI6ImNrOTI0NzU3YTA0azYzZ21rZHRtM2tuYTcifQ.6aQ9nlBpGbomhySWPF98DA"


#########################################################
## helpers
#########################################################
def read_data(app):
    fname = "ridesharesample.csv"
    df = pd.read_csv(fname)
    df = df.sort_values(by='timestamp', ignore_index=True)  # sort data by timestamp

    if app == "Uber":   # filtering data
        df = df[df.cab_type == "Uber"]
    elif app == "Lyft":
        df = df[df.cab_type == "Lyft"]

    return df

def get_dates(df):
    lst1 = []
    lst2 = []
    for index, row in df.iterrows():
        date = []
        date.append(row['month'])
        date.append(row['day'])
        date = tuple(date)
        if date not in lst1:
            lst1.append(date)
    for i in lst1:
        date = ""
        for j in range(2):
            s = str(i[j])
            if len(s) == 1:
                s = s.replace(s, "0"+s)
            date += s
            if j == 1:
                continue
            else:
                date += '/'
        lst2.append(date)

    return lst2  # a list of dates (MM/DD)

def get_hours(df):
    lst = []
    first = df.hour.min()
    last = df.hour.max()
    for i in np.arange(first, last+1):
        if len(str(i)) == 1 and i != 9:
            s = '0'+str(i)+'-0'+str(i+1)
        elif i == 9:
            s = '0'+str(i)+'-'+str(i+1)
        else:
            s = str(i)+'-'+str(i+1)
        lst.append(s)

    return lst  # a list of timeframe (HH-HH)

def time_select(df, format):
    time_list = []
    if format == 'day':
        time_list = get_dates(df)
    elif format == 'hour':
        time_list = get_hours(df)
    # slider that specifies desired timeframe
    time = st.select_slider(f"Slider by {format}:", options=time_list, value=time_list[0])
    return time, time_list

def display_map(df1):
    locations = [[index, row] for index, row in df1.items()]
    coordinates = [loc+LOCATIONS[loc[0]] for loc in locations]
    df2 = pd.DataFrame(coordinates, columns=['loc','rides','lat','lon'])

    view_state = pdk.ViewState(latitude=df2['lat'].mean(),
                               longitude=df2['lon'].mean(),
                               zoom=12,
                               pitch=0
                               )
    layer1 = pdk.Layer('ScatterplotLayer',
                       data=df2,
                       get_position='[lon, lat]',
                       get_radius=70,
                       get_color=[255,0,0],
                       pickable=True
                       )
    tool_tip = {"html": "<b>{loc}</b> <br/>({lat}, {lon}) <br/>{rides} rides ", # text format
                "style": {"backgroundColor": "red",  # box color red
                          "color": "white"}          # text color white
                }
    map = pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=view_state,
        mapbox_api_key=MAPKEY, 
        layers=[layer1],
        tooltip=tool_tip)

    st.pydeck_chart(map)


#########################################################
## graphing charts
#########################################################
def bar_chart(format, x_val, y_val, avg):
    if format == 'By day':
        xlabel = 'Date'
        title = 'day'
    else:
        xlabel = 'Timeframe'
        title = 'hour'

    avg_list = [avg for i in np.arange(len(x_val))]
    lst = list(zip(y_val, avg_list))
    df = pd.DataFrame(lst, columns=['Number of rides','Average rides'], index=x_val)

    df['Number of rides'].plot(kind='bar', color='r', figsize=(8,6))
    df['Average rides'].plot(kind='line')
    plt.xticks(rotation=-90)
    plt.ylabel('Number of rides')
    plt.xlabel(xlabel)
    plt.title(f"Change in number of rides by {title}")
    plt.legend(loc='best')
    st.pyplot(plt)

def scatter_plot(lst1, lst2, lst3):
    s = [(i*5)**2 for i in lst3]
    fig, ax = plt.subplots(figsize=(10, 7))
    scatter = ax.scatter(lst1, lst2, c='r', s=s)  # color: red, size of each dot: s

    handles, labels = scatter.legend_elements(prop='sizes',
                                              alpha=0.2,
                                              fmt='{x:.2f}',
                                              func=lambda s: np.sqrt(s)/5)  # displaying surge value
    ax.legend(handles, labels, loc='best', title='Surge')
    plt.xticks(np.arange(0,24,1))
    plt.xlabel('Hour')
    plt.ylabel('Temperature')
    plt.title('Scatterplot of demand, hour, and outside temperature')
    st.pyplot(plt)


#########################################################
## menu
#########################################################
def part1(app, app_name):
    st.header("Part 1: Rides Summary")
    st.write(f"_A summary of total, average, min, max number of {app_name} rides in Boston_")
    df = read_data(app)
    st.write("")

    # total sum
    st.write(f"**Total number of sample {app_name} rides:**")
    count = len(df)
    st.write(count)
    st.write("")

    # select time format
    format = st.selectbox('Time selection by day or hour:', list(MENU_3.keys()))
    time, time_list = time_select(df, MENU_3[format])
    st.write("")

    # number of rides by day or by our
    st.write(f"**Number of {app_name} rides by day or by hour:**")

    y_val = []  # list of y values for graphing later
    if format == 'By day':
        for t in time_list:
            month = int(t.split("/")[0])
            day = int(t.split("/")[1])
            df1 = df[(df.month == month) & (df.day == day)][['cab_type', 'source', 'destination']]
            count1 = len(df1)
            y_val.append(count1)

            if t == time:  # only displays info with the specified time from slider
                st.write(f"There were **{count1}** {app_name} rides on **{time}**.")
                st.write(df1)
    else:
        for t in time_list:
            hour = int(t.split("-")[0])
            df1 = df[df.hour == hour][['cab_type', 'source', 'destination']]
            count1 = len(df1)
            y_val.append(count1)

            if t == time:  # only displays info with the specified time from slider
                st.write(f"There were **{count1}** {app_name} rides between timeframe **{time}**.")
                st.write(df1)
    st.write("")

    # average rides per day or per hour & max, min number of rides
    st.write(f"**{app_name}'s average rides per day or per hour & max, min number of rides:**")
    avgRides = int(count/(len(time_list)))
    max_val = max(y_val)
    min_val = min(y_val)
    max_pos = y_val.index(max_val)
    min_pos = y_val.index(min_val)

    st.write(f"There were **{avgRides}** {app_name} rides per {MENU_3[format]}.")
    st.write(f"Max number of rides is **{max_val}** on **{time_list[max_pos]}**.")
    st.write(f"Min number of rides is **{min_val}** on **{time_list[min_pos]}**.")
    st.write("")

    # visualization
    st.write(f"**Visualization:**")
    bar_chart(format, time_list, y_val, avgRides)

def part2(app, app_name):
    st.header("Part 2: Pickups and Destinations")
    st.write(f"_{app_name}'s most requested pickups and destinations in Boston_")
    df = read_data(app)
    st.write("")

    df2_pickup = df['source'].value_counts().sort_values(ascending=False)
    top_pickup = df2_pickup.head(3)
    st.write("**Top 3 pickups (total rides):**", top_pickup)
    display_map(top_pickup)
    st.write("")

    df2_destination = df['destination'].value_counts().sort_values(ascending=False)
    top_destination = df2_destination.head(3)
    st.write("**Top 3 destinations (total rides):**", top_destination)
    display_map(top_destination)

def part3(app, app_name):
    st.header("Part 3: Ridesharing Demand")
    st.write(f"_{app_name} ridesharing traffic by hour in Boston_")
    df = read_data(app)
    st.write("")
    with st.expander("Demand and surge multiplier?"):  # expander to explain
        st.write("""
        The higher the surge multiplier, the higher the demand of ridesharing.
         """)
    st.write("")

    # find surge multiplier greater than 1
    st.write("**Rides with surge multipliers greater than 1:**")
    df3 = df[df.surge_multiplier > 1][['cab_type', 'hour', 'temperature', 'surge_multiplier']] # filering data with surge multiplier > 1

    if len(df3) == 0:
        st.write(f"There were no {app} rides that have surge multipliers greater than 1 in the sample data.")
        st.write("Please select the other app.")
    else:
        st.write(df3)
        st.write("")

        # relationship between hour, temperature, and demand
        st.write('**Visualization:**')

        surge_list = [row['surge_multiplier'] for index, row in df3.iterrows()]
        time_list = [row['hour'] for index, row in df3.iterrows()]
        temp_list = [row['temperature'] for index, row in df3.iterrows()]

        scatter_plot(time_list, temp_list, surge_list)


#########################################################
## web interface
#########################################################
def main():
    st.title("Ride Sharing Sample Data")
    st.sidebar.header("Final Project")
    st.sidebar.write("""
    Name:   Linh Tran\n
    CS230:  Section SN5\n
    Data:   ridesharesample.csv\n
    URL:    https://ridesharing-final-project.herokuapp.com/""")

    st.sidebar.header("Inputs")
    analysis = st.sidebar.radio("Select an analysis:", list(MENU_1.values()))
    app = st.sidebar.radio("Select an app:", list(MENU_2.values()))

    if app == "Both apps":
        app_name = "Uber and Lyft"
    else:
        app_name = app

    if analysis == MENU_1[0]:
        part1(app, app_name)
    elif analysis == MENU_1[1]:
        part2(app, app_name)
    else:
        part3(app, app_name)

main()
