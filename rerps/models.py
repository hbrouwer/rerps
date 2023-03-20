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

import copy
import math
import time
import collections

import numpy as np
import pandas as pd

import scipy.stats as sps

"""regression-based ERP estimation.
    
Minimal implementation of regression-based ERP (rERP) waveform estimation,
as proposed in:

Smith, N.J., Kutas, M., Regression-based estimation of ERP waveforms: I. The
    rERP framework, Psychophysiology, 2015, Vol. 52, pp. 157-168

Smith, N.J., Kutas, M., Regression-based estimation of ERP waveforms: II.
    Non-linear effects, overlap correction, and practical considerations,
    Psychophysiology, 2015, Vol. 52, pp. 169-181

This module implements data structures, model fitting, and rERP estimation.

"""

class Set:
    """Wrapper for data and regression coefficient sets.

    Attributes:
        array (:obj:`ndarray`):
            array of data or coefficients
        descriptors (:obj:`OrderedDict`):
            mapping of descriptor column names (keys) to column
            indices (values).

    """
    def __init__(self):
        self.array = np.zeros((0,0))
        self.descriptors = collections.OrderedDict()

    def copy(self):
        """Returns a shallow copy of this set.

        Returns:
            (:obj:`Set`): shallow copy of this set.

        """
        c = copy.copy(self)
        c.array = self.array.copy()
        return(c)

    def default_sort(self):
        """Sort the array by all descriptors.

        Sorts thearray by all data descriptors, such that this set can be
        compared value-by-value to another set.
        
        """
        dv_splits(self, list(self.descriptors.keys()), sort=True)

    def rename_descriptor(self, name, newname):
        """Rename a given descriptor column.

        Args:
            name (:obj:`str`):
                name of descriptor to rename.
            newname (:obj:`str):
                new name of descriptor.

        """
        self.descriptors = collections.OrderedDict([
            (newname, v) if (k == name) else (k, v)
            for k,v in self.descriptors.items()])

    def rename_descriptor_level(self, descriptor, level, newlevel):
        """Rename a given level of a descriptor column.

        Args:
            descriptor (:obj:`str`):
                name of descriptor column.
            level (:obj:`str`):
                name of level to rename.
            newlevel (:obj:`str):
                new name of level.

        """
        idx = self.descriptors[descriptor]
        self.array[self.array[:,idx] == level, idx] = newlevel

