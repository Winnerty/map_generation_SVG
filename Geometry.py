from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple


class GeometryObject(ABC):
    @staticmethod
    @abstractmethod
    def FromDict(data: dict) -> 'GeometryObject':
        if data["type"] == "Point":
            return Point.FromDict(data)
        elif data["type"] == "LineString":
            return LineString.FromDict(data)
        elif data["type"] == "Polygon":
            return Polygon.FromDict(data)
        elif data["type"] in ["MultiPoint", "MultiLineString", "MultiPolygon", "GeometryCollection"]:
            return Composite.FromDict(data)

    @abstractmethod
    def bounding_box(self) -> Tuple[float, float, float, float]:
        return +float("inf"), +float("inf"), -float("inf"), -float("inf")

    def to_svg(self, classname: str) -> str:
        return "<fix>"

    def __str__(self):
        return self.to_svg("")


@dataclass
class Point(GeometryObject):
    x: float
    y: float

    @staticmethod
    def FromDict(data: dict) -> 'Point':
        coordinates = data["coordinates"]
        return Point(coordinates[0], coordinates[1])

    def bounding_box(self) -> Tuple[float, float, float, float]:
        return self.x, self.y, self.x, self.y

    def to_svg(self, classname: str) -> str:
        return f'<circle class="{classname}" cx="{self.x}" cy="{self.y}" />'


@dataclass
class LineString(GeometryObject):
    coordinates: List[Point]

    @staticmethod
    def FromDict(data: dict) -> 'LineString':
        coordinates = [Point(x, y) for x, y in data["coordinates"]]
        return LineString(coordinates)

    def bounding_box(self) -> Tuple[float, float, float, float]:
        min_x, min_y, max_x, max_y = 0, 0, 0, 0
        for i in self.coordinates:
            min_x = min(i.x, min_x)
            min_y = min(i.y, min_y)
            max_x = max(i.x, max_x)
            max_y = max(i.y, max_y)
        return min_x, min_y, max_x, max_y

    def to_svg(self, classname: str) -> str:
        s = f"<polyline class=\"{classname}\" points=\""
        for p in self.coordinates:
            s += f"{p.x},{p.y} "
        s += "\" />"
        return s


@dataclass
class Polygon(GeometryObject):
    line: LineString

    @staticmethod
    def FromDict(data: dict) -> 'Polygon':
        line = LineString([Point(x, y) for x, y in data["coordinates"][0]])
        return Polygon(line)

    def bounding_box(self) -> Tuple[float, float, float, float]:
        return self.line.bounding_box()

    def to_svg(self, classname: str) -> str:
        s = f"<polygon class=\"{classname}\" points=\""
        for p in self.line.coordinates:
            s += f"{p.x},{p.y} "
        s += "\" />"
        return s


@dataclass
class Composite(GeometryObject):
    objects: List[GeometryObject]

    @staticmethod
    def FromDict(data: dict) -> 'Composite':
        if data["type"] == "MultiPoint":
            return Composite([Point(x, y) for x, y in data["coordinates"]])
        elif data["type"] == "MultiLineString":
            return Composite([LineString([Point(x, y) for (x, y) in line]) for line in data["coordinates"]])
        elif data["type"] == "MultiPolygon":
            return Composite(
                [Polygon(LineString([Point(x, y) for (x, y) in polygon[0]])) for polygon in data["coordinates"]])
        elif data["type"] == "GeometryCollection":
            return Composite([GeometryObject.FromDict(obj) for obj in data["geometries"]])

    def bounding_box(self) -> Tuple[float, float, float, float]:
        min_x, min_y, max_x, max_y = 0, 0, 0, 0
        for obj in self.objects:
            mix, miy, mx, may = obj.bounding_box()
            min_x = min(mix, min_x)
            min_y = min(miy, min_y)
            max_x = max(mx, max_x)
            max_y = max(may, max_y)
        return min_x, min_y, max_x, max_y

    def to_svg(self, classname: str) -> str:
        s = ""
        for obj in self.objects:
            s += obj.to_svg(classname) + "\n"
        return s
