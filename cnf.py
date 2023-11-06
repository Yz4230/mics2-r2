
class Literal:
    count = 0

    def __init__(self, *, _id: int | None = None, name: str | None = None) -> None:
        if _id is None:
            self.id = Literal.count + 1
            Literal.count += 1
        else:
            self.id = _id

        self.name = name or f'x{self.id}'

    def __neg__(self):
        return self.__class__(_id=-self.id)

    def __invert__(self):
        return self.__neg__()

    def __str__(self) -> str:
        return self.name


class CNF:
    def __init__(self) -> None:
        self.clauses: list[list[Literal]] = []

    def add_clause(self, literals: list[Literal]):
        self.clauses.append(literals)

    def to_dimacs(self):
        out = f'p cnf {Literal.count} {len(self.clauses)}\n'
        lines = []
        for clause in self.clauses:
            line = ' '.join(map(str, map(lambda x: x.id, clause))) + ' 0'
            lines.append(line)
        out += '\n'.join(lines)
        return out
