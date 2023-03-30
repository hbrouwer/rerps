#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2020-2023 Harm Brouwer <me@hbrouwer.eu>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ---- Last modified: March 2023, Harm Brouwer ----

import rerps.models as models

import matplotlib.pyplot as plt
import numpy as np

"""regression-based ERP estimation.
    
Minimal implementation of regression-based ERP (rERP) waveform estimation,
as proposed in:

Smith, N.J., Kutas, M., Regression-based estimation of ERP waveforms: I. The
    rERP framework, Psychophysiology, 2015, Vol. 52, pp. 157-168

Smith, N.J., Kutas, M., Regression-based estimation of ERP waveforms: II.
    Non-linear effects, overlap correction, and practical considerations,
    Psychophysiology, 2015, Vol. 52, pp. 169-181

This module implements plotting of (r)ERP waveforms and model coefficients
in terms of betas, t-values, and p-values.

"""

def plot_voltages(dsm, x, y, groupby, title=None, legend=True, ax=None, colors=None, ymin=None, ymax=None, hlt_tws=[(300,500), (600,1000)]):
    """Plots voltages for a single electrode.

    Args:
        dsm (:obj:`DataSummary`):
            Summary of an Event-Related brain Potentials data set.
        x (:obj:`str`):
            name of the descriptor column that determines the x-axis
            (typically 'time').
        y (:obj:`str`):
            name of electrode to be plotted.
        groupby (:obj:`str`):
            name of the descriptor column that determines the grouping
            (typically 'condition').
        title (:obj:`str`):
            title of the graph.
        legend (:obj:`bool`):
            flags whether a legend should be added.
        ax (:obj:`Axes`):
            axes.Axes object to plot to.
        colors (:obj:`list` of :obj:`str`):
            list of colors to use for plotting.
        ymin (:obj:`float`):
            minimum of y axis.
        ymax (:obj:`float`):
            maximum of y axis.
        hlt_tws (:obj:`list` of :obj:`tuple` of :obj:`int`):
            time-window (start, end) tuples to highlight, where start is
            inclusive and end is non-inclusive.

    Returns:
        (:obj:`Figure`, optional): Figure.
        (:obj:`Axes`): axes.Axes object.

    """
    newfig = False
    if (ax == None):
        newfig = True
        fig, ax = plt.subplots()
        ax.invert_yaxis()

    if (colors):
        ax.set_prop_cycle(color=colors)

    groups = np.unique(dsm.means[:,dsm.descriptors[groupby]])
    for g in groups:
        # means
        x_vals = dsm.means[dsm.means[:,
            dsm.descriptors[groupby]] == g,
            dsm.descriptors[x]]
        x_vals = x_vals.astype(float)
        y_vals = dsm.means[dsm.means[:,
            dsm.descriptors[groupby]] == g,
            dsm.electrodes[y]]
        y_vals = y_vals.astype(float)
        ax.plot(x_vals, y_vals, label=g)
        # CIs
        y_serr = dsm.serrs[dsm.serrs[:,
            dsm.descriptors[groupby]] == g,
            dsm.electrodes[y]]
        y_serr = y_serr.astype(float)
        y_lvals = y_vals - 2 * y_serr
        y_uvals = y_vals + 2 * y_serr
        ax.fill_between(x_vals, y_lvals, y_uvals, alpha=.2)

    ax.grid()
    for (start, end) in hlt_tws:
        ax.axvspan(start, end,  color="grey", alpha=0.2)
    ax.axhline(y=0, color="black")
    ax.axvline(x=0, color="black")
    
    ax.tick_params(axis="both", which="major", labelsize=12)
    ax.tick_params(axis="both", which="minor", labelsize=12)
    
    if (ymin and ymax):
        ax.set_ylim(ymin, ymax)
    
    if (legend):
        ax.legend(loc = "lower left", fontsize=14)
    if (title):
        ax.set_title(title, fontsize=16)

    if (newfig):
        return fig, ax
    else:
        return ax