class DataSet(Set):
    """Event-Related brain Potentials data set.

    Args:
        filename (:obj:`str`):
            name of a CSV file in wide format.
        descriptors (:obj:`list` of :obj:`str`): 
            names of columns identifying data descriptors.
        electrodes (:obj:`list` of :obj:`str`):
            names of columns identifying electrodes.
        predictors (:obj:`list` of :obj:`str`):
            names of columns identifying predictors.

    Attributes:
        array (:obj:`ndarray`):
            data array
        descriptors (:obj:`OrderedDict`):
            mapping of descriptor column names (keys) to column
            indices (values).
        electrodes (:obj:`OrderedDict`):
            mapping of electrode column names (keys) to column
            indices (values).
        predictors (:obj:`OrderedDict`):
            mapping of predictor column names (keys) to column
            indices (values).

    """
    def __init__(self, filename, descriptors, electrodes, predictors):
        st = time.time()

        print("[DataSet.__init__()]: Reading data ...")
        cols = descriptors + electrodes + predictors
        if (not(all(map(lambda x: isinstance(x, str), cols)))):
            print("[DataSet.__init__()]: please provide column names]")
            return
        df = pd.read_csv(filename, usecols=cols)
        self.descriptors = collections.OrderedDict([
            *map(lambda x: (x, list(df.columns).index(x)), descriptors)])
        self.electrodes = collections.OrderedDict([
            *map(lambda x: (x, list(df.columns).index(x)), electrodes)])
        self.predictors = collections.OrderedDict([
            *map(lambda x: (x, list(df.columns).index(x)), predictors)])
        self.array = df.to_numpy()

        et = time.time()
        print("[DataSet.__init__()]: Completed in",
                round(et - st, 2), "seconds.")

    def zscore_predictor(self, predictor):
        """Transform predictor values into z-scores.

        Args:
            predictor (:obj:`str`):
                name of predictor to transform.

        """
        idx = self.predictors[predictor]
        # self.array[:,idx] = sps.zscore(self.array[:,idx])
        self.array[:,idx] = sps.zscore(self.array[:,idx].astype(float))

    def invert_predictor(self, predictor, maximum=None):
        """Subtract every predictor values from the overall maximum.

        Args:
            predictor (:obj:`str`):
                name of predictor to transform.
            maximum (:obj:`float`, optional):
                user-specified maximum for the predictor.

        """
        idx = self.predictors[predictor]
        if (maximum == None):
            maximum = max(self.array[:,idx])
        self.array[:,idx] = maximum - self.array[:,idx]

    def rename_electrode(self, name, newname):
        """Rename a given electrode column.

        Args:
            name (:obj:`str`):
                name of electrode to rename.
            newname (:obj:`str):
                new name of electrode.

        """
        self.electrodes = collections.OrderedDict([
            (newname, v) if (k == name) else (k, v)
            for k,v in self.electrodes.items()])

    def rename_predictor(self, name, newname):
        """Rename a given predictor column.

        Args:
            name (:obj:`str`):
                name of predictor to rename.
            newname (:obj:`str):
                new name of predictor.

        """
        self.predictors = collections.OrderedDict([
            (newname, v) if (k == name) else (k, v)
            for k,v in self.predictors.items()])

    def save(self, filename):
        """Save dataset to file.

        Args:
            filename (:obj:`str`):
                name of the CSV file to write.

        """
        st = time.time()
        
        print("[DataSet.save()]: Saving data ...")
        cols = ["" for i in range(sum(map(len, 
            [self.descriptors.items(), self.electrodes.items(), self.predictors.items()])))]
        for c, i in self.descriptors.items(): cols[i] = c
        for c, i in self.electrodes.items():  cols[i] = c
        for c, i in self.predictors.items():  cols[i] = c
        df = pd.DataFrame(data=self.array, index=None, columns=cols)
        df.to_csv(filename, index=False)

        et = time.time()
        print("[DataSet.save()]: Completed in",
                round(et - st, 2), "seconds.")

