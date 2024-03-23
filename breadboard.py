import svg
from typing import cast
from itertools import groupby
from dataclasses import dataclass, field
from connect import Point, Connectable, Tie, Pin, Wire, ConnectedGroup, distance
from component import Component


class BreadboardPart(Component):
    def __init__(self, name: str, shape: Point, padding: Point):
        super().__init__(name, shape, padding)

    def __getattr__(self, name: str) -> Connectable:
        """Get a connectable by name"""
        return self.connectables[name.upper()]          # case-insensitive

    def rails(self) -> list[ConnectedGroup]:
        ties = cast(list[Tie], list(self.connectables.values()))
        groups = groupby(sorted(ties, key=lambda t: t.rail), lambda t: t.rail)
        return [
            ConnectedGroup(connectables=list(ties))
            for (_, ties) in groups
        ]


class BreadboardMain(BreadboardPart):
    """
    breadboard has 64 rows of 5 + 5
    3 units between inner pins across groove
    7 units between outer pins across a rail
    |. o o o o o | | o o o o o .|. o o .|. o ...

    vertically rail skips 2, 10 groups of 5 + 1, skip 2
    |. . . o o o o o . o o o o o . ...
    """

    _cols = "ABCDE..FGHIJ"

    def __init__(self, name='BB'):
        super().__init__(name, Point(11, 63), Point(1.5, 1.5))
        ties = [
            Tie(self, f'{self._cols[c]}{r}', Point(c, r), r if c > 6 else -r)
            for r in range(64)
            for c in range(12)
            if c not in (5,6)
        ]
        self.connectables = {t.name: t for t in ties}

    def draw(self):
        g = super().draw()

        g.elements.append(svg.Rect(
            x=5, y=-self.padding.y,
            width=1, height=self.shape.y + 2*self.padding.y,
            class_=['groove']
        ))
        g.elements += [
            svg.Rect(
                width=0.4, height=0.4,
                x=tie.at_local.x-0.2, y=tie.at_local.y-0.2,
                class_=['tie']
            )
            for tie in self.connectables.values()
        ]
        g.elements += [
            t for r in range(64) for t in [
                svg.Text(text=str(r), x=-1, y=r),
                svg.Text(text=str(r), x=12, y=r)
            ]
        ]
        g.elements += [
            t for c in range(12) for t in [
                svg.Text(text=self._cols[c], x=c, y=-1),
                svg.Text(text=self._cols[c], x=c, y=64)
            ] if c not in (5,6)
        ]
        return g


class BreadboardRail(BreadboardPart):
    _cols = "PN"
    _syms = "+-"

    def __init__(self, name='BBR'):
        super().__init__(name, Point(1, 63), Point(1.5, 1.5))
        ties = [
            Tie(self, f'{self._cols[c]}{r}', Point(c, r), 1-c)
            for r in range(2, 62)
            for c in range(2)
            if r % 6 != 1
        ]
        self.connectables = {t.name: t for t in ties}

    def draw(self):
        g = super().draw()

        g.elements += [
            svg.Rect(
                width=0.4, height=0.4,
                x=tie.at_local.x-0.2, y=tie.at_local.y-0.2,
                class_=['tie']
            )
            for tie in self.connectables.values()
        ]
        g.elements += [
            svg.Line(x1=-1, x2=-1, y1=1, y2=61, class_=self._cols[0]),
            svg.Line(x1=2,  x2=2,  y1=1, y2=61, class_=self._cols[1]),
        ]
        g.elements += [
            t for c in range(2) for t in [
                svg.Text(text=self._syms[c], x=2*c-1/2, y=0,  class_=[self._cols[c]]),
                svg.Text(text=self._syms[c], x=2*c-1/2, y=62, class_=[self._cols[c]]),
            ]
        ]
        return g


BreadboardMain.register(name='BB')
BreadboardRail.register(name='BBR')


class BreadboardLayout:
    """The breaboard layout manages layout and placement of a collection of components"""
    def __init__(self, picture='|=|'):

        self.connected_groups: list[ConnectedGroup] = []
        self.grouping: dict[Connectable, ConnectedGroup] = {}
        self.at_map: dict[Point, Tie] = {}
        self.parts: dict[str, Component] = {}
        self.wires: list[Wire] = []

        assert not set(picture) - set('|=')
        top_right = Point(0.5, 0.5)
        tl, extent = Point(), Point()       # pre-declare for typing
        ns = dict(BB=1, BBR=1)
        for c in picture:
            kind = 'BB' if c == '=' else 'BBR'
            name = f"{kind}{ns[kind]}"
            part = (BreadboardMain if kind == 'BB' else BreadboardRail).new(kind, name)
            ns[kind] += 1
            tl, _ = part.viewbox()
            part.set_transform(at=Point(top_right.x - tl.x, top_right.y - tl.y))
            tl, extent = part.viewbox()
            top_right = Point(tl.x + extent.x, tl.y)
            self.parts[name] = part
            rails = part.rails()
            self.connected_groups += rails
            self.grouping.update({
                c: cg for cg in rails for c in cg.connectables
            })
            self.at_map.update({
                c.at_global: c for c in part.connectables.values()
            })

        self.shape = Point(tl.x + extent.x + 0.5, tl.y + extent.y + 0.5)

    def __getattr__(self, name: str):
        return self.parts[name]

    def place(self, *args: tuple[Connectable, Connectable]):
        for (pin, tie) in args:
            assert isinstance(pin, Pin) and isinstance(tie, Tie), \
                "BreadboardLayout.place expected Pin @ Tie, not {pin} @ {tie}"
            # first position the part so it coincides with target tie
            dst = tie.at_global
            part = pin.owner
            src = pin.at_global
            part.set_transform(at=Point(dst.x-src.x, dst.y-src.y))
            # now check all pins match an available tie
            for pin in part.connectables.values():
                at = pin.at_global
                tie = self.at_map[at]
                group = self.grouping[tie]
                group.connectables.append(pin)
                self.grouping[pin] = group
                del self.at_map[at]
            self.parts[part.name] = part

    def free_tie(self, group: ConnectedGroup, near: Connectable):
        ties = [c for c in group.connectables if isinstance(c, Tie) and c.at_global in self.at_map]
        return min(ties, key=lambda tie: distance(tie.at_global, near.at_global))

    def wiring(self, *wires: Wire, color=None):
        for wire in wires:
            (a, b) = wire.ends
            if a.at_global not in self.at_map:
                a = self.free_tie(self.grouping[a], b)
            if b.at_global not in self.at_map:
                b = self.free_tie(self.grouping[b], a)

            self.wires.append(Wire(a, b, color or wire.color))

    def draw(self):
        return svg.G(elements=[
            part.draw() for part in self.parts.values()
        ] + [
            wire.draw() for wire in self.wires
        ])

    def to_svg(self, fname: str, css='style.css'):
        canvas = svg.SVG(
            width=self.shape.x*10, height=self.shape.y*10,
            viewBox=svg.ViewBoxSpec(0, 0, self.shape.x, self.shape.y),
            elements=[
                svg.Style(text=open(css).read()),
                self.draw()
            ]
        )
        open(fname, 'w').write(str(canvas))
