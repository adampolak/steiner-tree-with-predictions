# Steiner Tree approximation with predictions

This is the source code accompanying paper
**"Approximation algorithms for combinatorial optimization with predictions"**
by Antonios Antoniadis, Marek Eliáš, Adam Polak, and Moritz Venzin.

## Requirements

To run this code you will need:

- a Linux operating system (in principle, the code should also run on macOS, but the 3rd party solver that we use does not compile correctly with a macOS version of g++)
- a C++ compiler (we used g++ 8.5 but other versions should also be fine; we do not use any fancy features above the C++11 standard)
- Python 3.6+ (with pandas and matplotlib for drawing plots)

## Usage

First, run:

`./setup.sh`

It will clone a repository with the dataset, clone a repository with a Steiner Tree solver, and compile our implementation of the Mehlhorn algorithm.

To run our experiments on a single graph, do, e.g.,:

`python3 steiner.py SteinerTree-PACE-2018-instances/Track3/instance001.gr`

To run it on all instances, do:

`for i in SteinerTree-PACE-2018-instances/Track3/*.gr; do python3 steiner.py $i > results.csv; done`

Note that running it on all instances is going to take about 600 hours. We run it in parallel on a couple of multi-core machines -- how to do it will depend on your setup. A single execution of `steiner.py` runs on a single CPU core and should require no more than 500MB of RAM.

For your convenience, we provide the results of runnning the experiments on all instances in the `results.csv` file.

In order to generate the plots from the paper based on the data from the `results.csv` file, go to the plots folder and run:

``python3 createPlotsLearned.py
python3 createPlotsSynthetic.py``
