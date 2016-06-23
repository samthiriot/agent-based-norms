# agent-based-norms

The implementation of a model that describes the behaviour of individuals under the pressure of institutional and social norms.
It is provided to enable the replication of experiments described in academic publications.

Provided "as is" without express or implied warrant.

# prerequires

This model was developped under in Python 2.7 under Linux. 

It is supposed to be ran in command line into a terminal. If you don't understand what these words mean, you better call a friend. 

To run it, you need:
* a Linux machine (might run on any OS having a Python intepreter)
* a python installation (python 2.7 or higher)

To plot the graphics, you need:
* a Linux machine (some twists would be required to make it run under another system)
* a working gnuplot installation (4.6 or higher)
* "epstopdf' should be installed (often packaged into texlive-font-utils)
* "pdfcrop" should be installed (often packaged into texlive-extra-utils)

# drive simulation experiments

## how to start the simulation

To start the simulation, assuming you are at the root of the repository, I recommand you create a subdirectory that will store all the files 
that will result from the simulation experiment:

```bash
$ mkdir xp1
$ cd xp1
```

Then to start the simulation, type in:
```bash
$ python ../model/model.py  &> simulation.log &
[2] 27165
```

This will run the simulation, and write the simulation results into the file `simulation.log` .

The simulation takes time (~2 to 5 minutes for 100 agents and 200 time steps on a standard computer). 

While waiting, you can watch the very verbose logs that are written during the simulation:
```bash
$ tail -f simulation.log 
```
During the generation, many files are generated:
* `time_to_action_to_proportion_gnuplot.csv` : contains, at each timstep, the proportion of agents that do every action. Is formatted so it can be used as grid data by gnuplot. 
* `time_to_points.dat` : contains the proportion of agents having 0, 1, 2... 12 points on their driving license at each time step
* for each observed agent, the following files contain gnuplot-ready data
    * `utility_aggregated_agent<agentid>`: contains at each time step, the agregated utility for the agent having this id 
    * `utility_<criteria>_agent<agentid>`: contains at each time step, the utility of for the agent of this id for each criteria 

## how to experiment

By tuning the `Experiment` initialization in the `model/model.py` file, you can drive various experiments.

```python
Experiment(
            agents_count=100,
            duration=200, 
            law=Norm(
                        "90kmh", 
                        { a:{"points":{-3}} if a>90 else {} for a in current_model.actions},
                        { a: ({"points":{-3}} if a>95 else {"points":{0}} ) for a in current_model.actions}
                        ),
            inform_law_step=10,
            campain_application=[(50,100,0.3) ], #, (200,300,0.1)
            campains_information=[],#[(20,50,0.1, { a:{"hedonism":{0}} if a>100 else {} for a in current_model.actions})],
            count_interactions_observation=0, 
            count_interaction_social_coercition=5, 
            count_interaction_small_talk=0,
            agents_to_observe={"agent1","agent2"}
            ).run()
```

* Tune `agents_count` to change the count of simulated agents
* Tune `duration` to change the duration of the simulation
* Tune `inform_law_step` to change when the law is transmitted into the populatiopn
* Tune `campain_application` to define no, one or several campains of application of the norm; each campain is defined by timestep of begin, end and probability of control `(50,100,0.3)` 
* Tune `campains_information` to define no, one or several campains of information of the norm; each campain is defined by timestep of begin, end, the probability of control and the message sent to agents
* Tune `count_interactions_observation` to define how many agents each agent is observing at each timestep
* Tune `count_interactions_social_coercition` to define how many agents each agent is observing and possibly sanctionning at each timestep
* Tune `count_interactions_small_talk` to define how many agents each agent is discussing with at each timestep
* Tune the `agents_to_observe` list to monitor what happens for other individual agents. 

You can also:
* to enable replicability of the experiments (i.e. they always give the same results), comment the `random.seed()` or define a specific seed, such as `random.seed(5)` 

# how to plot results

All these command lines assume you are in the directory `<repository_root>/<experiment_directory>/`


## plot the graph of the behaviours of the entire population

```bash
$ gnuplot ../plotting/plot_count_heatmap.gnuplot 
press a key to close

generating the graph
PDFCROP 1.38, 2012/11/02 - Copyright (c) 2002-2012 by Heiko Oberdiek.
==> 1 page written on 'plot_count_heatmap_1.pdf'.

```

It should:
* display the heatmap of the agents behaviours within the simulated population
* generate files for this graph into `plot_count_heatmap_1.eps` and `plot_count_heatmap_1.pdf`


## plot several graphs 

To generate graphs that represent the utilities of one given agent of the simulation, type in 
```bash
$ gnuplot ../plotting/plot_agent_heatmaps.gnuplot 
press a key to shift to the next graph...

writing the eps and pdf versions of the graph...
PDFCROP 1.38, 2012/11/02 - Copyright (c) 2002-2012 by Heiko Oberdiek.
==> 1 page written on 'plot_1_utility_aggregated.pdf'.
press a key to shift to the next graph...

writing the eps and pdf versions of the graph...
PDFCROP 1.38, 2012/11/02 - Copyright (c) 2002-2012 by Heiko Oberdiek.
==> 1 page written on 'plot_1_utility_points.pdf'.
press a key to shift to the next graph...

writing the eps and pdf versions of the graph...
PDFCROP 1.38, 2012/11/02 - Copyright (c) 2002-2012 by Heiko Oberdiek.
==> 1 page written on 'plot_1_utility_social_sanction.pdf'.
press a key to shift to the next graph...

writing the eps and pdf versions of the graph...
PDFCROP 1.38, 2012/11/02 - Copyright (c) 2002-2012 by Heiko Oberdiek.
==> 1 page written on 'plot_1_utility_hedonism.pdf'.

```

It will display each utility individually, waiting for you to press a key to pass to the next graph. 

It should also generate:
* one eps figure for each utility for the selected agent, in the form `plot_<agentid>_utility_<criteria>.eps`
* the pdf counterparts of these figures `plot_<agentid>_utility_<criteria>.pdf`

You can change the id of the agent for which to plot the utilities by changing the value of the variable `agentid` in the gnuplot script (first line)


## plot all the graphs in one unique graph

To generate the combined graph, type in 
```bash
$ gnuplot ../plotting/plot_agent_heatmaps_multi.gnuplot 
PDFCROP 1.38, 2012/11/02 - Copyright (c) 2002-2012 by Heiko Oberdiek.
==> 1 page written on 'plot_agent1_utilities.pdf'.
```
It should generate:
* an eps file into `plot_agent1_utilities.eps`
* a pdf counterpart into `plot_agent1_utilities.pdf`
and should open the pdf file in the default viewer configured in your system.

You can:
* hide some of the graphs by commenting them in the gnuplot script
* change the id of the agent for which to plot the utilities by changing the value of the variable `agentid` in the gnuplot script (first line)