class ModelSet(Set):
    """Linear regression coefficients set.

    Args:
        ds (:obj:`DataSet`):
            Event-Related brain Potentials data set.
        dv (:obj:`list` of :obj:`str`):
            names of descriptor columns that determine how the
            dependent variables are constructed
        ivs (:obj:`` of :obj:`str`):
            names of predictor columns representing the independent
            variables            

    Attributes:
        descriptors (:obj:`OrderedDict`):
            mapping of descriptor column names (keys) to column
            indices (values).
        predictors (:obj:`list` of :obj:`str`):
            list of the independent variables used to fit the models.
        electrodes (:obj:`list` of :obj:`str`):
            list of the electrodes for which models were fitted.
        coefficients (:obj:`OrderedDict`):
            mapping of (electrode, coefficient) tuples (keys) to column
            indices (values).
        standard_errors (:obj:`OrderedDict`):
            mapping of (electrode, coefficient) tuples (keys) to column
            indices (values).
        tvalues (:obj:`OrderedDict`):
            mapping of (electrode, coefficient) tuples (keys) to column
            indices (values).
        pvalues (:obj:`OrderedDict`):
            mapping of (electrode, coefficient) tuples (keys) to column
            indices (values).
        array (:obj:`ndarray`):
            coefficients array.

    """
    def __init__(self, ds, dv, ivs):
        self.predictors = ["(intercept)"] + ivs
        elec_coefs_betas = [("beta",e,c)
                for e in ds.electrodes
                for c in self.predictors]
        elec_coefs_serrs = [("se",e,c)
                for e in ds.electrodes
                for c in self.predictors]
        elec_coefs_tvals = [("tval",e,c)
                for e in ds.electrodes
                for c in self.predictors]
        elec_coefs_pvals = [("pval",e,c)
                for e in ds.electrodes
                for c in self.predictors]
        cols = dv + elec_coefs_betas + elec_coefs_serrs + elec_coefs_tvals + elec_coefs_pvals
        
        num_cbn = 1
        for v in dv:
            num_cbn *= len(np.unique(ds.array[:,ds.descriptors[v]]))
        self.array = np.zeros((num_cbn, len(cols)), dtype=object)
        
        self.electrodes = ds.electrodes.keys()
        self.coefficients = collections.OrderedDict([
            *map(lambda x: (x, cols.index(x)), elec_coefs_betas)]) 
        self.standard_errors = collections.OrderedDict([
            *map(lambda x: (x, cols.index(x)), elec_coefs_serrs)]) 
        self.tvalues = collections.OrderedDict([
            *map(lambda x: (x, cols.index(x)), elec_coefs_tvals)]) 
        self.pvalues = collections.OrderedDict([
            *map(lambda x: (x, cols.index(x)), elec_coefs_pvals)]) 
        self.descriptors = collections.OrderedDict([
            *map(lambda x: (x, cols.index(x)), dv)])

    def save(self, filename):
        """Save linear regression coeffcients to file.

        Args:
            filename (:obj:`str`):
                name of the CSV file to write.

        """
        st = time.time()

        print("[ModelSet.save()]: Saving coefficients ...")
        cols = ["" for i in range(sum(map(len, 
            [self.descriptors.items(),
             self.coefficients.items(),
             self.standard_errors.items(),
             self.tvalues.items(),
             self.pvalues.items()])))]
        for c, i in self.descriptors.items(): cols[i] = c
        for (t, e, c), i in self.coefficients.items():
            cols[i] = t + ":" + e + ":" + c
        for (t, e, c), i in self.standard_errors.items():
            cols[i] = t + ":" + e + ":" + c
        for (t, e, c), i in self.tvalues.items():
            cols[i] = t + ":" + e + ":" + c
        for (t, e, c), i in self.pvalues.items():
            cols[i] = t + ":" + e + ":" + c
        df = pd.DataFrame(data=self.array, index=None, columns=cols)
        df.to_csv(filename, index=False)

        et = time.time()
        print("[ModelSet.save()]: Completed in",
                round(et - st, 2), "seconds.")

###########################################################################
###########################################################################

class SetSummary:
    """Wrapper for a summary of a data or regression coefficients set.

    Attributes:
        means (:obj:`ndarray`):
            mean voltages for each electrode by descriptor columns
            (dv).
        serrs (:obj:`ndarray`):
            standard errors of the mean voltage for each electrode by
            descriptor columns (dv).
        descriptors (:obj:`OrderedDict`):
            mapping of descriptor column names (keys) to column
            indices (values).

    """
    def __init__(self):
        means = np.zeros((0,0))
        serrs = np.zeros((0,0))
        descriptors = collections.OrderedDict()

    def copy(self):
        """Returns a shallow copy of this summary.

        Returns:
            (:obj:`SummarySet`): shallow copy of this summary.

        """
        c = copy.copy(self)
        c.means = self.means.copy()
        c.serrs = self.serrs.copy()
        return(c)

