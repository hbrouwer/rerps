# About

Example regression-based waveform estimation analysis of:

[Aurnhammer, C., Delogu, F., Schulz, M., Brouwer, H., and Crocker, M. W. (2021). Retrieval (N400) and Integration (P600) in Expectation-based Comprehension. PLoS ONE 16(9): e0257430. doi: 10.1371/journal.pone.0257430](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0257430)

**Note: see
[caurnhammer/plosone21lmererp](https://github.com/caurnhammer/plosone21lmererp)
for the full rERP analysis reported in the paper.**

# Data

Download [PLOSONE21lmerERP_ObservedData.zip](https://osf.io/cqv9y),
decompress the archive, and place the CSV files in `data/`.

# Usage

To build the rERP analysis:

```
$ make analysis
```

To undo everything:

```
$ make clean
```
