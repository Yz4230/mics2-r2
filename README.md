# MICS実験第2 第2ラウンド

## 実行環境

- CPU: Apple M1
- OS: macOS Sonoma 14.1.1
- Python: 3.12.0

## 実行方法

### 環境構築

```bash
pip install python-sat
```

### 実行

#### 数独ソルバーの実行

```bash
python sudoku/main.py sudoku/problem/sudoku1.dat -o sudoku1.cnf
```

#### ナンバーリンクソルバーの実行

```bash
python numberlink/main.py numberlink/ADC2014_QA/Q/NL_Q06.txt -c 2 3 -o numberlink06.cnf
```