def plot_voltages_grid(dsm, x, ys, groupby, title=None, colors=None, ymin=None, ymax=None, hlt_tws=[(300,500), (600,1000)]):
    """Plots voltages for a grid of electrodes.

    Args:
        dsm (:obj:`DataSet`):
            Summary of an Event-Related brain Potentials data set.
        x (:obj:`str`):
            name of the descriptor column that determines the x-axis
            (typically 'time').
        ys (:obj:`list` of :obj`list` of :obj:`str`):
            electrode array to be plotted.
        groupby (:obj:`str`):
            name of the descriptor column that determines the grouping
            (typically 'condition').
        title (:obj:`str`):
            global title of the graph.
        colors (:obj:`list` of :obj:`str`):
            list of colors to use for plotting.
        ymin (:obj:`float`):
            minimum of y axis.
        ymax (:obj:`float`):
            maximum of y axis.
        hlt_tws (:obj:`list` of :obj:`tuple` of :obj:`int`):
            time-window (start, end) tuples to highlight, where start is
            inclusive and end is non-inclusive.

    Returns:
        (:obj:`Figure`): Figure.
        (:obj:`Axes`): axes.Axes object.

    """
    fig, axes = plt.subplots(len(ys)+1, len(ys[0])+2, sharey=True)

    for r in range(0, len(ys)+1):
        axes[r,0].set_visible(False)
        axes[r,len(ys[0])+1].set_visible(False)
        for c in range(0, len(ys[0])+2):
            axes[len(ys),c].set_visible(False)
    
    axes[0,0].invert_yaxis()
    
    for r, electrodes in enumerate(ys):
        for c, y in enumerate(electrodes):
            if (y == "##"):
                axes[r,c+1].set_visible(False)
            else:
                legend = False
                if (y[len(y)-1] == '+'):
                    legend = True;
                    y = y[0:len(y)-1]
                plot_voltages(dsm, x, y, groupby, title=y, legend=legend, ax=axes[r,c+1], colors=colors, ymin=ymin, ymax=ymax, hlt_tws=hlt_tws)

    if (title):
        fig.suptitle(title, fontsize=18, x=.5, y=.95)
   
    return fig, axes

def plot_coefficients(msm, x, y, anchor=True, title=None, legend=True, ax=None, colors=None, ymin=None, ymax=None, hlt_tws=[(300,500), (600,1000)]):
    """Plots coefficients for a single electrode.
    
    Args:
        msm (:obj:`DataSet`):
            Summary of a Linear regression coefficients set.
        x (:obj:`str`):
            name of the descriptor column that determines the x-axis
            (typically 'time').
        y (:obj:`str`):
            name of electrode to be plotted.
        anchor (:obj:`bool`):
            flags whether slopes should be anchored to the intercept.
        title (:obj:`str`):
            global title of the graph.
        legend (:obj:`bool`):
            flags whether a legend should be added.
        ax (:obj:`Axes`):
            axes.Axes object to plot to.
        colors (:obj:`list` of :obj:`str`):
            list of colors to use for plotting.
        ymin (:obj:`float`):
            minimum of y axis.
        ymax (:obj:`float`):
            maximum of y axis.
        hlt_tws (:obj:`list` of :obj:`tuple` of :obj:`int`):
            time-window (start, end) tuples to highlight, where start is
            inclusive and end is non-inclusive.

    Returns:
        (:obj:`Figure`, optional): Figure.
        (:obj:`Axes`): axes.Axes object.
    
    """
    newfig = False
    if (ax == None):
        newfig = True
        fig, ax = plt.subplots()
        ax.invert_yaxis()

    if (colors):
        ax.set_prop_cycle(color=colors)
    
    for i, p in enumerate(msm.predictors):
        # means
        x_vals = msm.means[:,msm.descriptors[x]]
        x_vals = x_vals.astype(float)
        y_vals = msm.means[:,msm.coefficients[("beta",y,p)]]
        y_vals = y_vals.astype(float)
        l = p
        if (anchor and i > 0):
            i_vals = msm.means[:,msm.coefficients[("beta",y,msm.predictors[0])]]
            i_vals = i_vals.astype(float)
            y_vals = y_vals + i_vals
            l = msm.predictors[0] + " + " + p
        ax.plot(x_vals, y_vals, label=l)
        # CIs
        y_serr = msm.serrs[:,msm.coefficients[("beta",y,p)]]
        y_serr = y_serr.astype(float)
        y_lvals = y_vals - 2 * y_serr
        y_uvals = y_vals + 2 * y_serr
        ax.fill_between(x_vals, y_lvals, y_uvals, alpha=.2)

    ax.grid()
    for (start, end) in hlt_tws:
        ax.axvspan(start, end,  color="grey", alpha=0.2)
    ax.axhline(y=0, color="black")
    ax.axvline(x=0, color="black")
    
    ax.tick_params(axis="both", which="major", labelsize=12)
    ax.tick_params(axis="both", which="minor", labelsize=12)
    
    if (ymin and ymax):
        ax.set_ylim(ymin, ymax)
    
    if (legend):
        ax.legend(loc = "lower left", fontsize=14)
    if (title):
        ax.set_title(title, fontsize=16)

    if (newfig):
        return fig, ax
    else:
        return ax

