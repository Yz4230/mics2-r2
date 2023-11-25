from argparse import ArgumentParser
import io
import requests
import tarfile

urls = [
    'https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf20-91.tar.gz',
    'https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf50-218.tar.gz',
    'https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf75-325.tar.gz',
    'https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf100-430.tar.gz',
    'https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf125-538.tar.gz',
    'https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf150-645.tar.gz',
    'https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf175-753.tar.gz',
    'https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf200-860.tar.gz',
    'https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf225-960.tar.gz',
    'https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf250-1065.tar.gz',
    'https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/QG/QG.tar.gz',
    'https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/BMC/bmc.tar.gz'
]

parser = ArgumentParser(description='SATLIB problem downloader')
parser.add_argument('outdir', type=str, help='output directory')
opts = parser.parse_args()

for url in urls:
    print(f'Downloading {url}...')
    r = requests.get(url, allow_redirects=True)
    r.raise_for_status()
    with tarfile.open(fileobj=io.BytesIO(r.content), mode='r:gz') as tar:
        tar.extractall(opts.outdir)
