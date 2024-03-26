import json
from abc import ABC
from dataclasses import dataclass
from typing import List, Tuple, ClassVar
from Geometry import GeometryObject


@dataclass
class MapElement(ABC):
    geometry: GeometryObject
    stroke: ClassVar[str] = "black"
    stroke_width: ClassVar[float] = 1
    fill: ClassVar[str] = "none"
    marker: ClassVar[str] = "none"
    filter: ClassVar[str] = "none"
    z_order: ClassVar[float] = 0

    def __str__(self):
        return self.geometry.to_svg(self.__class__.__name__)

    @staticmethod
    def FromDict(data: dict) -> 'MapElement':
        g = GeometryObject.FromDict(data)
        if data["id"] == "earth":
            return Earth(geometry=g)
        if data["id"] == "rivers":
            return River(geometry=g)
        if data["id"] == "walls":
            return Wall(geometry=g)
        if data["id"] == "planks":
            return Plank(geometry=g)
        if data["id"] == "roads":
            return Road(geometry=g)
        if data["id"] == "buildings":
            return Building(geometry=g)
        if data["id"] == "prisms":
            return Prism(geometry=g)
        if data["id"] == "squares":
            return Square(geometry=g)
        if data["id"] == "greens":
            return Green(geometry=g)
        if data["id"] == "fields":
            return Field(geometry=g)
        if data["id"] == "trees":
            return Tree(geometry=g)
        if data["id"] == "districts":
            return District(geometry=g)
        if data["id"] == "water":
            return Water(geometry=g)

    def bounding_box(self) -> Tuple[float, float, float, float]:
        return self.geometry.bounding_box()


class Earth(MapElement):
    pass


class River(MapElement):
    stroke = "#779988"
    pass


class Wall(MapElement):
    stroke = "#606661"
    marker = "url(#wall)"
    pass


class Plank(MapElement):
    stroke = "#FFF2C8"
    pass


class Road(MapElement):
    stroke = "#FFF2C8"
    z_order = 1
    pass


class Building(MapElement):
    fill = "#D6A36E"
    filter = "url(#shadow)"
    pass


class Prism(MapElement):
    pass


class Square(MapElement):
    fill = "#F2F2DA"
    pass


class Green(MapElement):
    stroke = "#99AA77"
    fill = "url(#green)"
    pass


class Field(MapElement):
    stroke = "#99AA77"
    fill = "url(#green)"
    pass


class Tree(MapElement):
    fill = "#667755"
    pass


class District(MapElement):
    stroke = "none"
    pass


class Water(MapElement):
    fill = "#779988"
    pass


@dataclass
class Map:
    items: List[MapElement]

    @staticmethod
    def LoadFromGeoJson(filename: str) -> 'Map':
        items = []
        roads = []
        with open(filename, 'r') as f:
            data = json.load(f)
        for feature in data['features']:
            if feature['id'] == "values":
                Road.stroke_width = feature['roadWidth']
                Wall.stroke_width = feature['roadWidth']
                if 'riverWidth' in data['features'][0]:
                    River.stroke_width = feature['riverWidth']
            elif feature['id'] == "roads":
                roads.append(MapElement.FromDict(feature))
            else:
                items.append(MapElement.FromDict(feature))
            items += roads
        return Map(items)

    def bounding_box(self) -> Tuple[float, float, float, float]:
        min_x, min_y, max_x, max_y = 0, 0, 0, 0
        for obj in self.items:
            if isinstance(obj, District):
                mix, miy, mx, may = obj.bounding_box()
                min_x = min(mix, min_x)
                min_y = min(miy, min_y)
                max_x = max(mx, max_x)
                max_y = max(may, max_y)
        delta_x = (max_x - min_x) / 5
        delta_y = (max_y - min_y) / 5
        return min_x - delta_x, min_y - delta_y, max_x + delta_x, max_y + delta_y
