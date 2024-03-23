import svg
from dip import DIP
from sip import SIP
from breadboard import BreadboardLayout, Wire


#TODO
"""
/xx => _xx in pinmap;  what about 2Y0?
.<pin> and subtraction for wires
cpu.RST - R1 - GND  # R1 subtraction could be non-commutative to spec both ends

slicing via['PB0':'PB7']  or via.PB0:via.PB7
"""

layout = BreadboardLayout('|=|=||=|=|')

power = SIP.new('power')
via = DIP.new('W65C22')
cpu = DIP.new('W65C02')
ram = DIP.new('62256')
rom = DIP.new('28C256')
nand = DIP.new('74LS00')
ff = DIP.new('74LS74')
demux = DIP.new('74LS139')
sdshft = DIP.new('74LS595')
kbshft = DIP.new('74LS595')

layout.place(
    power @ layout.BBR1.P2,
    via @ layout.BB2.D23,
    cpu @ layout.BB4.C8,
    ram @ layout.BB4.C32,
    rom @ layout.BB4.C49,
    nand @ layout.BB3.E6,
    ff @ layout.BB2.E6,
    demux @ layout.BB2.E14,
    sdshft @ layout.BB1.E15,
    kbshft @ layout.BB1.E33,
)

layout.wiring(
    cpu.VDD - power.VDD,
    via.VDD - power.VDD,
    color='red'
)
layout.wiring(
    cpu.GND - power.GND,
)
layout.wiring(
    *Wire.zip(cpu['D0':], via['D0':]),
    color='blue',
#    loop=True,
)

layout.to_svg('bb.svg')

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