class DataSummary(SetSummary):
    """Summary of an Event-Related brain potentials data set.

    Args:
        ds (:obj:`DataSet`):
            Event-Related brain Potentials data set.
        dv (:obj:`list` of :obj:`str`):
            names of descriptor columns that determine how the data
            is summarized.
        
    Attributes:
        means (:obj:`ndarray`):
            mean voltages for each electrode by descriptor columns
            (dv).
        serrs (:obj:`ndarray`):
            standard errors of the mean voltage for each electrode by
            descriptor columns (dv).
        descriptors (:obj:`OrderedDict`):
            mapping of descriptor column names (keys) to column
            indices (values).
        electrodes (:obj:`OrderedDict`):
            mapping of electrode column names (keys) to column
            indices (values).

    """
    def __init__(self, ds, dv):
        if isinstance(ds, DataSummary):
            ds = ds.copy()
            ds.array = ds.means

        indices = dv_splits(ds, dv, sort=True)

        st = time.time()
        print("[DataSummary.__init__()]: Summarizing data ...")
       
        num_agr = 1
        for v in dv:
            num_agr *= len(np.unique(ds.array[:,ds.descriptors[v]]))
        cols = dv + list(ds.electrodes.keys())

        self.means = np.zeros(shape=(num_agr, len(cols)), dtype=object)
        self.serrs = np.zeros(shape=(num_agr, len(cols)), dtype=object)
        
        elec_indices = list(ds.electrodes.values())
        for agr_idx, (l, u) in enumerate(zip(indices, indices[1:])):
            dv_vals  = list(map(lambda x: ds.array[l,ds.descriptors[x]], dv))
            self.means[agr_idx,:] = dv_vals + list(
                    ds.array[l:u,elec_indices].astype(float).mean(axis=0))
            # Assuming multiple data points for the descriptors, compute
            # their standard error.
            if (u - l > 1):
                self.serrs[agr_idx,:] = dv_vals + list(
                        ds.array[l:u,elec_indices].astype(float).std(axis=0, ddof=1)
                            / math.sqrt(u - l))
            # When averaging over a single data point, define the standard
            # error as zero.
            else:
                self.serrs[agr_idx,:] = dv_vals + list(
                        np.zeros(len(elec_indices)))

        self.descriptors = collections.OrderedDict([
            *map(lambda x: (x, cols.index(x)), dv)])
        self.electrodes  = collections.OrderedDict([
            *map(lambda x: (x, cols.index(x)), list(ds.electrodes.keys()))])
        
        et = time.time()
        print("[DataSummary.__init__()]: Completed in",
                round(et - st, 2), "seconds.")

    def save(self, filename):
        """Save data summary to file.

        Args:
            filename (:obj:`str`):
                name of the CSV file to write.

        """
        st = time.time()
        
        print("[DataSummary.save()]: Saving data ...")
        cols = ["" for i in range(sum(map(len, 
            [self.descriptors.items(), self.electrodes.items(), self.electrodes.items()])))]
        for c, i in self.descriptors.items(): cols[i] = c
        for c, i in self.electrodes.items():  cols[i] = c + ":mean"
        for c, i in self.electrodes.items():  cols[i + len(self.electrodes.items())] = c + ":se"
        array = np.hstack((
            self.means[:,:len(self.descriptors.items())],
            self.means[:,len(self.descriptors.items()):],
            self.serrs[:,len(self.descriptors.items()):]))
        df = pd.DataFrame(data=array, index=None, columns=cols)
        df.to_csv(filename, index=False)

        et = time.time()
        print("[DataSummary.save()]: Completed in",
                round(et - st, 2), "seconds.")

