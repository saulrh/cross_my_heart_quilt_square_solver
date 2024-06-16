import rich
import functools
import rich.style
import sys
import click
import dataclasses
import cpmpy
import rich.text
import rich.console

import quilt_square_color_placer.render_rich

@dataclasses.dataclass
class Color:
    name: str
    count: int
    style: rich.style.Style


@dataclasses.dataclass
class QuiltInstance:
    colors: list[Color]
    major_width: int
    major_height: int

    def __post_init__(self):
        assert(sum(c.count for c in self.colors) == self.square_count)

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
        Color("blue", 7, rich.style.Style(color="blue")),
        Color("orange", 9, rich.style.Style(color="orange3")),
        Color("yellow", 8, rich.style.Style(color="yellow")),
        Color("green", 8, rich.style.Style(color="green")),
        Color("aqua", 5, rich.style.Style(color="aquamarine3")),
        Color("brown", 4, rich.style.Style(color="orange4")),
        Color("red", 7, rich.style.Style(color="red")),
        Color("purple", 8, rich.style.Style(color="purple")),
        Color("pink", 5, rich.style.Style(color="magenta3")),
    ],
    major_width = 6,
    major_height = 6,
)

def format_colors(q):
    result = rich.text.Text()
    for idx, color in enumerate(q.colors):
        result.append(f"{idx}: {color.name} ({color.count}x)", style=color.style)
        result.append("\n")
    return result
    

def format_solution(soln, q):
    result = rich.text.Text()
    for row in range(q.major_height):
        for col in range(q.major_width):
            square = soln[q.major_idx(row, col)]
            result.append(str(square), style=q.colors[square].style)
            result.append(" ")
        result.append("\n")

        if row >= q.minor_height:
            continue

        result.append(" ")
        for col in range(q.minor_width):
            square = soln[q.minor_idx(row, col)]
            result.append(str(square), style=q.colors[square].style)
            result.append(" ")
        result.append("\n")
    return result

def add_diagonal_constraints(square_colors, q, m):
    for row in range(q.major_height):
        for col in range(q.major_width):
            if row - 1 >= 0 and col - 1 >= 0:
                m += (square_colors[q.major_idx(row, col)] != square_colors[q.minor_idx(row-1, col-1)])
            if row - 1 >= 0 and col < q.minor_width:
                m += (square_colors[q.major_idx(row, col)] != square_colors[q.minor_idx(row-1, col)])
            if row < q.major_height - 1 and col - 1 >= 0:
                m += (square_colors[q.major_idx(row, col)] != square_colors[q.minor_idx(row, col-1)])
            if row < q.major_height - 1 and col < q.minor_width:
                m += (square_colors[q.major_idx(row, col)] != square_colors[q.minor_idx(row, col)])

def add_ortho_major_constraints(square_colors, q, m):
    for row in range(q.major_height):
        for col in range(q.major_width):
            if row - 1 >= 0:
                m += (square_colors[q.major_idx(row, col)] != square_colors[q.major_idx(row-1, col)])
            if col - 1 >= 0:
                m += (square_colors[q.major_idx(row, col)] != square_colors[q.major_idx(row, col-1)])
            if row + 1 < q.major_height:
                m += (square_colors[q.major_idx(row, col)] != square_colors[q.major_idx(row+1, col)])
            if col + 1 < q.major_width:
                m += (square_colors[q.major_idx(row, col)] != square_colors[q.major_idx(row, col+1)])

def add_ortho_minor_constraints(square_colors, q, m):
    for row in range(q.minor_height):
        for col in range(q.minor_width):
            if row - 1 >= 0:
                m += (square_colors[q.minor_idx(row, col)] != square_colors[q.minor_idx(row-1, col)])
            if col - 1 >= 0:
                m += (square_colors[q.minor_idx(row, col)] != square_colors[q.minor_idx(row, col-1)])
            if row + 1 < q.minor_height:
                m += (square_colors[q.minor_idx(row, col)] != square_colors[q.minor_idx(row+1, col)])
            if col + 1 < q.minor_width:
                m += (square_colors[q.minor_idx(row, col)] != square_colors[q.minor_idx(row, col+1)])


@click.command
def main():
    con = rich.console.Console()

    m = cpmpy.Model()

    square_colors = cpmpy.intvar(0, len(QUILT.colors) - 1, name="square_colors", shape=QUILT.square_count)
    
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
    
    con.print(format_colors(QUILT))

    while len(solutions) < TARGET_SOLUTION_COUNT and solver.solve(random_seed=20):
        soln = square_colors.value()
        solutions.append(soln)
        con.print(format_solution(soln, QUILT))
        solver.maximize(sum([sum(square_colors != past_soln) for past_soln in solutions]))


if __name__ == "__main__":
    main()
