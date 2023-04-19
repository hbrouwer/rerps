#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Example regression-based Waveform Estimation (rERP) analysis of:
#
# Aurnhammer, C., Delogu, F., Schulz, M., Brouwer, H., and Crocker, M. W.
#   (2021). Retrieval (N400) and Integration (P600) in Expectation-based
#   Comprehension. PLoS ONE 16(9): e0257430. doi: 10.1371/journal.pone.0257430

import rerps.models
import rerps.plots

import numpy as np
import pandas as pd

def generate():
    obs_data = rerps.models.DataSet(
        filename    = "data/CAPExp.csv",
        descriptors = ["Subject", "Timestamp", "Condition", "ItemNum"],
        # electrodes  = ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FC5",
                       # "FC1", "FC2", "FC6", "C3", "Cz", "C4", "CP5", "CP1",
                       # "CP2", "CP6", "P7", "P3", "Pz", "P4", "P8", "O1",
                       # "Oz", "O2"],
        electrodes  = ["Fz", "Cz", "Pz"],
        predictors  = ["Cloze", "rcnoun"])
 
    obs_data.rename_descriptor_level("Condition", "A", "A: A+E+")
    obs_data.rename_descriptor_level("Condition", "B", "B: A-E+")
    obs_data.rename_descriptor_level("Condition", "C", "C: A+E-")
    obs_data.rename_descriptor_level("Condition", "D", "D: A-E-")

    obs_data.rename_predictor("Cloze",  "cloze")
    obs_data.rename_predictor("rcnoun", "noun-association")

    # log(cloze + 0.01)
    # obs_data.array[:,obs_data.predictors["cloze"]] += 0.01
    # obs_data.array[:,obs_data.predictors["cloze"]] = np.log(obs_data.array[:,obs_data.predictors["cloze"]].astype(float))
    
    # z-standardization
    obs_data.zscore_predictor("cloze")
    obs_data.zscore_predictor("noun-association")

    # inversion
    obs_data.array[:,obs_data.predictors["cloze"]] *= -1
    obs_data.array[:,obs_data.predictors["noun-association"]] *= -1
  
    # array = [["F3",  "Fz", "F4"],
             # ["C3",  "Cz", "C4"],
             # ["P3+", "Pz", "P4"]]
    array = [["Fz" ],
             ["Cz" ],
             ["Pz+"]]

        ####################
        #### potentials ####
        ####################
    
    print("\n[ figures/capexp21_potentials.pdf ]\n")
    obs_data_summary = rerps.models.DataSummary(obs_data, ["Condition", "Subject", "Timestamp"])
    obs_data_summary = rerps.models.DataSummary(obs_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    fig, ax = rerps.plots.plot_voltages_grid(obs_data_summary, "Timestamp", array,
            "Condition", title="Event-Related Potentials", colors=colors, hlt_tws=[(300,500), (600,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/capexp21_potentials.pdf", bbox_inches='tight')

    print("\n[ stats/capexp21_potentials_300-500.csv ]\n")
    time_window_averages(obs_data, 300, 500 ).to_csv("stats/capexp21_potentials_300-500.csv",  index=False)
    print("\n[ stats/capexp21_potentials_600-1000.csv ]\n")
    time_window_averages(obs_data, 600, 1000).to_csv("stats/capexp21_potentials_600-1000.csv", index=False)
    print("\n[ stats/capexp21_potentials_700-1000.csv ]\n")
    time_window_averages(obs_data, 700, 1000).to_csv("stats/capexp21_potentials_700-1000.csv", index=False)
    print("\n[ stats/capexp21_potentials_800-1000.csv ]\n")
    time_window_averages(obs_data, 800, 1000).to_csv("stats/capexp21_potentials_800-1000.csv", index=False)

        ####################################################
        #### cloze + noun-association (across subjects) ####
        ####################################################

    print("\n[ figures/capexp21_cloze+noun-assoc_est_across.pdf ]\n")
    models = rerps.models.regress(obs_data, ["Timestamp"], ["cloze", "noun-association"])
    est_data = rerps.models.estimate(obs_data, models)
    est_data_summary = rerps.models.DataSummary(est_data, ["Condition", "Subject", "Timestamp"])
    est_data_summary = rerps.models.DataSummary(est_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    fig, ax = rerps.plots.plot_voltages_grid(est_data_summary, "Timestamp", array,
            "Condition", title="regression-based Event-Related Potentials", colors=colors, hlt_tws=[(300,500), (600,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/capexp21_cloze+noun-assoc_est_across.pdf", bbox_inches='tight')

    print("\n[ figures/capexp21_cloze+noun-assoc_res_across.pdf ]\n")
    res_data = rerps.models.residuals(obs_data, est_data)
    res_data_summary = rerps.models.DataSummary(res_data, ["Condition", "Subject", "Timestamp"])
    res_data_summary = rerps.models.DataSummary(res_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    fig, ax = rerps.plots.plot_voltages_grid(res_data_summary, "Timestamp", array,
            "Condition", title="Residuals", colors=colors, ymin=4, ymax=-4, hlt_tws=[(300,500), (600,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/capexp21_cloze+noun-assoc_res_across.pdf", bbox_inches='tight')
    
    print("\n[ figures/capexp21_plaus+noun-assoc_coef_across.pdf ]\n")
    models_summary = rerps.models.ModelSummary(models, ["Timestamp"])
    colors = ["#d62728", "#9467bd", "#8c564b"]
    fig, ax = rerps.plots.plot_coefficients_grid(models_summary, "Timestamp", array,
            anchor=True, title="Coefficients", colors=colors, hlt_tws=[(300,500), (600,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/capexp21_cloze+noun-assoc_coef_across.pdf", bbox_inches='tight')
    
    print("\n[ figures/capexp21_cloze+noun-assoc_tval_across.pdf ]\n")
    #models = rerps.models.pvalue_correction(models, "Timestamp", [(300,500), (600,1000)], est_data.electrodes) # end-exclusive
    models = rerps.models.pvalue_correction(models, "Timestamp", [(300,502), (600,1002)], est_data.electrodes) # end-inclusive
    models_summary = rerps.models.ModelSummary(models, ["Timestamp"])
    colors = ["#9467bd", "#8c564b"]
    fig, ax = rerps.plots.plot_tvalues_grid(models_summary, "Timestamp", array, intercept=False,
            pvalues=True, alpha=0.05, title="t-values", colors=colors, hlt_tws=[(300,500), (600,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/capexp21_clozes+noun-assoc_tval_across.pdf", bbox_inches='tight')

###########################################################################
###########################################################################

def time_window_averages(ds, start, end):
    ts_idx = ds.descriptors["Timestamp"]
    sds = ds.copy()
    sds.array = sds.array[(sds.array[:,ts_idx] >= start) & (sds.array[:,ts_idx] < end),:] # end-exclusive
    # sds.array = sds.array[(sds.array[:,ts_idx] >= start) & (sds.array[:,ts_idx] <= end),:] # end-inclusive
    sds_summary = rerps.models.DataSummary(sds, ["Condition", "Subject"])

    nrows = sds_summary.means.shape[0] * len(sds_summary.electrodes)
    sds_lf = np.empty((nrows, 4), dtype=object)

    sds_idx = 0
    for idx in range(0, sds_summary.means.shape[0]):
        c = sds_summary.means[idx, sds_summary.descriptors["Condition"]]
        s = sds_summary.means[idx, sds_summary.descriptors["Subject"]]
        for e, i in sds_summary.electrodes.items():
            sds_lf[sds_idx,:] = [c, s, e, sds_summary.means[idx,i]]
            sds_idx = sds_idx + 1

    return pd.DataFrame(sds_lf, columns=["cond", "subject", "ch", "eeg"])

###########################################################################
###########################################################################

if __name__ == "__main__":
    generate()
