#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Example regression-based Waveform Estimation (rERP) analysis of:
#
# Aurnhammer, C., Delogu, F., Brouwer, H., and Crocker, M. W. (in press).
#   The P600 as a Continuous Index of Integration Effort. Psychophysiology.

import rerps.models
import rerps.plots

import numpy as np
import pandas as pd

def generate():
    obs_data = rerps.models.DataSet(
        filename    = "data/adbc23_erp.csv",
        descriptors = ["Subject", "Timestamp", "Condition", "Item"],
        electrodes  = ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", "FC5",
                       "FC1", "FC2", "FC6", "C3", "Cz", "C4", "CP5", "CP1",
                       "CP2", "CP6", "P7", "P3", "Pz", "P4", "P8", "O1",
                       "Oz", "O2"],
        predictors  = ["Plaus", "Cloze_distractor"])
 
    obs_data.rename_predictor("Plaus",            "plausibility")
    obs_data.rename_predictor("Cloze_distractor", "dist-cloze")

    # z-standardization
    obs_data.zscore_predictor("plausibility")
    obs_data.zscore_predictor("dist-cloze")

    # inversion
    obs_data.array[:,obs_data.predictors["plausibility"]] *= -1
    # obs_data.array[:,obs_data.predictors["dist-cloze"]] *= -1

    array = [["F3",  "Fz", "F4"],
             ["C3",  "Cz", "C4"],
             ["P3+", "Pz", "P4"]]

        ####################
        #### potentials ####
        ####################
    
    print("\n[ figures/psyp23_potentials.pdf ]\n")
    obs_data_summary = rerps.models.DataSummary(obs_data, ["Condition", "Subject", "Timestamp"])
    obs_data_summary = rerps.models.DataSummary(obs_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    fig, ax = rerps.plots.plot_voltages_grid(obs_data_summary, "Timestamp", array,
            "Condition", title="Event-Related Potentials", colors=colors, hlt_tws=[(300,500), (600,1000)])
    fig.set_size_inches(30, 20)
    fig.savefig("figures/psyp23_potentials.pdf", bbox_inches='tight')

        #####################################################
        #### plausibility + dist-cloze (across subjects) ####
        #####################################################

    print("\n[ figures/psyp23_plaus+dist-cloze_est_across.pdf ]\n")
    models = rerps.models.regress(obs_data, ["Timestamp"], ["plausibility", "dist-cloze"])
    est_data = rerps.models.estimate(obs_data, models)
    est_data_summary = rerps.models.DataSummary(est_data, ["Condition", "Subject", "Timestamp"])
    est_data_summary = rerps.models.DataSummary(est_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    fig, ax = rerps.plots.plot_voltages_grid(est_data_summary, "Timestamp", array,
            "Condition", title="regression-based Event-Related Potentials", colors=colors, hlt_tws=[(300,500), (600,1000)])
    fig.set_size_inches(30, 20)
    fig.savefig("figures/psyp23_plaus+dist-cloze_est_across.pdf", bbox_inches='tight')

    print("\n[ figures/psyp23_plaus+dist-cloze_res_across.pdf ]\n")
    res_data = rerps.models.residuals(obs_data, est_data)
    res_data_summary = rerps.models.DataSummary(res_data, ["Condition", "Subject", "Timestamp"])
    res_data_summary = rerps.models.DataSummary(res_data_summary, ["Condition", "Timestamp"])
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    fig, ax = rerps.plots.plot_voltages_grid(res_data_summary, "Timestamp", array,
            "Condition", title="Residuals", colors=colors, ymin=4, ymax=-4, hlt_tws=[(300,500), (600,1000)])
    fig.set_size_inches(30, 20)
    fig.savefig("figures/psyp23_plaus+dist-cloze_res_across.pdf", bbox_inches='tight')
    
    print("\n[ figures/psyp23_plaus+dist-cloze_coef_across.pdf ]\n")
    models_summary = rerps.models.ModelSummary(models, ["Timestamp"])
    colors = ["#d62728", "#9467bd", "#8c564b"]
    fig, ax = rerps.plots.plot_coefficients_grid(models_summary, "Timestamp", array,
            anchor=True, title="Coefficients", colors=colors, hlt_tws=[(300,500), (600,1000)])
    fig.set_size_inches(30, 20)
    fig.savefig("figures/psyp23_plaus+dist-cloze_coef_across.pdf", bbox_inches='tight')
    
    print("\n[ figures/psyp23_plaus+dist-cloze_tval_across.pdf ]\n")
    # models = rerps.models.pvalue_correction(models, "Timestamp", [(300,500), (600,1000)], est_data.electrodes) # end-exclusive
    models = rerps.models.pvalue_correction(models, "Timestamp", [(300,502), (600,1002)], est_data.electrodes) # end-inclusive
    models_summary = rerps.models.ModelSummary(models, ["Timestamp"])
    colors = ["#9467bd", "#8c564b"]
    fig, ax = rerps.plots.plot_tvalues_grid(models_summary, "Timestamp", array, intercept=False,
            pvalues=True, alpha=0.05, title="t-values", colors=colors, hlt_tws=[(300,500), (600,1000)])
    fig.set_size_inches(30, 20)
    fig.savefig("figures/psyp23_plaus+dist-cloze_tval_across.pdf", bbox_inches='tight')

###########################################################################
###########################################################################

if __name__ == "__main__":
    generate()
