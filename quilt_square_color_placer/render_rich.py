import rich
import rich.text

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
