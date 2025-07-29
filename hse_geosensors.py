import folium
from flask import Flask, render_template_string
from functools import partial
from shapely.geometry import shape, mapping
from shapely.ops import transform
import pyproj
import requests
from datetime import datetime, timedelta
import json

# https://flask.palletsprojects.com/en/stable/quickstart
app = Flask(__name__)
app.config["CACHE_TYPE"] = "null"


@app.route("/")
def generate_root_page():
    # https://python-visualization.github.io/folium/latest/getting_started.html
    # m = folium.Map(location=(57.0, 39.0), tiles="cartodb darkmatter")
    m = folium.Map(location=(55.650443, 37.501211), zoom_start=14)

    # https://fraunhoferiosb.github.io/FROST-Server/
    url = f"http://94.154.11.74/frost/v1.1/Locations?" \
    f"$expand=Things(" \
        f"$expand=MultiDatastreams(" \
            f"$expand=Observations(" \
                f"$top=100;" \
                f"$count=true;" \
                f"$orderby=phenomenonTime desc;" \
                f"$filter=phenomenonTime ge {(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')}T00:00:00%2B03:00" \
            f")" \
        f")" \
    f")" \
    # f"&$resultFormat=GeoJSON" # for the GeoJSON option

    source_crs = pyproj.CRS("EPSG:3857")
    target_crs = pyproj.CRS("EPSG:4326")

    project = partial(pyproj.transform, source_crs, target_crs, always_xy=True)
    
    ###################
    # # GeoJSON option
    ###################
    # geojson_data = requests.get(url).json()
    # pass
    # reproj_geojson_data = {
    #     "type": geojson_data["type"],
    #     "@iot.nextLink": geojson_data["@iot.nextLink"],
    #     "features": [],
    # }

    # for ft in geojson_data["features"]:
    #     orig_geom = shape(ft["geometry"])
    #     reproj_geom = transform(project, orig_geom)
    #     reproj_geojson_geom = mapping(reproj_geom)
    #     ft["geometry"] = reproj_geojson_geom
    #     reproj_geojson_data["features"].append(ft)

    # for gj_feature in reproj_geojson_data["features"]:
    #     gj = folium.GeoJson(gj_feature)
    #     gj.add_child(folium.Popup("outline Popup on GeoJSON"))
    #     gj.add_to(m)
    ############################
    ###end of geojson option####
    ############################ 
    
    ###############
    # JSON option
    ###############
    
    json_data = requests.get(url).json()
    pass

    # http://94.154.11.74/frost/v1.1/MultiDatastreams('RudnMeteoRawDataMultiStream')/description
    obs_props = [
        # {"name": "timestamp", "desc": "timestamp"},
        {"name": "Dn", "desc": "minimum value for wind direction"},
        {"name": "Dm", "desc": "average value for wind direction"},
        {"name": "Dx", "desc": "maximum value for wind direction"},
        {"name": "Sn", "desc": "minimum value for wind speed"},
        {"name": "Sm", "desc": "average wind speed"},
        {"name": "Sx", "desc": "maximum value for wind speed"},
        {"name": "Ta", "desc": "air temperature (0C)"},
        {"name": "Ua", "desc": "air humidity (%)"},
        {"name": "Pa", "desc": "atmospheric pressure (hPa)"},
        {"name": "Rc", "desc": "precipitation (mm)"}
    ]
    
    for location in json_data.get("value"):
        reproj_geom = transform(project, shape(location.get("location")))
        reproj_gj_geom = json.loads(json.dumps(mapping(reproj_geom)))   # this is to convert coord pairs from tuples to lists
        gj = folium.GeoJson({"type": "Feature", "geometry": reproj_gj_geom, "properties": {}})
        
        for thing in location["Things"]:
            for mdstream in thing.get("MultiDatastreams"):
                pass
                values = [
                    {
                        k: v
                        for k, v in zip(
                            [x["name"] for x in [{"name": "timestamp", "desc": "timestamp"}] + obs_props],
                            [obs["phenomenonTime"]] + obs["result"],
                        )
                    }
                    for obs in mdstream["Observations"]
                ]
                values = values[::-1]
                pass
                
                values = []
                for obs in mdstream["Observations"]:
                    for i, prop in enumerate(obs_props):
                        values.append(
                            {
                                "timestamp": obs["phenomenonTime"],
                                "prop": prop["name"],
                                "prop_desc": prop["desc"],
                                "value": obs['result'][i]
                            }
                        )
                pass
                    
            
            
                # values = []
                # for obs in mdstream['Observations']:

                # https://vega.github.io/vega-lite/tutorials/getting_started.html
                # https://vega.github.io/vega-lite/tutorials/explore.html
                vega_lite_diagram = {
                    "data": {
                        "values": values
                    },
                    "mark": "line",
                    "encoding": {
                        # https://vega.github.io/vega-lite/docs/format.html#temporal-data
                        "x": {
                            "bin": False,  # это если надо дискретизировать по интервалам
                            # "timeUnit": "day", # это чтобы посчитать среднемноголетнее по месяцам https://vega.github.io/vega-lite/docs/timeunit.html
                            "field": "timestamp", "type": "temporal",
                            "title": "Время"
                        },
                        "y": {
                            # "aggregate": "mean", # это нужно, если используем timeUnit или bin
                            "field": "value", 
                            "type": "quantitative"                            
                        },
                        "color": {"field": "prop", "type": "nominal"}
                    },
                    "transform": [  # https://vega.github.io/vega-lite/docs/transform.html
                        {"filter": {"field": "value", "gt": 0}}
                    ]
                }
                pass
                # https://python-visualization.github.io/folium/latest/reference.html#folium.features.VegaLite
                vega_lite = folium.VegaLite(
                    vega_lite_diagram, width="1000", height="100%"
                )
                popup = folium.Popup()
                vega_lite.add_to(popup)
                popup.add_to(gj)

        # gj.add_child(folium.Popup("outline Popup on GeoJSON"))
        gj.add_to(m)
        
    ############################
    ###end of json option####
    ############################    
    
    # folium.GeoJson(reproj_geojson_data).add_to(m)

    m.save("output/index.htm")

    return render_template_string(m._repr_html_())


