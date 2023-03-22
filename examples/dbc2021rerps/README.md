# About

Example regression-based waveform estimation analysis of:

[Delogu, F., Brouwer, H., and Crocker, M. W. (2021). When components collide: Spatiotemporal overlap of the N400 and P600 in language comprehension. *Brain Research*. doi: 10.1016/j.brainres.2021.147514](https://www.sciencedirect.com/science/article/pii/S0006899321003711)

**Note: see
[hbrouwer/dbc2021rerps](https://github.com/hbrouwer/dbc2021rerps) for the
full rERP analysis reported in the paper.**

# Data

Download
[dbc2021data.tar.gz](https://github.com/hbrouwer/dbc2021rerps/releases/tag/v1.0)
and decompress the archive in the repository folder to place the CSV files
in `data/`.

# Usage

To build the rERP analysis:

```
$ make analysis
```

To undo everything:

```
$ make clean
```
