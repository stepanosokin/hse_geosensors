import folium
from flask import Flask, render_template_string

# https://flask.palletsprojects.com/en/stable/quickstart
app = Flask(__name__)

@app.route("/")
def hello_world():
    # https://python-visualization.github.io/folium/latest/getting_started.html
    m = folium.Map(location=(57.0, 39.0), tiles="cartodb darkmatter")

    geojson_url = "http://192.168.117.3:5000/collections/blocks_rosnedra_lists/items?f=json&limit=1000"
    folium.GeoJson(geojson_url).add_to(m)
    return render_template_string(m._repr_html_())

# m.save('output/index.htm')

# для запуска тестового сервера выполнить команду 
# ./.venv/Scripts/python.exe -m flask --app hse_geosensors run


# инструкции
# https://www.bing.com/search?pglt=299&q=how+to+create+web+map+with+changing+data+using+python&cvid=401ee5b3872143eda01bf1448ec19412&gs_lcrp=EgRlZGdlKgYIABBFGDkyBggAEEUYOdIBCTMyNjA5ajBqMagCCLACAQ&FORM=ANNTA1&PC=U531
# https://flask.palletsprojects.com/en/stable/quickstart/#a-minimal-application
# дальнейшие инструкции 
# https://flask.palletsprojects.com/en/stable/quickstart