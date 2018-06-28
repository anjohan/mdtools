# mdtools

This is a (growing) collection of tools I use when working with LAMMPs.

## logplotter.py

This serves two purposes:
* A command line interface for quickly inspecting the results of a simulation (the simulation does not have to be finished!).
Basic usage: `logplotter.py -i log.part1 log.part2 -x Time -y Temp`. Use `logplotter.py -h` to see more options.
* A module containing the `find_data` function, which reads a log file and returns the contained data as a dictionary.
Basic usage: `data = find_data("log.lammps"); plt.plot(data["Step"], data["Temp"])`.
