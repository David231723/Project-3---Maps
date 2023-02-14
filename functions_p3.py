# PROJECT 3

import pandas as pd 

import geopandas as gdp
from cartoframes.viz import Map, Layer, popup_element

import folium
from folium import Choropleth, Circle, Marker, Icon, Map
from folium.plugins import HeatMap, MarkerCluster

import requests

from pymongo import MongoClient
from pymongo import GEOSPHERE
import json

client = MongoClient("localhost:27017")
client.list_database_names()


# Mongodb collection 

def setting_db_collection():
    db = client["Ironhack"]
    c = db.get_collection("companies")

# Exploring_business_categories

def explore_categories():
    print(c.distinct("category_code"))
    print("Number of gaming companies: ",len(list(c.find({"category_code": "games_video"}))))
    print("---------------------------------------------------------------------------------")
    print("Number of design companies: ",len(list(c.find({"category_code": "design"}))))

def design_explore():
    filter1 = {"category_code": "design"}
    projection1 = {"_id": 0, "name": 1,
               "offices.country_code":1,
               "offices.latitude":1,
               "offices.longitude":1 }

    design_list = list(c.find(filter1 , projection1).sort("number_of_employees",-1).limit(10))

    filter1 = {"category_code": "design","offices.country_code":"USA"}
    projection1 = {"_id": 0, "name": 1,
               "offices.country_code":1,
               "offices.latitude":1,
               "offices.longitude":1 }

    design_list_USA = list(c.find(filter1 , projection1).sort("number_of_employees",-1).limit(10))

# Converting data into readable df
def convert_df():
    df_design = pd.DataFrame(design_list_USA)
    df_design = df_design.explode('offices')
    df_design = df_design.merge(df_design['offices'].apply(pd.Series), left_index=True, right_index=True)
    df_design = df_design[['name', 'country_code','latitude', 'longitude']]

# Transforming df

def df_transformation():
    df_design_USA = df_design[df_design["country_code"] == "USA"]
    df_design_USA.drop_duplicates(inplace=True)
    df_design_USA.dropna(inplace=True)

# First map 

def exploratory_map():

    us_lat = 37.795531
    us_lon = -122.400598

    us_map = Map(location=[us_lat, us_lon], zoom_start = 5)

    # Convert the dataframe to a GeoDataFrame
    gdf = gdp.GeoDataFrame(df_design_USA, geometry=gdp.points_from_xy(df_design_USA.longitude, df_design_USA.latitude))
    # Create a folium map centered in Barcelona
    us_map = folium.Map(location=[us_lat, us_lon], zoom_start=4.4)
    # Loop through each row of the GeoDataFrame and add a marker for each coffee shop
    for idx, row in gdf.iterrows():
        folium.Marker(location=[row.latitude, row.longitude],
                    popup=row['name']).add_to(us_map)
    # Display the map
    us_map

# Look for nearby companies

def near_by_companies():
    filter1 = {"offices.country_code":"USA", "offices.state_code": "CA"}

    projection1 = {"_id": 0, "name": 1,
                "offices.state_code":1,
                "total_money_raised":1,
                "offices.latitude":1,
                "offices.longitude":1}

    CA_companies = list(c.find(filter1 , projection1).sort("number_of_employees",-1))

# Transform list

def transform_list():
    df_1 = pd.DataFrame(CA_companies)
    df_1 = df_1.explode('offices')
    df_1 = df_1.reset_index(drop=True)
    df_2 = pd.DataFrame(df_1['offices'].tolist())
    df_merged = pd.merge(df_1, df_2, left_index=True, right_index=True)

    df = df_merged[df_merged["state_code"] == "CA"]
    df.drop(columns=["offices"], inplace=True)
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True ,inplace=True)

# map of all the CA companies

