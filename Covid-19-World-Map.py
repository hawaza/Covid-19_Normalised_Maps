#Import Modules
import folium
import pandas
import json
import recursive_json as rjs

#Open Files and import data
confirmed_covid = pandas.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
deaths_covid = pandas.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
World_Population = pandas.read_csv("API_SP.POP.TOTL_DS2_en_csv_v2_988606.csv")
with open ('World_folium.json', 'r') as file:
    world_json = json.load(file)

#Extract State names from GeoJSON and US State Population Data
c_name_world_json = rjs.extract_values(world_json, 'name')
c_name_c_pop = World_Population["Country Name"].tolist()

#Remove unneeded columns from Conifrmed Cases DataFrame, rename last column Total, group and sum by State
confirmed_covid_update = confirmed_covid.drop(confirmed_covid.columns[0],1)
confirmed_covid_update = confirmed_covid_update.drop(confirmed_covid_update.columns[1:3],1)
#confirmed_covid_update["Total"] = confirmed_covid_update.sum(axis=1)   #Not needed as Last day is total cases
confirmed_covid_update = confirmed_covid_update.set_axis([*confirmed_covid_update.columns[:-1], 'Total'], axis=1, inplace=False)
confirmed_covid_updated = confirmed_covid_update.rename(columns={"Country/Region":"Country"})
confirmed_covid_updated = confirmed_covid_updated.groupby(["Country"]).sum().reset_index() #reset index resets index and stops "country/region" NOT being a header

#Remove unneeded columns from Death Cases DataFrame, rename last column Total, group and sum by State
deaths_covid_update = deaths_covid.drop(deaths_covid.columns[0],1)
deaths_covid_update = deaths_covid_update.drop(deaths_covid_update.columns[1:3],1)
deaths_covid_update = deaths_covid_update.set_axis([*deaths_covid_update.columns[:-1], 'Total'], axis=1, inplace=False)
deaths_covid_updated = deaths_covid_update.rename(columns={"Country/Region":"Country"})
deaths_covid_updated = deaths_covid_updated.groupby(["Country"]).sum().reset_index() #reset index resets index and stops "country/region" NOT being a header

#Remove uneeded columns from DataFrame and rename columns to allow easier merger
World_Population_update = World_Population.drop(World_Population.columns[1:62],1)
World_Population_update = World_Population_update.drop(World_Population_update.columns[-1],1)
World_Population_update.columns=["Country", "Population"]

#NEED TO MATCH UP COUNTRIES WITH DIFFERING NAMES.  Updating World_Population_update with values as stated in Covid Datasets:
World_Population_update.loc[(World_Population_update.Country == 'Yemen, Rep.'),'Country'] = 'Yemen'
World_Population_update.loc[(World_Population_update.Country == 'Venezuela, RB'),'Country'] = 'Venezuela'
World_Population_update.loc[(World_Population_update.Country == 'United States'),'Country'] = 'US'
World_Population_update.loc[(World_Population_update.Country == 'Syrian Arab Republic'),'Country'] = 'Syria'
World_Population_update.loc[(World_Population_update.Country == 'Slovak Republic'),'Country'] = 'Slovakia'
World_Population_update.loc[(World_Population_update.Country == 'St. Vincent and the Grenadines'),'Country'] = 'Saint Vincent and the Grenadines'
World_Population_update.loc[(World_Population_update.Country == 'St. Lucia'),'Country'] = 'Saint Lucia'
World_Population_update.loc[(World_Population_update.Country == 'St. Kitts and Nevis'),'Country'] = 'Saint Kitts and Nevis'
World_Population_update.loc[(World_Population_update.Country == 'Russian Federation'),'Country'] = 'Russia'
World_Population_update.loc[(World_Population_update.Country == 'Lao PDR'),'Country'] = 'Laos'
World_Population_update.loc[(World_Population_update.Country == 'Kyrgyz Republic'),'Country'] = 'Kyrgyzstan'
World_Population_update.loc[(World_Population_update.Country == 'Korea, Rep.'),'Country'] = 'Korea, South'
World_Population_update.loc[(World_Population_update.Country == 'Iran, Islamic Rep.'),'Country'] = 'Iran'
World_Population_update.loc[(World_Population_update.Country == 'Gambia, The'),'Country'] = 'Gambia'
World_Population_update.loc[(World_Population_update.Country == 'Egypt, Arab Rep.'),'Country'] = 'Egypt'
World_Population_update.loc[(World_Population_update.Country == 'Czech Republic'),'Country'] = 'Czechia'
World_Population_update.loc[(World_Population_update.Country == 'Congo, Dem. Rep.'),'Country'] = 'Congo (Kinshasa)'
World_Population_update.loc[(World_Population_update.Country == 'Congo, Rep.'),'Country'] = 'Congo (Brazzaville)'
World_Population_update.loc[(World_Population_update.Country == 'Myanmar'),'Country'] = 'Burma'
World_Population_update.loc[(World_Population_update.Country == 'Brunei Darussalam'),'Country'] = 'Brunei'
World_Population_update.loc[(World_Population_update.Country == 'Bahamas, The'),'Country'] = 'Bahamas'

