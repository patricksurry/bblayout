import svg
from typing import cast, overload

from component import Component
from connect import Point, Connectable, Pin


class DIP(Component):
    def __init__(
            self,
            name: str,
            width: int,
            picture: str,
            padding=Point(0, 0.5),
            description: str='',
            tags: list[str] = []
    ):
        pairs = [
            line.strip().split()
            for line in picture.strip().splitlines()
        ]
        super().__init__(name,  Point(width, len(pairs)-1), padding, description=description)
        names = [left for (left, _) in pairs] + [right for (_, right) in reversed(pairs)]
        self.connectables = {
            name: Pin(self, name, Point(
                0 if i <= self.shape.y else self.shape.x,
                i if i <= self.shape.y else 2*self.shape.y + 1 - i
            ), i+1)
            for i, name in enumerate(names)
        }

    @overload
    def __getitem__(self, v: str) -> Connectable:
        ...
    @overload
    def __getitem__(self, v: int) -> Connectable:
        ...
    @overload
    def __getitem__(self, v: slice) -> list[Connectable]:
        ...
    def __getitem__(self, v):
        if isinstance(v, int):
            return next(pin for pin in self.connectables.values() if cast(Pin, pin).number==v)
        else:
            return super().__getitem__(v)

    def default_connectable(self):
        return self[1 if self.rotation != 180 else self.shape.y+2]

    def draw(self):
        g = super().draw()
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
                transform=[svg.Translate(pin.at_local.x, pin.at_local.y)],
                elements=[
                    svg.Rect(x=0 if pin.at_local.x else -0.1, y=-0.2, width=0.1, height=0.4),
                    svg.Text(
                        text=cast(Pin, pin).symbol,
                        class_=['rhs' if pin.at_local.x else 'lhs'],
                        dx=-0.2 if pin.at_local.x else 0.2,
                    )
                ]
            )
            for pin in self.connectables.values()
        ]
        return g

DIP.register(
    name='W65C02',
    description='CPU',
    tags=['65xx'],
    width=6,
    picture="""
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

DIP.register(
    name='W65C22',
    description='VIA',
    tags=['65xx'],
    width=6,
    picture="""
GND     CA1
PA0     CA2
PA1     RS0
PA2     RS1
PA3     RS2
PA4     RS3
PA5     RESB
PA6     D0
PA7     D1
PB0     D2
PB1     D3
PB2     D4
PB3     D5
PB4     D6
PB5     D7
PB6     PHI2
PB7     CS1
CB1     CS2B
CB2     RWB
VDD     IRQB
""")


DIP.register(
    name='28C256',
    description='32Kx8 EEPROM',
    tags=['eeprom'],
    width=6,
    picture="""
A14    VDD
A12    /WE
 A7    A13
 A6    A8
 A5    A9
 A4    A11
 A3    /OE
 A2    A10
 A1    /CE
 A0    IO7
IO0    IO6
IO1    IO5
IO2    IO4
GND    IO3
""")


DIP.register(
    name='62256',
    description='32Kx8 SRAM (256K)',
    tags=['sram'],
    width=6,
    picture="""
A14    VDD
A12    /WE
 A7    A13
 A6    A8
 A5    A9
 A4    A11
 A3    /OE
 A2    A10
 A1    /CE
 A0    IO7
IO0    IO6
IO1    IO5
IO2    IO4
GND    IO3
""")


DIP.register(
    name='74LS00',
    description='4xNAND',
    tags=['gate'],
    width=3,
    picture="""
 A1    VDD
 B1    B4
 Y1    A4
 A2    Y4
 B2    B3
 Y2    A3
GND    Y3
""")


DIP.register(
    name='555',
    description='Timer',
    tags=['analog'],
    width=3,
    picture="""
  GND    VDD
 /TRI    DCH
  OUT    THR
 /RST    CTV
""")


DIP.register(
    name='74LS139',
    description='2x2to4 Dec',
    tags=['demux'],
    width=3,
    picture="""
/1G    VDD
 1A    /2G
 1B    2A
1Y0    2B
1Y1    2Y0
1Y2    2Y1
1Y3    2Y2
GND    2Y3
""")


DIP.register(
    name='74LS595',
    description='8b Shift Reg',
    tags=['flipflop'],
    width=3,
    picture="""
 QB    VDD
 QC    QA
 QD    SER
 QE    /OE
 QF    RCLK
 QG    SCLK
 QH    /SCLR
GND    /QH
""")


DIP.register(
    name='74LS04',
    description='6xNOT',
    tags=['gate'],
    width=3,
    picture="""
  A1    VDD
  Y1    A6
  A2    Y6
  Y2    A5
  A3    Y5
  Y3    A4
 GND    Y4
""")


DIP.register(
    name='74LS74',
    description='2xD-FF',
    tags=['flipflop'],
    width=3,
    picture="""
/1CLR    VDD
   1D    /2Q
 1CLK    2Q
/1PRE    /2PRE
   1Q    2CLK
  /1Q    2D
  GND    /2CLR
""")