def ca_map():
    ca_lat = 37.795531
    ca_lon = -122.400598

    ca_map = Map(location=[ca_lat, ca_lon], zoom_start = 5)
    #us_map


    # Convert the dataframe to a GeoDataFrame
    ca_1 = gdp.GeoDataFrame(df, geometry=gdp.points_from_xy(df.longitude, df.latitude))

    # Create a folium map centered in California
    ca_map = folium.Map(location=[ca_lat, ca_lon], zoom_start=4.75)

    # Loop through each row of the GeoDataFrame and add a marker for each coffee shop
    for idx, row in ca_1.iterrows():
        folium.Marker(location=[row.latitude, row.longitude],
                    popup=row['name']).add_to(ca_map)
    # Display the map
    ca_map

# Filtering by distance

def distance_filter():
    my_location = [ 37.795531, -122.400598]

    def type_point (list_):
        formatted_dict_ = {"type": "Point", "coordinates": list_}
        return formatted_dict_

    max_distance = 500
    converted_location = type_point(my_location)

    # math 

    import math
    def haversine(coord1, coord2):
 
        # Coordinates in decimal degrees (e.g. 2.89078, 12.79797)
        lon1, lat1 = coord1
        lon2, lat2 = coord2

        R = 6371000  # radius of Earth in meters
        phi_1 = math.radians(lat1)
        phi_2 = math.radians(lat2)

        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        meters = R * c  # output distance in meters
        km = meters / 1000.0  # output distance in kilometers

        meters = round(meters, 3)
        km = round(km, 3)

        return meters

    df['Distance_meters'] = df.apply(lambda x: haversine ([x['longitude'],x['latitude']],[-122.400598, 37.795531]),axis=1)

    close_companies = df[df['Distance_meters'] <= 500]
    close_companies.sort_values(by=['Distance_meters'],inplace=True)
# Map companies nearby

def nearby_map():
    sa_lat = 37.795531
    sa_lon = -122.400598

    sa_map = Map(location=[sa_lat, sa_lon], zoom_start = 5)
    #us_map


    # Convert the dataframe to a GeoDataFrame
    sa_1 = gdp.GeoDataFrame(close_companies, geometry=gdp.points_from_xy(close_companies.longitude, close_companies.latitude))

    # Create a folium map centered in California
    sa_map = folium.Map(location=[sa_lat, sa_lon], zoom_start=17)

    # Loop through each row of the GeoDataFrame and add a marker for each coffee shop
    for idx, row in sa_1.iterrows():
        folium.Marker(location=[row.latitude, row.longitude],
                    popup=row['name']).add_to(sa_map)
    # Display the map
    sa_map

# Getting Nearby places

