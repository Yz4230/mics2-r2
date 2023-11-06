
class Literal:
    count = 0

    def __init__(self, *, _id: int | None = None) -> None:
        if _id is not None:
            self.id = _id
        else:
            self.id = Literal.count + 1  # 1-indexed
            Literal.count += 1

    def __neg__(self):
        return self.__class__(_id=-self.id)

    def __invert__(self):
        return self.__neg__()


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
