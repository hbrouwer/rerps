# About

Example regression-based waveform estimation analysis of:

[Delogu, F., Brouwer, H., and Crocker, M. W. (2019). Event-related potentials index lexical retrieval (N400) and integration (P600) during language comprehension. *Brain and Cognition, 135*. doi: 10.1016/j.bandc.2019.05.007](https://www.sciencedirect.com/science/article/pii/S0278262618304299)

See [hbrouwer/dbc2019rerps](https://github.com/hbrouwer/dbc2019rerps)] for
the full rERP analysis reported in:

[Brouwer, H., Delogu, F., and Crocker, M. W. (2021). Splitting Event-Related Potentials: Modeling Latent Components using Regression-based Waveform Estimation. *European Journal of Neuroscience, 53*, pp. 974-995. doi: 10.1111/ejn.14961](https://onlinelibrary.wiley.com/doi/abs/10.1111/ejn.14961)

# Data

Download
[dbc2019data.tar.gz](https://github.com/hbrouwer/dbc2019rerps/releases/tag/v1.0),
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
