from dataclasses import dataclass
import json

from cnf import CNF, Literal


@dataclass(frozen=True)
class Sudoku:
    name = 'sudoku'
    rows: int
    cols: int


@dataclass(frozen=True)
class Hint:
    row: int  # 1-indexed
    col: int  # 1-indexed
    value: int  # 1-indexed


def _main():
    with open('sudoku.txt') as f:
        sudoku: Sudoku | None = None
        hints: list[Hint] = []
        for line in f.readlines():
            parts = line.split()
            if parts[0] == 'p' and parts[1] == Sudoku.name:
                sudoku = Sudoku(*map(int, parts[2:]))
            else:
                h = Hint(*map(int, parts))
                hints.append(h)
        assert sudoku is not None

    cnf = CNF()

    # p[i][j][k] := マス(i, j)に数字kが入る
    p: list[list[list[Literal]]] = []

    # 全てのマスについて、1~9のうち1つの数字が入る
    for i in range(9):
        p.append([])
        for j in range(9):
            p[i].append([])
            for k in range(9):
                literal = Literal(name=f'p_{i}{j}={k}')
                p[i][j].append(literal)
            # p[i][j][1~9]のうち、少なくとも1つは真
            cnf.add_clause(p[i][j])
            for a in range(9):
                for b in range(a + 1, 9):
                    # p[i][j][a]とp[i][j][b]のうち、両方とも真になることはない
                    cnf.add_clause([-p[i][j][a], -p[i][j][b]])

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
                    cnf.add_clause([-p[i][j][n], -p[r][c][n]])

            # 1行につき1つの数字
            for row in range(9):
                if row <= i:
                    # 現在のマスと同じ行は除外
                    continue
                if row // 3 == block_row:
                    # 現在のマスと同じブロックは除外
                    continue
                for n in range(9):
                    cnf.add_clause([-p[i][j][n], -p[row][j][n]])

            # 1列につき1つの数字
            for col in range(9):
                if col <= j:
                    # 現在のマスと同じ列は除外
                    continue
                if col // 3 == block_col:
                    # 現在のマスと同じブロックは除外
                    continue
                for n in range(9):
                    cnf.add_clause([-p[i][j][n], -p[i][col][n]])

    for hint in hints:
        cnf.add_clause([p[hint.row-1][hint.col-1][hint.value-1]])

    with open('sudoku.cnf', 'w') as f:
        f.write(cnf.to_dimacs())

    with open('id_to_str.json', 'w') as f:
        d = {}
        for i in range(9):
            for j in range(9):
                for k in range(9):
                    p_ijk = p[i][j][k]
                    d[str(p_ijk.id)] = p_ijk.name
        json.dump(d, f)


def main():
    with open('id_to_str.json') as f:
        json_str = f.read()
        id_to_str = json.loads(json_str)

    with open('result.txt') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('s '):
                if line == 's SATISFIABLE\n':
                    print('SATISFIABLE')
                else:
                    print('UNSATISFIABLE')
            elif line.startswith('v '):
                literals = list(map(int, line.split()[1:]))
                for literal in literals:
                    if literal > 0:
                        print(id_to_str[str(literal)], end=' ')
        print()


if __name__ == '__main__':
    main()
