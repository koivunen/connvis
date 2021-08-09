from flask import Flask, request, send_from_directory, jsonify, render_template, Response
import folium
import threading
import random
import sys
import math
import geojson
from geojson import Feature, Point, FeatureCollection

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')


@app.route('/folium')
def index():
    start_coords = (46.9540700, 142.7360300)
    folium_map = folium.Map(location=start_coords, zoom_start=14)
    return folium_map._repr_html_()


import connections
@app.route('/ipinfo.json')
def ipinfo():
    return jsonify({        "activity": connections.getIPActivity()    })

@app.route('/geo.json')
def geodata():
    features = []
    features.append(Feature(properties={
        "id": "1",
        "ip": "10.0.0.0",
        "asnname": "localhost",
    },geometry=Point((random.random() * 360 - 180, random.random() * 360 - 180))))
    features.append(Feature(properties={    
        "id": "2",
        "ip": "10.0.0.1",
        "asnname": "localhost2",
    },geometry=Point((random.random() * 360 - 180, random.random() * 360 - 180))))

    data = FeatureCollection(features)

    return Response(
            response=geojson.dumps(data, sort_keys=False),
            mimetype='application/json',
            status=200) 


@app.route('/sankey.json')
def sankeyjson():
    return jsonify({
        "nodes": [{
            "id": "101"
        }, {
            "id": "102"
        }, {
            "id": "103"
        }, {
            "id": "104"
        }, {
            "id": "105"
        }, {
            "id": "106"
        }, {
            "id": "107"
        }, {
            "id": "1.1.1.1"
        }],
        "links": [{
            "source": "101",
            "target": "1.1.1.1",
            "value": 1
        }]
    })


@app.route("/")
def main():
    return render_template("hello.html")


def run(use_reloader=False):
    app.run(debug=True, host='0.0.0.0', use_reloader=use_reloader)


if __name__ == "__main__":
    run(use_reloader=True)


def run_threaded():
    threading.Thread(target=run).start()