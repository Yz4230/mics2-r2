from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, cast

from cnf import CnfComposer, Literal

T = TypeVar('T')
Matrix = list[list[T]]


@dataclass(frozen=True, kw_only=True)
class Hint:
    n: int
    row: int
    col: int


class Pattern(Enum):
    TOP_LEFT = 1
    TOP = 2
    LEFT = 3
    CENTER = 4
    TOP_RIGHT = 5
    BOTTOM_LEFT = 6
    RIGHT = 7
    BOTTOM = 8
    BOTTOM_RIGHT = 9


@dataclass(frozen=True, kw_only=True)
class Numberlink:
    name = 'numberlink'
    rows: int
    cols: int
    num_lines: int
    hints: tuple[Hint, ...]
    is_blank: Matrix[bool]

    def get_cell_pattern(self, row: int, col: int) -> Pattern:
        # パターン分け (4x7の場合)
        # 1. 左上
        # 2. 上辺
        # 3. 左辺
        # 4. 中央
        # 5. 右上
        # 6. 左下
        # 7. 右辺
        # 8. 下辺
        # 9. 右下
        #    | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
        #  ─ ┏━━━┯━━━┯━━━┯━━━┯━━━┯━━━┯━━━┓
        #  0 ┃ 1 │ 2 │ 2 │ 2 │ 2 │ 2 │ 5 ┃
        #  ─ ┠───┼───┼───┼───┼───┼───┼───┨
        #  1 ┃ 3 │ 4 │ 4 │ 4 │ 4 │ 4 │ 7 ┃
        #  ─ ┠───┼───┼───┼───┼───┼───┼───┨
        #  2 ┃ 3 │ 4 │ 4 │ 4 │ 4 │ 4 │ 7 ┃
        #  ─ ┠───┼───┼───┼───┼───┼───┼───┨
        #  3 ┃ 6 │ 8 │ 8 │ 8 │ 8 │ 8 │ 9 ┃
        #  ─ ┗━━━┷━━━┷━━━┷━━━┷━━━┷━━━┷━━━┛
        top = row == 0
        bottom = row == self.rows-1
        left = col == 0
        right = col == self.cols-1
        if top and left:
            return Pattern.TOP_LEFT
        elif top and right:
            return Pattern.TOP_RIGHT
        elif bottom and left:
            return Pattern.BOTTOM_LEFT
        elif bottom and right:
            return Pattern.BOTTOM_RIGHT
        elif top:
            return Pattern.TOP
        elif bottom:
            return Pattern.BOTTOM
        elif left:
            return Pattern.LEFT
        elif right:
            return Pattern.RIGHT
        return Pattern.CENTER

    def show(self, *, with_answer: tuple[Matrix[bool], Matrix[bool]] | None = None):
        answer_s: Matrix[bool] | None = None
        answer_e: Matrix[bool] | None = None
        if with_answer is not None:
            answer_s, answer_e = with_answer

        grid = [['' for _ in range(self.cols)] for _ in range(self.rows)]
        for h in self.hints:
            grid[h.row][h.col] = str(h.n + 1)

        output = '┌' + '───┬' * (self.cols-1) + '───┐\n'
        for i in range(self.rows):
            for j in range(self.cols):
                north = answer_s is not None \
                    and i != 0 and answer_s[i-1][j]
                south = answer_s is not None \
                    and i != self.rows-1 and answer_s[i][j]
                east = answer_e is not None \
                    and j != self.cols-1 and answer_e[i][j]
                west = answer_e is not None \
                    and j != 0 and answer_e[i][j-1]

                if j == 0:
                    output += '│'
                if grid[i][j]:
                    output += f'{grid[i][j]:^3}'
                elif north and south:
                    output += ' ┃ '
                elif east and west:
                    output += '━━━'
                elif north and east:
                    output += ' ┗━'
                elif north and west:
                    output += '━┛ '
                elif south and east:
                    output += ' ┏━'
                elif south and west:
                    output += '━┓ '
                else:
                    output += '   '
                if east:
                    output += '┿'
                else:
                    output += '│'
            output += '\n'

            if i == self.rows-1:
                continue
            for j in range(self.cols):
                if j == 0:
                    output += '├'
                if answer_s is not None and answer_s[i][j]:
                    output += '─╂─'
                else:
                    output += '───'
                if j == self.cols-1:
                    output += '┤'
                else:
                    output += '┼'
            output += '\n'

        output += '└' + '───┴' * (self.cols-1) + '───┘'

        print(output)