class ModelSummary(SetSummary):
    """Summary of a Linear regression coefficients set.

    Args:
        ms (:obj:`ModelSet`):
            set of fitted models
        dv (:obj:`list` of :obj:`str`):
            names of descriptor columns that determine how the data
            is summarized.
    
    Attributes:
        means (:obj:`ndarray`):
            mean coeffcients for each electrode by descriptor columns (dv).
        serrs (:obj:`ndarray`):
            standard errors of the mean coefficients for each electrode by
            descriptor columns (dv).
        tvals (:obj:`ndarray`):
            t-values for each coeffcients for each electrode by descriptor columns (dv).
        pvals (:obj:`ndarray`):
        
        descriptors (:obj:`OrderedDict`):
            mapping of descriptor column names (keys) to column
            indices (values).
        coefficients (:obj:`OrderedDict`):
            mapping of (electrode, coefficient) tuples (keys) to column
            indices (values).
        predictors (:obj:`list` of :obj:`str`):
            list of the independent variables used to fit the models.

    """
    def __init__(self, ms, dv):
        indices = dv_splits(ms, dv, sort=True)

        st = time.time()
        print("[ModelSummary.__init__()]: Summarizing models ...")

        num_agr = 1
        for v in dv:
            num_agr *= len(np.unique(ms.array[:,ms.descriptors[v]]))
        cols = dv + list(ms.coefficients.keys())

        self.means = np.zeros(shape=(num_agr, len(cols)), dtype=object)
        self.serrs = np.zeros(shape=(num_agr, len(cols)), dtype=object)
        self.tvals = np.zeros(shape=(num_agr, len(cols)), dtype=object)
        self.pvals = np.zeros(shape=(num_agr, len(cols)), dtype=object)

        coef_indices = list(ms.coefficients.values())
        serr_indices = list(ms.standard_errors.values())
        tval_indices = list(ms.tvalues.values())
        pval_indices = list(ms.pvalues.values())

        for agr_idx, (l, u) in enumerate(zip(indices, indices[1:])):
            dv_vals  = list(map(lambda x: ms.array[l,ms.descriptors[x]], dv))
            # Compute the mean coefficients.
            self.means[agr_idx,:] = dv_vals + list(
                    ms.array[l:u,coef_indices].astype(float).mean(axis=0))
            # If there are multiple sets of coefficients for the
            # descriptors, compute their standard error. In this case,
            # t-values will be set to zero and p-values to one.
            if (u - l > 1):
                self.serrs[agr_idx,:] = dv_vals + list(
                        ms.array[l:u,coef_indices].astype(float).std(axis=0, ddof=1)
                            / math.sqrt(u - l))
                self.tvals[agr_idx,:] = dv_vals + list(
                        np.zeros(self.tvals.shape[1] - len(dv_vals)))
                self.pvals[agr_idx,:] = dv_vals + list(
                        np.ones(self.pvals.shape[1] - len(dv_vals)))
            # If there is a single set of coefficients for the descriptors,
            # use the standard error from the least squares solution, and
            # add the t-value and p-value for each coefficient.
            else:
                self.serrs[agr_idx,:] = dv_vals + list(
                        ms.array[l:u,serr_indices].astype(float)[0])
                self.tvals[agr_idx,:] = dv_vals + list(
                        ms.array[l:u,tval_indices].astype(float)[0])
                self.pvals[agr_idx,:] = dv_vals + list(
                        ms.array[l:u,pval_indices].astype(float)[0])

        self.descriptors  = collections.OrderedDict([
            *map(lambda x: (x, cols.index(x)), dv)])
        self.coefficients = collections.OrderedDict([
            *map(lambda x: (x, cols.index(x)), list(ms.coefficients.keys()))])
        self.predictors   = ms.predictors
    
        et = time.time()
        print("[ModelSummary.__init__()]: Completed in",
                round(et - st, 2), "seconds.")

    def save(self, filename):
        """Save model summary to file.

        Args:
            filename (:obj:`str`):
                name of the CSV file to write.

        """
        st = time.time()
        
        print("[ModelSummary.save()]: Saving data ...")
        cols = ["" for i in range(sum(map(len, 
            [self.descriptors.items(), self.coefficients.items(), self.coefficients.items()])))]
        for c, i in self.descriptors.items(): cols[i] = c
        for (e, c), i in self.coefficients.items(): cols[i] = e + ":" + c + ":mean"
        for (e, c), i in self.coefficients.items(): cols[i + len(self.coefficients.items())] = e + ":" + c + ":se"
        array = np.hstack((
            self.means[:,:len(self.descriptors.items())],
            self.means[:,len(self.descriptors.items()):],
            self.sems[:,len(self.descriptors.items()):]))
        df = pd.DataFrame(data=array, index=None, columns=cols)
        df.to_csv(filename, index=False)

        et = time.time()
        print("[ModelSummary.save()]: Completed in",
                round(et - st, 2), "seconds.")

###########################################################################
###########################################################################

