#!/usr/bin/env python


def find_data(filename="log.lammps", verbose=False):
    """
    Extract data from a LAMMPs log file.

    Parameters
    ----------
    filename: str, optional
        Name of LAMMPs log fil.
        Default: log.lammps.
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

    if verbose:
        print("Reading " + filename)

    for i in range(N):
        line = lines[i]
        if "Per MPI rank memory" in line:
            i = i + 1
            line = lines[i]
            if verbose:
                print(line)
            headers = line.split()
            for word in headers:
                if word not in data.keys():
                    data[word] = []
            i += 1
            while i < N and "Loop time" not in lines[i]:
                word = lines[i].split()
                if len(word) != len(headers):
                    return data
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
        ny[i] = mean(y[i - width : i + width + 1])
    for i in range(width):
        ny[i] = mean(y[:width])
        ny[-i - 1] = mean(y[N - width : N])
    return ny


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(
        "Example: " "logplotter.py -i log.lammps -x Time -y Press\n"
    )

    parser.add_argument("-x", "--x", default="Step", dest="x", metavar="XAXIS_QUANTITY")
    parser.add_argument(
        "-y", "--y", default="Temp", dest="y", metavar="YAXIS_QUANTITY", nargs="+"
    )
    parser.add_argument("--xlabel", metavar="XLABEL")
    parser.add_argument("--ylabel", metavar="YLABEL")
    parser.add_argument("-i", "--input", nargs="+", dest="f", metavar="INPUT_FILE(s)")
    parser.add_argument("-s", "--save", default=None, dest="s", metavar="PLOT_FILENAME")
    parser.add_argument("--smooth", default=0, type=int, metavar="SMOOTHING_PARAMETER")
    parser.add_argument("--dump", default=None, metavar="DATA_FILENAME")
    parser.add_argument(
        "--dumpnum",
        default=0,
        type=int,
        metavar="NUMBER_OF_VALUES",
        help="Set the number of values in the output data file,"
        " in order to reduce file size.",
    )
    parser.add_argument("--noplot", action="store_true", help="No plotting.")
    parser.add_argument("--noshow", action="store_true", help="Do not show plot.")

    args = parser.parse_args()
    if not args.noplot:
        import matplotlib.pyplot as plt

        plt.style.use("seaborn")

    x = []
    ys = [[] for i in args.y]

    if not type(args.f) == list:
        args.f = [args.f]

    for infile in args.f:
        data = find_data(infile, verbose=True)
        if data:
            x += data[args.x]
            for i, qty in enumerate(args.y):
                ys[i] += data[qty]

    if not args.smooth == 0:
        for i, y in enumerate(ys):
            ys[i] = smooth(y, args.smooth)

    finished_length = min(len(x), min([len(y) for y in ys]))
    x = x[:finished_length]
    for y in ys:
        y = y[:finished_length]

    if not args.noplot:
        fig, axs = plt.subplots(
            len(ys), 1, sharex=True, tight_layout=True, figsize=(6, 2 * len(ys))
        )
        if len(ys) == 1:
            axs = [axs]
        xlabel = args.xlabel if args.xlabel else args.x
        axs[-1].set_xlabel(xlabel)
        for ax, y, yname in zip(axs, ys, args.y):
            ax.plot(x, y)
            ylabel = args.ylabel if args.ylabel else yname
            ax.set_ylabel(ylabel)
            ax.grid()
        if args.s is not None:
            fig.savefig(args.s, bbox_inches="tight")
        if not args.noshow:
            plt.show()
    if args.dump is not None:
        import numpy as np

        args.dumpnum = finished_length if args.dumpnum == 0 else args.dumpnum
        res = np.column_stack((x, *ys))
        np.savetxt(args.dump, res[:: finished_length // args.dumpnum])