def load_problem(filename: str) -> Numberlink:
    nl_rows = 0
    nl_cols = 0
    nl_line_num = 0
    hints: list[Hint] = []
    with open(filename) as f:
        for line in f.readlines():
            line = line.strip()
            if line == '' or line.startswith('#'):
                # if line is empty or comment, skip
                continue

            parts = line.split()
            if parts[0] == 'SIZE':
                # SIZE 10X10
                cols, rows = map(int, parts[1].split('X'))
                nl_rows = rows
                nl_cols = cols
            elif parts[0] == 'LINE_NUM':
                # LINE_NUM 7
                nl_line_num = int(parts[1])
            else:
                # LINE#1 (8,1)-(8,8)
                n = int(parts[0].split('#')[1])
                ps = parts[1].split('-')
                p1_text = ps[0].removeprefix('(').removesuffix(')')
                p1_col, p1_row = map(int, p1_text.split(','))
                p1 = Hint(n=n-1, row=p1_row, col=p1_col)
                p2_text = ps[1].removeprefix('(').removesuffix(')')
                p2_col, p2_row = map(int, p2_text.split(','))
                p2 = Hint(n=n-1, row=p2_row, col=p2_col)
                hints.append(p1)
                hints.append(p2)

    is_blank: Matrix[bool] = []
    for i in range(nl_rows):
        is_blank.append([])
        for j in range(nl_cols):
            is_blank[i].append(True)
    for h in hints:
        is_blank[h.row][h.col] = False

    return Numberlink(
        rows=nl_rows,
        cols=nl_cols,
        num_lines=nl_line_num,
        hints=tuple(hints),
        is_blank=is_blank,
    )


class Constraint(Enum):
    BASIC = 1
    U_SHAPE = 2
    U_SHAPE_LONG = 3

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def from_string(cls, s: str) -> 'Constraint':
        return cls(int(s))


parser = ArgumentParser(
    prog='numberlink solver',
    description='numberlink solver',
)
parser.add_argument(
    'filename',
    help='problem file',
)
parser.add_argument(
    '-c', '--constraint',
    choices=[Constraint.U_SHAPE, Constraint.U_SHAPE_LONG],
    default=[],
    type=Constraint.from_string,
    help='select constraint',
    nargs='+',
)
parser.add_argument(
    '-t', '--show-only-elapsed-time',
    action='store_true',
    help='show only elapsed time',
)
parser.add_argument(
    '-o', '--output',
    help='output dimacs file',
)
opts = parser.parse_args()