def dv_splits(s, dv, sort=True):
    """Sort Set and identify dependent variable splits.

    Args:
        s (:obj:`Set`):
            Event-Related brain Potentials data set, or
            Linear regression coefficients set.
        dv (:obj:`list` of :obj:`str`):
            names of descriptor columns that determine how the
            dependent variables are constructed
        sort (:obj:`bool`):
            Flags whether the data sets should be sorted by
            descriptors (dv).

    Returns:
        (:obj:`ndarray`): lower/upper bound indices of dependent
            variable splits.

    """
    st = time.time()

    # Sort data based on DV (in reversed order)
    if sort:
        print("[dv_splits()]: Sorting set ... (", hex(id(s)), ")")
        for v in reversed(dv):
            s.array = s.array[s.array[:,
                s.descriptors[v]].argsort(kind="stable")]

    # Blocks of identical values in the last (but first sorted DV)
    # split the data
    print("[dv_splits()]: Identifying splits ...")
    # First sorted DV could be categorical, if so we convert it into a
    # numeric variable. However, conversion is time consuming so we
    # skip it if unnecessary
    if isinstance(s.array[:,s.descriptors[dv[-1]]][0],str):
        split_dv_vals = list(np.unique(s.array[:,s.descriptors[dv[-1]]]))
        indices = np.diff([split_dv_vals.index(x)
            for x in s.array[:,s.descriptors[dv[-1]]]]).nonzero()[0]
    else:
        indices = np.diff(s.array[:,s.descriptors[dv[-1]]]).nonzero()[0]
    # Let indices mark the start of a new subet, rather than the end
    indices = indices + 1
    # Add index for the initial lower bound
    indices = np.hstack((np.array([0]), indices))
    # Add index for the final upper bound 
    indices = np.hstack((indices, np.array(s.array.shape[0])))

    et = time.time()
    print("[dv_splits()]: Completed in", round(et - st, 2), "seconds.")

    return(indices)

def regress(ds, dv, ivs, sort=True):
    """Fit linear regression models.

    Args:
        ds (:obj:`DataSet`):
            Event-Related brain Potentials data set.
        dv (:obj:`list` of :obj:`str`):
            names of descriptor columns that determine how the
            dependent variables are constructed
        ivs (:obj:`list` of :obj:`str`):
            names of columns that will serve as independent
            variables
        sort (:obj:`bool`):
            Flags whether the data sets should be sorted by
            descriptors (dv).

    Returns:
        (:obj:`ModelSet`): set of fitted models

    """
    indices = dv_splits(ds, dv, sort)

    ms = ModelSet(ds, dv, ivs)

    st = time.time()
    ivs_indices = list(map(lambda x: ds.predictors[x], ivs))
    num_models = len(indices[1:]) * len(ds.electrodes.values())
    print("[regress()]: Fitting", num_models, "models ...")
   
    for dv_idx, (l, u) in enumerate(zip(indices, indices[1:])):
        # predictors
        X = ds.array[l : u, ivs_indices]
        X = np.hstack((np.ones((u - l, 1)), X))
        X = X.astype(float)
        # target values
        y = ds.array[l : u, list(ds.electrodes.values())]
        y = y.astype(float)
        # coefficients
        coefs, resids, _, _ = np.linalg.lstsq(X, y, rcond=None)
        coefs = coefs.transpose().reshape((coefs.shape[0] * coefs.shape[1],))
        # standard errors 
        ssq = resids / (X.shape[0] - len(ms.predictors))
        dgl = np.diag(np.linalg.inv(np.matmul(np.transpose(X), X)))
        ses = np.sqrt(ssq * dgl.reshape(dgl.shape[0],1))
        ses = ses.transpose().reshape((ses.shape[0] * ses.shape[1],))
        # t-values
        tvals = coefs / ses
        # p-values (uncorrected)
        pvals = 2.0 * (1.0 - sps.t.cdf(abs(tvals), X.shape[0] - len(ms.predictors)))
        # store models
        dv_vals = list(map(lambda x: ds.array[l, ds.descriptors[x]], dv))
        ms.array[dv_idx,:] = dv_vals + list(coefs) + list(ses) + list(tvals) + list(pvals)

    et = time.time()
    print("[regress()]: Completed in", round(et - st, 2), "seconds.")

    return(ms)

