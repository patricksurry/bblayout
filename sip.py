import svg
from typing import Literal, cast
from component import Component
from connect import Point, Pin


class SIP(Component):
    def __init__(
            self,
            name: str,
            picture: str,
            padding=Point(0.5, 0.5),
            description: str='',
            tags: list[str] = [],
            orientation: Literal['vertical', 'horizontal'] = 'vertical'
    ):
        pins = picture.strip().split()
        super().__init__(name,  Point(0, len(pins)-1), padding, description=description)
        self.connectables = {
            s.upper(): Pin(self, s, Point(0, i), i+1)
            for i, s in enumerate(pins)
        }
        if orientation == 'horizontal':
            self.set_transform(rotation=270)

    def draw(self):
        g = super().draw()
        g.elements += [
            svg.G(
                class_='pin',
                transform=[svg.Translate(pin.at_local.x, pin.at_local.y)],
                elements=[
                    #svg.Rect(x=-0.2, y=-0.2, width=0.4, height=0.4),
                    svg.Text(
                        text=cast(Pin, pin).symbol,
                        dy=0.1
                    )
                ]
            )
            for pin in self.connectables.values()
        ]
        return g


SIP.register(
    name='power',
    description='power',
    tags=['power'],
    picture="VDD GND",
    orientation='horizontal'
)
