import json
import Geometry
import Map
import chevron
import sys
from pathlib import Path


def count_items(data):
    type = data['type']
    # if the type is a multi* type, then we need to count the number of items in the coordinates array
    if type in ["MultiPolygon", "MultiLineString", "MultiPoint"]:
        return len(data['coordinates'])
    # if the type is a *Collection type, then we need to count recursively the number of items in the geometries array
    elif type == "GeometryCollection":
        s = 0
        for x in data['geometries']:
            s += count_items(x)
        return s
    else:
        return 1


def map_summary(filename):
    with open(filename, 'r') as f:
        data = json.load(f)

    for feature in data['features']:
        id = feature['id']
        type = feature['type']
        count = count_items(feature)
        myobj = Geometry.GeometryObject.FromDict(feature)
        print(f"Feature {id} is a {type} with {count} items.")
        print("It's value is", myobj)


def settings(path):
    print(path)
    map = Map.Map.LoadFromGeoJson(path)
    x1, y1, x2, y2 = map.bounding_box()
    data = {
        "classes": [Map.Wall, Map.River, Map.Plank, Map.Building, Map.Prism, Map.Square, Map.Green, Map.Field,
                    Map.Tree, Map.District, Map.Water, Map.Earth, Map.Road],
        "bbox": {
            "x": x1,
            "y": y1,
            "width": x2 - x1,
            "height": y2 - y1,
        },
        "items": map.items,
    }
    output = chevron.render(open("map-template.svg"), data)
    open(path.with_suffix('.svg'), "w").write(output)


folder = sys.argv[1]
p = Path(folder)
filelists = [file for file in p.iterdir() if file.suffix == ".json"]
for file in filelists:
    settings(file)
