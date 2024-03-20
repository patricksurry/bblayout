import svg
from component import Component, Point
import breadboard
import dip


#TODO
"""
/xx => _xx in pinmap;  what about 2Y0?
.<pin> and subtraction for wires
cpu.RST - R1 - GND  # R1 subtraction could be non-commutative to spec both ends
"""


layout = breadboard.layout('|=|=||=|=|')

via = Component.new('W65C22') @ layout.BB2.D23.at
cpu = Component.new('W65C02') @ layout.BB4.C8.at
ram = Component.new('62256')  @ layout.BB4.C32.at
rom = Component.new('28C256') @ layout.BB4.C49.at
nand = Component.new('74LS00') @ layout.BB3.E6.at
ff = Component.new('74LS74') @ layout.BB2.E6.at
demux = Component.new('74LS139') @ layout.BB2.E14.at
sdshft = Component.new('74LS595') @ layout.BB1.E15.at
kbshft = Component.new('74LS595') @ layout.BB1.E33.at
pt, extent = layout.viewbox()

canvas = svg.SVG(
    width=extent.x*10, height=extent.y*10,
    viewBox=svg.ViewBoxSpec(pt.x, pt.y, extent.x, extent.y),
    elements=[
        svg.Style(text=open('style.css').read()),
        layout.draw(),
        cpu.draw(),
        via.draw(),
        ram.draw(),
        rom.draw(),
        nand.draw(),
        ff.draw(),
        demux.draw(),
        sdshft.draw(),
        kbshft.draw(),
        (layout.BB1.J17 - layout.BB2.C32).draw(),
        svg.Line(x1=cpu.GND.at.x, y1=cpu.GND.at.y, x2=via.GND.at.x, y2=via.GND.at.y, class_=['wire']),
    ]
)
open('bb.svg', 'w').write(str(canvas))


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
