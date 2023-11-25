from argparse import ArgumentParser
from dataclasses import dataclass
from typing import cast

from cnf import CnfComposer, Literal


@dataclass(frozen=True, kw_only=True)
class Hint:
    row: int  # 0-indexed
    col: int  # 0-indexed
    value: int  # 0-indexed


@dataclass(frozen=True, kw_only=True)
class Sudoku:
    name = 'sudoku'
    rows: int
    cols: int
    hints: tuple[Hint, ...]


def load_problem(filename: str) -> Sudoku:
    with open(filename) as f:
        rows = 0
        cols = 0
        hints: list[Hint] = []
        for line in f.readlines():
            parts = line.split()
            if parts[0] == 'p' and parts[1] == Sudoku.name:
                rows = int(parts[2])
                cols = int(parts[3])
            else:
                h = Hint(
                    row=int(parts[0]) - 1,
                    col=int(parts[1]) - 1,
                    value=int(parts[2]) - 1)
                hints.append(h)
        return Sudoku(rows=rows, cols=cols, hints=tuple(hints))


def display(grid: list[list[int]]):
    s = '┏━━━┯━━━┯━━━┳━━━┯━━━┯━━━┳━━━┯━━━┯━━━┓\n'
    for r in range(9):
        s += '┃'
        for c in range(9):
            if grid[r][c] == -1:
                s += '   '
            else:
                s += f' {grid[r][c]+1} '
            s += '┃' if c % 3 == 2 else '│'
        if r == 8:
            s += '\n┗━━━┷━━━┷━━━┻━━━┷━━━┷━━━┻━━━┷━━━┷━━━┛'
        elif r % 3 == 2:
            s += '\n┣━━━┿━━━┿━━━╋━━━┿━━━┿━━━╋━━━┿━━━┿━━━┫\n'
        else:
            s += '\n┠───┼───┼───╂───┼───┼───╂───┼───┼───┨\n'
    print(s)


parser = ArgumentParser(
    prog='sudoku',
    description='sudoku solver',
)
parser.add_argument(
    'filename',
    help='problem file',
)
parser.add_argument(
    '-o', '--output',
    help='output dimacs file',
)
opts = parser.parse_args()


def main():
    sudoku = load_problem(opts.filename)
    cc = CnfComposer()

    # p[i][j][k] := マス(i, j)に数字kが入る
    p: list[list[list[Literal]]] = []

    # 全てのマスについて、1~9のうち1つの数字が入る
    for i in range(9):
        p.append([])
        for j in range(9):
            p[i].append([])
            for k in range(9):
                literal = cc.new_literal(name=f'p_{i}{j}={k}')
                p[i][j].append(literal)
            # p[i][j][1~9]のうち、少なくとも1つは真
            cc.add_clause(p[i][j])
            for a in range(9):
                for b in range(a + 1, 9):
                    # p[i][j][a]とp[i][j][b]のうち、両方とも真になることはない
                    cc.add_clause([-p[i][j][a], -p[i][j][b]])

    # 全てのマスについて...
    for i in range(9):
        for j in range(9):

            #    | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
            #  ─ ┏━━━┯━━━┯━━━┳━━━┯━━━┯━━━┳━━━┯━━━┯━━━┓
            #  0 ┃ 0 │ 1 │ 2 ┃ 0 │ 1 │ 2 ┃ 0 │ 1 │ 2 ┃
            #  ─ ┠───┼───┼───╋───┼───┼───╋───┼───┼───┨
            #  1 ┃ 3 │ 4 │ 5 ┃ 3 │ 4 │ 5 ┃ 3 │ 4 │ 5 ┃
            #  ─ ┠───┼───┼───╋───┼───┼───╋───┼───┼───┨
            #  2 ┃ 6 │ 7 │ 8 ┃ 6 │ 7 │ 8 ┃ 6 │ 7 │ 8 ┃
            #  ─ ┣━━━┿━━━┿━━━╋━━━┿━━━┿━━━╋━━━┿━━━┿━━━┫
            #  3 ┃ 0 │ 1 │ 2 ┃ 0 │ 1 │ 2 ┃ 0 │ 1 │ 2 ┃
            #  ─ ┠───┼───┼───╋───┼───┼───╋───┼───┼───┨
            #  4 ┃ 3 │ 4 │ 5 ┃ 3 │ 4 │ 5 ┃ 3 │ 4 │ 5 ┃
            #  ─ ┠───┼───┼───╋───┼───┼───╋───┼───┼───┨
            #  5 ┃ 6 │ 7 │ 8 ┃ 6 │ 7 │ 8 ┃ 6 │ 7 │ 8 ┃
            #  ─ ┣━━━┿━━━┿━━━╋━━━┿━━━┿━━━╋━━━┿━━━┿━━━┫
            #  6 ┃ 0 │ 1 │ 2 ┃ 0 │ 1 │ 2 ┃ 0 │ 1 │ 2 ┃
            #  ─ ┠───┼───┼───╋───┼───┼───╋───┼───┼───┨
            #  7 ┃ 3 │ 4 │ 5 ┃ 3 │ 4 │ 5 ┃ 3 │ 4 │ 5 ┃
            #  ─ ┠───┼───┼───╋───┼───┼───╋───┼───┼───┨
            #  8 ┃ 6 │ 7 │ 8 ┃ 6 │ 7 │ 8 ┃ 6 │ 7 │ 8 ┃
            #  ─ ┗━━━┷━━━┷━━━┻━━━┷━━━┷━━━┻━━━┷━━━┷━━━┛

            # ブロックのインデックス
            block_row = i // 3
            block_col = j // 3

            # ブロック内のインデックス
            self_k = i % 3 * 3 + j % 3

            # 1ブロックにつき1つの数字
            for k in range(self_k + 1, 9):
                r = block_row * 3 + k // 3
                c = block_col * 3 + k % 3
                for n in range(9):
                    cc.add_clause([-p[i][j][n], -p[r][c][n]])

            # 1行につき1つの数字
            for row in range(9):
                if row <= i:
                    # 現在のマスと同じ行は除外
                    continue
                if row // 3 == block_row:
                    # 現在のマスと同じブロックは除外
                    continue
                for n in range(9):
                    cc.add_clause([-p[i][j][n], -p[row][j][n]])

            # 1列につき1つの数字
            for col in range(9):
                if col <= j:
                    # 現在のマスと同じ列は除外
                    continue
                if col // 3 == block_col:
                    # 現在のマスと同じブロックは除外
                    continue
                for n in range(9):
                    cc.add_clause([-p[i][j][n], -p[i][col][n]])

    for hint in sudoku.hints:
        cc.add_clause([p[hint.row][hint.col][hint.value]])

    if opts.output:
        with open(opts.output, 'w') as f:
            f.write(cc.to_dimacs())

    print("Problem:")
    grid = [[-1 for _ in range(9)] for _ in range(9)]
    for hint in sudoku.hints:
        grid[hint.row][hint.col] = hint.value
    display(grid)

    solver = cc.to_solver()
    is_satisfiable = solver.solve()
    if not is_satisfiable:
        print("No solution")
        return

    model = cast(list[int], solver.get_model())
    for i in range(9):
        for j in range(9):
            for k in range(9):
                if model[p[i][j][k].id-1] > 0:
                    grid[i][j] = k
                    break

    print("Solution:")
    display(grid)


if __name__ == '__main__':
    main()
