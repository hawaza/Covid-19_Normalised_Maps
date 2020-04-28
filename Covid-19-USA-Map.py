#Import Modules
import folium
import pandas
import json
import recursive_json as rjs

#Open Files and import data
confirmed_covid = pandas.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv")
deaths_covid = pandas.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv")
US_state_Population = pandas.read_csv("http://www2.census.gov/programs-surveys/popest/datasets/2010-2019/national/totals/nst-est2019-alldata.csv?#")
with open ('USA_World.json', 'r') as file:
    usa_json = json.load(file)

#Extract State names from GeoJSON and US State Population Data
s_name_usa_json = rjs.extract_values(usa_json, 'name')
s_name_s_pop = US_state_Population["NAME"].tolist()

#Remove unneeded columns from Conifrmed Cases DataFrame, rename last column Total, group and sum by State
confirmed_covid_update = confirmed_covid.drop(confirmed_covid.columns[0:6],1)
confirmed_covid_update = confirmed_covid_update.drop(confirmed_covid_update.columns[1:5],1)
#confirmed_covid_update["Total"] = confirmed_covid_update.sum(axis=1)   #Not needed as Last day is total cases
confirmed_covid_update = confirmed_covid_update.set_axis([*confirmed_covid_update.columns[:-1], 'Total'], axis=1, inplace=False)
confirmed_covid_update = confirmed_covid_update.groupby(["Province_State"]).sum().reset_index() #reset index resets index and stops "country/region" NOT being a header

#Remove unneeded columns from Death Cases DataFrame, rename last column Total, group and sum by State
deaths_covid_update = deaths_covid.drop(deaths_covid.columns[0:6],1)
deaths_covid_update = deaths_covid_update.drop(deaths_covid_update.columns[1:5],1)
deaths_covid_update = deaths_covid_update.set_axis([*deaths_covid_update.columns[:-1], 'Total'], axis=1, inplace=False)
deaths_covid_update = deaths_covid_update.groupby(["Province_State"]).sum().reset_index() #reset index resets index and stops "country/region" NOT being a header


#Remove uneeded columns from DataFrame and rename columns to allow easier merger
US_state_Population_update = US_state_Population.drop(US_state_Population.columns[0:4],1)
US_state_Population_update = US_state_Population_update.drop(US_state_Population_update.columns[1:12],1)
US_state_Population_update = US_state_Population_update.drop(US_state_Population_update.columns[2:],1)
US_state_Population_update.columns=["Province_State", "Population"]

#Add Population estimate to main Confirmed Cases DataFrame.  NOT NEEDED ON DEATHS AS ALREADY HAS POPULATION INCLUDED
ccu = confirmed_covid_update.merge(US_state_Population_update, how='left', left_on='Province_State', right_on='Province_State')
dcu = deaths_covid_update

#Add and work out cases per 1000 people
ccu["Cases per 1000"] = ccu["Total"] / (ccu["Population"] / 1000)
dcu["Deaths per 1000"] = dcu["Total"] / (dcu["Population"] / 1000)

#Extract District of Columbia data as not included in JSON
#Need to add this as its own marker on the map later
ccu_washingtondc = ccu.loc[ccu['Province_State'] == 'District of Columbia']
dcu_washingtondc = dcu.loc[ccu['Province_State'] == 'District of Columbia']

#Generate list noting which States are/are not included in the JSON for Confirmed Cases
c_in_list = []
c_not_in_list = []
for country in ccu["Province_State"]:
    if country in s_name_usa_json:
        c_in_list.append(country)
    else:
        c_not_in_list.append(country)

#Remove entries of States not in the JSON for Confirmed Cases
ccu_drop = ccu
for country in c_not_in_list:
    ccu_drop = ccu_drop[~ccu_drop.Province_State.str.contains(country)]

#Generate list noting which States are/are not included in the JSON for Covid Deaths
d_in_list = []
d_not_in_list = []
for country in dcu["Province_State"]:
    if country in s_name_usa_json:
        d_in_list.append(country)
    else:
        d_not_in_list.append(country)

#Remove entries of States not in the JSON for Covid Deaths
dcu_drop = dcu
for country in d_not_in_list:
    dcu_drop = dcu_drop[~dcu_drop.Province_State.str.contains(country)]

#Create Map
map = folium.Map(location = [39.50, -98.35], zoom_start = 4, tiles="Stamen Terrain", max_bounds=True)

#Create Choropleth Map for Confirmed Covid Cases
folium.Choropleth(
    geo_data = usa_json,
    name = 'Infections',
    data = ccu_drop,
    columns = ['Province_State', 'Cases per 1000'],
    key_on = 'properties.name',
    fill_color = 'YlGnBu',
    fill_opacity = 0.7,
    line_opacity = 0.2,
    legend_name = 'Confirmed Covid-19 Infections per 1000 people'
).add_to(map)

#Create Choropleth Map for Covid Deaths
folium.Choropleth(
    geo_data = usa_json,
    name = 'Deaths',
    data = dcu_drop,
    columns = ['Province_State', 'Deaths per 1000'],
    key_on = 'properties.name',
    fill_color = 'YlOrRd',
    fill_opacity = 0.7,
    line_opacity = 0.2,
    legend_name = 'Deaths due to Covid-19 per 1000 people'
).add_to(map)

#Add Layer Control
folium.LayerControl().add_to(map)

html = """<h5>Washington DC Covid Information:</h5>
<font size="2">
Confirmed: <strong>%s</strong> per thousand people <br>
Deaths: <strong>%s</strong> per thousand people
</font>
"""
iframe = folium.IFrame(html=html % (round(float(ccu_washingtondc["Cases per 1000"]),2), round(float(dcu_washingtondc["Deaths per 1000"]),2)), width=300, height=100)
map.add_child(folium.CircleMarker(location = [38.90, -77.03], radius = 6, popup = folium.Popup(iframe), fill_color = 'black', color = 'grey', fill_opacity = 0.9))

#Save map
map.save("USA_Covid_Map.html")