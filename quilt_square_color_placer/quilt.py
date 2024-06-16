import dataclasses
import functools


@dataclasses.dataclass
class Color:
    name: str
    count: int
    hex_color: str


@dataclasses.dataclass
class Quilt:
    colors: list[Color]
    major_width: int
    major_height: int

    def __post_init__(self):
        assert sum(c.count for c in self.colors) == self.square_count

    @functools.cached_property
    def major_square_count(self):
        return self.major_width * self.major_height

    @functools.cached_property
    def minor_width(self):
        return self.major_width - 1

    @functools.cached_property
    def minor_height(self):
        return self.major_height - 1

    @functools.cached_property
    def minor_square_count(self):
        return self.minor_width * self.minor_height

    @functools.cached_property
    def square_count(self):
        return self.major_square_count + self.minor_square_count

    def major_idx(self, row, col):
        return col + (row * self.major_width)

    def minor_idx(self, row, col):
        return self.major_square_count + col + (row * self.minor_width)
