from dataclasses import dataclass
import subprocess
from glob import glob
from sys import executable


@dataclass(frozen=True, kw_only=True)
class Problem:
    rows: int
    cols: int
    num_lines: int


@dataclass(frozen=True, kw_only=True)
class Result:
    label: str
    elapsed: float
    problem: Problem


def parse_problem(path: str) -> Problem:
    with open(path, 'r') as f:
        lines = f.readlines()
    # SIZE 10X10
    rows, cols = map(int, lines[0].split(' ')[1].split('X'))
    # LINE_NUM 7
    num_lines = int(lines[1].split(' ')[1])
    return Problem(rows=rows, cols=cols, num_lines=num_lines)


def main():
    # numberlink/ADC2014_QA/Q
    problems = glob('numberlink/ADC2014_QA/Q/*.txt')
    problems.sort()

    # path: details
    details: dict[str, Problem] = {}
    for problem in problems:
        details[problem] = parse_problem(problem)

    # label: args
    competitors = {
        "original": "",
        "original + u-shape": "-c 2",
        "original + u-shape-long": "-c 3",
        "original + u-shape + u-shape-long": "-c 2 3",
    }

    results: list[Result] = []

    for label, args in competitors.items():
        for problem in problems:
            cmd = f'{executable} numberlink/main.py -t {problem} {args}'
            elapsed_list: list[float] = []
            for i in range(3):
                process = subprocess.run(cmd, shell=True, capture_output=True)
                # output should be time elapsed
                elapsed = float(process.stdout.decode('utf-8').strip())
                elapsed_list.append(elapsed)
                print(f'{label}:{i} {problem} {elapsed}')

            avg_elapsed = sum(elapsed_list) / len(elapsed_list)
            result = Result(
                label=label,
                elapsed=avg_elapsed,
                problem=details[problem])
            results.append(result)

    # export to csv
    with open('numberlink/results.csv', 'w') as f:
        f.write('label,elapsed,rows,cols,num_lines\n')
        for result in results:
            data = [
                result.label,
                result.elapsed,
                result.problem.rows,
                result.problem.cols,
                result.problem.num_lines,
            ]
            f.write(','.join(map(str, data)) + '\n')


if __name__ == '__main__':
    main()
