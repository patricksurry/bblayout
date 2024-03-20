from typing import Self
import svg
import sys

from collections import namedtuple
from dataclasses import dataclass


Point = namedtuple('Point', ('x', 'y'), defaults=(0, 0))

_pin_symbols = dict(
    VDD='＋',    # fullwidth plus sign
    GND='⏚'
)


def pin_symbol(name: str) -> str:
    return _pin_symbols.get(name, name)


class Component:
    registry: dict[str, tuple[type[Self], dict]] = {}
    created: set[str] = set()

    def __init__(
            self,
            name: str,
            shape: Point,
            padding=Point(0.5, 0.5),
            at=Point(),
            rotated=False,
            description: str='',
            tags: list[str] = []
    ):
        self.name = name
        self.shape = shape
        self.padding = padding
        self.at = at
        self.rotated = rotated
        self.description = description
        self.tags = tags

    def __matmul__(self, at: Point):
        self.at = at
        return self

    def __imatmul__(self, at: Point):
        self.at = at
        return self

    @classmethod
    def register(cls, name, **kwargs):
        Component.registry[name] = (cls, kwargs)

    @staticmethod
    def new(name, aka=''):
        if name not in Component.registry:
            print("Unknown component", name)
            print("All components", list(Component.registry.keys()))
            sys.exit()
        kls, d = Component.registry[name]
        aka = aka or name
        n = 1
        while aka in Component.created:
            n += 1
            aka = aka.rsplit('-', 1)[0] + f"-{n}"
        Component.created.add(aka)
        return kls(aka, **d)

    def viewbox(self):     # xmin, xmax, ymin, ymax
        return (
            Point(
                self.at.x - self.padding.x,
                self.at.y - self.padding.y,
            ),
            Point(
                self.shape.x + 2*self.padding.x,
                self.shape.y + 2*self.padding.y,
            )
        )

    def draw(self):
        t = [svg.Translate(self.at.x, self.at.y)]
        if self.rotated:
            t.append(svg.Rotate(180))
        return svg.G(
            class_=['component', self.__class__.__name__.lower(), self.name],
            transform=t,
            elements=[
                svg.Rect(
                    x=-self.padding.x,
                    y=-self.padding.y,
                    width=self.shape.x + 2*self.padding.x,
                    height=self.shape.y + 2*self.padding.y,
                ),
            ]
        )


@dataclass
class Wire:
    p: Point
    q: Point
    color: str = ''

    def draw(self):
        return svg.Line(x1=self.p.x, y1=self.p.y, x2=self.q.x, y2=self.q.y, class_=['wire']),


@dataclass
class Pin:
    number: int
    name: str
    at: Point

    def __matmul__(self, at: Point):
        return Pin(self.number, self.name, Point(self.at.x + at.x, self.at.y + at.y))


@dataclass
class Tie:
    name: str
    at: Point
    rail: int

    def __matmul__(self, at: Point):
        return Tie(self.name, Point(self.at.x + at.x, self.at.y + at.y), self.rail)

    def __sub__(self, other: Self):
        return Wire(self.at, other.at)