#COVIDS / WORLDPOP
#Yemen / Yemen, Rep.
#Western Sahara / ?
#Venezuela / Venezuela, RB
#US / United States
#Taiwan* / ?
#Syria / Syrian Arab Republic
#Slovakia / Slovak Republic
#Saint Vincent and the Grenadines / St. Vincent and the Grenadines
#Saint Lucia / St. Lucia
#Saint Kitts and Nevis / St. Kitts and Nevis
#Russia / Russian Federation
#MS Zaandam / ?
#Laos / Lao PDR
#Kyrgyzstan / Kyrgyz Republic
#Korea, South / Korea, Rep.
#Iran / Iran, Islamic Rep.
#Holy See / ?
#Gambia / Gambia, The
#Egypt / Egypt, Arab Rep.
#Diamond Princess / ?
#Czechia / Czech Republic
#Congo (Kinshasa) / Congo, Dem. Rep.
#Congo (Brazzaville) / Congo, Rep.
#Burma / Myanmar
#Brunei / Brunei Darussalam
#Bahamas / Bahamas, The

#Add Population estimate to main Confirmed Cases DataFrame. 
ccu = confirmed_covid_updated.merge(World_Population_update, how='left', left_on='Country', right_on='Country')
dcu = deaths_covid_updated.merge(World_Population_update, how='left', left_on='Country', right_on='Country')

#Add and work out cases per 1000 people
ccu["Cases per 1000"] = ccu["Total"] / (ccu["Population"] / 1000)
dcu["Deaths per 1000"] = dcu["Total"] / (dcu["Population"] / 1000)

#Match JSON countries with Covid DataFrames.  Updating Covid datasets with country names as per the map JSON.
ccu.loc[(ccu.Country == 'West Bank and Gaza'),'Country'] = 'West Bank'
ccu.loc[(ccu.Country == 'US'),'Country'] = 'United States of America'
ccu.loc[(ccu.Country == 'Tanzania'),'Country'] = 'United Republic of Tanzania'
ccu.loc[(ccu.Country == 'Taiwan*'),'Country'] = 'Taiwan'
ccu.loc[(ccu.Country == 'Timor-Leste'),'Country'] = 'East Timor'
ccu.loc[(ccu.Country == 'Eswatini'),'Country'] = 'Swaziland'
ccu.loc[(ccu.Country == 'Serbia'),'Country'] = 'Republic of Serbia'
ccu.loc[(ccu.Country == 'Burma'),'Country'] = 'Myanmar'
ccu.loc[(ccu.Country == 'North Macedonia'),'Country'] = 'Macedonia'
ccu.loc[(ccu.Country == 'Korea, South'),'Country'] = 'South Korea'
ccu.loc[(ccu.Country == 'Guinea-Bissau'),'Country'] = 'Guinea Bissau'
ccu.loc[(ccu.Country == 'Czechia'),'Country'] = 'Czech Republic'
ccu.loc[(ccu.Country == 'Congo (Brazzaville)'),'Country'] = 'Republic of the Congo'
ccu.loc[(ccu.Country == 'Congo (Kinshasa)'),'Country'] = 'Democratic Republic of the Congo'
ccu.loc[(ccu.Country == "Cote d'Ivoire"),'Country'] = 'Ivory Coast'
ccu.loc[(ccu.Country == 'Bahamas'),'Country'] = 'The Bahamas'

