#!/usr/bin/python


def find_data(filename="log.lammps",
              l0="Step Time",
              l1="Loop time",
              verbose=False):
    """
    Extract data from a LAMMPs log file.

    Parameters
    ----------
    filename: str, optional
        Name of LAMMPs log fil.
        Default: log.lammps.
    l0: str, optional
        String which must be contained in the header
        of each chunk of data.
        Default: "Step Time", which comes from
        "thermo_style custom step time".
    l1: str, optional
        String contained in the first line after
        each chunk of data.
        Default: "Loop time".
    verbose: bool, optional
        If True, the header of each chunk will
        be printed. Default: False.

    Returns
    -------
    data: dict
        Dictionary where the keys are the headers
        in the log file, and the values are lists
        of data.
    """

    with open(filename, "r") as infile:
        lines = infile.readlines()
    N = len(lines)
    data = {}

    for i in range(N):
        line = lines[i]
        if l0 in line:
            if verbose:
                print(line)
            headers = line.split()
            for word in headers:
                if word not in data.keys():
                    data[word] = []
            i += 1
            while i < N and l1 not in lines[i]:
                word = lines[i].split()
                for j in range(len(word)):
                    data[headers[j]].append(float(word[j]))
                i += 1
    return data


def smooth(y, width):
    """
    A stupid moving-average smoothing function.

    Parameters
    ----------
    y: array_like
        Data to be smoothed.
    width: int
        Half the width of the moving average box.

    Returns
    -------
    ny: array
        The smoothed version of `y`.
    """
    from numpy import asarray, zeros, mean
    y = asarray(y)
    N = len(y)
    ny = zeros(N)
    for i in range(width, N - width):
        ny[i] = mean(y[i - width:i + width + 1])
    for i in range(width):
        ny[i] = mean(y[:width])
        ny[-i - 1] = mean(y[N - width:N])
    return ny


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser("Example: "
                            "logplotter.py -i log.lammps -x Time -y Press\n")

    parser.add_argument(
        "-x", "--x", default="Step", dest="x", metavar="XAXIS_QUANTITY")
    parser.add_argument(
        "-y", "--y", default="Temp", dest="y", metavar="YAXIS_QUANTITY")
    parser.add_argument(
        "-i", "--input", nargs="+", dest="f", metavar="INPUT_FILE(s)")
    parser.add_argument(
        "-l0",
        "--startdataline",
        default="Step Time",
        dest="l0",
        help="String contained in the header of each chunk of data.\
         Default: \"Step Time\",\
         which comes from \"thermo_style custom step time...\".")
    parser.add_argument(
        "-l1",
        "--enddataline",
        default="Loop time",
        dest="l1",
        help="String contained in the first line after each chunk of data.\
         Default: \"Loop time\".")
    parser.add_argument(
        "-s", "--save", default=None, dest="s", metavar="PLOT_FILENAME")
    parser.add_argument(
        "--smooth", default=0, type=int, metavar="SMOOTHING_PARAMETER")
    parser.add_argument("--dump", default=None, metavar="DATA_FILENAME")
    parser.add_argument(
        "--dumpnum",
        default=0,
        type=int,
        metavar="NUMBER_OF_VALUES",
        help="Set the number of values in the output data file,"
        " in order to reduce file size.")
    parser.add_argument("--noplot", action="store_true", help="No plotting.")

    args = parser.parse_args()
    if not args.noplot:
        import matplotlib.pyplot as plt

    x = []
    y = []

    if not type(args.f) == list:
        args.f = [args.f]

    for infile in args.f:
        data = find_data(infile, args.l0, args.l1, verbose=True)
        x += data[args.x]
        y += data[args.y]

    if not args.smooth == 0:
        y = smooth(y, args.smooth)

    finished_length = min(len(x), len(y))
    x = x[:finished_length]
    y = y[:finished_length]
    if not args.noplot:
        plt.plot(x, y)
        plt.xlabel(args.x)
        plt.ylabel(args.y)
        plt.grid()
        if args.s is not None:
            plt.savefig(args.s, bbox_inches="tight")
        plt.show()
    if args.dump is not None:
        import numpy as np
        args.dumpnum = finished_length if args.dumpnum == 0 else args.dumpnum
        res = np.array([x, y]).transpose()
        np.savetxt(args.dump, res[::finished_length // args.dumpnum])