def nearby_places():
    from getpass import getpass
    token = getpass()

    url = "https://api.foursquare.com/v3/places/search?query=starbucks&ll=37.795531%2C-122.400598&sort=DISTANCE&limit=5"

    headers = {
        "accept": "application/json",
        "Authorization": f"{token}"
    }

    response = requests.get(url, headers=headers)

    print(response.text)

    coordinates = response.json()["results"][0]["geocodes"]["main"]

    lat, lon = coordinates["latitude"], coordinates["longitude"]
    
    name = response.json()["results"][0]["name"]

    def name_coordinates (dict_):
    
        processed_dict = {"name": dict_["name"],
                        "lat": dict_["geocodes"]["main"]["latitude"],
                        "lon": dict_["geocodes"]["main"]["longitude"]}
        
        return processed_dict

    new_list = []
    for i in response.json()["results"]:
        new_list.append(name_coordinates(i))
    
    close_5_starbucks = pd.DataFrame(new_list)

    # Schools

    url = "https://api.foursquare.com/v3/places/search?query=Preschool&ll=37.795531%2C-122.400598&sort=DISTANCE&limit=3"

    headers = {
        "accept": "application/json",
        "Authorization": f"{token}"
    }

    response = requests.get(url, headers=headers)

    print(response.text)

    kinder_list = []
    for i in response.json()["results"]:
        kinder_list.append(name_coordinates(i))
    kinder_list

    close_kinder = pd.DataFrame(kinder_list)

    url = "https://api.foursquare.com/v3/places/search?query=nightclub&ll=37.795531%2C-122.400598&sort=DISTANCE&limit=3"

    headers = {
        "accept": "application/json",
        "Authorization": f"{token}"
    }

    response = requests.get(url, headers=headers)

    club_list = []
    for i in response.json()["results"]:
        club_list.append(name_coordinates(i))

    pub = pd.DataFrame(club_list)

    url = "https://api.foursquare.com/v3/places/search?query=VeganRestaurant&ll=37.795531%2C-122.400598&sort=DISTANCE&limit=3"

    headers = {
        "accept": "application/json",
        "Authorization": f"{token}"
    }

    response = requests.get(url, headers=headers)

    print(response.text)
    
    vegan_list = []
    for i in response.json()["results"]:
        vegan_list.append(name_coordinates(i))
    vegan_list

    vegan = pd.DataFrame(vegan_list)

    # Vegan

    vegan['type'] = vegan['type'] = 'vegan'
    vegan.drop([1], inplace=True)

    # Pub

    pub['type'] = pub['type'] = 'pub'
    pub.drop([0], inplace=True)
    pub.drop([2], inplace=True)

    # kinder

    close_kinder['type'] = close_kinder['type'] = 'kindergarden'
    close_kinder.drop([0,2], inplace=True)

    # Starbucks

    close_5_starbucks['type'] = close_5_starbucks['type'] = 'coffe'

    new_df = pd.concat([close_kinder, vegan], axis=0)
    df_def = pd.concat([new_df,pub],axis=0)
    df_2 = pd.concat([df_def,close_5_starbucks],axis=0, ignore_index=True)

    design_df = close_companies[close_companies['name'] == '99designs']
    design_df = design_df.rename(columns={'latitude': 'lat', 'longitude': 'lon'})  # old method
    design_df['type'] = design_df['type'] = 'design_company' 
    design_df.drop(['total_money_raised','state_code','geometry','Distance_meters'],axis=1,inplace=True)

    df_3 = pd.concat([df_2,design_df],axis=0, ignore_index=True)

    webly_df = close_companies[close_companies['name'] == 'BrightRoll']
    webly_df = webly_df.rename(columns={'latitude': 'lat', 'longitude': 'lon'})  # old method
    webly_df['type'] = webly_df['type'] = 'new_venue' 
    webly_df.drop(['total_money_raised','state_code','geometry','Distance_meters'],axis=1,inplace=True)

    df_vf = pd.concat([df_3,webly_df],axis=0, ignore_index=True)

# Final Map

def final_map():
    us_lat = 37.795531
    us_lon = -122.400598

    def_map = Map(location=[us_lat, us_lon], zoom_start = 17)

    for index, row in df_vf.iterrows():
        
        #1. MARKER without icon
        district = {"location": [row["lat"], row["lon"]], "tooltip": row["name"]}
        
        #2. Icon
        if row["type"] == "new_venue":        
            icon = Icon (
                color="blue",
                opacity = 0.6,
                prefix = "fa",
                icon="briefcase",
                icon_color = "white",
                radius=45
            )
        elif row["type"] == "pub":
            icon = Icon (
                color="red",
                opacity = 0.6,
                prefix = "fa",
                icon="beer",
                icon_color = "yellow"
            )
        elif row["type"] == "coffe":
            icon = Icon (
                color="darkgreen",
                opacity = 0.6,
                prefix = "fa",
                icon="coffee",
                icon_color = "white"
            )
        elif row["type"] == "kindergarden":
            icon = Icon (
                color="darkpurple",
                opacity = 0.6,
                prefix = "fa",
                icon="school",
                icon_color = "white"
            )
        
        elif row["type"] == "design_company":
            icon = Icon (
                color="orange",
                opacity = 0.6,
                prefix = "fa",
                icon="pen",
                icon_color = "white"
                
            )
        
        else:
            icon = Icon (
                color="green",
                opacity = 0.6,
                prefix = "fa",
                icon="leaf",
                icon_color = "white",
                icon_size=(35, 35)
            )
        #3. Marker
        new_marker = Marker(**district, icon = icon, radius = 2)
        
        #4. Add the Marker
        new_marker.add_to(def_map)

    def_map