#!/usr/bin/env python
# encoding: utf-8

"""
functions_oc.py

If used, please cite: 
Colizoli, O., de Gee, J. W., Urai, A. E. & Donner, T. H.
Task-evoked pupil responses reflect internal belief states. Scientific Reports 8, 13702 (2018).

"""
from __future__ import division

import os, sys, datetime, pickle
import subprocess, logging, time

import numpy as np
import numpy
import numpy.random as random
import pandas as pd
import scipy as sp
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
import mne
import statsmodels.formula.api as sm
import statsmodels.api as sm2

from IPython import embed as shell


def extract_for_apa(k, aov, values = ['F', 'mse', 'eta', 'p']):
    # Gets statistics out of the AOV 
    # Note factors = aov.keys() returns a list of factors in current model
    results = {}
    for key,result in aov[k].iteritems():
        # print(key)
        # print(result)
        if key in values:
            results[key] = result
    return results

def get_colors(factor='boosted'):
    # Color scheme for all conditions of interest
    
    labels = []
    colors = []
    alphas = []
    f = factor
    # following pandas data frame 0 will always be "not" of title
    # e.g. boosted 0 = tone, boosted 1 = white noise

    if f == 'pupil_high':
        labels = ['low','high']
        colors = ['blue','red']
        alphas = [1, 1] 
    # elif f == 'yes':
    elif f == 'response':
        labels = ['choice: down','up']
        colors = ['green','orange']
        alphas = [1, 1] 
    elif f == 'correct':
        labels = ['error','correct']
        colors = ['red','green']
        alphas = [1, 1] 
    # elif f == 'present':
    elif f == 'stimulus':
        labels = ['signal: down','up']      
        colors = ['green','orange']   
        alphas = [1, 1] 
    elif f == 'boosted':
        labels = ['tone','wn']      
        colors = ['purple','red']
        alphas = [1, 1] 
    elif f == 'easy':
        labels = ['Hard','Easy']      
        colors = ['purple','green']   
        alphas = [1, 1]
    elif f == 'hemiL':
        labels = ['right','left']      
        colors = ['blue','green']   
        alphas = [1, 1]
    elif f == 'all':
        labels = ['all']
        colors = ['black']
        alphas = [1]
    elif f == 'interact':
        labels = ['Cue','Feedback']
        colors = ['blue','purple']
        alphas = [1,1]
    elif f == 'tesla':
        labels = ['3T','7T']
        colors = ['green','green']
        alphas = [.5,1]
    elif f == 'roi_high':
        labels = ['low','high']  
        colors = ['orange','blue']
        alphas = [1, 1]
    # interactions
    elif f == 'easy*correct':
        labels = ['Hard Error', 'Hard Correct', 'Easy Error', 'Easy Correct']
        colors = ['red','green','red','green']
        alphas = [1, 1, .3, .3]
    elif f == 'easy*boosted':
        labels = ['hard + tone', 'hard + wn', 'easy + tone', 'easy + wn']
        colors = ['purple', 'red','purple', 'red']
        alphas = [1, 1, .3, .3]
    elif f == 'boosted*correct':
        labels = ['tone + error' ,'tone + correct', 'wn + error', 'wn + correct']
        colors = ['red', 'green','red', 'green']
        alphas = [.3, .3, 1, 1]
    elif f == 'roi_high*easy':
        labels = ['low + hard' ,'low + easy', 'high + hard', 'high + easy']
        colors = ['orange', 'blue','orange', 'blue']
        alphas = [.3, .3, 1, 1]
    return labels, colors, alphas


def line_plot_anova(MEANS, SEMS, dv, aov, cond, ylabel, fac):
    # Plots the interaction effects for the 2x2 conditions as line plots
    # Adds statistics from the AOV as xlabel

    # whole figure
    fig = plt.figure(figsize=(2,2))
    ax = fig.add_subplot(111)
    # ax.axhline(0, lw=0.25, alpha=1, color = 'k') # Add horizontal line at t=0
    
    ### LINE GRAPH ###
    ind = [0.3,0.5]
    xlim = [0.275,0.575]
    # get xlabels and color scheme for two conditions
    ls = fac[1] # corresponding to lines
    scheme = get_colors(factor=ls)
    leg_label = scheme[0]
    colors = scheme[1]
    alphas = scheme[2]
    s2 = get_colors(factor=fac[0]) # corresponding to xticks
    xticklabels = s2[0]

    # Plot by looping through 'keys' in grouped dataframe
    x=0 # count 'groups'
    for key,grp in MEANS.groupby(ls):
        # print(key)
        print(grp)
        ax.errorbar(ind,grp[dv],yerr=[SEMS[0][x],SEMS[1][x]], label=leg_label[x], color=colors[x], alpha=alphas[x])
        x=x+1
        
    if aov.shape[0] > 0:
        p = aov['p'] # only term
        f = aov['F']
        p = np.round(p,3)
        f = np.round(f,2)
        xlabel = '{}: F={}, p={}\n{}: F={}, p={}\n{}: F={}, p={}'.format(fac[0],f[0],p[0],fac[1],f[1],p[1],cond,f[2],p[2])

    # Figure parameters
        ax.set_xlabel(xlabel, fontsize=4, fontstyle='italic') # TURNED OFF FOR FINAL FIGURES
    ax.set_xticks(ind)
    # ax.set_xlim(xlim)
    ax.set_xticklabels(xticklabels)    
    ax.legend(loc='best', fontsize=4)
    ax.set_ylabel(ylabel)       
    
    return(fig , ax)


