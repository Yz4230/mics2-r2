import csv
from glob import glob
from argparse import ArgumentParser
from pathlib import Path
from typing import cast
from pysat.formula import CNF
from pysat.solvers import Solver

parser = ArgumentParser(description='SAT solver benchmarking tool')
parser.add_argument('cnfdir', type=str, help='directory of CNF files')
parser.add_argument('csvfile', type=str, help='output CSV file')
args = parser.parse_args()

solver_names = [
    'cadical153',
    'glucose42',
    'minisat22',
]

cnfs: dict[str, CNF] = {}
files = sorted(glob(f'{args.cnfdir}/*.cnf'))

for cnfpath in files:
    p = Path(cnfpath)
    print(f'Loading {p.name} ...')
    cnfs[p.name] = CNF(from_file=cnfpath, comment_lead=['c', '%', '0'])

results = []

for solver_name in solver_names:
    for cnfpath in files:
        p = Path(cnfpath)
        print(f'Solving {p.name} with {solver_name} ...')
        solver = Solver(name=solver_name,
                        bootstrap_with=cnfs[p.name].clauses,
                        use_timer=True)
        is_sat = cast(bool, solver.solve())
        elapsed = cast(float, solver.time())
        sat = 'SAT' if is_sat else 'UNSAT'
        print(f'{solver_name}, {p.name}, {elapsed:.3f}, {sat}')
        results.append((solver_name, p.name, elapsed, sat))

with open(args.csvfile, 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['solver', 'cnf', 'elapsed', 'result'])
    for row in results:
        writer.writerow(row)
