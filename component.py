from typing_extensions import overload
import svg
import re

from connect import Connectable, Point


class Component:
    registry: dict[str, dict] = {}
    created: set[str] = set()

    def __init__(
            self,
            name: str,
            shape: Point,
            padding=Point(0.5, 0.5),
            description: str='',
            tags: list[str] = []
    ):
        self.name = name
        self.shape = shape
        self.padding = padding
        self.at = Point()
        self.rotation = 0
        self.description = description
        self.tags = tags
        self.connectables: dict[str, Connectable] = {}

    @classmethod
    def register(cls, name, **kwargs):
        cls.registry[name] = kwargs

    @classmethod
    def new(cls, name, aka='', **kwargs):
        assert name in cls.registry, \
            f"Unknown component {name}.\nKnown components: {list(cls.registry.keys())}"

        aka = aka or name
        n = 1
        while aka in Component.created:
            n += 1
            aka = aka.rsplit('-', 1)[0] + f"-{n}"
        Component.created.add(aka)
        return cls(aka, **cls.registry[name], **kwargs)

    def __getattr__(self, name: str) -> Connectable:
        """Get a connectable by name"""
        return self.connectables[name]

    def default_connectable(self):
        return next(iter(self.connectables.values()))

    def name_offset(self, name: str, offset: int) -> str | None:
        m = re.match(r'(.*?)(\d+)', name)
        assert m, f"connection slice requires numeric suffix, found {name}"
        name = m.group(1) + str(int(m.group(2)) + offset)
        return name if name in self.connectables else None

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
        if not isinstance(v, slice):
            return getattr(self, v)

        assert v.step is None, "step not supported for connection slicing"

        ks: list[str | int]

        if v.start is None:
            if v.stop is None:
                ks = list(self.connectables.keys())
            elif isinstance(v.stop, int):
                ks = list(range(1, vars.stop))
            else:
                assert isinstance(v.stop, str), f"don't understand {v.stop} in connection slice"
                k = v.stop
                ks = [k]
                while True:
                    k = self.name_offset(k, -1)
                    if not k:
                        break
                    ks.insert(0, k)
        else:
            if isinstance(v.start, str):
                assert v.stop is None or isinstance(v.stop, str), \
                    f"incompatible types {v.start} and {v.stop} in connection slice"
                k = v.start
                ks = [k]
                while k != v.stop:
                    k = self.name_offset(k, 1)
                    if not k:
                        break
                    ks.append(k)
            else:
                assert isinstance(v.start, int), f"don't understand {v.start} in connection slice"
                assert v.stop is None or isinstance(v.stop, int), \
                    f"incompatible types {v.start} and {v.stop} in connection slice"
                ks = list(range(v.start, v.stop or len(self.connectables)))

        return [self[i] for i in ks]

    def __matmul__(self, tie: Connectable):
        return (self.default_connectable(), tie)

    def set_transform(self, at: Point|None=None, rotation: int|None=None):
        if at is not None:
            self.at = at
        if rotation is not None:
            self.rotation = rotation

    def flipped(self):
       self.set_transform(self.at, 180)
       return self

    def transform(self, p: Point) -> Point:
        match self.rotation:
            case 0:
                q = p
            case 90:
                q = Point(-p.y, p.x)
            case 180:
                q = Point(-p.x, -p.y)
            case 270:
                q = Point(p.y, -p.x)
            case _:
                raise ValueError("only 90 deg rotations are implemented")
        return Point(self.at.x + q.x, self.at.y + q.y)

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
        if self.rotation:
            t.append(svg.Rotate(self.rotation))
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
