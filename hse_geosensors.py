import folium
from flask import Flask, render_template_string
from functools import partial
from shapely.geometry import shape, mapping
from shapely.ops import transform
import pyproj
import requests
from datetime import datetime, timedelta

# https://flask.palletsprojects.com/en/stable/quickstart
app = Flask(__name__)
app.config["CACHE_TYPE"] = "null"


@app.route("/")
def generate_root_page():
    # https://python-visualization.github.io/folium/latest/getting_started.html
    # m = folium.Map(location=(57.0, 39.0), tiles="cartodb darkmatter")
    m = folium.Map(location=(55.0, 37.0))

    # geojson_url = "http://192.168.117.3:5000/collections/blocks_rosnedra_lists/items?f=json&limit=1000"
    # folium.GeoJson(geojson_url).add_to(m)

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
    f"&$resultFormat=GeoJSON"

    geojson_data = requests.get(url).json()

    reproj_geojson_data = {
        "type": geojson_data["type"],
        "@iot.nextLink": geojson_data["@iot.nextLink"],
        "features": [],
    }

    source_crs = pyproj.CRS("EPSG:3857")
    target_crs = pyproj.CRS("EPSG:4326")

    project = partial(pyproj.transform, source_crs, target_crs, always_xy=True)

    for ft in geojson_data["features"]:
        orig_geom = shape(ft["geometry"])
        reproj_geom = transform(project, orig_geom)
        reproj_geojson_geom = mapping(reproj_geom)
        ft["geometry"] = reproj_geojson_geom
        reproj_geojson_data["features"].append(ft)

    folium.GeoJson(reproj_geojson_data).add_to(m)

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
# Vega-altair
# https://altair-viz.github.io/gallery/multiline_tooltip.html

if __name__ == "__main__":
    generate_root_page()