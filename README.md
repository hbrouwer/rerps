# About

Development repository of `rerps`, a Python implementation of
regression-based Event-Related Potential (ERP) waveform estimation (rERP):

[Smith, N. J., & Kutas, M. (2015). Regression‐based estimation of ERP waveforms: I. The rERP framework. *Psychophysiology, 52*(2), pp. 157-168. doi: 10.1111/psyp.12317](https://onlinelibrary.wiley.com/doi/10.1111/psyp.12317)
    
[Smith, N. J., & Kutas, M. (2015). Regression‐based estimation of ERP waveforms: II. Nonlinear effects, overlap correction, and practical considerations. *Psychophysiology, 52*(2), pp. 169-181. doi: 10.1111/psyp.12320](https://onlinelibrary.wiley.com/doi/10.1111/psyp.12320)

See also:

[Brouwer, H., Delogu, F., and Crocker, M. W. (2021). Splitting Event-Related Potentials: Modeling Latent Components using Regression-based Waveform Estimation. *European Journal of Neuroscience, 53*, pp. 974-995. doi: 10.1111/ejn.14961](https://onlinelibrary.wiley.com/doi/abs/10.1111/ejn.14961)

# Getting started

Clone this repository, download the relevant data files (see `examples/`)
and decompress them in the relevant `data/` folder.

# Requirements

To run the analyses in `examples/`, you need:

* A recent version of Python 3, with recent versions of:
  * NumPy
  * pandas
  * SciPy
  * Matplotlib
* GNU Make (optional)

# Full rERP analyses

This repository contains the current implementation of `rerps`, and the rERP
analyses in `examples` serve as illustrations of functionality. Examples of
full rERP analyses using earlier, frozen, versions of `rerps` can be found
here:

[hbrouwer/dbc2019rerps](https://github.com/hbrouwer/dbc2019rerps) implements
the rERP analysis of:

[Delogu, F., Brouwer, H., and Crocker, M. W. (2019). Event-related potentials index lexical retrieval (N400) and integration (P600) during language comprehension. *Brain and Cognition, 135*. doi: 10.1016/j.bandc.2019.05.007](https://www.sciencedirect.com/science/article/pii/S0278262618304299)

as described in:

[Brouwer, H., Delogu, F., and Crocker, M. W. (2021). Splitting Event-Related Potentials: Modeling Latent Components using Regression-based Waveform Estimation. *European Journal of Neuroscience, 53*, pp. 974-995. doi: 10.1111/ejn.14961](https://onlinelibrary.wiley.com/doi/abs/10.1111/ejn.14961)

[hbrouwer/dbc2021rerps](https://github.com/hbrouwer/dbc2021rerps) implements
the rERP analysis in:

[Delogu, F., Brouwer, H., and Crocker, M. W. (2021). When components collide: Spatiotemporal overlap of the N400 and P600 in language comprehension. *Brain Research*. doi: 10.1016/j.brainres.2021.147514](https://www.sciencedirect.com/science/article/pii/S0006899321003711)
