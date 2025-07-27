import folium
from functools import partial
from shapely.geometry import shape, mapping
from shapely.ops import transform
import pyproj
import requests



# https://python-visualization.github.io/folium/latest/getting_started.html
# m = folium.Map(location=(57.0, 39.0), tiles="cartodb darkmatter")
m = folium.Map(location=(55.6, 37.5))

# geojson_url = "http://192.168.117.3:5000/collections/blocks_rosnedra_lists/items?f=json&limit=1000"
# folium.GeoJson(geojson_url).add_to(m)

url = "http://94.154.11.74/frost/v1.1/Locations?    \
$expand=Things($expand=MultiDatastreams(    \
    $expand=Observations(\
        $top=100;\
        $count=true;\
        $orderby=phenomenonTime desc;\
        $filter=phenomenonTime ge 2025-07-23T00:00:00%2B03:00)))\
&$resultFormat=GeoJSON"    
geojson_data = requests.get(url).json()
reproj_geojson_data = {
    "type": geojson_data["type"], 
    "@iot.nextLink": geojson_data["@iot.nextLink"],
    "features": []
    }

source_crs = pyproj.CRS("EPSG:3857")
target_crs = pyproj.CRS("EPSG:4326")
project = partial(
    pyproj.transform,
    source_crs,
    target_crs,
    always_xy=True
)
for ft in geojson_data['features']:
    
    orig_geom = shape(ft['geometry'])
    reproj_geom = transform(project, orig_geom)
    reproj_geojson_geom = mapping(reproj_geom)
    ft['geometry'] = reproj_geojson_geom
    reproj_geojson_data["features"].append(ft)

folium.GeoJson(reproj_geojson_data).add_to(m)
    
    
   

m.save('output/index.htm')

# для запуска тестового сервера выполнить команду 
# ./.venv/Scripts/python.exe -m flask --app hse_geosensors run


# инструкции
# https://www.bing.com/search?pglt=299&q=how+to+create+web+map+with+changing+data+using+python&cvid=401ee5b3872143eda01bf1448ec19412&gs_lcrp=EgRlZGdlKgYIABBFGDkyBggAEEUYOdIBCTMyNjA5ajBqMagCCLACAQ&FORM=ANNTA1&PC=U531
# https://flask.palletsprojects.com/en/stable/quickstart/#a-minimal-application
# дальнейшие инструкции 
# https://flask.palletsprojects.com/en/stable/quickstart