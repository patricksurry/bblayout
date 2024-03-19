from collections import namedtuple
from dataclasses import dataclass
import svg


Point = namedtuple('Point', ('x', 'y'), defaults=(0, 0))


css = """
text {
    stroke: none;
    fill: #ccc;
    font-size: 0.7px;
    font-family: Sans,Arial;
    alignment-baseline: central;
}
text.rhs {
    text-anchor: end;
}
.component {
    fill: none;
    stroke: grey;
    stroke-width: 0.1;
}
.component.dip {
    fill: #333;
}
.polarity-mark {
    fill: #111;
    stroke: none;
}
.BB .groove {
    fill: #eee;
}
"""


class Component:
    def __init__(self, name: str, shape: Point, padding=Point(0.5, 0.5)):
        self.name = name
        self.shape = shape
        self.padding = padding

    def draw(self, at=Point(), rotated=False):
        return svg.G(
            class_=['component', self.__class__.__name__.lower(), self.name],
            transform=[svg.Translate(at.x, at.y), svg.Rotate(180 if rotated else 0)],
            elements=[
                svg.Rect(
                    x=-self.padding.x,
                    y=-self.padding.y,
                    width=self.shape.x + 2*self.padding.x,
                    height=self.shape.y + 2*self.padding.y,
                ),
            ]
        )

class Breadboard(Component):
    """
    breadboard has 64 rows of 5 + 5
    3 units between inner pins across groove
    7 units between outer pins across a rail
    |. o o o o o | | o o o o o .|. o o .|. o ...

    vertically rail skips 2, 10 groups of 5 + 1, skip 2
    |. . . o o o o o . o o o o o . ...
    """
    def __init__(self):
        super().__init__('BB', Point(11, 63), Point(1.5, 1.5))

    def draw(self, at=Point(), rotated=False):
        g = super().draw(at, rotated)

        g.elements.append(svg.Rect(
            x=5, y=-self.padding.y,
            width=1, height=self.shape.y + 2*self.padding.y,
            class_=['groove']
        ))
        g.elements += [
            svg.Rect(
                width=0.4, height=0.4,
                x=col-0.2, y=row-0.2,
                class_=['tie']
            )
            for row in range(64)
            for col in range(12)
            if col not in (5,6)
        ]
        return g


@dataclass
class Pin:
    number: int
    name: str
    at: Point


class DIP(Component):
    def __init__(self, name: str, picture: str, width: int, padding=Point(0, 0.5)):
        pairs = [
            line.strip().split()
            for line in picture.strip().splitlines()
        ]
        super().__init__(name,  Point(width, len(pairs)-1), padding)
        names = [left for (left, _) in pairs] + [right for (_, right) in reversed(pairs)]
        self.pinmap = {
            name: Pin(i+1, name, Point(
                0 if i <= self.shape.y else self.shape.x,
                i if i <= self.shape.y else 2*self.shape.y + 1 - i
            ))
            for i, name in enumerate(names)
        }

    def draw(self, at=Point(), rotated=False):
        g = super().draw(at, rotated)
        g.elements.append(
            svg.Path(class_='polarity-mark', d=[
                svg.MoveTo(x=(self.shape.x-1)/2, y=-self.padding.y),
                svg.ArcRel(rx=1/2, ry=1/2, angle=0, dx=1, dy=0, sweep=False, large_arc=False),
                svg.ClosePath()
            ])
        )
        g.elements += [
            svg.G(
                class_='pin',
                transform=[svg.Translate(pin.at.x, pin.at.y)],
                elements=[
                    svg.Rect(x=0 if pin.at.x else -0.1, y=-0.2, width=0.1, height=0.4),
                    svg.Text(
                        text=pin.name,
                        class_=['rhs' if pin.at.x else 'lhs'],
                        dx=-0.2 if pin.at.x else 0.2,
                    )
                ]
            )
            for pin in self.pinmap.values()
        ]
        return g


cpu = DIP(width=6, name='WD65C02', picture="""
  VPB   RESB
  RDY   PHI2O
PHI1O   SOB
 IRQB   PHI2
  MLB   BE
 NMIB   NC
 SYNC   RWB
  VDD   D0
   A0   D1
   A1   D2
   A2   D3
   A3   D4
   A4   D5
   A5   D6
   A6   D7
   A7   A15
   A8   A14
   A9   A13
  A10   A12
  A11   GND
""")

"""
DIP({
    '+5V': 1,   'NC': 16,
    ...
})

DIP(['+5V', ..., 'NC'])


class SIP:
    pass

SIP("+5V SDA SCL GND")

SIP(['+5V', 'SDA', ...])

class FlexibleComponent:
    "min/max spacing"
    pass
"""



canvas = svg.SVG(
    width=180, height=700,
    viewBox=svg.ViewBoxSpec(-2, -2, 18, 70),
    elements=[
        svg.Style(text=css),
        Breadboard().draw(),
        cpu.draw(Point(3, 6)),
        cpu.draw(Point(9, 50), True)
    ]
)
print(canvas)