def estimate(ds, ms, sort=True):
    """Estimate Event-related Potentials from fitted models.

    Args:
        ds (:obj:`DataSet`):
            Event-Related brain Potentials data set.
        ms (:obj:`ModelSet`):
            set of fitted models
        sort (:obj:`bool`):
            Flags whether the data sets should be sorted by
            descriptors (dv).

    Returns:
        (:obj:`DataSet`):
            Estimated Event-Related brain Potentials data set.

    """
    indices = dv_splits(ds, list(ms.descriptors.keys()), sort)
    dv_splits(ms, list(ms.descriptors.keys()), sort)
    
    eds = ds.copy()
    st = time.time()
    ivs_indices = list(map(lambda x: eds.predictors[x], ms.predictors[1:]))

    print("[estimate()]: Estimating data ...")
    # broadcast coefficients
    coef_array = np.zeros((eds.array.shape[0], len(ms.coefficients.keys())))
    for dv_idx, (l, u) in enumerate(zip(indices, indices[1:])):
        coef_array[l:u,:] = ms.array[dv_idx,len(ms.descriptors):len(ms.descriptors) + len(ms.coefficients.keys())]
    # compute estimates
    for elec in eds.electrodes.keys():
        coef_indices = list(map(lambda x: ms.coefficients[x] - len(ms.descriptors),
            map(lambda y: ("beta", elec, y), ms.predictors)))
        b0 = coef_array[:,coef_indices[0]]
        bs = coef_array[:,coef_indices[1:]] * eds.array[:,ivs_indices]
        eds.array[:,eds.electrodes[elec]] = b0 + np.sum(bs, axis=1)

    et = time.time()
    print("[estimate()]: Completed in", round(et - st, 2), "seconds.")

    return(eds)

def residuals(ods, eds, sort=True):
    """Compute residuals.

    Args:
        ods (:obj:`DataSet`):
            Observed Event-Related brain Potentials data set.
        eds (:obj:`DataSet`):
            Estimated Event-Related brain Potentials data set.
        sort (:obj:`bool`):
            Flags whether the data sets should be default sorted.

    Returns:
        (:obj:`DataSet`):
            Residual Event-Related brain Potentials data set.

    """
    if sort:
        ods.default_sort()
        eds.default_sort()
    rds = ods.copy()
    indices = list(rds.electrodes.values())
    rds.array[:,indices] = ods.array[:,indices] - eds.array[:,indices]
    return(rds)

def pvalue_correction(ms, ts_var, time_windows, electrodes):
    """
    p-value correction using the Benjamini-Hochberg procedure.

    Args:
        ms (:obj:`ModelSet`):
            set of fitted models.
        ts_var (:obj:`str`):
            timestamp descriptor.
        time_windows (:obj:`list` of :obj:`tuple` of :obj:`int`):
            time-window (start, end) tuples, where start is inclusive
            and end is non-inclusive.
        electrodes (:obj:`list` of :obj:`str`):
            electrodes of interest

    Returns:
        msc (:obj:`ModelSet`):
            set of fitted models
    """
    if (len(ms.descriptors) > 1 or list(ms.descriptors.keys())[0] != ts_var):
        return
    msc = ms.copy()
    msc.array[:,list(msc.pvalues.values())] = 1.0
    
    ts_index = ms.descriptors[ts_var]
    for p in ms.predictors:
        pval_indices = list(map(lambda e: ms.pvalues[("pval", e, p)], electrodes))
        for start, end in time_windows:
            l = list(msc.array[:,ts_index]).index(start)
            u = list(msc.array[:,ts_index]).index(end)
            pvals = ms.array[l:u,pval_indices]
            num_pvals = pvals.shape[0]
            num_elecs = pvals.shape[1]
            pvals = pvals.reshape(num_pvals * num_elecs)
            # adapted from p.adjust() in R:
            #
            # i <- lp:1L
            # o <- order(p, decreasing = TRUE)
            # ro <- order(o)
            # pmin(1, cummin(n/i * p[o]))[ro]
            n  = pvals.shape[0]
            i  = np.array(range(n, 0, -1))
            o  = (-pvals).argsort(axis=0)
            ro = o.argsort(axis=0)
            adj_pvals = np.minimum(1.0, np.minimum.accumulate((n / i) * pvals[o]))[ro]
            msc.array[l:u,pval_indices] = adj_pvals.reshape((num_pvals, num_elecs))

    return msc
