import svg
from component import Component, Point, Tie


class Breadboard(Component):
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
            Tie(f'{self._cols[c]}{r}', Point(c, r), r if c > 6 else -r)
            for r in range(64)
            for c in range(12)
            if c not in (5,6)
        ]
        self.tiemap = {tie.name: tie for tie in ties}

    def __getattr__(self, label: str):
        return self.tiemap[label.upper()] @ self.at

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
                x=tie.at.x-0.2, y=tie.at.y-0.2,
                class_=['tie']
            )
            for tie in self.tiemap.values()
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


class BreadboardRail(Component):
    _cols = "PN"
    _syms = "+-"

    def __init__(self, name='BBR'):
        super().__init__(name, Point(1, 63), Point(1.5, 1.5))
        ties = [
            Tie(f'{self._cols[c]}{r}', Point(c, r), 1-c)
            for r in range(2, 62)
            for c in range(2)
            if r % 6 != 1
        ]
        self.tiemap = {tie.name: tie for tie in ties}

    def __getattr__(self, label: str):
        return self.tiemap[label.upper()] @ self.at

    def draw(self):
        g = super().draw()

        g.elements += [
            svg.Rect(
                width=0.4, height=0.4,
                x=tie.at.x-0.2, y=tie.at.y-0.2,
                class_=['tie']
            )
            for tie in self.tiemap.values()
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


class BreadboardLayout(Component):
    def __init__(self, name='layout', picture='|=|'):
        assert not set(picture) - set('|=')
        super().__init__(name, Point())
        at = Point()
        self.parts: dict[str, Component] = {}
        p, extent = Point(), Point()
        ns = dict(BB=1, BBR=1)
        for c in picture:
            kind = 'BB' if c == '=' else 'BBR'
            name = f"{kind}{ns[kind]}"
            part = Component.new(kind, name)
            ns[kind] += 1
            part @= Point(at.x + part.padding.x, at.y + part.padding.y)
            p, extent = part.viewbox()
            at = Point(p.x+extent.x, p.y)
            self.parts[name] = part
        self.shape = Point(p.x+extent.x, extent.y)

    def __getattr__(self, name: str):
        return self.parts[name]

    def draw(self):
        return svg.G(elements=[
            part.draw() for part in self.parts.values()
        ])


Breadboard.register(name='BB')
BreadboardRail.register(name='BBR')


def layout(picture='|=|'):
    return BreadboardLayout(picture=picture)
