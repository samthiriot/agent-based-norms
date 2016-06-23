agentid = "1"

set encoding utf8
set term push

set xrange [0:*]
set yrange [*:*]
set zrange [*:*]

set ylabel "action (speed)"
set palette gray


#set grid layerdefault
set pm3d map 


set term postscript eps enhanced color font 'Verdana,16'
set output "plot_agent".agentid."_utilities.eps"

unset key 

set origin 0,0
set size 1.0,2.6
set multiplot
set size 1,0.6

set origin 0,0
set xlabel "time steps"
set xtics


sizeY = 0.4
currentY = 0

set title "aggregated" offset -15,-0.5
currentY = currentY+sizeY
set origin 0,currentY
set view map
splot 'utility_aggregated_agent'.agentid with pm3d title ""
set xtics format ""
unset xlabel
#unset xtics

set title "hedonism" offset -15,-0.5
currentY = currentY+sizeY
set origin 0,currentY
splot 'utility_hedonism_agent'.agentid

set title "social" offset -15,-0.5
currentY = currentY+sizeY
set origin 0,currentY
splot 'utility_social_sanction_agent'.agentid

#set title "points" offset -15,-0.5
#currentY = currentY+sizeY
#set origin 0,currentY
#splot 'utility_points_agent'.agentid 

set title "proportion of actions in the population" offset -6,-0.5
currentY = currentY+sizeY
set origin 0,currentY
set cbrange [0:1]
set palette defined (0 "white",0.0001 "yellow",1.0 "red")
set xtics (0,20,40,60,80,100,120,140,160,180,200)
splot 'time_to_action_to_proportion_gnuplot.csv'

unset multiplot

system("epstopdf plot_agent".agentid."_utilities.eps")
system("pdfcrop plot_agent".agentid."_utilities.pdf plot_agent".agentid."_utilities.pdf") 
system("xdg-open plot_agent".agentid."_utilities.pdf")