def exact_mc_perm_test(xs, ys, nmc=10000):
    # Permutation test using Monte-Carlo method (JW's functions)
    n, k = len(xs), 0
    diff = np.abs(np.mean(xs) - np.mean(ys))
    zs = np.concatenate([xs, ys])
    for j in range(nmc):
        np.random.shuffle(zs) # shuffle the original order of data
        # take the difference of the two samples which have been shuffled, is it greater than original difference?
        k += diff < np.abs(np.mean(zs[:n]) - np.mean(zs[n:])) 
    return k / nmc

        
def perm_2sample(group1, group2, nrand=10000, tail=0, paired=True):
    # Take from JW's functions
    """
    non-parametric permutation test (Efron & Tibshirani, 1998)
    tail = 0 (test A~=B), 1 (test A>B), -1 (test A<B)
    """

    a = group1
    b = group2
    ntra = len(a)
    ntrb = len(b) 
    meana = np.mean(a)
    meanb = np.mean(b)
    triala = np.zeros(nrand)
    trialb = np.zeros(nrand)
    
    if paired:
        for i in range(nrand):
            alldat = np.vstack((a,b)).T
            for j in range(ntra):
                alldat[j,:] = alldat[j,np.argsort(np.random.rand(2))]
            triala[i] = alldat[:,0].mean()
            trialb[i] = alldat[:,1].mean()
            
    else:
        alldat = np.concatenate((a,b))
        indices = np.arange(alldat.shape[0])
        for i in range(nrand):
            random.shuffle(indices)
            triala[i] = np.mean(alldat[indices[:ntra]])
            trialb[i] = np.mean(alldat[indices[ntra:]])
            
    if tail == 0:
        p_value = sum(abs(triala-trialb)>=abs(meana-meanb)) / float(nrand)
    else:
        p_value = sum((tail*(triala-trialb))>=(tail*(meana-meanb))) / float(nrand)

    return(meana-meanb, p_value)
    

def cluster_sig_bar_1samp(array, x, yloc, color, ax, threshold=0.05, nrand=5000, cluster_correct=True):
        
    if yloc == 1:
        yloc = 10
    if yloc == 2:
        yloc = 20
    if yloc == 3:
        yloc = 30
    if yloc == 4:
        yloc = 40
    if yloc == 5:
        yloc = 50
    
    if cluster_correct:
        whatever, clusters, pvals, bla = mne.stats.permutation_cluster_1samp_test(array, n_permutations=nrand, n_jobs=10)
        for j, cl in enumerate(clusters):
            if len(cl) == 0:
                pass
            else:
                if pvals[j] < threshold:
                    for c in cl:
                        sig_bool_indices = np.arange(len(x))[c]
                        xx = np.array(x[sig_bool_indices])
                        try:
                            xx[0] = xx[0] - (np.diff(x)[0] / 2.0)
                            xx[1] = xx[1] + (np.diff(x)[0] / 2.0)
                        except:
                            xx = np.array([xx - (np.diff(x)[0] / 2.0), xx + (np.diff(x)[0] / 2.0),]).ravel()
                        ax.plot(xx, np.ones(len(xx)) * ((ax.get_ylim()[1] - ax.get_ylim()[0]) / yloc)+ax.get_ylim()[0], color, alpha=1, linewidth=2.5)
    else:
        p = np.zeros(array.shape[1])
        for i in range(array.shape[1]):
            p[i] = sp.stats.ttest_rel(array[:,i], np.zeros(array.shape[0]))[1]
        sig_indices = np.array(p < 0.05, dtype=int)
        sig_indices[0] = 0
        sig_indices[-1] = 0
        s_bar = zip(np.where(np.diff(sig_indices)==1)[0]+1, np.where(np.diff(sig_indices)==-1)[0])
        for sig in s_bar:
            ax.hlines(((ax.get_ylim()[1] - ax.get_ylim()[0]) / yloc)+ax.get_ylim()[0], x[int(sig[0])]-(np.diff(x)[0] / 2.0), x[int(sig[1])]+(np.diff(x)[0] / 2.0), color=color, alpha=1, linewidth=2.5)

def lin_regress_betas(Y, X, eq='ols'):
    # prepare data:
    d = {'Y' : pd.Series(Y),}
    for i in range(len(X)):        
        d['X{}'.format(i)] = pd.Series(X[i])
    data = pd.DataFrame(d) # columns = Y plus X0 ... XN
    
    # using formulas adds constant in statsmodesl by default, otherwise sm2.add_constant(data)
    formula = 'Y ~ X0' 
    if len(X) > 1:
        for i in range(1,len(X)):
            formula = formula + ' + X{}'.format(i) # 'Y ~ X0 + X1 + X2 + X3'
    # fit:
    if eq == 'ols':
        model = sm.ols(formula=formula, data=data)
    fitted = model.fit()
    return np.array(fitted.params) # return beta coefficients


def fischer_transform(r):
    return 0.5*np.log((1+r)/(1-r))
