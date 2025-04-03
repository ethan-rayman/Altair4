#!/usr/bin/env python
# coding: utf-8

# # **SI311 W25 Altair Homework #4**
# ## Overview
# 
# We'll focus on maps and cartrographic visualization. In this lab, you will practice:
# * Point Maps
# * Symbol Maps
# * Choropleth maps
# * Interactions with maps
# 
# 
# After building these charts, you will make a website with these charts using streamlit.
# 
# ### Lab Instructions
# 
# *   Save, rename, and submit the ipynb file (use your username in the name).
# *   Complete all the checkpoints, to create the required visualization at each cell.
# *   Run every cell (do Runtime -> Restart and run all to make sure you have a clean working version), print to pdf, submit the pdf file.
# *   If you end up stuck, show us your work by including links (URLs) that you have searched for. You'll get partial credit for showing your work in progress.

# In[11]:


import pandas as pd
import altair as alt
from vega_datasets import data

alt.data_transformers.disable_max_rows()

df = pd.read_csv('https://raw.githubusercontent.com/pratik-mangtani/si649-hw/main/airports.csv')
url = "https://raw.githubusercontent.com/pratik-mangtani/si649-hw/main/small-airports.json"

import warnings
warnings.filterwarnings('ignore')


# ## Visualization 1: Dot Density Map

# ![vis1](https://pratik-mangtani.github.io/si649-hw/dot_density.png)
# **Description of the visualization:**
# 
# We want to visualize the density of small airports in the world. Each small airport is represented by a dot.
# The visualization has two layers:
# * The base layer shows the outline of the world map.
# * The point map shows different small airports.
# * The tooltip shows the **name** of the airport.
# 
# **Hint:**
# * How can we show continents on the map? Which object can be used from the json dataset ?
# * How can we show only small airports on the map?

# In[24]:


worldmap = alt.topo_feature(data.world_110m.url, 'countries')
base = alt.Chart(worldmap).mark_geoshape(fill='lightgray', stroke='white').properties(width=800,height=400)
small_airports = df[df['type'] == 'small_airport']
points = alt.Chart(small_airports).mark_circle(color='red', size=10).encode(
    longitude='longitude_deg:Q',
    latitude='latitude_deg:Q',
    tooltip='name:N'
)
chart = base + points
chart.properties(title='Small airports in the world')


# ## Visualization 2: Propotional Symbol

# ![vis2](https://pratik-mangtani.github.io/si649-hw/symbol_map.png)
# **Description of the visualization:**
# 
# The visualization shows faceted maps pointing the 20 most populous cities in the world by 2100. There are two layers in faceted charts:
# * The base layer shows the map of countries.
# * The second layer shows size encoded points indicating the population of those countries.
# * Tooltip shows **city** name and **population**.
# 
# **Hint:**
# * Which projection has been used in individual charts?
# * How to create a faceted chart with different years and 2 columns?

# In[46]:


countries_url = data.world_110m.url
source = 'https://raw.githubusercontent.com/pratik-mangtani/si649-hw/main/population_prediction.csv'
df = pd.read_csv(source)


# In[60]:


df


# In[93]:


countries = alt.topo_feature(countries_url, 'countries')
def mapfunc(year):
    base = alt.Chart(countries).mark_geoshape(fill='lightgray', stroke='white').properties(width=300, height=150)
    points = alt.Chart(df[df['year'] == year]).mark_circle(color='green', opacity=0.8
    ).encode(longitude='lon:Q', latitude='lat:Q', size=alt.Size('population:Q', 
        scale=alt.Scale(range=[10, 100]), title='Population (million)'),
        tooltip=['city:N', 'population:Q']
    )
    return base + points

chart2010 = mapfunc(2010).properties(title='2010')
chart2025 = mapfunc(2025).properties(title='2025')
chart2050 = mapfunc(2050).properties(title='2050')
chart2075 = mapfunc(2075).properties(title='2075')
chart2100 = mapfunc(2100).properties(title='2100')
top = alt.hconcat(chart2010, chart2025)
mid = alt.hconcat(chart2050, chart2075)
bot = chart2100

