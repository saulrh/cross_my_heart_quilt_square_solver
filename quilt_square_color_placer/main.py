import rich
import rich.style
import sys
import click
import dataclasses
import cpmpy
import rich.text
import rich.console

@dataclasses.dataclass
class Color:
    name: str
    count: int
    style: rich.style.Style


COLORS = [
    Color("blue", 7, rich.style.Style(color="blue")),
    Color("orange", 9, rich.style.Style(color="orange3")),
    Color("yellow", 8, rich.style.Style(color="yellow")),
    Color("green", 8, rich.style.Style(color="green")),
    Color("aqua", 5, rich.style.Style(color="aquamarine3")),
    Color("brown", 4, rich.style.Style(color="orange4")),
    Color("red", 7, rich.style.Style(color="red")),
    Color("purple", 8, rich.style.Style(color="purple")),
    Color("pink", 5, rich.style.Style(color="magenta3")),
]

MAJOR_WIDTH = 6
MAJOR_HEIGHT = 6
MAJOR_SQUARE_COUNT = MAJOR_WIDTH * MAJOR_HEIGHT

MINOR_WIDTH = MAJOR_WIDTH - 1
MINOR_HEIGHT = MAJOR_HEIGHT - 1
MINOR_SQUARE_COUNT = MINOR_WIDTH * MINOR_HEIGHT


# number of squares on grid centers plus number of squares on grid
# corners
SQUARE_COUNT = MAJOR_SQUARE_COUNT + MINOR_SQUARE_COUNT

def major_idx(row, col):
    return col + (row * MAJOR_WIDTH)

def minor_idx(row, col):
    return MAJOR_SQUARE_COUNT + col + (row * MINOR_WIDTH)

def format_colors():
    result = rich.text.Text()
    for idx, color in enumerate(COLORS):
        result.append(f"{idx}: {color.name} ({color.count}x)", style=color.style)
        result.append("\n")
    return result
    

def format_solution(soln):
    result = rich.text.Text()
    for row in range(MAJOR_HEIGHT):
        for col in range(MAJOR_WIDTH):
            square = soln[major_idx(row, col)]
            result.append(str(square), style=COLORS[square].style)
            result.append(" ")
        result.append("\n")

        if row >= MINOR_HEIGHT:
            continue

        result.append(" ")
        for col in range(MINOR_WIDTH):
            square = soln[minor_idx(row, col)]
            result.append(str(square), style=COLORS[square].style)
            result.append(" ")
        result.append("\n")
    return result


def add_diagonal_constraints(square_colors, m):
    for row in range(MAJOR_HEIGHT):
        for col in range(MAJOR_WIDTH):
            if row - 1 >= 0 and col - 1 >= 0:
                m += (square_colors[major_idx(row, col)] != square_colors[minor_idx(row-1, col-1)])
            if row - 1 >= 0 and col < MINOR_WIDTH:
                m += (square_colors[major_idx(row, col)] != square_colors[minor_idx(row-1, col)])
            if row < MAJOR_HEIGHT - 1 and col - 1 >= 0:
                m += (square_colors[major_idx(row, col)] != square_colors[minor_idx(row, col-1)])
            if row < MAJOR_HEIGHT - 1 and col < MINOR_WIDTH:
                m += (square_colors[major_idx(row, col)] != square_colors[minor_idx(row, col)])

def add_ortho_major_constraints(square_colors, m):
    for row in range(MAJOR_HEIGHT):
        for col in range(MAJOR_WIDTH):
            if row - 1 >= 0:
                m += (square_colors[major_idx(row, col)] != square_colors[major_idx(row-1, col)])
            if col - 1 >= 0:
                m += (square_colors[major_idx(row, col)] != square_colors[major_idx(row, col-1)])
            if row + 1 < MAJOR_HEIGHT:
                m += (square_colors[major_idx(row, col)] != square_colors[major_idx(row+1, col)])
            if col + 1 < MAJOR_WIDTH:
                m += (square_colors[major_idx(row, col)] != square_colors[major_idx(row, col+1)])

def add_ortho_minor_constraints(square_colors, m):
    for row in range(MINOR_HEIGHT):
        for col in range(MINOR_WIDTH):
            if row - 1 >= 0:
                m += (square_colors[minor_idx(row, col)] != square_colors[minor_idx(row-1, col)])
            if col - 1 >= 0:
                m += (square_colors[minor_idx(row, col)] != square_colors[minor_idx(row, col-1)])
            if row + 1 < MINOR_HEIGHT:
                m += (square_colors[minor_idx(row, col)] != square_colors[minor_idx(row+1, col)])
            if col + 1 < MINOR_WIDTH:
                m += (square_colors[minor_idx(row, col)] != square_colors[minor_idx(row, col+1)])


@click.command
def main():
    con = rich.console.Console()

    assert(sum(c.count for c in COLORS) == SQUARE_COUNT)

    m = cpmpy.Model()

    square_colors = cpmpy.intvar(0, len(COLORS) - 1, name="square_colors", shape=SQUARE_COUNT)
    
    m += cpmpy.expressions.globalconstraints.GlobalCardinalityCount(
        square_colors,
        range(len(COLORS)),
        [c.count for c in COLORS],
    )

    add_ortho_major_constraints(square_colors, m)
    add_ortho_minor_constraints(square_colors, m)
    add_diagonal_constraints(square_colors, m)

    solver = cpmpy.SolverLookup.get("ortools", m)

    TARGET_SOLUTION_COUNT = 3
    solutions = []
    
    con.print(format_colors())

    while len(solutions) < TARGET_SOLUTION_COUNT and solver.solve():
        soln = square_colors.value()
        solutions.append(soln)
        con.print(format_solution(soln))
        solver.maximize(sum([sum(square_colors != past_soln) for past_soln in solutions]))


if __name__ == "__main__":
    main()
