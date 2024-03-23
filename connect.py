from dataclasses import dataclass, field
from collections import namedtuple
from typing import Self
from typing_extensions import TYPE_CHECKING
import svg
from math import sqrt


if TYPE_CHECKING:
    from component import Component


Point = namedtuple('Point', ('x', 'y'), defaults=(0, 0))


def distance(p: Point, q: Point):
    return sqrt(pow(p.x-q.x, 2) + pow(p.y-q.y, 2))


@dataclass(frozen=True)
class Connectable:
    owner: 'Component'
    name: str
    at_local: Point

    def __sub__(self, other: Self, color='black'):
        return Wire(self, other, color)

    @property
    def at_global(self):
        return self.owner.transform(self.at_local)


@dataclass(frozen=True)
class Tie(Connectable):
    rail: int


@dataclass(frozen=True)
class Pin(Connectable):
    number: int

    _symbols = dict(
        VDD='＋',    # fullwidth plus sign
        GND='⏚'
    )

    def __matmul__(self, tie: Tie):
        return (self, tie)

    @property
    def symbol(self) -> str:
        return Pin._symbols.get(self.name, self.name)


class Wire:
    def __init__(self, a: Connectable, b: Connectable, color='black'):
        self.color = color
        self.ends = (a, b)
        self.pts = a.at_global, b.at_global

    @staticmethod
    def zip(starts: list[Connectable], ends: list[Connectable], **kwargs):
        return [Wire(a, b, **kwargs) for (a,b) in zip(starts, ends)]

    def draw(self):
        p1, p2 = self.pts
        return svg.Line(x1=p1.x, y1=p1.y, x2=p2.x, y2=p2.y, stroke=self.color, class_=['wire'])


@dataclass
class ConnectedGroup:
    connectables: list[Connectable] = field(default_factory=list)