def plot_coefficients_grid(msm, x, ys, anchor=True, title=None, colors=None, ymin=None, ymax=None, hlt_tws=[(300,500), (600,1000)]):
    """Plots coefficients for a grid of electrodes.

    Args:
        msm (:obj:`DataSet`):
            Summary of a Linear regression coefficients set.
        x (:obj:`str`):
            name of the descriptor column that determines the x-axis
            (typically 'time').
        ys (:obj:`list` of :obj`list` of :obj:`str`):
            electrode array to be plotted.
        anchor (:obj:`bool`):
            flags whether slopes should be anchored to the intercept.
        title (:obj:`str`):
            global title of the graph.
        colors (:obj:`list` of :obj:`str`):
            list of colors to use for plotting.
        ymin (:obj:`float`):
            minimum of y axis.
        ymax (:obj:`float`):
            maximum of y axis.
        hlt_tws (:obj:`list` of :obj:`tuple` of :obj:`int`):
            time-window (start, end) tuples to highlight, where start is
            inclusive and end is non-inclusive.

    Returns:
        (:obj:`Figure`): Figure.
        (:obj:`Axes`): axes.Axes object.

    """
    fig, axes = plt.subplots(len(ys)+1, len(ys[0])+2, sharey=True)

    for r in range(0, len(ys)+1):
        axes[r,0].set_visible(False)
        axes[r,len(ys[0])+1].set_visible(False)
        for c in range(0, len(ys[0])+2):
            axes[len(ys),c].set_visible(False)
    
    axes[0,0].invert_yaxis()
    
    for r, electrodes in enumerate(ys):
        for c, y in enumerate(electrodes):
            if (y == "##"):
                axes[r,c+1].set_visible(False)
            else:
                legend = False
                if (y[len(y)-1] == '+'):
                    legend = True;
                    y = y[0:len(y)-1]
                plot_coefficients(msm, x, y, anchor=anchor, title=y, legend=legend, ax=axes[r,c+1], colors=colors, ymin=ymin, ymax=ymax, hlt_tws=hlt_tws)

    if (title):
        fig.suptitle(title, fontsize=18, x=.5, y=.95)
   
    return fig, axes