final = alt.vconcat(top, mid, bot).properties(title='The 20 Most Populous Cities in the World by 2100')
final


# ## Visualization 3: Hurricane Trajectories
# 
# 
# 

# ![vis3](https://pratik-mangtani.github.io/si649-hw/hurricane_trajectories.png)
# **Description of the visualization:**
# 
# Create a map that shows the paths (trajectories) of the 2017 hurricanes. Filter the data so that only 2017 hurricanes are shown. Remove Alaska and Hawaii from the map (Filter out ids 2 and 15).
# 
# **Hint:**
# * How will you filter out 2017 hurricanes?
# * Which object can be used to show state boundaries?

# In[74]:


states_url = data.us_10m.url
hurricane_data = pd.read_csv('https://raw.githubusercontent.com/pratik-mangtani/si649-hw/main/hurdat2.csv')
hurricane_data


# In[103]:


hurricane_data['datetime'] = hurricane_data['datetime'].apply(pd.to_datetime)
hurricane_data['year'] = hurricane_data['datetime'].dt.year

dat2017 = hurricane_data[hurricane_data['year'] == 2017]
dat2017 = dat2017.sort_values(by=['identifier', 'datetime'])
states = alt.topo_feature(data.us_10m.url, 'states')
base = alt.Chart(states).mark_geoshape(fill=None, stroke='black'
).transform_filter(
    (alt.datum.id != 2) & (alt.datum.id != 15)
).properties(width=1000, height=600)

paths = alt.Chart(dat2017).mark_line(color='blue', opacity=0.6
).encode(
    longitude='longitude:Q',
    latitude='latitude:Q',
    order='datetime:T',
    detail='identifier:N'
)
chart = base + paths
chart


# ## Visualization 4: Choropleth Map
# 

# ![vis4](https://pratik-mangtani.github.io/si649-hw/choropleth.png)
# 
# **Interaction**
# 
# ![vis4](https://pratik-mangtani.github.io/si649-hw/choropleth-interaction.gif)
# 
# **Description of the visualization:**
# 
# The visualization has a choropleth map showing the population of different states and a sorted bar chart showing the top 15 states by population. These charts are connected using a click interaction.
# 
# **Hint**
# 
# * Which object can be used to show states on the map?
# * Which transform can be used to add population data to the geographic data? How can we combine two datasets in Altair?
# 
# 

# In[87]:


state_map = data.us_10m.url
state_pop = data.population_engineers_hurricanes()[['state', 'id', 'population']]
state_pop


# In[109]:


state_shapes = alt.topo_feature(data.us_10m.url, 'states')
hover = alt.selection_single(fields=['state'], on='mouseover', empty='all')

choropleth = alt.Chart(state_shapes).mark_geoshape().encode(
    color=alt.Color('population:Q', scale=alt.Scale(scheme='greens')),
    opacity=alt.condition(hover, alt.value(1), alt.value(0.3)),
    tooltip=['state:N', 'population:Q']
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(state_pop, 'id', ['state', 'population'])
).project(
    type='albersUsa'
).add_selection(
    hover
).properties(
    width=500,
    height=300
)

bars = alt.Chart(state_pop).transform_window(
    rank='rank()',
    sort=[alt.SortField('population', order='descending')]
).transform_filter(
    alt.datum.rank <= 15
).mark_bar().encode(
    y=alt.Y('state:N', sort='-x'),
    x=alt.X('population:Q'),
    color=alt.Color('population:Q', scale=alt.Scale(scheme='greens')),
    opacity=alt.condition(hover, alt.value(1), alt.value(0.3)),
    tooltip=['state:N', 'population:Q']
).add_selection(
    hover
).properties(
    width=500,
    height=300,
    title='Top 15 states by population'
)

final_chart = choropleth | bars
final_chart


# In[ ]:




