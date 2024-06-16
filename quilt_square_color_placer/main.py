import functools
import sys
import click
import dataclasses
import cpmpy

import quilt_square_color_placer.render_rich


@dataclasses.dataclass
class Color:
    name: str
    count: int
    hex_color: int


@dataclasses.dataclass
class QuiltInstance:
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


QUILT = QuiltInstance(
    colors=[
        Color("blue", 7, "#0000ff"),
        Color("orange", 9, "#d78700"),
        Color("yellow", 8, "#ffff00"),
        Color("green", 8, "#008700"),
        Color("aqua", 5, "#5fd7af"),
        Color("brown", 4, "#875f00"),
        Color("red", 7, "#ff0000"),
        Color("purple", 8, "#af00ff"),
        Color("pink", 5, "#d700d7"),
    ],
    major_width=6,
    major_height=6,
)


def add_diagonal_constraints(square_colors, q, m):
    for row in range(q.major_height):
        for col in range(q.major_width):
            if row - 1 >= 0 and col - 1 >= 0:
                m += (
                    square_colors[q.major_idx(row, col)]
                    != square_colors[q.minor_idx(row - 1, col - 1)]
                )
            if row - 1 >= 0 and col < q.minor_width:
                m += (
                    square_colors[q.major_idx(row, col)]
                    != square_colors[q.minor_idx(row - 1, col)]
                )
            if row < q.major_height - 1 and col - 1 >= 0:
                m += (
                    square_colors[q.major_idx(row, col)]
                    != square_colors[q.minor_idx(row, col - 1)]
                )
            if row < q.major_height - 1 and col < q.minor_width:
                m += (
                    square_colors[q.major_idx(row, col)]
                    != square_colors[q.minor_idx(row, col)]
                )


def add_ortho_major_constraints(square_colors, q, m):
    for row in range(q.major_height):
        for col in range(q.major_width):
            if row - 1 >= 0:
                m += (
                    square_colors[q.major_idx(row, col)]
                    != square_colors[q.major_idx(row - 1, col)]
                )
            if col - 1 >= 0:
                m += (
                    square_colors[q.major_idx(row, col)]
                    != square_colors[q.major_idx(row, col - 1)]
                )
            if row + 1 < q.major_height:
                m += (
                    square_colors[q.major_idx(row, col)]
                    != square_colors[q.major_idx(row + 1, col)]
                )
            if col + 1 < q.major_width:
                m += (
                    square_colors[q.major_idx(row, col)]
                    != square_colors[q.major_idx(row, col + 1)]
                )


def add_ortho_minor_constraints(square_colors, q, m):
    for row in range(q.minor_height):
        for col in range(q.minor_width):
            if row - 1 >= 0:
                m += (
                    square_colors[q.minor_idx(row, col)]
                    != square_colors[q.minor_idx(row - 1, col)]
                )
            if col - 1 >= 0:
                m += (
                    square_colors[q.minor_idx(row, col)]
                    != square_colors[q.minor_idx(row, col - 1)]
                )
            if row + 1 < q.minor_height:
                m += (
                    square_colors[q.minor_idx(row, col)]
                    != square_colors[q.minor_idx(row + 1, col)]
                )
            if col + 1 < q.minor_width:
                m += (
                    square_colors[q.minor_idx(row, col)]
                    != square_colors[q.minor_idx(row, col + 1)]
                )


@click.command
def main():
    m = cpmpy.Model()

    square_colors = cpmpy.intvar(
        0, len(QUILT.colors) - 1, name="square_colors", shape=QUILT.square_count
    )

    m += cpmpy.expressions.globalconstraints.GlobalCardinalityCount(
        square_colors,
        range(len(QUILT.colors)),
        [c.count for c in QUILT.colors],
    )

    add_ortho_major_constraints(square_colors, QUILT, m)
    add_ortho_minor_constraints(square_colors, QUILT, m)
    add_diagonal_constraints(square_colors, QUILT, m)

    solver = cpmpy.SolverLookup.get("ortools", m)

    TARGET_SOLUTION_COUNT = 10
    solutions = []

    quilt_square_color_placer.render_rich.render_colors(QUILT)

    while len(solutions) < TARGET_SOLUTION_COUNT and solver.solve(random_seed=20):
        soln = square_colors.value()
        solutions.append(soln)
        quilt_square_color_placer.render_rich.render_solution(soln, QUILT)
        solver.maximize(
            sum([sum(square_colors != past_soln) for past_soln in solutions])
        )


if __name__ == "__main__":
    main()