# для запуска тестового сервера выполнить команду
# ./.venv/Scripts/python.exe -m flask --app hse_geosensors run


# инструкции
# https://www.bing.com/search?pglt=299&q=how+to+create+web+map+with+changing+data+using+python&cvid=401ee5b3872143eda01bf1448ec19412&gs_lcrp=EgRlZGdlKgYIABBFGDkyBggAEEUYOdIBCTMyNjA5ajBqMagCCLACAQ&FORM=ANNTA1&PC=U531
# https://flask.palletsprojects.com/en/stable/quickstart/#a-minimal-application
# дальнейшие инструкции
# https://flask.palletsprojects.com/en/stable/quickstart


# useful links
# https://shapely.readthedocs.io/en/2.1.1/manual.html#shapely.geometry.mapping
# https://python-visualization.github.io/folium/latest/reference.html
# https://pyproj4.github.io/pyproj/stable/examples.html
# https://www.google.com/search?q=python+shapely+reproject+geojson&sca_esv=952a6d257a96d14c&ei=mkGCaMCaNvOXjgbZ69-JBg&ved=0ahUKEwjAz7bs2NWOAxXzi8MKHdn1N2EQ4dUDCBA&uact=5&oq=python+shapely+reproject+geojson&gs_lp=Egxnd3Mtd2l6LXNlcnAiIHB5dGhvbiBzaGFwZWx5IHJlcHJvamVjdCBnZW9qc29uMgUQABjvBTIFEAAY7wUyCBAAGIAEGKIEMggQABiABBiiBDIFEAAY7wVIhhdQ7AhYvBVwAXgAkAEAmAGpAaAB1wmqAQMwLjm4AQPIAQD4AQGYAgigAuIHwgIKEAAYsAMY1gQYR8ICBhAAGA0YHsICCxAAGIAEGIYDGIoFmAMAiAYBkAYFkgcDMS43oAfwIrIHAzAuN7gH2gfCBwUwLjYuMsgHFg&sclient=gws-wiz-serp
# https://fraunhoferiosb.github.io/FROST-Server/sensorthingsapi/requestingData/STA-ResultFormats.html
# https://fraunhoferiosb.github.io/FROST-Server/sensorthingsapi/requestingData/STA-ResultFormats.html


# Проблема: почему flask приложение не обновляется после изменения кода?!

# диаграммы в попапах Folium
# https://python-visualization.github.io/folium/latest/user_guide/ui_elements/popups.html
# https://python-visualization.github.io/folium/latest/reference.html#folium.features.VegaLite
# https://vega.github.io/vega-lite/tutorials/explore.html

# Vega-altair
# https://altair-viz.github.io/gallery/multiline_tooltip.html

if __name__ == "__main__":
    generate_root_page()