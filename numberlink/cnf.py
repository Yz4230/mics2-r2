from pysat.solvers import Solver


class Literal:
    def __init__(self, _id: int, *, name: str | None = None) -> None:
        self.id = _id
        self.name = name or f'x{self.id}'

    def __neg__(self):
        return self.__class__(-self.id)

    def __invert__(self):
        return self.__neg__()

    def __str__(self) -> str:
        return self.name


class CnfComposer:
    def __init__(self) -> None:
        self.clauses: list[list[Literal]] = []
        self.num_literals = 0
        self.id_to_literal: dict[int, Literal] = {}

    def new_literal(self, *, name: str | None = None) -> Literal:
        self.num_literals += 1
        literal = Literal(self.num_literals, name=name)
        self.id_to_literal[literal.id] = literal
        return literal

    def add_clause(self, literals: list[Literal]):
        self.clauses.append(literals)

    def to_dimacs(self):
        out = f'p cnf {self.num_literals} {len(self.clauses)}\n'
        lines = []
        for clause in self.clauses:
            line = ' '.join(map(str, map(lambda x: x.id, clause))) + ' 0'
            lines.append(line)
        out += '\n'.join(lines)
        return out

    def to_solver(self) -> Solver:
        clauses = [[l.id for l in c] for c in self.clauses]
        s = Solver(name='cadical153', bootstrap_with=clauses, use_timer=True)
        return s
