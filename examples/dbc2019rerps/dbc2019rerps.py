#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Example regression-based Waveform Estimation (rERP) analysis of:
#
# Delogu, F., Brouwer, H., and Crocker, M. W. (2019). Event-related
#   potentials index lexical retrieval (N400) and integration (P600) during
#   language comprehension. Brain and Cognition, 135. doi:
#   10.1016/j.bandc.2019.05.007
#
# as reported in:
#
# Brouwer, H., Delogu, F., and Crocker, M. W. (2021). Splitting
#   Event-Related Potentials: Modeling Latent Components using
#   Regression-based Waveform Estimation. European Journal of Neuroscience,
#   53, pp. 974-995. doi: 10.1111/ejn.14961

import rerps.models
import rerps.plots

import numpy as np
import pandas as pd

def generate():
    obs_data = rerps.models.DataSet(
        filename    = "data/dbc_data.csv",
        descriptors = ["Subject", "Timestamp", "Condition", "ItemNum"],
        electrodes  = ["Fz", "Cz", "Pz", "F3", "FC1", "FC5", "F4", "FC2", "FC6",
                       "P3", "CP1", "CP5", "P4", "CP2", "CP6", "O1", "Oz", "O2"],
        predictors  = ["Plaus", "Assoc"])
 
    obs_data.rename_descriptor_level("Condition", "control",          "baseline")
    obs_data.rename_descriptor_level("Condition", "script-related",   "event-related")
    obs_data.rename_descriptor_level("Condition", "script-unrelated", "event-unrelated")

    obs_data.rename_predictor("Plaus", "plausibility")
    obs_data.rename_predictor("Assoc", "association")

    # z-standardization
    obs_data.zscore_predictor("plausibility")
    obs_data.zscore_predictor("association")

    # inversion
    obs_data.array[:,obs_data.predictors["plausibility"]] *= -1
    obs_data.array[:,obs_data.predictors["association"]] *= -1
    
    #array = [["Pz+" ]]
    array = [["Fz" ],
             ["Cz" ],
             ["Pz+"]]

        ####################
        #### potentials ####
        ####################
    
    print("\n[ figures/dbc19_potentials.pdf ]\n")
    obs_data_summary = rerps.models.DataSummary(obs_data, ["Condition", "Subject", "Timestamp"])
    obs_data_summary = rerps.models.DataSummary(obs_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    fig, ax = rerps.plots.plot_voltages_grid(obs_data_summary, "Timestamp", array, #array,
            "Condition", title="Event-Related Potentials", colors=colors, hlt_tws=[(300,500), (800,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/dbc19_potentials.pdf", bbox_inches='tight')

    print("\n[ stats/dbc19_potentials_300-500.csv ]\n")
    time_window_averages(obs_data, 300, 500 ).to_csv("stats/dbc19_potentials_300-500.csv",  index=False)
    print("\n[ stats/dbc19_potentials_600-1000.csv ]\n")
    time_window_averages(obs_data, 600, 1000).to_csv("stats/dbc19_potentials_600-1000.csv", index=False)
    print("\n[ stats/dbc19_potentials_700-1000.csv ]\n")
    time_window_averages(obs_data, 700, 1000).to_csv("stats/dbc19_potentials_700-1000.csv", index=False)
    print("\n[ stats/dbc19_potentials_800-1000.csv ]\n")
    time_window_averages(obs_data, 800, 1000).to_csv("stats/dbc19_potentials_800-1000.csv", index=False)

        ########################
        #### intercept-only ####
        ########################

    print("\n[ figures/dbc19_intercept_est.pdf ]\n")
    models = rerps.models.regress(obs_data, ["Subject", "Timestamp"], [])
    est_data = rerps.models.estimate(obs_data, models)
    # isolate baseline, and rename
    est_data0 = est_data.copy()
    est_data0.array = est_data0.array[est_data0.array[:,est_data0.descriptors["Condition"]] == "baseline",:]
    est_data0.rename_descriptor_level("Condition", "baseline", "baseline / event-related / event-unrelated")
    est_data0_summary = rerps.models.DataSummary(est_data0, ["Condition", "Subject", "Timestamp"])
    est_data0_summary = rerps.models.DataSummary(est_data0_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    fig, ax = rerps.plots.plot_voltages_grid(est_data0_summary, "Timestamp", array, 
            "Condition", title="regression-based Event-Related Potentials", colors=colors, hlt_tws=[(300,500), (800,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/dbc19_intercept_est.pdf", bbox_inches='tight')

    print("\n[ figures/dbc19_intercept_res.pdf ]\n")
    res_data = rerps.models.residuals(obs_data, est_data)
    res_data_summary = rerps.models.DataSummary(res_data, ["Condition", "Subject", "Timestamp"])
    res_data_summary = rerps.models.DataSummary(res_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    fig, ax = rerps.plots.plot_voltages_grid(res_data_summary, "Timestamp", array,
            "Condition", title="Residuals", colors=colors, hlt_tws=[(300,500), (800,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/dbc19_intercept_res.pdf", bbox_inches='tight')
  
        ######################
        #### plausibility ####
        ######################

    print("\n[ figures/dbc19_plaus_est.pdf ]\n")
    models = rerps.models.regress(obs_data, ["Subject", "Timestamp"], ["plausibility"])
    est_data = rerps.models.estimate(obs_data, models)
    est_data_summary = rerps.models.DataSummary(est_data, ["Condition", "Subject", "Timestamp"])
    est_data_summary = rerps.models.DataSummary(est_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    fig, ax = rerps.plots.plot_voltages_grid(est_data_summary, "Timestamp", array,
            "Condition", title="regression-based Event-Related Potentials", colors=colors, hlt_tws=[(300,500), (800,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/dbc19_plaus_est.pdf", bbox_inches='tight')

    print("\n[ figures/dbc19_plaus_res.pdf ]\n")
    res_data = rerps.models.residuals(obs_data, est_data)
    res_data_summary = rerps.models.DataSummary(res_data, ["Condition", "Subject", "Timestamp"])
    res_data_summary = rerps.models.DataSummary(res_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    fig, ax = rerps.plots.plot_voltages_grid(res_data_summary, "Timestamp", array,
            "Condition", title="Residuals", colors=colors, hlt_tws=[(300,500), (800,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/dbc19_plaus_res.pdf", bbox_inches='tight')

        #####################
        #### association ####
        #####################

    print("\n[ figures/dbc19_assoc_est.pdf ]\n")
    models = rerps.models.regress(obs_data, ["Subject", "Timestamp"], ["association"])
    est_data = rerps.models.estimate(obs_data, models)
    est_data_summary = rerps.models.DataSummary(est_data, ["Condition", "Subject", "Timestamp"])
    est_data_summary = rerps.models.DataSummary(est_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    fig, ax = rerps.plots.plot_voltages_grid(est_data_summary, "Timestamp", array,
            "Condition", title="regression-based Event-Related Potentials", colors=colors, hlt_tws=[(300,500), (800,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/dbc19_assoc_est.pdf", bbox_inches='tight')

    print("\n[ figures/dbc19_assoc_res.pdf ]\n")
    res_data = rerps.models.residuals(obs_data, est_data)
    res_data_summary = rerps.models.DataSummary(res_data, ["Condition", "Subject", "Timestamp"])
    res_data_summary = rerps.models.DataSummary(res_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    fig, ax = rerps.plots.plot_voltages_grid(res_data_summary, "Timestamp", array,
            "Condition", title="Residuals", colors=colors, hlt_tws=[(300,500), (800,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/dbc19_assoc_res.pdf", bbox_inches='tight')

        ######################################################
        #### plausibility + association (within subjects) ####
        ######################################################

    print("\n[ figures/dbc19_plaus+assoc_est.pdf ]\n")
    models = rerps.models.regress(obs_data, ["Subject", "Timestamp"], ["plausibility", "association"])
    est_data = rerps.models.estimate(obs_data, models)
    est_data_summary = rerps.models.DataSummary(est_data, ["Condition", "Subject", "Timestamp"])
    est_data_summary = rerps.models.DataSummary(est_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    fig, ax = rerps.plots.plot_voltages_grid(est_data_summary, "Timestamp", array,
            "Condition", title="regression-based Event-Related Potentials", colors=colors, hlt_tws=[(300,500), (800,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/dbc19_plaus+assoc_est.pdf", bbox_inches='tight')

    print("\n[ stats/dbc19_plaus+assoc_300-500.csv ]\n")
    time_window_averages(est_data, 300, 500 ).to_csv("stats/dbc19_plaus+assoc_300-500.csv",  index=False)
    print("\n[ stats/dbc19_plaus+assoc_600-1000.csv ]\n")
    time_window_averages(est_data, 600, 1000).to_csv("stats/dbc19_plaus+assoc_600-1000.csv", index=False)
    print("\n[ stats/dbc19_plaus+assoc_700-1000.csv ]\n")
    time_window_averages(est_data, 700, 1000).to_csv("stats/dbc19_plaus+assoc_700-1000.csv", index=False)
    print("\n[ stats/dbc19_plaus+assoc_800-1000.csv ]\n")
    time_window_averages(est_data, 800, 1000).to_csv("stats/dbc19_plaus+assoc_800-1000.csv", index=False)
    
    print("\n[ figures/dbc19_plaus+assoc_res.pdf ]\n")
    res_data = rerps.models.residuals(obs_data, est_data)
    res_data_summary = rerps.models.DataSummary(res_data, ["Condition", "Subject", "Timestamp"])
    res_data_summary = rerps.models.DataSummary(res_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    fig, ax = rerps.plots.plot_voltages_grid(res_data_summary, "Timestamp", array,
            "Condition", title="Residuals", colors=colors, ymin=2, ymax=-2, hlt_tws=[(300,500), (800,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/dbc19_plaus+assoc_res.pdf", bbox_inches='tight')
    
    print("\n[ figures/dbc19_plaus+assoc_coef.pdf ]\n")
    models_summary = rerps.models.ModelSummary(models, ["Timestamp"])
    colors = ["#d62728", "#9467bd", "#8c564b"]
    fig, ax = rerps.plots.plot_coefficients_grid(models_summary, "Timestamp", array,
            anchor=True, title="Coefficients", colors=colors, hlt_tws=[(300,500), (800,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/dbc19_plaus+assoc_coef.pdf", bbox_inches='tight')

    print("\n[ figures/dbc19_plaus0+assoc_est.pdf ]\n")
    obs_data0 = obs_data.copy()
    obs_data0.array[:,obs_data0.predictors["plausibility"]] = 0
    est_data = rerps.models.estimate(obs_data0, models)
    est_data_summary = rerps.models.DataSummary(est_data, ["Condition", "Subject", "Timestamp"])
    est_data_summary = rerps.models.DataSummary(est_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    fig, ax = rerps.plots.plot_voltages_grid(est_data_summary, "Timestamp", array,
            "Condition", title="regression-based Event-Related Potentials", colors=colors, hlt_tws=[(300,500), (800,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/dbc19_plaus0+assoc_est.pdf", bbox_inches='tight')

    print("\n[ stats/dbc19_plaus0+assoc_300-500.csv ]\n")
    time_window_averages(est_data, 300, 500 ).to_csv("stats/dbc19_plaus0+assoc_300-500.csv",  index=False)
    print("\n[ stats/dbc19_plaus0+assoc_600-1000.csv ]\n")
    time_window_averages(est_data, 600, 1000).to_csv("stats/dbc19_plaus0+assoc_600-1000.csv", index=False)
    print("\n[ stats/dbc19_plaus0+assoc_700-1000.csv ]\n")
    time_window_averages(est_data, 700, 1000).to_csv("stats/dbc19_plaus0+assoc_700-1000.csv", index=False)
    print("\n[ stats/dbc19_plaus0+assoc_800-1000.csv ]\n")
    time_window_averages(est_data, 800, 1000).to_csv("stats/dbc19_plaus0+assoc_800-1000.csv", index=False)

    print("\n[ figures/dbc19_plaus+assoc0_est.pdf ]\n")
    obs_data0 = obs_data.copy()
    obs_data0.array[:,obs_data0.predictors["association"]] = 0
    est_data = rerps.models.estimate(obs_data0, models)
    est_data_summary = rerps.models.DataSummary(est_data, ["Condition", "Subject", "Timestamp"])
    est_data_summary = rerps.models.DataSummary(est_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    fig, ax = rerps.plots.plot_voltages_grid(est_data_summary, "Timestamp", array,
            "Condition", title="regression-based Event-Related Potentials", colors=colors, hlt_tws=[(300,500), (800,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/dbc19_plaus+assoc0_est.pdf", bbox_inches='tight')

    print("\n[ stats/dbc19_plaus+assoc0_300-500.csv ]\n")
    time_window_averages(est_data, 300, 500 ).to_csv("stats/dbc19_plaus+assoc0_300-500.csv",  index=False)
    print("\n[ stats/dbc19_plaus+assoc0_600-1000.csv ]\n")
    time_window_averages(est_data, 600, 1000).to_csv("stats/dbc19_plaus+assoc0_600-1000.csv", index=False)
    print("\n[ stats/dbc19_plaus+assoc0_700-1000.csv ]\n")
    time_window_averages(est_data, 700, 1000).to_csv("stats/dbc19_plaus+assoc0_700-1000.csv", index=False)
    print("\n[ stats/dbc19_plaus+assoc0_800-1000.csv ]\n")
    time_window_averages(est_data, 800, 1000).to_csv("stats/dbc19_plaus+assoc0_800-1000.csv", index=False)
        
        ######################################################
        #### plausibility + association (across subjects) ####
        ######################################################

    print("\n[ figures/dbc19_plaus+assoc_est_across.pdf ]\n")
    models = rerps.models.regress(obs_data, ["Timestamp"], ["plausibility", "association"])
    est_data = rerps.models.estimate(obs_data, models)
    est_data_summary = rerps.models.DataSummary(est_data, ["Condition", "Subject", "Timestamp"])
    est_data_summary = rerps.models.DataSummary(est_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    fig, ax = rerps.plots.plot_voltages_grid(est_data_summary, "Timestamp", array,
            "Condition", title="regression-based Event-Related Potentials", colors=colors, hlt_tws=[(300,500), (800,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/dbc19_plaus+assoc_est_across.pdf", bbox_inches='tight')

    print("\n[ figures/dbc19_plaus+assoc_res_across.pdf ]\n")
    res_data = rerps.models.residuals(obs_data, est_data)
    res_data_summary = rerps.models.DataSummary(res_data, ["Condition", "Subject", "Timestamp"])
    res_data_summary = rerps.models.DataSummary(res_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    fig, ax = rerps.plots.plot_voltages_grid(res_data_summary, "Timestamp", array,
            "Condition", title="Residuals", colors=colors, ymin=2, ymax=-2, hlt_tws=[(300,500), (800,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/dbc19_plaus+assoc_res_across.pdf", bbox_inches='tight')
    
    print("\n[ figures/dbc19_plaus+assoc_coef_across.pdf ]\n")
    models_summary = rerps.models.ModelSummary(models, ["Timestamp"])
    colors = ["#d62728", "#9467bd", "#8c564b"]
    fig, ax = rerps.plots.plot_coefficients_grid(models_summary, "Timestamp", array,
            anchor=True, title="Coefficients", colors=colors, hlt_tws=[(300,500), (800,1000)]) 
    fig.set_size_inches(30, 15)
    fig.savefig("figures/dbc19_plaus+assoc_coef_across.pdf", bbox_inches='tight')
    
    print("\n[ figures/dbc19_plaus+assoc_tval_across.pdf ]\n")
    # models = rerps.models.pvalue_correction(models, "Timestamp", [(300,500), (800,1000)], est_data.electrodes) # end-exclusive
    models = rerps.models.pvalue_correction(models, "Timestamp", [(300,502), (800,1002)], est_data.electrodes) # end-inclusive
    models_summary = rerps.models.ModelSummary(models, ["Timestamp"])
    colors = ["#9467bd", "#8c564b"]
    fig, ax = rerps.plots.plot_tvalues_grid(models_summary, "Timestamp", array, intercept=False,
            pvalues=True, alpha=0.05, title="t-values", colors=colors, hlt_tws=[(300,500), (800,1000)])
    fig.set_size_inches(30, 15)
    fig.savefig("figures/dbc19_plaus+assoc_tval_across.pdf", bbox_inches='tight')

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