dcu.loc[(dcu.Country == 'West Bank and Gaza'),'Country'] = 'West Bank'
dcu.loc[(dcu.Country == 'US'),'Country'] = 'United States of America'
dcu.loc[(dcu.Country == 'Tanzania'),'Country'] = 'United Republic of Tanzania'
dcu.loc[(dcu.Country == 'Taiwan*'),'Country'] = 'Taiwan'
dcu.loc[(dcu.Country == 'Timor-Leste'),'Country'] = 'East Timor'
dcu.loc[(dcu.Country == 'Eswatini'),'Country'] = 'Swaziland'
dcu.loc[(dcu.Country == 'Serbia'),'Country'] = 'Republic of Serbia'
dcu.loc[(dcu.Country == 'Burma'),'Country'] = 'Myanmar'
dcu.loc[(dcu.Country == 'North Macedonia'),'Country'] = 'Macedonia'
dcu.loc[(dcu.Country == 'Korea, South'),'Country'] = 'South Korea'
dcu.loc[(dcu.Country == 'Guinea-Bissau'),'Country'] = 'Guinea Bissau'
dcu.loc[(dcu.Country == 'Czechia'),'Country'] = 'Czech Republic'
dcu.loc[(dcu.Country == 'Congo (Brazzaville)'),'Country'] = 'Republic of the Congo'
dcu.loc[(dcu.Country == 'Congo (Kinshasa)'),'Country'] = 'Democratic Republic of the Congo'
dcu.loc[(dcu.Country == "Cote d'Ivoire"),'Country'] = 'Ivory Coast'
dcu.loc[(dcu.Country == 'Bahamas'),'Country'] = 'The Bahamas'

#JSON / COVIDS
#West Bank / West Bank and Gaza
#Vanuatu / ?
#United States of America / US
#United Republic of Tanzania / Tanzania
#Taiwan / Taiwan*
#East Timor / Timor-Leste
#Turkmenistan / ?
#Tajikistan / ?
#Swaziland / Eswatini
#Republic of Serbia / Serbia
#Somaliland / ?
#Solomon Islands / ?
#North Korea / ?
#Puerto Rico / ?
#New Caledonia / ?
#Myanmar / Burma
#Macedonia / North Macedonia
#Lesotho / ?
#South Korea / Korea, South
#Greenland / ?
#Guinea Bissau / Guinea-Bissau
#Falkland Islands / ?
#Czech Republic / Czechia
#Northern Cyprus / ?
#Republic of the Congo / Congo (Brazzaville)
#Democratic Republic of the Congo / Congo (Kinshasa)
#Ivory Coast / Cote d'Ivoire
#The Bahamas / Bahamas
#French Southern and Antarctic Lands / ?
#Antarctica / ?

#Generate list noting which Countries are/are not included in the JSON for Confirmed Cases
c_in_list = []
c_not_in_list = []
for country in ccu["Country"]:
    if country in c_name_world_json:
        c_in_list.append(country)
    else:
        c_not_in_list.append(country)

#Remove entries of Countries not in the JSON for Confirmed Cases
ccu_drop = ccu
for country in c_not_in_list:
    ccu_drop = ccu_drop[~ccu_drop.Country.str.contains(country)]

#Generate list noting which States are/are not included in the JSON for Covid Deaths
d_in_list = []
d_not_in_list = []
for country in dcu["Country"]:
    if country in c_name_world_json:
        d_in_list.append(country)
    else:
        d_not_in_list.append(country)

#Remove entries of States not in the JSON for Covid Deaths
dcu_drop = dcu
for country in d_not_in_list:
    dcu_drop = dcu_drop[~dcu_drop.Country.str.contains(country)]

#Create Map
map = folium.Map(location = [40.41, 3.70], zoom_start = 2.4, tiles="Stamen Terrain", max_bounds=True)

#Create Choropleth Map for Confirmed Covid Cases
folium.Choropleth(
    geo_data = world_json,
    name = 'Infections',
    data = ccu_drop,
    columns = ['Country', 'Cases per 1000'],
    key_on = 'properties.name',
    fill_color = 'YlGnBu',
    fill_opacity = 0.85,
    line_opacity = 0.2,
    legend_name = 'Confirmed Covid-19 Infections per 1000 people'
).add_to(map)

#Create Choropleth Map for Covid Deaths
folium.Choropleth(
    geo_data = world_json,
    name = 'Deaths',
    data = dcu_drop,
    columns = ['Country', 'Deaths per 1000'],
    key_on = 'properties.name',
    fill_color = 'YlOrRd',
    fill_opacity = 0.75,
    line_opacity = 0.2,
    legend_name = 'Deaths due to Covid-19 per 1000 people'
).add_to(map)

#Add Layer Control
folium.LayerControl().add_to(map)

#Save map
map.save("World_Covid_Map.html")