def plot_tvalues(msm, x, y, intercept=False, pvalues=True, alpha=0.05, title=None, legend=True, ax=None, colors=None, ymin=None, ymax=None, hlt_tws=[(300,500), (600,1000)]):
    """Plots t-values for a single electrode.
    
    Args:
        msm (:obj:`DataSet`):
            Summary of a Linear regression coefficients set.
        x (:obj:`str`):
            name of the descriptor column that determines the x-axis
            (typically 'time').
        y (:obj:`str`):
            name of electrode to be plotted.
        intercept (:obj:`bool`):
            flags whether t-values for intercept should be plotted.
        pvalues (:obj:`bool`):
            flags whether p-values should be plotted.
        alpha (:obj:`float`):
            significance level.
        title (:obj:`str`):
            global title of the graph.
        legend (:obj:`bool`):
            flags whether a legend should be added.
        ax (:obj:`Axes`):
            axes.Axes object to plot to.
        colors (:obj:`list` of :obj:`str`):
            list of colors to use for plotting.
        ymin (:obj:`float`):
            minimum of y axis.
        ymax (:obj:`float`):
            maximum of y axis.
        hlt_tws (:obj:`list` of :obj:`tuple` of :obj:`int`):
            time-window (start, end) tuples to highlight, where start is
            inclusive and end is non-inclusive.

    Returns:
        (:obj:`Figure`, optional): Figure.
        (:obj:`Axes`): axes.Axes object.
    
    """
    newfig = False
    if (ax == None):
        newfig = True
        fig, ax = plt.subplots()
        ax.invert_yaxis()
    
    if (colors):
        ax.set_prop_cycle(color=colors)
   
    fp = 1
    if (intercept):
        fp = 0
    for i, p in enumerate(msm.predictors[fp:]):
        # t-values
        x_vals = msm.tvals[:,msm.descriptors[x]]
        x_vals = x_vals.astype(float)
        y_vals = msm.tvals[:,msm.coefficients[("beta",y,p)]]
        y_vals = y_vals.astype(float)
        ax.plot(x_vals, y_vals, label=p)
        # p-values
        if (not(pvalues)):
            continue
        for j, x_val in enumerate(x_vals):
            pval = msm.pvals[j,msm.coefficients[("beta",y,p)]]
            if (pval < alpha):
                pval_off = 0.5
                pval_pos = np.max(y_vals) + pval_off
                if (np.abs(np.min(y_vals)) > pval_pos):
                    pval_pos = np.min(y_vals) - pval_off
                ax.plot(x_val, pval_pos, marker='|', color=colors[i], alpha=.5, markersize=5)

    ax.grid()
    for (start, end) in hlt_tws:
        ax.axvspan(start, end,  color="grey", alpha=0.2)
    ax.axhline(y=0, color="black")
    ax.axvline(x=0, color="black")
    
    ax.tick_params(axis="both", which="major", labelsize=12)
    ax.tick_params(axis="both", which="minor", labelsize=12)
    
    if (ymin and ymax):
        ax.set_ylim(ymin, ymax)

    if (legend):
        ax.legend(loc = "lower left", fontsize=14)
    if (title):
        ax.set_title(title, fontsize=16)

    if (newfig):
        return fig, ax
    else:
        return ax

def plot_tvalues_grid(msm, x, ys, intercept=False, pvalues=True, alpha=0.05, title=None, colors=None, ymin=None, ymax=None, hlt_tws=[(300,500), (600,1000)]):
    """Plots t-values for a grid of electrodes.

    Args:
        msm (:obj:`DataSet`):
            Summary of a Linear regression coefficients set.
        x (:obj:`str`):
            name of the descriptor column that determines the x-axis
            (typically 'time').
        ys (:obj:`list` of :obj`list` of :obj:`str`):
            electrode array to be plotted.
        intercept (:obj:`bool`):
            flags whether t-values for intercept should be plotted.
        pvalues (:obj:`bool`):
            flags whether p-values should be plotted.
        alpha (:obj:`float`):
            significance level.
        title (:obj:`str`):
            global title of the graph.
        colors (:obj:`list` of :obj:`str`):
            list of colors to use for plotting.
        ymin (:obj:`float`):
            minimum of y axis.
        ymax (:obj:`float`):
            maximum of y axis.
        hlt_tws (:obj:`list` of :obj:`tuple` of :obj:`int`):
            time-window (start, end) tuples to highlight, where start is
            inclusive and end is non-inclusive.

    Returns:
        (:obj:`Figure`): Figure.
        (:obj:`Axes`): axes.Axes object.

    """
    fig, axes = plt.subplots(len(ys)+1, len(ys[0])+2, sharey=True)


    for r in range(0, len(ys)+1):
        axes[r,0].set_visible(False)
        axes[r,len(ys[0])+1].set_visible(False)
        for c in range(0, len(ys[0])+2):
            axes[len(ys),c].set_visible(False)
    
    axes[0,0].invert_yaxis()
    
    for r, electrodes in enumerate(ys):
        for c, y in enumerate(electrodes):
            if (y == "##"):
                axes[r,c+1].set_visible(False)
            else:
                legend = False
                if (y[len(y)-1] == '+'):
                    legend = True;
                    y = y[0:len(y)-1]
                plot_tvalues(msm, x, y, intercept=intercept, pvalues=pvalues, alpha=alpha, title=y, legend=legend, ax=axes[r,c+1], colors=colors, ymin=ymin, ymax=ymax, hlt_tws=hlt_tws)

    if (title):
        fig.suptitle(title, fontsize=18, x=.5, y=.95)
   
    return fig, axes
