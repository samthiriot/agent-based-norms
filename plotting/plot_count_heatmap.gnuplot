
set encoding utf8
#set title "proportion des agents réalisant chaque action dans le temps"
set xlabel "pas de temps"
set ylabel "vitesse"

set xrange [*:*]
set yrange [*:*]
set zrange [0:1]

set cbrange [0:1]
set palette defined (0 "white",0.0001 "yellow",1.0 "red")

set size ratio 1/2.4

set grid layerdefault
set pm3d map
#set samples 2

splot 'time_to_action_to_proportion_gnuplot.csv'

print "press a key to close"
pause -1
print "generating the graph"
set term postscript eps enhanced color font 'Verdana,16'
set output "plot_count_heatmap_1.eps"
replot 
!epstopdf plot_count_heatmap_1.eps 
!pdfcrop plot_count_heatmap_1.pdf plot_count_heatmap_1.pdf 
