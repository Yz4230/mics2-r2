#!/opt/homebrew/bin/gnuplot -persist

set terminal png
set font "Helvetica, 16"
set xlabel "Number of Solved Instances" font "Helvetica, 16"
set ylabel "Time (s)" font "Helvetica,16"
set output "cactus.png"
csv = "result.csv"

cactus(method) = sprintf("< echo 0; grep %s %s | grep -v 'UNSAT' | cut -d',' -f 3 | sort -g", method, csv)

set key top left
set style data points
set pointsize 0.9
set style increment user

# Set x range to [2500:3500]
set xrange [3000:3150]


plot \
cactus("^cadical153") title "cadical", \
cactus("^glucose42") title "glucose", \
cactus("^minisat22") title "minisat"