def main():
    nl = load_problem(opts.filename)
    cc = CnfComposer()

    # s_ijは(i, j)から下に線が伸びているかどうか
    # s_ij in {0, 1}
    s: Matrix[Literal] = []
    for i in range(nl.rows-1):  # 最後の行からは線が伸びない
        s.append([])
        for j in range(nl.cols):
            s[i].append(cc.new_literal(name=f's_{i}{j}'))

    # e_ijは(i, j)から右に線が伸びているかどうか
    # e_ij in {0, 1}
    e: Matrix[Literal] = []
    for i in range(nl.rows):
        e.append([])
        for j in range(nl.cols-1):  # 最後の列からは線が伸びない
            e[i].append(cc.new_literal(name=f'e_{i}{j}'))

    # x_ijnは(i, j)がnのセルにつながっているかどうか
    # x_ijn in {0, 1, 2, ..., nl.line_num}
    # x[i][j][n] -> x_ijn = n
    x: Matrix[list[Literal]] = []
    for i in range(nl.rows):
        x.append([])
        for j in range(nl.cols):
            x[i].append([])
            for n in range(nl.num_lines):
                x[i][j].append(cc.new_literal(name=f'x_{i}{j}{n}'))
            # at least one x_ijn is true
            # cc.add_clause(x[i][j])
            # at most one x_ijn is true
            for a in range(nl.num_lines):
                for b in range(a + 1, nl.num_lines):
                    cc.add_clause([-x[i][j][a], -x[i][j][b]])

    for h in nl.hints:
        cc.add_clause([x[h.row][h.col][h.n]])

    # 1. 空白マス(i, j)から線が2本出るか、1本も出ない
    # 2. 数字マス(i, j)から線が1本だけ出る
    for i in range(nl.rows):
        for j in range(nl.cols):
            # 上のマスから線が出ているかどうか
            # p1 = s[i-1][j]
            # 左のマスから線が出ているかどうか
            # p2 = e[i][j-1]
            # 下のマスへ線が出ているかどうか
            # p3 = s[i][j]
            # 右のマスへ線が出ているかどうか
            # p4 = e[i][j]

            pat = nl.get_cell_pattern(i, j)
            if nl.is_blank[i][j]:  # 空白マスの場合
                if pat == Pattern.TOP_LEFT:  # パターン1: 左上
                    p3 = s[i][j]
                    p4 = e[i][j]
                    # s_ij + e_ij <= 2は自動的に成立する
                    # s_ij + e_ij != 1
                    cc.add_clause([-p3, p4])
                    cc.add_clause([p3, -p4])
                elif pat == Pattern.TOP:  # パターン2: 上辺
                    p2 = e[i][j-1]
                    p3 = s[i][j]
                    p4 = e[i][j]
                    # e_i(j-1) + s_ij + e_ij <= 2
                    cc.add_clause([-p2, -p3, -p4])
                    # e_i(j-1) + s_ij + e_ij != 1
                    cc.add_clause([-p2, p3, p4])
                    cc.add_clause([p2, -p3, p4])
                    cc.add_clause([p2, p3, -p4])
                elif pat == Pattern.LEFT:  # パターン3: 左辺
                    p1 = s[i-1][j]
                    p3 = s[i][j]
                    p4 = e[i][j]
                    # s_(i-1)j + s_ij + e_ij <= 2
                    cc.add_clause([-p1, -p3, -p4])
                    # s_(i-1)j + s_ij + e_ij != 1
                    cc.add_clause([-p1, p3, p4])
                    cc.add_clause([p1, -p3, p4])
                    cc.add_clause([p1, p3, -p4])
                elif pat == Pattern.CENTER:  # パターン4: 中央
                    p1 = s[i-1][j]
                    p2 = e[i][j-1]
                    p3 = s[i][j]
                    p4 = e[i][j]
                    # s_(i-1)j + e_i(j-1) + s_ij + e_ij <= 2
                    cc.add_clause([-p1, -p2, -p3])
                    cc.add_clause([-p1, -p2, -p4])
                    cc.add_clause([-p1, -p3, -p4])
                    cc.add_clause([-p2, -p3, -p4])
                    # s_(i-1)j + e_i(j-1) + s_ij + e_ij != 1
                    cc.add_clause([-p1, p2, p3, p4])
                    cc.add_clause([p1, -p2, p3, p4])
                    cc.add_clause([p1, p2, -p3, p4])
                    cc.add_clause([p1, p2, p3, -p4])
                elif pat == Pattern.TOP_RIGHT:  # パターン5: 右上
                    p2 = e[i][j-1]
                    p3 = s[i][j]
                    # e_i(j-1) + s_ij <= 2は自動的に成立する
                    # e_i(j-1) + s_ij != 1
                    cc.add_clause([-p2, p3])
                    cc.add_clause([p2, -p3])
                elif pat == Pattern.BOTTOM_LEFT:  # パターン6: 左下
                    p1 = s[i-1][j]
                    p4 = e[i][j]
                    # s_(i-1)j + e_ij <= 2は自動的に成立する
                    # s_(i-1)j + e_ij != 1
                    cc.add_clause([-p1, p4])
                    cc.add_clause([p1, -p4])
                elif pat == Pattern.RIGHT:  # パターン7: 右辺
                    p1 = s[i-1][j]
                    p2 = e[i][j-1]
                    p3 = s[i][j]
                    # s_(i-1)j + e_i(j-1) + s_ij <= 2
                    cc.add_clause([-p1, -p2, -p3])
                    # s_(i-1)j + e_i(j-1) + s_ij != 1
                    cc.add_clause([-p1, p2, p3])
                    cc.add_clause([p1, -p2, p3])
                    cc.add_clause([p1, p2, -p3])
                elif pat == Pattern.BOTTOM:  # パターン8: 下辺
                    p1 = s[i-1][j]
                    p2 = e[i][j-1]
                    p4 = e[i][j]
                    # s_(i-1)j + e_i(j-1) + e_ij <= 2
                    cc.add_clause([-p1, -p2, -p4])
                    # s_(i-1)j + e_i(j-1) + e_ij != 1
                    cc.add_clause([-p1, p2, p4])
                    cc.add_clause([p1, -p2, p4])
                    cc.add_clause([p1, p2, -p4])
                elif pat == Pattern.BOTTOM_RIGHT:  # パターン9: 右下
                    p1 = s[i-1][j]
                    p2 = e[i][j-1]
                    # s_(i-1)j + e_i(j-1) <= 2は自動的に成立する
                    # s_(i-1)j + e_i(j-1) != 1
                    cc.add_clause([-p1, p2])
                    cc.add_clause([p1, -p2])
                else:
                    raise RuntimeError('unreachable')
            else:  # 数字マスの場合
                if pat == Pattern.TOP_LEFT:  # パターン1: 左上
                    p3 = s[i][j]
                    p4 = e[i][j]
                    # s_ij + e_ij >= 1
                    cc.add_clause([p3, p4])
                    # s_ij + e_ij <= 2
                    cc.add_clause([-p3, -p4])
                elif pat == Pattern.TOP:  # パターン2: 上辺
                    p2 = e[i][j-1]
                    p3 = s[i][j]
                    p4 = e[i][j]
                    # e_i(j-1) + s_ij + e_ij >= 1
                    cc.add_clause([p2, p3, p4])
                    # e_i(j-1) + s_ij + e_ij < 2
                    cc.add_clause([-p2, -p3])
                    cc.add_clause([-p2, -p4])
                    cc.add_clause([-p3, -p4])
                elif pat == Pattern.LEFT:  # パターン3: 左辺
                    p1 = s[i-1][j]
                    p3 = s[i][j]
                    p4 = e[i][j]
                    # s_(i-1)j + s_ij + e_ij >= 1
                    cc.add_clause([p1, p3, p4])
                    # s_(i-1)j + s_ij + e_ij < 2
                    cc.add_clause([-p1, -p3])
                    cc.add_clause([-p1, -p4])
                    cc.add_clause([-p3, -p4])
                elif pat == Pattern.CENTER:  # パターン4: 中央
                    p1 = s[i-1][j]
                    p2 = e[i][j-1]
                    p3 = s[i][j]
                    p4 = e[i][j]
                    # s_(i-1)j + e_i(j-1) + s_ij + e_ij >= 1
                    cc.add_clause([p1, p2, p3, p4])
                    # s_(i-1)j + e_i(j-1) + s_ij + e_ij < 2
                    cc.add_clause([-p1, -p2])
                    cc.add_clause([-p1, -p3])
                    cc.add_clause([-p1, -p4])
                    cc.add_clause([-p2, -p3])
                    cc.add_clause([-p2, -p4])
                    cc.add_clause([-p3, -p4])
                elif pat == Pattern.TOP_RIGHT:  # パターン5: 右上
                    p2 = e[i][j-1]
                    p3 = s[i][j]
                    # e_i(j-1) + s_ij >= 1
                    cc.add_clause([p2, p3])
                    # e_i(j-1) + s_ij < 2
                    cc.add_clause([-p2, -p3])
                elif pat == Pattern.BOTTOM_LEFT:  # パターン6: 左下
                    p1 = s[i-1][j]
                    p4 = e[i][j]
                    # s_(i-1)j + e_ij >= 1
                    cc.add_clause([p1, p4])
                    # s_(i-1)j + e_ij < 2
                    cc.add_clause([-p1, -p4])
                elif pat == Pattern.RIGHT:  # パターン7: 右辺
                    p1 = s[i-1][j]
                    p2 = e[i][j-1]
                    p3 = s[i][j]
                    # s_(i-1)j + e_i(j-1) + s_ij >= 1
                    cc.add_clause([p1, p2, p3])
                    # s_(i-1)j + e_i(j-1) + s_ij < 2
                    cc.add_clause([-p1, -p2])
                    cc.add_clause([-p1, -p3])
                    cc.add_clause([-p2, -p3])
                elif pat == Pattern.BOTTOM:  # パターン8: 下辺
                    p1 = s[i-1][j]
                    p2 = e[i][j-1]
                    p4 = e[i][j]
                    # s_(i-1)j + e_i(j-1) + e_ij >= 1
                    cc.add_clause([p1, p2, p4])
                    # s_(i-1)j + e_i(j-1) + e_ij < 2
                    cc.add_clause([-p1, -p2])
                    cc.add_clause([-p1, -p4])
                    cc.add_clause([-p2, -p4])
                elif pat == Pattern.BOTTOM_RIGHT:  # パターン9: 右下
                    p1 = s[i-1][j]
                    p2 = e[i][j-1]
                    # s_(i-1)j + e_i(j-1) >= 1
                    cc.add_clause([p1, p2])
                    # s_(i-1)j + e_i(j-1) < 2
                    cc.add_clause([-p1, -p2])

    # s_ij = 1 -> x_ij = x_(i+1)j
    for i in range(nl.rows-1):
        for j in range(nl.cols):
            for n in range(nl.num_lines):
                # if (i, j) has down line, then (i, j) is connected to (i+1, j)
                cc.add_clause([-s[i][j], -x[i][j][n], x[i+1][j][n]])
                cc.add_clause([-s[i][j], x[i][j][n], -x[i+1][j][n]])

    # e_ij = 1 -> x_ij = x_i(j+1)
    for i in range(nl.rows):
        for j in range(nl.cols-1):
            for n in range(nl.num_lines):
                # if (i, j) has right line, then (i, j) is connected to (i, j+1)
                cc.add_clause([-e[i][j], -x[i][j][n], x[i][j+1][n]])
                cc.add_clause([-e[i][j], x[i][j][n], -x[i][j+1][n]])

    if Constraint.U_SHAPE in opts.constraint:
        # 回り道を排除する
        # 1: 2x2の場合
        # 1.1:
        # ┌───┬───┐
        # │ ━━┿━┓ │
        # ├───┼─╂─┤
        # │ ━━┿━┛ │
        # └───┴───┘
        # 1.2:
        # ┌───┬───┐
        # │ ┏━┿━┓ │
        # ├─╂─┼─╂─┤
        # │ ┃ │ ┃ │
        # └───┴───┘
        # 1.3:
        # ┌───┬───┐
        # │ ┏━┿━━ │
        # ├─╂─┼───┤
        # │ ┗━┿━━ │
        # └───┴───┘
        # 1.4:
        # ┌───┬───┐
        # │ ┃ │ ┃ │
        # ├─╂─┼─╂─┤
        # │ ┗━┿━┛ │
        # └───┴───┘
        for i in range(nl.rows-1):
            for j in range(nl.cols-1):
                # 1
                cc.add_clause([-e[i][j], -s[i][j+1], -e[i+1][j]])
                # 2
                cc.add_clause([-e[i][j], -s[i][j], -s[i][j+1]])
                # 3
                cc.add_clause([-e[i][j], -s[i][j], -e[i+1][j]])
                # 4
                cc.add_clause([-s[i][j], -s[i][j+1], -e[i+1][j]])

    if Constraint.U_SHAPE_LONG in opts.constraint:
        # 2: 3x2の場合
        # 2.1:
        # ┌───┬───┐
        # │ ━━┿━┓ │
        # ├───┼─╂─┤
        # │ b │ ┃ │
        # ├───┼─╂─┤
        # │ ━━┿━┛ │
        # └───┴───┘
        # 2.2:
        # ┌───┬───┐
        # │ ┏━┿━━ │
        # ├─╂─┼───┤
        # │ ┃ │ b │
        # ├─╂─┼───┤
        # │ ┗━┿━━ │
        # └───┴───┘
        for i in range(nl.rows-2):
            for j in range(nl.cols-1):
                # 1
                if nl.is_blank[i+1][j]:
                    cc.add_clause(
                        [-e[i][j], -s[i][j+1], -s[i+1][j+1], -e[i+2][j]])
                # 2
                if nl.is_blank[i+1][j+1]:
                    cc.add_clause([-e[i][j], -s[i][j], -s[i+1][j], -e[i+2][j]])

        # 3: 2x3の場合
        # 3.1:
        # ┌───┬───┬───┐
        # │ ┏━┿━━━┿━┓ │
        # ├─╂─┼───┼─╂─┤
        # │ ┃ │ b │ ┃ │
        # └───┴───┴───┘
        # 3.2:
        # ┌───┬───┬───┐
        # │ ┃ │ b │ ┃ │
        # ├─╂─┼───┼─╂─┤
        # │ ┗━┿━━━┿━┛ │
        # └───┴───┴───┘
        for i in range(nl.rows-1):
            for j in range(nl.cols-2):
                # 1
                if nl.is_blank[i+1][j+1]:
                    cc.add_clause([-e[i][j], -s[i][j], -e[i][j+1], -s[i][j+2]])
                # 2
                if nl.is_blank[i][j+1]:
                    cc.add_clause(
                        [-s[i][j], -e[i+1][j], -e[i+1][j+1], -s[i][j+2]])

    if opts.output is not None:
        with open(opts.output, 'w') as f:
            f.write(cc.to_dimacs())

    if not opts.show_only_elapsed_time:
        print('Problem:')
        nl.show()

    solver = cc.to_solver()
    is_satisfiable = solver.solve()

    if opts.show_only_elapsed_time:
        print(solver.time())
        return

    if (not is_satisfiable):
        print('UNSAT')
        core = solver.get_core()
        print(core)
        return

    model = cast(list[int], solver.get_model())
    answer_s: Matrix[bool] = []
    for i in range(nl.rows-1):
        answer_s.append([])
        for j in range(nl.cols):
            answer_s[i].append(model[s[i][j].id-1] > 0)
    answer_e: Matrix[bool] = []
    for i in range(nl.rows):
        answer_e.append([])
        for j in range(nl.cols-1):
            answer_e[i].append(model[e[i][j].id-1] > 0)

    print('Answer:')
    nl.show(with_answer=(answer_s, answer_e))


if __name__ == '__main__':
    main()
