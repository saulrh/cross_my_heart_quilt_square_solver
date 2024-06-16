import svg
import itertools
import math
import collections.abc
import textwrap

from quilt_square_color_placer import quilt

STROKE_WIDTH = 2

U = 15

INSIDE = U
OUTSIDE = 2 * U

SQRT2 = math.sqrt(2)

DIAG = math.sqrt(2 * (4 * U) ** 2)


def rotate_pt(x: float, y: float) -> tuple[float, float]:
    return (
        x * 0.5 * SQRT2 + y * 0.5 * SQRT2,
        -x * 0.5 * SQRT2 + y * 0.5 * SQRT2,
    )


def rotate(
    seq: collections.abc.Sequence[tuple[float, float]]
) -> list[tuple[float, float]]:
    return [rotate_pt(*el) for el in seq]


def translate(
    xy: tuple[float, float], seq: collections.abc.Sequence[tuple[float, float]]
) -> list[tuple[float, float]]:
    x, y = xy
    return [(x + el_x, y + el_y) for el_x, el_y in seq]


def flatten(seq: collections.abc.Sequence) -> list[float]:
    return [x for xs in seq for x in xs]


def square_element(
    centered_at: tuple[float, float], color: quilt.Color
) -> list[svg.Element]:
    return [
        svg.Polygon(
            points=flatten(
                translate(
                    centered_at,
                    rotate(
                        [
                            (INSIDE, OUTSIDE),
                            (INSIDE, INSIDE),
                            (OUTSIDE, INSIDE),
                            (OUTSIDE, -INSIDE),
                            (INSIDE, -INSIDE),
                            (INSIDE, -OUTSIDE),
                            (-INSIDE, -OUTSIDE),
                            (-INSIDE, -INSIDE),
                            (-OUTSIDE, -INSIDE),
                            (-OUTSIDE, INSIDE),
                            (-INSIDE, INSIDE),
                            (-INSIDE, OUTSIDE),
                        ]
                    ),
                )
            ),
            stroke="black",
            fill=color.hex_color,
            stroke_width=STROKE_WIDTH,
        ),
        svg.Text(
            text=color.name,
            x=centered_at[0],
            y=centered_at[1],
            fill="black",
            text_anchor="middle",
            dominant_baseline="middle",
            font_size="13",
        ),
    ]


def center_from_idx(idx: int, q: quilt.Quilt) -> tuple[float, float]:
    is_major, row, col = q.rc_from_idx(idx)
    if is_major:
        return (
            (0.5 + col) * DIAG,
            (0.5 + row) * DIAG,
        )
    else:
        return (
            (1 + col) * DIAG,
            (1 + row) * DIAG,
        )


def render_solution(soln, q: quilt.Quilt):
    square_elements = list(
        itertools.chain.from_iterable(
            square_element(center_from_idx(idx, q), q.colors[s])
            for idx, s in enumerate(soln)
        )
    )

    return svg.SVG(
        width=q.major_width * DIAG,
        height=q.major_height * DIAG,
        elements=square_elements,
    )
