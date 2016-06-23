agentid = "1"

set encoding utf8
set term push

set xrange [0:*]
set yrange [*:*]
set zrange [*:*]

set ylabel "action (vitesse)"
set palette gray

set size ratio 1/4

#set grid layerdefault
set pm3d map 
#set pm3d interpolate 1,1

#set samples 2



# ============= agent 1 utility / aggregated

# display
set title "aggregated utility"
splot 'utility_aggregated_agent'.agentid 

# write to file
print "press a key to shift to the next graph..."
pause -1
print "writing the eps and pdf versions of the graph..."
set term postscript eps enhanced color font 'Verdana,16'
set output "plot_agent".agentid."_utility_aggregated.eps"
unset title
replot 
system("epstopdf plot_agent".agentid."_utility_aggregated.eps")
system("pdfcrop plot_agent".agentid."_utility_aggregated.pdf plot_".agentid."_utility_aggregated.pdf") 
set term pop

# ============= agent 1 utility / points

# display
set title "points utility"
splot 'utility_points_agent'.agentid 

# write to file
print "press a key to shift to the next graph..."
pause -1
print "writing the eps and pdf versions of the graph..."
set term postscript eps enhanced color font 'Verdana,16'
set output "plot_agent".agentid."_utility_points.eps"
unset title
replot 
system("epstopdf plot_agent".agentid."_utility_points.eps")
system("pdfcrop plot_agent".agentid."_utility_points.pdf plot_".agentid."_utility_points.pdf") 
set term pop



# ============= agent 1 utility / social_sanction

# display
set title "social utility"
splot 'utility_social_sanction_agent'.agentid

# write to file
print "press a key to shift to the next graph..."
pause -1
print "writing the eps and pdf versions of the graph..."
set term postscript eps enhanced color font 'Verdana,16'
set output "plot_agent".agentid."_utility_social_sanction.eps"
unset title
replot 
system("epstopdf plot_agent".agentid."_utility_social_sanction.eps")
system("pdfcrop plot_agent".agentid."_utility_social_sanction.pdf plot_".agentid."_utility_social_sanction.pdf") 
set term pop


# ============= agent 1 utility / hedonism

# display
set title "hedonism utility"
set xlabel "pas de temps"
splot 'utility_hedonism_agent'.agentid

# write to file
print "press a key to shift to the next graph..."
pause -1
print "writing the eps and pdf versions of the graph..."
set term postscript eps enhanced color font 'Verdana,16'
set output "plot_agent".agentid."_utility_hedonism.eps"
unset title
replot 
system("epstopdf plot_agent".agentid."_utility_hedonism.eps")
system("pdfcrop plot_agent".agentid."_utility_hedonism.pdf plot_".agentid."_utility_hedonism.pdf") 
set term pop



