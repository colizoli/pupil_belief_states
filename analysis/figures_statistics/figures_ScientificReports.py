#!/usr/bin/env python
# encoding: utf-8
"""
================================================
figures_ScientificReports.py

If used, please cite: 
Colizoli, O., de Gee, J. W., Urai, A. E. & Donner, T. H.
Task-evoked pupil responses reflect internal belief states. Scientific Reports 8, 13702 (2018).
================================================
"""

import os
import sys
import numpy as np
import scipy as sp
import scipy.stats as stats
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import mne
import statsmodels.api as sm
from copy import deepcopy
import pyvttbl as pt
from pyvttbl import SimpleHTML
from IPython import embed as shell

sys.path.append(os.environ['ANALYSIS_HOME'])

from Tools.other_scripts import functions_jw as myfuncs
from Tools.other_scripts import functions_jw_GLM as GLM

import functions_oc as ocf

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
sns.set(style='ticks', font='Arial', font_scale=1, rc={
    'axes.linewidth': 1,
    'axes.labelsize': 7, 
    'axes.titlesize': 7,
    'xtick.labelsize': 6,
    'ytick.labelsize': 6,
    'legend.fontsize': 6,
    'xtick.major.width': 1,
    'ytick.major.width': 1,
    'text.color': 'Black',
    'axes.labelcolor':'Black',
    'xtick.color':'Black',
    'ytick.color':'Black',} )
sns.plotting_context()

class figureClass(object):
    def __init__(self, subjects, experiment_name, project_directory):
        
        self.subjects = subjects
        self.nr_subjects = len(self.subjects)
        self.experiment_name = experiment_name
        self.project_directory = project_directory
        self.data_folder = os.path.join(project_directory, 'data', 'across')
        self.figure_folder = os.path.join(project_directory, 'figures')
        self.dataframe_folder = os.path.join(project_directory, 'data_frames')
        self.dataframe_folder_IRF = os.path.join('/home/', 'measure_irf','data_frames')
        self.dataframe_folder_feedback = os.path.join('/home/', 'control','data_frames')
       
        ##############################    
        # Pupil time series information:
        ##############################
        self.sample_rate = 1000
        self.downsample_rate = 100       # 50
        self.new_sample_rate = self.sample_rate / self.downsample_rate
        self.interval = 15 # determines size of kernel when * with sample rate
        
        self.pupil_step_lim = [[-2,13],[-2,13],[-5,10]] # order is stim, feed, resp!
        self.pupil_xlim = [   
            # order is stim, feed, resp!
            [-0.5,7.5],[-0.5,7.5],[-1.5,7.5]
            ]

        self.time_locked = ['resp_locked','feed_locked']
        self.pupil_dvs = ['pupil_resp_d_clean_RT', 'pupil_d_feed_clean'] # 'clean' refers to sustained time window, not RT! 'RT' means RT in! [3,6] s
        self.pupil_dvs_rRT = ['pupil_resp_d_clean', 'pupil_d_feed_clean'] # RT out [3,6] s
        self.pupil_dvs_PRE = ['pupil_feed_stim_baseline_RT','pupil_d_feed_clean'] # later and shorter baseline locked to feedback [-0.5,0], RT in
        self.pupil_dvs_PRE_rRT = ['pupil_feed_stim_baseline','pupil_d_feed_clean'] # RT out [-0.5,0] s
        
        self.tick_offset = 5
    

    def behavior(self, controlITI):
        # Figure 3 panels, accuracy, RT and then RT accuracy x difficulty
        
        fig = plt.figure(figsize=(6,2))
        
        #######################
        # A accuracy
        #######################
        # Plot accuracy as a function of difficulty
        ax = fig.add_subplot(131)
        
        # grab the corresponding higher level file    
        sdata = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_subjects.csv'))
        
        # filter out unwanted trials
        if controlITI:             
            sdata = sdata[sdata['long_isi']] # use isi in relation to stimulus
            sdata.reset_index(inplace=True)
        
        sdata_sum = sdata.groupby(['subj_idx','easy'])['correct'].sum()
        sdata_count = sdata.groupby(['subj_idx','easy'])['correct'].count()
        percent_correct = np.true_divide(np.array(sdata_sum) , np.array(sdata_count)) * 100
        
        cdata = pd.DataFrame()
        cdata['subj_idx'] = sdata_sum.index.labels[0]
        cdata['easy'] = sdata_sum.index.labels[1]
        cdata['percent_correct'] = percent_correct
    
        # number of subjects
        ss = len(np.unique(sdata['subj_idx']))
        # Compute means, sems for all conditions of interest
        MEANS = pd.DataFrame(cdata.groupby(['easy'])['percent_correct'].mean().reset_index())
        stds = cdata.groupby(['easy'])['percent_correct'].std()
        stds = np.array(stds)
        SEMS = stds/np.sqrt(ss)
        
        ### LINE GRAPH ###
        ind = [0.3,0.5]
        xlim = [0.275,0.575]

        xticklabels = ['Hard','Easy']
        
        # plot
        ax.bar(ind,MEANS['percent_correct'],width=0.15, yerr=SEMS, color='grey', alpha=1,ecolor=['black','black'])
        
        # set figure parameters
        ax.set_ylabel('Percent correct')
        ax.set_ylim(50,100)
        ax.set_xticks(ind)
        ax.set_xticklabels(xticklabels)    

        print('')
        print('hard vs. easy')
        print('Means = ')
        print(MEANS)
        print('STD = ')
        print(stds)
        m,p = ocf.perm_2sample(cdata[cdata['easy']==0]['percent_correct'], cdata[cdata['easy']==1]['percent_correct'])
        print('mean={} , pval={}'.format(m, round(p,3)))
        
        #######################
        # B RT
        #######################
        # Plot RT as a function of difficulty 
        ax = fig.add_subplot(132)
        
        # grab the corresponding higher level file    
        sdata = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_subjects.csv'))
        
        # filter out unwanted trials
        if controlITI:             
            sdata = sdata[sdata['long_isi']] # use isi in relation to stimulus
            sdata.reset_index(inplace=True)
        
        sdata_rt = sdata.groupby(['subj_idx','easy'])['rt'].mean()
                
        cdata = pd.DataFrame()
        cdata['subj_idx'] = sdata_rt.index.labels[0]
        cdata['easy'] = sdata_rt.index.labels[1]
        cdata['rt'] = np.array(sdata_rt)
    
        # number of subjects
        ss = len(np.unique(sdata['subj_idx']))
        # Compute means, sems for all conditions of interest
        MEANS = pd.DataFrame(cdata.groupby(['easy'])['rt'].mean().reset_index())
        stds = cdata.groupby(['easy'])['rt'].std()
        stds = np.array(stds)
        SEMS = stds/np.sqrt(ss)
        
        ### LINE GRAPH ###
        ind = [0.3,0.5]
        xlim = [0.275,0.575]

        xticklabels = ['Hard','Easy']
        
        # plot
        ax.bar(ind,MEANS['rt'],width=0.15, yerr=SEMS, color='grey', alpha=0.6, ecolor='black')
        
        # set figure parameters
        ax.set_ylabel('RT (s)')
        ax.set_ylim(1,1.5)
        ax.set_xticks(ind)
        ax.set_xticklabels(xticklabels)    
        
        print('')
        print('hard vs. easy')
        print('Means = ')
        print(MEANS)
        print('STD = ')
        print(stds)
        m,p = ocf.perm_2sample(cdata[cdata['easy']==0]['rt'], cdata[cdata['easy']==1]['rt'])
        print('mean={} , pval={}'.format(m, round(p,3)))    
        
        #######################
        # B RT accuracy x difficulty
        #######################       
        # scalar plots of RT and pupil scalars (accuracy x difficulty)     
        ax = fig.add_subplot(133)
        
        ylim = [(1.05,1.4)] 
        dvs = ['rt'] # RT in the cue-locked scalars!
        cond = 'easy*correct'
        fig_part = ['d']
        dv_title = ['Reaction Time']
        
        for n,dv in enumerate(dvs):
            if controlITI: 
                if 'feed' in dv: # long ITIs only
                    postFix = '_ITI'
                else: # long ISIs only
                    postFix = '_isi'
            else: # use all trials
                postFix = ''
    
            # grab the corresponding higher level file    
            cdata = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_higher_{}{}.csv'.format(cond,postFix)))
    
            # labels for graphs
            ylabel = 'RT (s)'
            dv = dv+'_mean' # _mean or _med
    
            # Add statistics
            try:
                aov = pd.read_csv(os.path.join(self.dataframe_folder,'anova_output','csv','rm_anova_{}_{}{}.csv'.format(dv,cond,postFix)))
            except:
                shell()
            # number of subjects
            ss = len(np.unique(cdata['subj_idx']))
            # Compute means, sems for all conditions of interest
            MEANS = pd.DataFrame(cdata.groupby(['easy','correct'])[dv].mean().reset_index())
            stds = cdata.groupby(['easy','correct'])[dv].std()
            stds = np.array(stds)
            SEMS = stds/np.sqrt(ss)
            
            fac = ['easy','correct'] 
            ax.axhline(0, lw=0.25, alpha=1, color = 'k') # Add horizontal line at t=0
    
            ### LINE GRAPH ###
            ind = [0.3,0.5]
            xlim = [0.275,0.575]
            # get xlabels and color scheme for two conditions
            ls = fac[1] # corresponding to lines
            scheme = ocf.get_colors(factor=ls)
            leg_label = scheme[0]
            colors = scheme[1]
            alphas = scheme[2]
            s2 = ocf.get_colors(factor=fac[0]) # corresponding to xticks
            xticklabels = s2[0]

            # Plot by looping through 'keys' in grouped dataframe
            x=0 # count 'groups'
            for key,grp in MEANS.groupby(ls):
                # print(key)
                print(grp)
                ax.errorbar(ind,grp[dv],yerr=SEMS[x], label=leg_label[x], color=colors[x], alpha=alphas[x])
                x=x+1

            # Figure parameters
            ax.set_xticks(ind)
            ax.set_xticklabels(xticklabels)    
            ax.legend(loc='best', fontsize=4)
            ax.set_ylabel(ylabel)
            
            # set figure parameters
            ax.set_ylim(ylim[n])
        
            # STATS FOR PLOTTING
            print('controlITI {} '.format(controlITI))
            print(dv)
            aov.drop(['Unnamed: 0'],axis=1,inplace=True)
            print(aov)
        
            ttests = cdata[['easy','correct']+[dv]]
            hard_error = ttests[(ttests['easy'] ==0) & (ttests['correct'] ==0)] # hard error
            hard_correct = ttests[(ttests['easy'] ==0) & (ttests['correct'] ==1)] # hard correct
            easy_error = ttests[(ttests['easy'] ==1) & (ttests['correct'] ==0)] # easy error
            easy_correct = ttests[(ttests['easy'] ==1) & (ttests['correct'] ==1)] # easy correct
        
            hard_error = np.array(hard_error[dv])
            hard_correct = np.array(hard_correct[dv])
            easy_error = np.array(easy_error[dv])
            easy_correct = np.array(easy_correct[dv])
        
            print('')
            print('2 sample perm tests')
            print('hard_error vs. hard_correct')
            m,p = ocf.perm_2sample(hard_error, hard_correct)
            print('mean={} , std={}, pval={}'.format(m, np.std(hard_error-hard_correct), round(p,3)))
        
            print('')
            print('easy_error vs. easy_correct')
            m,p = ocf.perm_2sample(easy_error, easy_correct)
            print('mean={} , std={}, pval={}'.format(m, np.std(easy_error-easy_correct), round(p,3)))
        
            print('')
            print('hard_error vs. easy_error')
            m,p = ocf.perm_2sample(hard_error, easy_error)
            print('mean={} , std={}, pval={}'.format(m, np.std(hard_error-easy_error), round(p,3)))
            
            print('')
            print('hard_correct vs. easy_correct')
            m,p = ocf.perm_2sample(hard_correct, easy_correct)
            print('mean={} , std={}, pval={}'.format(m, np.std(hard_correct-easy_correct), round(p,3))) 
            
            print('')
            print('MAIN EFFECTS')
            print('hard vs. easy')
            hard = np.array(ttests[ttests['easy'] ==0][dv]) # hard
            easy = np.array(ttests[ttests['easy'] ==1][dv]) # easy
            m,p = ocf.perm_2sample(hard, easy)
            print('mean={}, std={}, pval={}'.format(m, np.std(hard-easy), round(p,3)))
        
            print('MAIN EFFECTS')
            print('error vs. correct')
            error = np.array(ttests[ttests['correct'] ==0][dv]) # error
            correct = np.array(ttests[ttests['correct'] ==1][dv]) # correct
            m,p = ocf.perm_2sample(error, correct)
            print('mean={}, std={}, pval={}'.format(m, np.std(error-correct), round(p,3)))
                        
        sns.despine(offset=10, trim=True)
        plt.tight_layout()
        fig.savefig(os.path.join(self.figure_folder, 'ScientificReports', 'behavior_controlITI_{}.pdf'.format(controlITI)))
        print('success: behavior')        
        
    
    def control_exp(self, controlITI):
        # feedback IRF task vs. feedback control correct/error
        nperms = 10000
        corr = True
        
        downsample_rate = 20 # 20 Hz
        downsample_factor = self.sample_rate / downsample_rate # 50
        interval = self.interval # determines size of kernel when * with sample rate
        k = self.interval*downsample_rate # length of kernel
        
        # for task evoked responses
        step_lim = [-2,13]
        xlim = [-0.5,7.5]
        xlabel = 'Time from event (s)'
        step = pd.Series(np.linspace(step_lim[0], step_lim[1], k), name=xlabel)
        # Step size for x axis:
        xlim_indices = np.array(step >= xlim[0]) * np.array(step <= xlim[1])
        
        # for testing significance of feedback experiment
        xlim_feedback = [0,3]
        # Step size for x axis:
        xlim_indices_feedback = np.array(step >= xlim_feedback[0]) * np.array(step <= xlim_feedback[1])
        
        # whole figure
        fig = plt.figure(figsize=(2,2))        
        ax1 = fig.add_subplot(111)
        ax1.axhline(0, lw=1, alpha=1, color = 'black') # Add horizontal line at t=0        
        ax1.axvline(0, lw=1, alpha=1, color = 'black') # Add vertical line at t=0   
        ax1.axvspan(3, 6, facecolor='black', alpha=0.5) # sustained window 3.75-7.5
        
        # Read in dataframe
        if controlITI:
            feed_data = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}.csv'.format('feed_locked','all','_ITI')))
        else:
            feed_data = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}.csv'.format('feed_locked','all')))
        control_data = pd.read_csv(os.path.join(self.dataframe_folder_feedback,'pupil','higher','pupil_events_{}_{}{}.csv'.format('feed_locked','correct','')))

        # downsample
        feed_data = feed_data.drop(['subj_idx'], axis=1, inplace=False)
        feed_data = np.array(feed_data)
        feed_data = sp.signal.decimate(feed_data, downsample_factor, ftype='fir')
        
        correct_data = control_data[control_data['correct'] == 1]
        # correct_data.reset_index(inplace=True)
        correct_data = correct_data.drop(['correct','subj_idx'], axis=1, inplace=False)
        correct_data = np.array(correct_data)
        correct_data = sp.signal.decimate(correct_data, downsample_factor, ftype='fir')
        
        error_data = control_data[control_data['correct'] == 0]
        error_data = error_data.drop(['correct','subj_idx'], axis=1, inplace=False)
        error_data = np.array(error_data)
        error_data = sp.signal.decimate(error_data, downsample_factor, ftype='fir')
                
        DIFF = correct_data - error_data
        DIFF = DIFF[:,xlim_indices_feedback]
        
        # cut xlim
        feed_data = feed_data[:,xlim_indices]
        correct_data = correct_data[:,xlim_indices]
        error_data = error_data[:,xlim_indices]
        
        # plot
        sns.tsplot(feed_data, time=step[xlim_indices], condition='Feedback', color='black', alpha=1, lw=1, ls='-', ax=ax1)
        sns.tsplot(correct_data, time=step[xlim_indices], condition='Green', color='green', alpha=1, lw=1, ls='-', ax=ax1)
        sns.tsplot(error_data, time=step[xlim_indices], condition='Red', color='red', alpha=1, lw=1, ls='-', ax=ax1)
        
        # add stats
        ocf.cluster_sig_bar_1samp(array=DIFF, x=np.array(step[xlim_indices_feedback]), yloc=3, color='grey', ax=ax1, threshold=0.05, nrand=nperms, cluster_correct=corr)
        
        # subplot parameters
        ax1.set_ylabel('Pupil response\n(% signal change)')
        ax1.legend(loc='best',fontsize=4)        
        
        sns.despine(offset=10, trim=True)
        plt.tight_layout()
        fig.savefig(os.path.join(self.figure_folder, 'ScientificReports', 'control_experiment_controlITI_{}.pdf'.format(controlITI)))        
        print('success: control_exp')  
   
        
    def get_sigma(self,):
        # estimate sigma from the data
        
        sdata = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_subjects.csv'))
        d = pd.DataFrame()
        d['easy'] = sdata['easy']
        d['response'] = sdata['response'] # 1 up, 0 down
        d['stimulus'] = sdata['stimulus'] # 1 up, 0 down
        d['coherence'] = sdata['coherence']
        d['coh_dir'] = d['coherence'] / np.sign(d['stimulus'] - 0.5) # adds direction 1,-1
        
        # x = coherence from neg to pos (coh_dir), 
        # y = up responses
        x = np.array(d['coh_dir'])
        y = np.array(d['response'])
        
        # logit and probit are both binomial fits     
        # probit is related to the normal distributions you are generating for the noise added to the DV
        sm_probit_Link = sm.genmod.families.links.probit
        glm_binom = sm.GLM(y, sm.add_constant(x), family=sm.families.Binomial(link=sm_probit_Link))
        glm_result = glm_binom.fit() # USE PROBIT!
        
        print glm_result.params
        d['probit'] = np.array(glm_result.fittedvalues) # get the parameter estimates for plotting curve
                       
        # Plot psychometric curve   
        fig = plt.figure(figsize=(2,2))
        ax = fig.add_subplot(111)
        
        # group only for plotting
        grouped = d.groupby(['coh_dir'])['response','probit'].mean()        
        grouped = grouped.reset_index()

        xg = np.array(grouped['coh_dir'])
        yg = np.array(grouped['response'])
        zg = np.array(grouped['probit'])
        
        ax.scatter(xg,yg,s=6, label='Data')
        ax.plot(xg,zg, label='Probit fit', color='red')
    
        ax.legend(loc='upper left');
        ax.set_xlabel('Motion coherence')
        ax.set_ylabel('Fraction choices: up')
        
        sns.despine(offset=10, trim=True)
        plt.tight_layout()
        fig.savefig(os.path.join(self.figure_folder, 'ScientificReports', 'psychometric_curve.pdf'))

        return np.round(1/glm_result.params[1],2) # sigma = 1/b(2)
        
    def get_sigma_subjects(self, IV):
        # estimate sigma from the data, for each individual subject
        # plot psychometric functions
        # either 'coh_direction' or 'motion_energy'
        fig = plt.figure(figsize=(10,10))
        
        sdata = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_subjects.csv'))
        sdata.drop(['Unnamed: 0'], axis=1, inplace=True)
        
        save_sigmas = []
        for s,subj in enumerate(np.unique(sdata['subj_idx'])):
        
            d = sdata[sdata['subj_idx']==s]
            # x = coherence from neg to pos (coh_dir), 
            # y = up responses
            x = np.array(d[IV]) # motion energy or coherence direction
            y = np.array(d['response'])
                    
            # logit and probit are both binomial fits     
            # probit is related to the normal distributions you are generating for the noise added to the DV
            sm_probit_Link = sm.genmod.families.links.probit
            glm_binom = sm.GLM(y, sm.add_constant(x), family=sm.families.Binomial(link=sm_probit_Link)) # USE PROBIT!
            glm_result = glm_binom.fit()
        
            print glm_result.params
            d['probit'] = np.array(glm_result.fittedvalues)
                
            # group only for plotting
            grouped = d.groupby(['coh_direction'])['response','probit','motion_energy'].mean()        
            grouped = grouped.reset_index()
        
            xg = np.array(grouped[IV])
            yg = np.array(grouped['response'])
            zg = np.array(grouped['probit'])
            
            if IV == 'motion_energy': # arbitrary units
                xg = xg/1000
            
            # Plot psychometric curve   
            ax = fig.add_subplot(4,4,s+1)
            ax.set_title('subj '+ str(s+1))
            ax.set_ylabel('Fraction choices: up')
            ax.scatter(xg,yg,s=20, label='Data')
            ax.plot(xg,zg, label='Probit fit', color='red')
            if IV == 'motion_energy': 
                ax.set_xticks([int(min(xg)),0,int(max(xg))])
                ax.set_xlabel('Motion energy (a.u.)') 
            else:
                ax.set_xlabel('Motion coherence') 
            ax.legend(loc='upper left');
        
            save_sigmas.append(np.round(1/glm_result.params[1],2))  # sigma = 1/b(2)
            
        s = pd.DataFrame(save_sigmas)
        s.to_csv(os.path.join(self.figure_folder, 'ScientificReports','model_subjects',IV,'sigmas_subjects_{}.csv'.format(IV)))
               
        sns.despine(offset=10, trim=True)
        plt.tight_layout()
        fig.savefig(os.path.join(self.figure_folder, 'ScientificReports','model_subjects',IV,'psychometric_curve_subjects_{}.pdf'.format(IV)))
        print('success: get_sigma_subjects')  
        
    def sdt_models(self):
        # Signal Detection Theory competing model predictions
        
        sigma = self.get_sigma()
        
        # sigma = 1/7.5
        print('sigma')
        print(sigma)        
        model_coh = np.arange(-.5,.5,0.01)
        
        model_evs = np.repeat(model_coh, 10000)
        model_dvs = model_evs + np.random.normal(0, sigma, len(model_evs)) # add noise to the decision variable
        model_choice = np.sign(model_dvs)
        model_correct = model_choice == np.sign(model_evs)

        def dv2conf(x,sigma):
            from scipy.special import erf
            return 0.5 * (1 + erf(np.abs(x) / (np.sqrt(2)*sigma)))
        
        # The difference in the two models is here: whether the confidence is a function of the external or internal decision variable
        model_confidence_belief = dv2conf(model_dvs,sigma); # model 1
        model_confidence = dv2conf(model_evs,sigma); # alternative model, # should sigma be 0 here? Because the EVs are not corrupted by the internal noise        
        model_feedback = model_correct;
        model_rpe_belief = model_feedback - model_confidence_belief; # model 1
        model_rpe = model_feedback - model_confidence; # alternative model
        
        # plot models
        # model_levels_evs = np.abs(model_evs) #
        model_levels_dvs = np.abs(model_dvs) # make 2 bins 
        
        model1 = pd.DataFrame()
        model1['evs'] = model_evs
        model1['dvs'] = model_dvs
        model1['ev_levels'] = np.abs(model_evs) 
        model1['correct'] = model_correct
        model1['confidence'] = model_confidence_belief
        model1['uncertainty'] = 1 - model_confidence_belief
        model1['pe'] = model_rpe_belief
        model1['pe_inv'] = 1 - model_rpe_belief        
        
        model2 = pd.DataFrame()
        model2['evs'] = model_evs
        model2['dvs'] = model_dvs
        model2['ev_levels'] = np.abs(model_evs) 
        model2['correct'] = model_correct
        model2['confidence'] = model_confidence
        model2['uncertainty'] = 1 - model_confidence
        model2['pe'] = model_rpe
        model2['pe_inv'] = 1 - model_rpe
    
        model1.to_csv(os.path.join(self.figure_folder, 'ScientificReports','model1.csv'))
        model2.to_csv(os.path.join(self.figure_folder, 'ScientificReports','model2.csv'))
        print('success: sdt_models')  
        
        
    def sdt_models_subjects(self, IV):
        # Signal Detection Theory competing model predictions
        # Single subject models based on internal noise estimates
        # either 'coh_direction' or 'motion_energy'
        
        self.get_sigma_subjects(IV) 
        sigmas = pd.read_csv(os.path.join(self.figure_folder, 'ScientificReports','model_subjects',IV,'sigmas_subjects_{}.csv'.format(IV)))
        sigmas = np.array(sigmas.iloc[:,1]) # get 2nd column
        
        sdata = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_subjects.csv'))
        sdata.drop(['Unnamed: 0'], axis=1, inplace=True)
        
        print('sigmas')
        print(sigmas)
        
        # define confidence transformation
        def dv2conf(x,sigma):
            from scipy.special import erf
            return 0.5 * (1 + erf(np.abs(x) / (np.sqrt(2)*sigma)))
        
        for s,sigma in enumerate(sigmas):
            if IV == 'motion_energy':
                # simulate for each trial
                d = sdata[sdata['subj_idx']==s]
                model_coh = np.array(d['motion_energy'])      
                reps = 10000          
            else:
                # use range of coherence
                model_coh = np.arange(-.5,.5,0.01)        
                reps = 10000
                
            model_evs = np.repeat(model_coh, reps)
            model_dvs = model_evs + np.random.normal(0, sigma, len(model_evs)) # add noise to the decision variable
            model_choice = np.sign(model_dvs)
            model_correct = model_choice == np.sign(model_evs)

            # The difference in the two models is here: whether the confidence is a function of the external or internal decision variable
            model_confidence_belief = dv2conf(model_dvs,sigma); # model 1
            model_confidence = dv2conf(model_evs,sigma); # alternative model, # should sigma be 0 here? Because the EVs are not corrupted by the internal noise
        
            model_feedback = model_correct;
            model_rpe_belief = model_feedback - model_confidence_belief; # model 1
            model_rpe = model_feedback - model_confidence; # alternative model
            # plot models
            # model_levels_evs = np.abs(model_evs) #
            model_levels_dvs = np.abs(model_dvs) # make 2 bins 
        
            model1 = pd.DataFrame()
            model1['evs'] = model_evs
            model1['dvs'] = model_dvs
            model1['ev_levels'] = np.abs(model_evs) 
            model1['correct'] = model_correct
            model1['confidence'] = model_confidence_belief
            model1['uncertainty'] = 1 - model_confidence_belief
            model1['pe'] = model_rpe_belief
            model1['pe_inv'] = 1 - model_rpe_belief        
        
            model2 = pd.DataFrame()
            model2['evs'] = model_evs
            model2['dvs'] = model_dvs
            model2['ev_levels'] = np.abs(model_evs) 
            model2['correct'] = model_correct
            model2['confidence'] = model_confidence
            model2['uncertainty'] = 1 - model_confidence
            model2['pe'] = model_rpe
            model2['pe_inv'] = 1 - model_rpe
        
            model1.to_csv(os.path.join(self.figure_folder, 'ScientificReports','model_subjects',IV,'model1_subj{}_{}.csv'.format(s, IV)))
            model2.to_csv(os.path.join(self.figure_folder, 'ScientificReports','model_subjects',IV,'model2_subj{}_{}.csv'.format(s, IV)))
        print('success: sdt_models_subjects')  
        
        
    def plot_sdt_models(self,):
        # Plots the model predictions (6 panels)
        
        # Which direction to plot? confidence or uncertainty?
        # CONFIDENCE
        # decision_dv = 'confidence'
        # feedback_dv = 'pe'
        # y lims
        # dec = [0.5,1]
        # feed = [-1,1]
        # inter = [-0.5,0.5]
        # UNCERTAINTY
        decision_dv = 'uncertainty'
        feedback_dv = 'pe_inv'
        # y lims
        dec = [0,0.5]
        feed = [0.4,2]
        inter = [-0.5,0.5]
        yticksfeed = [0.4,0.8,1.2,1.6,2]
        # xlims
        xdiff = [0,0.5]
        xdifflabels = ['Hard','Easy']
        
        # set number of bins for plotting
        nbins = 10
        bin_labels = range(1,nbins+1)
        
        model1 = pd.read_csv(os.path.join(self.figure_folder, 'ScientificReports','model1.csv'))
        model2 = pd.read_csv(os.path.join(self.figure_folder, 'ScientificReports','model2.csv'))
        
        # group by ev levels and accuracy
        model1_decision = model1.groupby(['ev_levels','correct'])[decision_dv].mean()
        model2_decision = model2.groupby(['ev_levels','correct'])[decision_dv].mean()

        model1_feedback = model1.groupby(['ev_levels','correct'])[feedback_dv].mean()
        model2_feedback = model2.groupby(['ev_levels','correct'])[feedback_dv].mean()
        
        m1_dec = model1_decision.reset_index() # gets indices as columns
        m2_dec = model2_decision.reset_index()
        m1_feed = model1_feedback.reset_index()
        m2_feed = model2_feedback.reset_index()
        
        #######################
        # whole figure
        #######################
        fig = plt.figure(figsize=(6,4))
        
        # for interaction plots
        ind = [0.3,0.5]
        xlim = [0.275,0.575]
        # get xlabels and color scheme for two conditions
        ls = 'interact' # corresponding to lines
        scheme = ocf.get_colors(factor=ls)
        leg_label = scheme[0]
        colors = scheme[1]
        alphas = scheme[2]
        s2 = ocf.get_colors(factor='interact') # corresponding to xticks
        xticklabels = s2[0]
        

        #######################
        # A model1 decision
        #######################
        ax = fig.add_subplot(231)
        
        # make equal size bins where correct==False 
        # average coherence and confidence in each bin
        valuelist = [False]
        F = m1_dec[m1_dec.correct.isin(valuelist)] # ev_levels that have errors
        valueList = np.array(F['ev_levels'])
        T =  m1_dec[m1_dec['correct']] # only true values
        # get only those ev_levels that are in m1_dec_F
        T = T[T.ev_levels.isin(valueList)]
        
        F = F.reset_index() 
        T = T.reset_index() 
        
        # Error
        bins_F = pd.qcut(F['ev_levels'], nbins, labels=bin_labels, retbins=True) 
        F['bins'] = np.array(bins_F[0]) # tupel, get first element out
        F_binned = F.groupby(['bins'])['ev_levels', decision_dv].mean()
        
        # Correct
        bins_T = pd.qcut(T['ev_levels'], nbins, labels=bin_labels, retbins=True) 
        T['bins'] = np.array(bins_T[0]) # tupel, get first element out
        T_binned = T.groupby(['bins'])['ev_levels', decision_dv].mean()
        
        # save for interaction plot
        easy_error_dec = F_binned.iloc[-1,-1] # last level, confidence/pe
        hard_error_dec = F_binned.iloc[0,-1] # first level, confidence/pe
        easy_correct_dec = T_binned.iloc[-1,-1] # last level, confidence/pe
        hard_correct_dec = T_binned.iloc[0,-1] # first level, confidence/pe

        ### LINE GRAPH ###        
        ax.plot(T_binned['ev_levels'],T_binned[decision_dv], label='Correct', color='green', alpha=1)
        ax.plot(F_binned['ev_levels'],F_binned[decision_dv], label='Error', color='red', alpha=1)
        
        # Figure parameters
        ax.set_xticks(xdiff)
        # ax.set_xlim(xlim)
        ax.set_ylim(dec)
        ax.set_xticklabels(xdifflabels)
        ax.legend(loc='best', fontsize=4)
        ax.set_ylabel('Decision uncertainty\n(1 - confidence)')
        ax.set_xlabel('Motion coherence')
        ax.set_title('Belief State Model')
        # ax.set_yticks([])
        
        #######################
        # B model1 feedback
        #######################
        ax = fig.add_subplot(232)

        # make equal size bins where correct==False 
        # average coherence and confidence in each bin
        valuelist = [False]
        F = m1_feed[m1_feed.correct.isin(valuelist)] # ev_levels that have errors
        valueList = np.array(F['ev_levels'])
        T =  m1_feed[m1_feed['correct']] # only true values
        # get only those ev_levels that are in m1_dec_F
        T = T[T.ev_levels.isin(valueList)]
        
        F = F.reset_index() 
        T = T.reset_index() 
        
        # Error
        bins_F = pd.qcut(F['ev_levels'], nbins, labels=bin_labels, retbins=True) 
        F['bins'] = np.array(bins_F[0]) # tupel, get first element out
        F_binned = F.groupby(['bins'])['ev_levels', feedback_dv].mean()
        
        # Correct
        bins_T = pd.qcut(T['ev_levels'], nbins, labels=bin_labels, retbins=True) 
        T['bins'] = np.array(bins_T[0]) # tupel, get first element out
        T_binned = T.groupby(['bins'])['ev_levels', feedback_dv].mean()
        
        # save for interaction plot
        easy_error_feed = F_binned.iloc[-1,-1] # last level, confidence/pe
        hard_error_feed = F_binned.iloc[0,-1] # first level, confidence/pe
        easy_correct_feed = T_binned.iloc[-1,-1] # last level, confidence/pe
        hard_correct_feed = T_binned.iloc[0,-1] # first level, confidence/pe

        ### LINE GRAPH ###        
        ax.plot(T_binned['ev_levels'],T_binned[feedback_dv], label='Correct', color='green', alpha=1)
        ax.plot(F_binned['ev_levels'],F_binned[feedback_dv], label='Error', color='red', alpha=1)
        
        # Figure parameters
        ax.set_xticks(xdiff)
        # ax.set_xlim(xlim)
        ax.set_ylim(feed)
        ax.set_yticks(yticksfeed)
        ax.set_xticklabels(xdifflabels)
        ax.legend(loc='best', fontsize=4)
        ax.set_ylabel('Prediction error\n1 - (feedback - confidence)')
        ax.set_xlabel('Motion coherence')
        ax.set_title('Belief State Model')
        # ax.set_yticks([])

        ######################
        # C model1 interaction
        ######################
        ax = fig.add_subplot(233)
                
        easy_error_dec = np.round(easy_error_dec,2)
        hard_error_dec = np.round(hard_error_dec,2)
        easy_correct_dec = np.round(easy_correct_dec,2)
        hard_correct_dec = np.round(hard_correct_dec,2)
        
        easy_error_feed = np.round(easy_error_feed,2)
        hard_error_feed = np.round(hard_error_feed,2)
        easy_correct_feed = np.round(easy_correct_feed,2)
        hard_correct_feed = np.round(hard_correct_feed,2)
        
        interaction_decision = (easy_error_dec - easy_correct_dec) - (hard_error_dec - hard_correct_dec)
        interaction_feed = (easy_error_feed - easy_correct_feed) - (hard_error_feed - hard_correct_feed)

        MEANS = [interaction_decision,interaction_feed]

        xticklabels = ['Decision','Feedback']

        for x,m in enumerate(MEANS):
            ax.plot(ind[x],MEANS[x], marker='o', color=colors[x], label=leg_label[x], alpha=alphas[x])

        # Figure parameters
        ax.set_xticks(ind)
        # ax.set_xlim(xlim)
        ax.set_ylim(inter)
        ax.set_xticklabels(xticklabels)
        # ax.legend(loc='best', fontsize=4)
        ax.legend([])
        ax.set_ylabel('Interaction term')
        ax.set_title('Belief State Model')
        # ax.set_yticks([])
        ax.axhline(0, lw=1, alpha=1, color = 'k') # Add horizontal line at t=0

        #######################
        # D model2 decision
        #######################
        ax = fig.add_subplot(234)

        # make equal size bins where correct==False 
        # average coherence and confidence in each bin
        valuelist = [False]
        F = m2_dec[m2_dec.correct.isin(valuelist)] # ev_levels that have errors
        valueList = np.array(F['ev_levels'])
        T =  m2_dec[m2_dec['correct']] # only true values
        # get only those ev_levels that are in m1_dec_F
        T = T[T.ev_levels.isin(valueList)]
        
        F = F.reset_index() 
        T = T.reset_index() 
        
        # Error
        bins_F = pd.qcut(F['ev_levels'], nbins, labels=bin_labels, retbins=True) 
        F['bins'] = np.array(bins_F[0]) # tupel, get first element out
        F_binned = F.groupby(['bins'])['ev_levels', decision_dv].mean()
        
        # Correct
        bins_T = pd.qcut(T['ev_levels'], nbins, labels=bin_labels, retbins=True) 
        T['bins'] = np.array(bins_T[0]) # tupel, get first element out
        T_binned = T.groupby(['bins'])['ev_levels', decision_dv].mean()
        
        # save for interaction plot
        easy_error_dec = F_binned.iloc[-1,-1] # last level, confidence/pe
        hard_error_dec = F_binned.iloc[0,-1] # first level, confidence/pe
        easy_correct_dec = T_binned.iloc[-1,-1] # last level, confidence/pe
        hard_correct_dec = T_binned.iloc[0,-1] # first level, confidence/pe

        ### LINE GRAPH ###        
        ax.plot(T_binned['ev_levels'],T_binned[decision_dv], label='Correct', color='green', alpha=1)
        ax.plot(F_binned['ev_levels'],F_binned[decision_dv], label='Error', color='red', alpha=1)

        # Figure parameters
        ax.set_xticks(xdiff)
        # ax.set_xlim(xlim)
        ax.set_ylim(dec)
        ax.set_xticklabels(xdifflabels)
        ax.legend(loc='best', fontsize=4)
        ax.set_ylabel('Decision uncertainty\n(1 - confidence)')
        ax.set_xlabel('Motion coherence')
        ax.set_title('Stimulus State Model')
        # ax.set_yticks([])

        #######################
        # E model2 feedback
        #######################
        ax = fig.add_subplot(235)

        # make equal size bins where correct==False 
        # average coherence and confidence in each bin
        valuelist = [False]
        F = m2_feed[m2_feed.correct.isin(valuelist)] # ev_levels that have errors
        valueList = np.array(F['ev_levels'])
        T =  m2_feed[m2_feed['correct']] # only true values
        # get only those ev_levels that are in m1_dec_F
        T = T[T.ev_levels.isin(valueList)]
        
        F = F.reset_index() 
        T = T.reset_index() 
        
        # Error
        bins_F = pd.qcut(F['ev_levels'], nbins, labels=bin_labels, retbins=True) 
        F['bins'] = np.array(bins_F[0]) # tupel, get first element out
        F_binned = F.groupby(['bins'])['ev_levels', feedback_dv].mean()
        
        # Correct
        bins_T = pd.qcut(T['ev_levels'], nbins, labels=bin_labels, retbins=True) 
        T['bins'] = np.array(bins_T[0]) # tupel, get first element out
        T_binned = T.groupby(['bins'])['ev_levels', feedback_dv].mean()
        
        # save for interaction plot
        easy_error_feed = F_binned.iloc[-1,-1] # last level, confidence/pe
        hard_error_feed = F_binned.iloc[0,-1] # first level, confidence/pe
        easy_correct_feed = T_binned.iloc[-1,-1] # last level, confidence/pe
        hard_correct_feed = T_binned.iloc[0,-1] # first level, confidence/pe

        ### LINE GRAPH ###        
        ax.plot(T_binned['ev_levels'],T_binned[feedback_dv], label='Correct', color='green', alpha=1)
        ax.plot(F_binned['ev_levels'],F_binned[feedback_dv], label='Error', color='red', alpha=1)

        # Figure parameters
        ax.set_xticks(xdiff)
        # ax.set_xlim(xlim)
        ax.set_ylim(feed)
        ax.set_yticks(yticksfeed)
        ax.set_xticklabels(xdifflabels)
        ax.legend(loc='best', fontsize=4)
        ax.set_ylabel('Prediction error\n1 - (feedback - confidence)')
        ax.set_xlabel('Motion coherence')
        ax.set_title('Stimulus State Model')
        # ax.set_yticks([])

        #######################
        # F model2 interaction
        #######################
        ax = fig.add_subplot(236)
        ax.axhline(0, lw=1, alpha=1, color = 'k') # Add horizontal line at t=0
                
        easy_error_dec = np.round(easy_error_dec,2)
        hard_error_dec = np.round(hard_error_dec,2)
        easy_correct_dec = np.round(easy_correct_dec,2)
        hard_correct_dec = np.round(hard_correct_dec,2)
        
        easy_error_feed = np.round(easy_error_feed,2)
        hard_error_feed = np.round(hard_error_feed,2)
        easy_correct_feed = np.round(easy_correct_feed,2)
        hard_correct_feed = np.round(hard_correct_feed,2)
        
        interaction_decision = (easy_error_dec - easy_correct_dec) - (hard_error_dec - hard_correct_dec)
        interaction_feed = (easy_error_feed - easy_correct_feed) - (hard_error_feed - hard_correct_feed)

        MEANS = [interaction_decision,interaction_feed]

        xticklabels = ['Decision','Feedback']

        for x,m in enumerate(MEANS):
            ax.plot(ind[x],MEANS[x], marker='o', color=colors[x], label=leg_label[x], alpha=alphas[x])

        # Figure parameters
        ax.set_xticks(ind)
        # ax.set_xlim(xlim)
        ax.set_ylim(inter)
        ax.set_xticklabels(xticklabels)
        # ax.legend(loc='best', fontsize=4)
        ax.legend([])
        ax.set_ylabel('Interaction term')
        ax.set_title('Stimulus State Model')
        # ax.set_yticks([])

        sns.despine(offset=10, trim=True)
        plt.tight_layout()
        fig.savefig(os.path.join(self.figure_folder, 'ScientificReports', 'model_predictions.pdf'))
        print('success: plot_sdt_models_subjects')
        
  
    def plot_sdt_models_subject_predictions(self, IV):
        # Plots the model predictions (subjects x 2 panels (belief state vs. stimulus state))

        sigmas = pd.read_csv(os.path.join(self.figure_folder, 'ScientificReports','model_subjects',IV,'sigmas_subjects_{}.csv'.format(IV)))
        sigmas = np.array(sigmas.iloc[:,1]) # get 2nd column
                
        # CONFIDENCE
        # decision_dv = 'confidence'
        # feedback_dv = 'pe'
        # y lims
        # dec = [0.5,1]
        # feed = [-1,1]
        # inter = [-0.5,0.5]
        # UNCERTAINTY
        decision_dv = 'uncertainty'
        feedback_dv = 'pe_inv'
        # y lims
        dec = [0,0.5]
        feed = [0.4,2]
        inter = [-0.5,0.5]
        yticksfeed = [0.4,0.8,1.2,1.6,2]
        # xlims
        xdiff = [0,0.5]
        xdifflabels = ['Hard','Easy']
        
        # set number of bins for plotting
        nbins = 10
        bin_labels = range(1,nbins+1)
        
        fig = plt.figure(figsize=(4,30))        # Which direction to plot? confidence or uncertainty?
        #######################
        # whole figure
        #######################        
        # for interaction plots
        ind = [0.3,0.5]
        xlim = [0.275,0.575]
        # get xlabels and color scheme for two conditions
        ls = 'interact' # corresponding to lines
        scheme = ocf.get_colors(factor=ls)
        leg_label = scheme[0]
        colors = scheme[1]
        alphas = scheme[2]
        s2 = ocf.get_colors(factor='interact') # corresponding to xticks
        xticklabels = s2[0]
        
        counter = 1
        for s,sigma in enumerate(sigmas):

            model1 = pd.read_csv(os.path.join(self.figure_folder, 'ScientificReports','model_subjects',IV,'model1_subj{}_{}.csv'.format(s,IV)))
            model2 = pd.read_csv(os.path.join(self.figure_folder, 'ScientificReports','model_subjects',IV,'model2_subj{}_{}.csv'.format(s,IV)))
            
            # group by ev levels and accuracy
            model1_decision = model1.groupby(['ev_levels','correct'])[decision_dv].mean()
            model2_decision = model2.groupby(['ev_levels','correct'])[decision_dv].mean()

            model1_feedback = model1.groupby(['ev_levels','correct'])[feedback_dv].mean()
            model2_feedback = model2.groupby(['ev_levels','correct'])[feedback_dv].mean()
        
            m1_dec = model1_decision.reset_index() # gets indices as columns
            m2_dec = model2_decision.reset_index()
            m1_feed = model1_feedback.reset_index()
            m2_feed = model2_feedback.reset_index()
        
            ######################
            # model1 interaction
            ######################
            
            ax = fig.add_subplot(len(sigmas),2,counter)
            counter = counter+1
            ax.axhline(0, lw=1, alpha=1, color = 'k') # Add horizontal line at t=0
            
            # make equal size bins where correct==False 
            # average coherence and confidence in each bin
            valuelist = [False]
            F = m1_dec[m1_dec.correct.isin(valuelist)] # ev_levels that have errors
            valueList = np.array(F['ev_levels'])
            T =  m1_dec[m1_dec['correct']] # only true values
            # get only those ev_levels that are in m1_dec_F
            T = T[T.ev_levels.isin(valueList)]
        
            F = F.reset_index() 
            T = T.reset_index() 
        
            # Error
            bins_F = pd.qcut(F['ev_levels'], nbins, labels=bin_labels, retbins=True) 
            F['bins'] = np.array(bins_F[0]) # tupel, get first element out
            F_binned = F.groupby(['bins'])['ev_levels', decision_dv].mean()
        
            # Correct
            bins_T = pd.qcut(T['ev_levels'], nbins, labels=bin_labels, retbins=True) 
            T['bins'] = np.array(bins_T[0]) # tupel, get first element out
            T_binned = T.groupby(['bins'])['ev_levels', decision_dv].mean()
        
            # save for interaction plot
            easy_error_dec = F_binned.iloc[-1,-1] # last level, confidence/pe
            hard_error_dec = F_binned.iloc[0,-1] # first level, confidence/pe
            easy_correct_dec = T_binned.iloc[-1,-1] # last level, confidence/pe
            hard_correct_dec = T_binned.iloc[0,-1] # first level, confidence/pe
            
            easy_error_dec = np.round(easy_error_dec,2)
            hard_error_dec = np.round(hard_error_dec,2)
            easy_correct_dec = np.round(easy_correct_dec,2)
            hard_correct_dec = np.round(hard_correct_dec,2)
            
            # make equal size bins where correct==False 
            # average coherence and confidence in each bin
            valuelist = [False]
            F = m1_feed[m1_feed.correct.isin(valuelist)] # ev_levels that have errors
            valueList = np.array(F['ev_levels'])
            T =  m1_feed[m1_feed['correct']] # only true values
            # get only those ev_levels that are in m1_dec_F
            T = T[T.ev_levels.isin(valueList)]
        
            F = F.reset_index() 
            T = T.reset_index() 
        
            # Error
            bins_F = pd.qcut(F['ev_levels'], nbins, labels=bin_labels, retbins=True) 
            F['bins'] = np.array(bins_F[0]) # tupel, get first element out
            F_binned = F.groupby(['bins'])['ev_levels', feedback_dv].mean()
        
            # Correct
            bins_T = pd.qcut(T['ev_levels'], nbins, labels=bin_labels, retbins=True) 
            T['bins'] = np.array(bins_T[0]) # tupel, get first element out
            T_binned = T.groupby(['bins'])['ev_levels', feedback_dv].mean()
        
            # save for interaction plot
            easy_error_feed = F_binned.iloc[-1,-1] # last level, confidence/pe
            hard_error_feed = F_binned.iloc[0,-1] # first level, confidence/pe
            easy_correct_feed = T_binned.iloc[-1,-1] # last level, confidence/pe
            hard_correct_feed = T_binned.iloc[0,-1] # first level, confidence/pe
        
            easy_error_feed = np.round(easy_error_feed,2)
            hard_error_feed = np.round(hard_error_feed,2)
            easy_correct_feed = np.round(easy_correct_feed,2)
            hard_correct_feed = np.round(hard_correct_feed,2)
        
            interaction_decision = (easy_error_dec - easy_correct_dec) - (hard_error_dec - hard_correct_dec)
            interaction_feed = (easy_error_feed - easy_correct_feed) - (hard_error_feed - hard_correct_feed)

            MEANS = [interaction_decision,interaction_feed]

            xticklabels = ['Decision','Feedback']

            for x,m in enumerate(MEANS):
                ax.plot(ind[x],MEANS[x], marker='o', color=colors[x], label=leg_label[x], alpha=alphas[x])

            # Figure parameters
            ax.set_xticks(ind)
            # ax.set_xlim(xlim)
            ax.set_ylim(inter)
            ax.set_xticklabels(xticklabels)
            # ax.legend(loc='best', fontsize=4)
            ax.legend([])
            ax.set_ylabel('Interaction term')
            ax.set_title('Belief State Model subj ' + str(s+1))
            ax.set_ylim([-0.5,0.5])
            ax.set_yticks([-0.4,0.4])
            ax.axhline(0, lw=1, alpha=1, color = 'k') # Add horizontal line at t=0

            #######################
            # model2 interaction
            #######################
            ax = fig.add_subplot(len(sigmas),2,counter)
            counter = counter+1
            ax.axhline(0, lw=1, alpha=1, color = 'k') # Add horizontal line at t=0
            
            # make equal size bins where correct==False 
            # average coherence and confidence in each bin
            valuelist = [False]
            F = m2_dec[m2_dec.correct.isin(valuelist)] # ev_levels that have errors
            valueList = np.array(F['ev_levels'])
            T =  m2_dec[m2_dec['correct']] # only true values
            # get only those ev_levels that are in m1_dec_F
            T = T[T.ev_levels.isin(valueList)]
        
            F = F.reset_index() 
            T = T.reset_index() 
        
            # Error
            bins_F = pd.qcut(F['ev_levels'], nbins, labels=bin_labels, retbins=True) 
            F['bins'] = np.array(bins_F[0]) # tupel, get first element out
            F_binned = F.groupby(['bins'])['ev_levels', decision_dv].mean()
        
            # Correct
            bins_T = pd.qcut(T['ev_levels'], nbins, labels=bin_labels, retbins=True) 
            T['bins'] = np.array(bins_T[0]) # tupel, get first element out
            T_binned = T.groupby(['bins'])['ev_levels', decision_dv].mean()
        
            # save for interaction plot
            easy_error_dec = F_binned.iloc[-1,-1] # last level, confidence/pe
            hard_error_dec = F_binned.iloc[0,-1] # first level, confidence/pe
            easy_correct_dec = T_binned.iloc[-1,-1] # last level, confidence/pe
            hard_correct_dec = T_binned.iloc[0,-1] # first level, confidence/pe
                
            easy_error_dec = np.round(easy_error_dec,2)
            hard_error_dec = np.round(hard_error_dec,2)
            easy_correct_dec = np.round(easy_correct_dec,2)
            hard_correct_dec = np.round(hard_correct_dec,2)
            
            # make equal size bins where correct==False 
            # average coherence and confidence in each bin
            valuelist = [False]
            F = m2_feed[m2_feed.correct.isin(valuelist)] # ev_levels that have errors
            valueList = np.array(F['ev_levels'])
            T =  m2_feed[m2_feed['correct']] # only true values
            # get only those ev_levels that are in m1_dec_F
            T = T[T.ev_levels.isin(valueList)]
        
            F = F.reset_index() 
            T = T.reset_index() 
        
            # Error
            bins_F = pd.qcut(F['ev_levels'], nbins, labels=bin_labels, retbins=True) 
            F['bins'] = np.array(bins_F[0]) # tupel, get first element out
            F_binned = F.groupby(['bins'])['ev_levels', feedback_dv].mean()
        
            # Correct
            bins_T = pd.qcut(T['ev_levels'], nbins, labels=bin_labels, retbins=True) 
            T['bins'] = np.array(bins_T[0]) # tupel, get first element out
            T_binned = T.groupby(['bins'])['ev_levels', feedback_dv].mean()
        
            # save for interaction plot
            easy_error_feed = F_binned.iloc[-1,-1] # last level, confidence/pe
            hard_error_feed = F_binned.iloc[0,-1] # first level, confidence/pe
            easy_correct_feed = T_binned.iloc[-1,-1] # last level, confidence/pe
            hard_correct_feed = T_binned.iloc[0,-1] # first level, confidence/pe
        
            easy_error_feed = np.round(easy_error_feed,2)
            hard_error_feed = np.round(hard_error_feed,2)
            easy_correct_feed = np.round(easy_correct_feed,2)
            hard_correct_feed = np.round(hard_correct_feed,2)
        
            interaction_decision = (easy_error_dec - easy_correct_dec) - (hard_error_dec - hard_correct_dec)
            interaction_feed = (easy_error_feed - easy_correct_feed) - (hard_error_feed - hard_correct_feed)

            MEANS = [interaction_decision,interaction_feed]

            xticklabels = ['Decision','Feedback']

            for x,m in enumerate(MEANS):
                ax.plot(ind[x],MEANS[x], marker='o', color=colors[x], label=leg_label[x], alpha=alphas[x])

            # Figure parameters
            ax.set_xticks(ind)
            # ax.set_xlim(xlim)
            ax.set_ylim(inter)
            ax.set_xticklabels(xticklabels)
            # ax.legend(loc='best', fontsize=4)
            ax.legend([])
            ax.set_ylabel('Interaction term')
            ax.set_title('Stimulus State Model subj ' + str(s+1))
            ax.set_ylim([-0.5,0.5])
            ax.set_yticks([-0.4,0.4])
            
        sns.despine(offset=10, trim=True)
        plt.tight_layout()
        fig.savefig(os.path.join(self.figure_folder, 'ScientificReports','model_subjects',IV,'model_predictions_subjects_{}.pdf'.format(IV)))
        print('success: plot_sdt_models_subject_predictions')
    
    def plot_sdt_models_fits_coherence(self, controlITI):
        # fits the subject-specific models to the pupil data
        # four levels (Pearson correlation)
        # correlation coefficents at group level tested with permutation test
        # for Belief State model (model1) and Stimulus State model (model2)
        
        IV = 'coh_direction'
        mdv = ['uncertainty','pe_inv'] # dvs of interest from model, get average per ev_level
        # resp_locked baseline wrt choice
        pdv = self.pupil_dvs_PRE # locked to feedback in pre-interval
        
        # single subject noise estimates
        sigmas = pd.read_csv(os.path.join(self.figure_folder, 'ScientificReports','model_subjects',IV,'sigmas_subjects_{}.csv'.format(IV)))
        sigmas = np.array(sigmas.iloc[:,1]) # get 2nd column
        
        # load pupil data
        sdata = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_subjects.csv'))
        sdata.drop(['Unnamed: 0'], axis=1, inplace=True)
                
        save_model_r = []
        save_model_interaction_all = [] # 4 x subjects x model1+stim, model1+feed, model2+stim, model2+feed
        save_pupil_interaction_all = []
        for m in ['model1', 'model2']:
            
            for t,time_locked in enumerate(self.time_locked):
                # for each model, interval plot the Spearman correlations
                figS = plt.figure(figsize=(10,10))
                # color = ['blue','purple']
                color = ['grey','grey']
                # loop over subjects
                save_interval_r = []
                save_model_interaction = []
                save_pupil_interaction = []
                
                if controlITI: 
                    if time_locked == 'feed_locked': # long ITIs only
                        D = sdata[sdata['long_ITI']]
                    else: # long ISIs only decision locked
                        D = sdata[sdata['long_isi']]
                    D.reset_index(inplace=True)
                    D.drop(['index'],axis=1,inplace=True)
                else:
                    D = deepcopy(sdata)

                for s,subj in enumerate(sigmas):
                    mdata = [] # clear variable
                    
                    mdata = pd.read_csv(os.path.join(self.figure_folder, 'ScientificReports','model_subjects',IV,'{}_subj{}_{}.csv'.format(m,s,IV)))
                    mdata.drop(['Unnamed: 0'], axis=1, inplace=True)
                    
                    d = D[D['subj_idx']==s]
                    d.reset_index(inplace=True)
                    d.drop(['index'], axis=1, inplace=True)

                    coh_fits = np.round(d['coherence'],2) # coherence levels presented to this subject
                    d['coh_fits'] = coh_fits

                    # get model estimations for coherence levels of this subject
                    this_coh_model = mdata.loc[mdata['ev_levels'].isin(np.unique(coh_fits))]
                    model_dvs = this_coh_model.groupby(['correct','ev_levels'])[mdv[t]].mean()
                    model_dvs = pd.DataFrame(model_dvs)
                    model_dvs.reset_index(inplace=True)
                                        
                    # get pupil scalars for coherence levels of this subject
                    this_coh_pupil = d.loc[d['coh_fits'].isin(np.unique(coh_fits))]
                    pupil_dvs = this_coh_pupil.groupby(['easy','correct','coh_fits'])[pdv[t]].mean()
                    pupil_dvs = pd.DataFrame(pupil_dvs)
                    pupil_dvs.reset_index(inplace=True)
                    
                    # for the models, have to get the specific coherence values presented for hard, easy
                    model_conditions = [] # hard+error, hard+correct, easy+error, easy+correct
                    for diff in [0,1]:
                        coh_diff = pupil_dvs[pupil_dvs['easy']==diff]['coh_fits'] # coh levels for easy/hard                             
                        c = model_dvs.loc[model_dvs['ev_levels'].isin(np.array(coh_diff))] # get model params for these coh levels
                        c_grouped = c.groupby(['correct'])[mdv[t]].mean() # group model params by correct/error
                        model_conditions.append(np.array(c_grouped))
                    model_conditions = np.concatenate(model_conditions)    
                    
                    # for the pupil just group by easy,correct
                    pupil_conditions = this_coh_pupil.groupby(['easy','correct'])[pdv[t]].mean()
                    pupil_conditions = np.array(pupil_conditions) # hard+error, hard+correct, easy+error, easy+correct
                                        
                    y = pupil_conditions
                    x = model_conditions
                    
                    labels = ['Hard Error', 'Hard Correct', 'Easy Error', 'Easy Correct']
                    
                    coeff,pval = sp.stats.pearsonr(x, y) 
                    # print('subj '+ str(s))
                    # print('Rank corr. coeff= '+ str(coeff) + ' p-val= ' + str(pval))
                    # save rhos for this interval
                    save_interval_r.append(coeff)
                    # computer interaction term in order defined in Fig2
                    # pupil_conditions = hard+error, hard+correct, easy+error, easy+correct
                    # same for both intervals: (easy+error - easy+correct) - (hard+error - hard+correct)
                    save_pupil_interaction.append( (pupil_conditions[2]-pupil_conditions[3])-(pupil_conditions[0]-pupil_conditions[1]) )
                    save_model_interaction.append( (model_conditions[2]-model_conditions[3])-(model_conditions[0]-model_conditions[1]) )
                                        
                    ## generate correlation plots for correlations
                    axS = figS.add_subplot(4,4,s+1)
                    axS.set_title(m + ' '+ time_locked +' subj '+ str(s) + '\nr=' + str(np.round(coeff,2)) + ' p=' + str(np.round(pval,3)) )
                    
                    a=[1.0,0.75,0.5,0.25]
                    for c,x2 in enumerate(x):
                        axS.scatter(x[c],y[c],s=200, color='black', alpha=a[c], label=labels[c]) 
                        # axS.plot(x,(coeff*np.array(x))+np.mean(y), color='red')
                    
                    r = np.polyfit(x, y, 1) # linear , [slope, intercept]
                    axS.plot(x, r[0]*np.array(x)+r[1], 'r-', label='linear fit')
                    
                    axS.set_xlabel('model '+ mdv[t]) # model dvs.0
                    axS.set_ylabel(pdv[t]) # pupil dvs
                    axS.legend(loc='best',fontsize=4)
                    
                # save plots for each model for each interval
                plt.tight_layout()
                figS.savefig(os.path.join(self.figure_folder, 'ScientificReports', 'Model_fits_{}_{}_{}_controlITI{}_{}_Corr.pdf'.format(pdv[0],m,time_locked,controlITI,IV)))
                    
                # save rhos for this model
                save_model_r.append(save_interval_r) # model1 dec, model1 feed, model2 dec, model2 feed
                save_pupil_interaction_all.append(save_pupil_interaction)
                save_model_interaction_all.append(save_model_interaction)
                
        ### SAVE INTERACTION TERMS FOR plot_sdt_model_corrs INDIVIDUAL DIFFERENCES ###
        save_pupil_interaction_all = pd.DataFrame(save_pupil_interaction_all) # model1 dec, model1 feed, model2 dec, model2 feed
        save_model_interaction_all = pd.DataFrame(save_model_interaction_all)
        save_pupil_interaction_all.to_csv(os.path.join(self.figure_folder, 'ScientificReports', 'Model_fits_{}_controlITI{}_interaction.csv'.format(pdv[0],controlITI,IV))) # which dec pupil?
        save_model_interaction_all.to_csv(os.path.join(self.figure_folder, 'ScientificReports', 'Model_fits_model_interaction_{}.csv'.format(IV)))
        
        ### STATS AND PLOTTING ###
        print('sigmas = [' + str(np.round(min(sigmas),2)) + ',' + str(np.round(max(sigmas),2)) + ']' )
        
        fig = plt.figure(figsize=(2,2))
        ax = fig.add_subplot(111)
        ax.axhline(0, lw=1, alpha=1, color = 'k') # Add horizontal line at t=0
        # for interaction plots
        ind = [0.3,0.35,0.5,0.55]
        xlim = [0.275,0.575]
        bar_width = 0.05

        xticklabels = ['Belief State (Pre)','Stimulus State (Pre)','Belief State (Post)','Stimulus State (Post)']
        colors = ['blue','blue','purple','purple']
        alphas = [1,0.8,1,0.8]
        
        # order save_model_r = model1 dec, model1 feed, model2 dec, model2 feed
        # want model1 dec, model2 dec, model1 feed, model2 feed
        reorder_m = [save_model_r[0],save_model_r[2],save_model_r[1],save_model_r[3]]
        # test model1dec vs. model2dec
        # test model1feed vs. model2feed
        
        for r,rhos in enumerate(range(len(reorder_m))): # model1 dec, model1 feed, model2 dec, model2 feed
            # FISCHER TRANSFORM r coefficients
            reorder_m[r] = ocf.fischer_transform(np.array(reorder_m[r]))
            
            MEAN = np.mean(reorder_m[r])
            STE = np.std(reorder_m[r]) / np.sqrt(len(reorder_m[r]))
            # plot
            ax.bar(ind[r], MEAN, width=bar_width, yerr=STE, color=colors[r], alpha=alphas[r])
            # plot subject points
            # for i in range(len(save_model_r[r])):
            
            P = ocf.exact_mc_perm_test(np.array(reorder_m[r]), np.repeat(0,len(reorder_m[r]))) # significantly different from 0?
            
            # corrected for multiple comparisons
            survive, adjustedp = mne.stats.fdr_correction(P, alpha=0.05, method='indep') 
            P = adjustedp
            
            locstar = MEAN + 0.2 # put star a bit above bar
            if P < 0.001:
                ax.text(ind[r]-0.00, locstar, '***', fontsize=6)
            elif P < 0.01:
                ax.text(ind[r]-0.00, locstar, '**', fontsize=6)
            elif P < 0.05:
                ax.text(ind[r]-0.00, locstar, '*', fontsize=6)
        
        # MODEL COMPARISONS
        # test model1dec vs. model2dec
        # test model1feed vs. model2feed
        PRE = np.array(reorder_m[0]) - np.array(reorder_m[1])
        P1 = ocf.exact_mc_perm_test(PRE, np.repeat(0,len(PRE)))

        POST = np.array(reorder_m[2]) - np.array(reorder_m[3])
        P2 = ocf.exact_mc_perm_test(POST, np.repeat(0,len(POST)))
        
        for i,P in enumerate([P1,P2]):
            pind = [0,2]
            locstar = MEAN + 0.22 # put star a bit above bar
            if P < 0.001:
                ax.text(ind[pind[i]]+(bar_width/2), locstar, '***', fontsize=6, color='red')
            elif P < 0.01:
                ax.text(ind[pind[i]]+(bar_width/2), locstar, '**', fontsize=6, color='red')
            elif P < 0.05:
                ax.text(ind[pind[i]]+(bar_width/2), locstar, '*', fontsize=6, color='red')
                
            print('MODEL DIFFERENCES')
            print('interval {}'.format(i))
            print('p = {}'.format(P))
            
        # set figure parameters
        ax.set_ylabel('Pearson r')
        # ax.set_ylim(0,0.25)
        ax.set_xticks(ind)
        
        sns.despine(offset=10, trim=True)
        ax.set_xticklabels(xticklabels,rotation=90,fontsize=4) # has to go after despine
        
        plt.tight_layout()
        fig.savefig(os.path.join(self.figure_folder, 'ScientificReports', 'Model_fits_{}_controlITI{}_{}.pdf'.format(pdv[0],controlITI,IV)))              
        print('success: plot_sdt_models_fits_coherence')
        
        
    def urai_feedback_pupil_median(self,):
        # Takes the single subject CSV files from Urai et al (code in Matlab)
        # Creates one new dataframe with columns for subject and condition
        # Plots the feedback locked scaling with uncertainty
        # {'error weak', 'error medium', 'error strong', 'correct weak', 'correct medium', 'correct strong'};
        
        # UNCERTAINTY
        # single subjects df to one big df, only need to make this once unless the data changes from urai
        if not os.path.isfile(os.path.join(self.dataframe_folder,'pupil','subjects','urai_data','event_related_feedback_urai_median.csv')):
            all_data = pd.DataFrame() # put all subjects here
            for subj in range(27):
                subj = subj+1
                this_subj = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','subjects','urai_data','subj{}_median.csv'.format(subj)),header=None)
                this_subj['subj_no'] = np.repeat(subj,4)
                this_subj['cond_no'] = np.array(range(4))+1
                all_data = pd.concat([all_data,this_subj], axis=0)
            all_data.to_csv(os.path.join(self.dataframe_folder,'pupil','subjects','urai_data','event_related_feedback_urai_median.csv'))
        else:
            all_data = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','subjects','urai_data','event_related_feedback_urai_median.csv'))
            all_data.drop(['Unnamed: 0'], axis=1, inplace=True)
        
        # ACCURACY    
        # single subjects df to one big df, only need to make this once unless the data changes from urai
        if not os.path.isfile(os.path.join(self.dataframe_folder,'pupil','subjects','urai_data','event_related_feedback_urai_accuracy.csv')):
            all_data_acc = pd.DataFrame() # put all subjects here
            for subj in range(27):
                subj = subj+1
                this_subj = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','subjects','urai_data','subj{}_accuracy.csv'.format(subj)),header=None)
                this_subj['subj_no'] = np.repeat(subj,2)
                this_subj['cond_no'] = np.array(range(2))+1
                all_data_acc = pd.concat([all_data_acc,this_subj], axis=0)
            all_data_acc.to_csv(os.path.join(self.dataframe_folder,'pupil','subjects','urai_data','event_related_feedback_urai_accuracy.csv'))
        else:
            all_data_acc = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','subjects','urai_data','event_related_feedback_urai_accuracy.csv'))
            all_data_acc.drop(['Unnamed: 0'], axis=1, inplace=True)
            
        # drop first 0.5 seconds from events so we have (-0.5,2) seconds
        nts = range(50)
        tcols = [str(n) for n in nts]
        all_data.drop(tcols, axis=1, inplace=True)
        all_data_acc.drop(tcols, axis=1, inplace=True)
    
        # Plot conditions
        k = 251 # length of kernel
    
        # for task evoked responses
        step_lim = [-0.5,2]
        xlim = [-0.5,2]
        xlabel = 'Time from feedback (s)'
        step = pd.Series(np.linspace(step_lim[0], step_lim[1], k), name=xlabel)
        # Step size for x axis:
        xlim_indices = np.array(step >= xlim[0]) * np.array(step <= xlim[1])
    
        # whole figure
        fig = plt.figure(figsize=(6,2))        
    
        #######################
        # A correct vs. error responses 
        #######################
        ax = fig.add_subplot(131)
        ax.axhline(0, lw=1, alpha=1, color = 'black') # Add horizontal line at t=0        
        ax.axvline(0, lw=1, alpha=1, color = 'black') # Add vertical line at t=0
    
        # need to average conditions within subjects
        ncols = range(50,301)
        cols = [str(n) for n in ncols]
            
        # errors are conditions 1
        error_subj = all_data_acc[ (all_data_acc['cond_no']==1)]
        error = error_subj.groupby(['subj_no'])[cols].mean()    # average for each subject
        error.reset_index(inplace=True)
        error.drop(['subj_no'], axis=1, inplace=True)
        error = np.array(error)
    
        # correct are conditions 2
        correct_subj = all_data_acc[ (all_data_acc['cond_no']==2)]
        # average for each subject
        correct = correct_subj.groupby(['subj_no'])[cols].mean()    # average for each subject
        correct.reset_index(inplace=True)
        correct.drop(['subj_no'], axis=1, inplace=True)
        correct = np.array(correct)
            
        # plot
        sns.tsplot(error, time=step[xlim_indices], condition='Error', color='red', alpha=1, lw=1, ls='-', ax=ax)
        sns.tsplot(correct, time=step[xlim_indices], condition='Correct', color='green', alpha=1, lw=1, ls='-', ax=ax)
    
        # add stats
        DIFF = error-correct
        nperms = 10000
        corr = True
        ocf.cluster_sig_bar_1samp(array=DIFF, x=np.array(step[xlim_indices]), yloc=3, color='black', ax=ax, threshold=0.05, nrand=nperms, cluster_correct=corr)
    
        # subplot parameters
        ax.set_yticks([-0.2,0,0.2,0.4])
        ax.set_xticks([0,1,2])
        ax.set_xlabel('Time from feedback (s)')
        ax.set_ylabel('Pupil response\n(Z-score)')
        ax.legend(loc='best',fontsize=4)
            
        #######################
        # B scaling with uncertainty
        #######################
        ax = fig.add_subplot(132)
        ax.axhline(0, lw=1, alpha=1, color = 'black') # Add horizontal line at t=0        
        ax.axvline(0, lw=1, alpha=1, color = 'black') # Add vertical line at t=0   
            
        # {'error weak', 'error strong', 'correct weak', 'correct strong'};
        error_weak = all_data[all_data['cond_no']==1]
        error_weak.reset_index(inplace=True)
        error_weak.drop(['index','subj_no','cond_no'], axis=1, inplace=True)
        error_weak = np.array(error_weak)
    
        error_strong = all_data[all_data['cond_no']==2]
        error_strong.reset_index(inplace=True)
        error_strong.drop(['index','subj_no','cond_no'], axis=1, inplace=True)
        error_strong = np.array(error_strong)
    
        correct_weak = all_data[all_data['cond_no']==3]
        correct_weak.reset_index(inplace=True)
        correct_weak.drop(['index','subj_no','cond_no'], axis=1, inplace=True)
        correct_weak = np.array(correct_weak)
    
        correct_strong = all_data[all_data['cond_no']==4]
        correct_strong.reset_index(inplace=True)
        correct_strong.drop(['index','subj_no','cond_no'], axis=1, inplace=True)
        correct_strong = np.array(correct_strong)

        # plot
        sns.tsplot(error_weak, time=step[xlim_indices], condition='Error Hard', color='red', alpha=0.3, lw=1, ls='-', ax=ax)
        sns.tsplot(error_strong, time=step[xlim_indices], condition='Error Easy', color='red', alpha=1, lw=1, ls='-', ax=ax)
        sns.tsplot(correct_weak, time=step[xlim_indices], condition='Correct Hard', color='green', alpha=0.3, lw=1, ls='-', ax=ax)
        sns.tsplot(correct_strong, time=step[xlim_indices], condition='Correct Easy', color='green', alpha=1, lw=1, ls='-', ax=ax)
    
        # subplot parameters
        ax.set_yticks([-0.2,0,0.2,0.4])
        ax.set_xticks([0,1,2])
        ax.set_xlabel('Time from feedback (s)')
        ax.set_ylabel('Pupil response\n(Z-score)')
        ax.legend(loc='best',fontsize=4)
    
        ###########################
        # C INTERACTION TERM SUBPLOT
        ###########################
        ax = fig.add_subplot(133)
        ax.axhline(0, lw=1, alpha=1, color = 'black') # Add horizontal line at t=0        
        ax.axvline(0, lw=1, alpha=1, color = 'black') # Add vertical line at t=0
        # compute "difference of differences"
        # EasyError-EasyCorrect) > HardError-HardCorrect)
        d1 = error_strong-correct_strong # easyerror-easycorrect)
        d2 = error_weak-correct_weak # harderror-hardcorrect
        DIFF = d1-d2 # iteraction term    
    
        # plot
        sns.tsplot(DIFF, time=step[xlim_indices], condition='Feedback', color='purple', alpha=1, lw=1, ls='-', ax=ax)  
    
        # add stats
        nperms = 10000
        corr = True
        ocf.cluster_sig_bar_1samp(array=DIFF, x=np.array(step[xlim_indices]), yloc=3, color='purple', ax=ax, threshold=0.05, nrand=nperms, cluster_correct=corr)
     
        # subplot parameters
        ax.set_yticks([-0.075,0,0.075,0.15])
        ax.set_xticks([0,1,2])
        ax.set_xlabel('Time from stimulus onset (s)')
        ax.set_ylabel('Interaction term\n(Z-score)')
        ax.legend(loc='best',fontsize=4) 
     
        sns.despine(offset=10, trim=True)
        plt.tight_layout()
        fig.savefig(os.path.join(self.figure_folder, 'ScientificReports', 'Urai_feedback_median.pdf'.format()))        
        print('success: urai_feedback_pupil_median')
    
    def RT_pupil_correlation(self, controlITI):
        # plots the correlation between the RT and pupil (trial-wise and within conditions)
        
        # make 10 bins of RT per subject (for plotting only)
        nbins = 10
        bin_labels = range(1,nbins+1)
        
        sdata = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_subjects.csv'))
        sdata['error'] = np.array(sdata['correct'] == 0, dtype=bool)
        sdata['hard'] = np.array(sdata['easy'] == 0, dtype=bool)
        sdata['correct1'] = np.array(sdata['correct'] == 1, dtype=bool) # save as boolean
        sdata['easy1'] = np.array(sdata['easy'] == 1, dtype=bool)

        ####################
        # Across all trials
        for pupil_dv in self.pupil_dvs_PRE:
            
            if controlITI: 
                if 'feed' in pupil_dv: # long ITIs only
                    D = sdata[sdata['long_ITI']]
                else: # long ISIs only decision locked
                    D = sdata[sdata['long_isi']]
                D.reset_index(inplace=True)
                D.drop(['index'],axis=1,inplace=True)
            else:
                D = deepcopy(sdata) 
        
            ## SINGLE FIGURE ##
            fig = plt.figure(figsize=(4,2))
            
            # loop over subjects
            save_corr_trialwise = []
            save_bins = []
            for subj in np.unique(D['subj_idx']):
                this_data = D[D['subj_idx']==subj]
                this_rt = np.array(this_data['rt'])
                this_pupil = np.array(this_data[pupil_dv])
                # single-trial correlation for this subject
                r, p = sp.stats.pearsonr(this_rt, this_pupil)
                save_corr_trialwise.append(r)
                
                bins = pd.qcut(this_rt, nbins, labels=bin_labels, retbins=True) # pd.qcut is better for equal sized bins!    
                save_bins.append(np.array(bins[0]))
                
            save_corr_trialwise = np.array(save_corr_trialwise)
            mean_r_trialwise = np.mean(save_corr_trialwise) # mean correlation coefficient
            ste_r_trialwise = np.true_divide(np.std(save_corr_trialwise), np.sqrt(len(self.subjects)))
            p = ocf.exact_mc_perm_test(save_corr_trialwise, np.repeat(0,len(self.subjects))) # significantly different from 0?
            
            print('')
            print('** Trialwise correlations')
            print('DV: ' + pupil_dv)
            print('Mean r: ' + str(mean_r_trialwise))
            print('p-value perm test: ' + str(p))
            
            D['bins_RT'] = np.concatenate(save_bins) # flatten
        
            grouped = D.groupby(['subj_idx', 'bins_RT'])[pupil_dv].agg(['mean','std']) # get average, std of each bin per subject
            # get mean and SEM of each DV-bin across subjects
            across_grouped = grouped.groupby(['bins_RT'])['mean'].agg(['mean','std'])
            across_grouped['sem'] = np.divide(across_grouped['std'],np.sqrt(len(self.subjects)))
                                
            # Plot scatter of bins
            ax = fig.add_subplot(121) # trialwise

            # scatter plot
            x = np.array(across_grouped.index)
            y = across_grouped['mean']
            e = across_grouped['sem']
            ax.errorbar(x, y, yerr=e, fmt='o', capsize=0, ls='none', color='grey', alpha=0.5, elinewidth=0.6, markersize=2, markeredgecolor='white')
            ax.plot(x, y, '.')

            ##########
            # STATS
            coeff,pval = sp.stats.pearsonr(x, y)  # 0 coeff, 1 pvalue
            # # fit regression line
            coeffs1 = np.polyfit(x, y, 1) # linear , [slope, intercept]
            coeffs2 = np.polyfit(x, y, 2) # quadratic , a2x2 + a1x2 + a0x0
            poly2 = np.poly1d(coeffs2)
            ax.plot(x, coeffs1[0]*x+coeffs1[1], '-')
            ax.set_title('r = ' + str(np.round(mean_r_trialwise,2)) +'\n p = ' + str(np.round(p,3)))  # TRIALWISE STATS

            ax.set_xlabel('RT bin')
            ax.set_ylabel(pupil_dv+ '\n (psc)')
            ax.set_xticks([x[0],x[-1]])
            ax.set_xticklabels(['low','high'])
                    
            ##########################################
            # Within conditions Accuracy x Difficulty
            ##########################################
            conditions = np.ones(D.shape[0])
            # NOTE ORDER DIFFERENT HERE THAN 'uncertainty' SCALING
            conditions[np.array(D['easy1']*D['correct1'])] = 4 # easy & correct
            conditions[np.array(D['hard']*D['correct1'])] = 3 # hard & correct
            conditions[np.array(D['hard']*D['error'])] = 2 # hard & error
            conditions[np.array(D['easy1']*D['error'])] = 1 # easy & error
            D['conditions'] = np.array(conditions, dtype=int)
            
            group_cond_mean = [] # save group mean for each condition
            group_cond_ste = []
            group_cond_p = []
            
            for c in range(4):
                cdata = D[D['conditions']==c+1] # get data only from current condition
                save_corr_cond = []
                
                for subj in np.unique(cdata['subj_idx']): 
                    this_data = cdata[cdata['subj_idx']==subj]
                    this_rt = np.array(this_data['rt'])
                    this_pupil = np.array(this_data[pupil_dv])
            
                    r, p = sp.stats.pearsonr(this_rt, this_pupil)
                    save_corr_cond.append(r)
                    
                save_corr_cond = np.array(save_corr_cond)
                mean_r_cond = np.mean(save_corr_cond) # mean correlation coefficient
                ste_r_cond = np.true_divide(np.std(save_corr_cond), np.sqrt(len(self.subjects)))
                p = ocf.exact_mc_perm_test(save_corr_cond, np.repeat(0,len(self.subjects))) # significantly different from 0?
                
                group_cond_mean.append(mean_r_cond)
                group_cond_ste.append(ste_r_cond)
                group_cond_p.append(p)
        
                print('')
                print('** Within condition correlations:')
                print('DV: ' + pupil_dv)
                print('Condition: ' + str(c+1))
                print('Mean r: ' + str(mean_r_cond))
                print('p-value perm test: ' + str(p))
                
            # Plot 4 conditions as bar graphs
            ax = fig.add_subplot(122)

            ind = [0.3,0.5,0.7,0.9]
            xlim = [0.275,0.575,0.775,0.975]
            bar_width = 0.1

            xticklabels = ['Easy Error','Hard Error','Hard Correct','Easy Correct']

            MEAN = np.array(group_cond_mean)
            STE = np.array(group_cond_ste)
            P = np.array(group_cond_p)

            # corrected for multiple comparisons
            survive, adjustedp = mne.stats.fdr_correction(P, alpha=0.05, method='indep')
            P = adjustedp

            # plot
            ax.bar(ind, MEAN, width=bar_width, yerr=STE, color='grey', alpha=1)

            # add significance stars
            for i in range(4):
                locstar = MEAN[i] + 0.04 # put star a bit above bar
                if P[i] < 0.001:
                    ax.text(ind[i]-0.05, locstar, '***', fontsize=6)
                elif P[i] < 0.01:
                    ax.text(ind[i]-0.03, locstar, '**', fontsize=6)
                elif P[i] < 0.05:
                    ax.text(ind[i]-0.01, locstar, '*', fontsize=6)

            # set figure parameters
            ax.set_ylabel('rs')
            ax.set_xticks(ind)

            sns.despine(offset=10, trim=True)
            ax.set_xticklabels(xticklabels,rotation=45) # has to go after despine
            
            plt.tight_layout()
            fig.savefig(os.path.join(self.figure_folder, 'ScientificReports', '{}_controlITI{}_RT_correlations.pdf'.format(pupil_dv, controlITI)))
        
        print('success: RT_pupil_correlation')
        

    def pupil_results_motion_energy(self, IV, controlITI, subjects, regressRT):
        # reproduce Fig3 e,f (scalar interaction) with motion energy or coherence (bins) on x-axis
        # 1 x 2 figure
        
        nbins = 4 # if too many, not enough errors in all bins
        bin_labels = range(1,nbins+1)
        
        ylim = [(4,9.5),(-2,1)]
        
        if IV == 'ME':
            IV = 'abs_motion_energy'
            xlabel = 'Motion energy bin'
        else:
            IV = 'coherence'
            xlabel = 'Coherence bin'
        
        #######################
        # E,F scalars decision phase
        #######################
        if regressRT:
            dvs = self.pupil_dvs_PRE_rRT
            postFixRT = '_rRT'
        else: 
            dvs = self.pupil_dvs_PRE
            postFixRT = ''
            
        dv_title = ['Pre-feedback interval','Post-feedback interval']
        ylabel = 'Pupil response (psc))'     
        
        sdata = pd.read_csv(os.path.join(self.dataframe_folder,'pupil', 'subjects', 'pupil_subjects.csv'))
        sdata.drop(['Unnamed: 0'],axis=1,inplace=True)     
        
        fig = plt.figure(figsize=(4,2)) 
        
        for n,dv in enumerate(dvs):
                
            ax = fig.add_subplot(1,2,n+1)
            # ax.axhline(0, lw=1, alpha=1, color = 'k') # Add horizontal line at t=0
            
            if controlITI: 
                if 'feed' in dv: # long ITIs only
                    good_pupil_data = sdata[sdata['long_ITI']]
                else: # long ISIs only decision locked
                    good_pupil_data = sdata[sdata['long_isi']]
                good_pupil_data.reset_index(inplace=True)
                good_pupil_data.drop(['index'],axis=1,inplace=True)
            else:
                good_pupil_data = deepcopy(sdata)
                
            # motion energy bins
            save_bins = []
            for s,subj in enumerate(subjects):
                this_data = good_pupil_data[good_pupil_data['subj_idx']==s]
                if IV == 'abs_motion_energy':
                    bins = pd.qcut(this_data[IV], nbins, labels=bin_labels, retbins=True, duplicates='drop')
                else:
                    bins = pd.cut(this_data[IV], nbins, labels=bin_labels, retbins=True) # pd.qcut is better for equal sized bins!
                save_bins.append(np.array(bins[0]))                    
            good_pupil_data['bins_IV'] = np.concatenate(save_bins) # flatten
            
            ###################
            ## Plotting PUPIL binned by motion energy ##
            cdata = good_pupil_data.groupby(['subj_idx','correct','bins_IV'])[dv].agg(['mean']) # get average, std of each bin per subject
            cdata.reset_index(inplace=True)                 
            
            # number of subjects
            ss = len(np.unique(cdata['subj_idx']))
            # Compute means, sems for all conditions of interest
            MEANS = pd.DataFrame(cdata.groupby(['bins_IV','correct'])['mean'].mean().reset_index()) # name of dv not in grouped dataframe, just 'mean'
            stds = cdata.groupby(['bins_IV','correct'])['mean'].std()
            stds = np.array(stds)
            SEMS = stds/np.sqrt(ss)

            ### LINE GRAPH ### 4 conditions, can't use func
            ind = [0.2,0.3,0.4,0.5]
            xlim = [0.175,0.575]
            colors = ['red','green']
            alphas = [1,1]
            leg_label = ['Error','Correct']
            # Plot by looping through 'keys' in grouped dataframe
            x=0
            for key,grp in MEANS.groupby('correct'): # ls, have to flip around
                # print(key)
                # print(grp)
                ax.errorbar(ind,grp['mean'],yerr=SEMS[x], label=leg_label[x], color=colors[x], alpha=alphas[x])
                x=x+1

            # Figure parameters
            ax.set_xticks([ind[0],ind[-1]])
            ax.set_xticklabels(['Low', 'High'])
            ax.legend(loc='best', fontsize=4)
            ax.set_ylabel(ylabel)
            ax.set_xlabel(xlabel)
            # ax.set_ylim(ylim[n])
            ax.set_title(dv_title[n])    
        
            sns.despine(ax=ax, offset=self.tick_offset, trim=True)
            plt.tight_layout()
            fig.savefig(os.path.join(self.figure_folder, 'ScientificReports', 'pupil_results_controlITI{}_{}{}.pdf'.format(controlITI,IV,postFixRT))) 
            
            ### save coherence values per subject
            subj_coh = good_pupil_data.groupby(['subj_idx','easy','coherence']).count()
            subj_coh.to_csv(os.path.join(self.figure_folder, 'ScientificReports','subjects_difficultyXcoherence_controlITI{}.csv'.format(controlITI)))
            ### 
            
        ############################################################
        ## sanity check: difference in motion energy for conditions of interest?
        # sanity = good_pupil_data.groupby(['subj_idx','easy','correct'])[IV].agg(['mean','std']) # get average, std of each bin per subject
        # sanity.reset_index(inplace=True)
        
        # actual magnitude of the difference, as % normalized by the mean motion energy for each level
        save_norm = []
        for s,subj in enumerate(subjects):
            this_data = good_pupil_data[good_pupil_data['subj_idx']==s]
            mdata = np.array(this_data['abs_motion_energy'])
            m = np.mean(mdata)
            normed = (100.0 * (mdata / m)) - 100.0
            save_norm.append(normed)                    
        good_pupil_data['me_norm'] = np.concatenate(save_norm) # flatten
        
        IV = 'me_norm'
        sanity = good_pupil_data.groupby(['subj_idx','easy','correct'])[IV].agg(['mean','std']) # get average, std of each bin per subject
        sanity.reset_index(inplace=True)

        daov = pt.DataFrame(sanity)
        # repeated measures anova
        aov = daov.anova('mean', sub='subj_idx', wfactors=['easy','correct'])
        # print(aov)
        save_output = []
        # Get important stats out
        terms = aov.keys() # returns a list of factors with interaction term
        for k in terms:
            r = ocf.extract_for_apa(k, aov, values = ['F', 'mse', 'eta', 'p']) # returns a dictionary object
            save_output.append(r)
        dout = pd.DataFrame(save_output)
        # csv: 1st row = 1st factor, 2nd row = factor, 3rd row = interaction
        dout.to_csv(os.path.join(self.figure_folder, 'ScientificReports','rm_anova_{}_{}_controlITI{}.csv'.format(IV, 'easy*correct', controlITI)))

        # save whole table in HTML format
        output = SimpleHTML.SimpleHTML('easy*correct')
        aov._within_html(output)
        output.write(os.path.join(self.figure_folder, 'ScientificReports','rm_anova_{}_{}_controlITI{}.html'.format(IV, 'easy*correct', controlITI)))

        # plot interaction figure: motion energy
        ss = len(np.unique(sanity['subj_idx']))
        # Compute means, sems for all conditions of interest
        MEANS = pd.DataFrame(sanity.groupby(['easy','correct'])['mean'].mean().reset_index()) # name of dv not in grouped dataframe, just 'mean'
        stds = sanity.groupby(['easy','correct'])['mean'].std()
        stds = np.array(stds)
        SEMS = stds/np.sqrt(ss)
        ### LINE GRAPH ###
        figS,axS = ocf.line_plot_anova(MEANS, SEMS, dv='mean', aov=dout, cond='easy*correct', ylabel='Motion energy (abs.)', fac=['easy','correct'])
        sns.despine(ax=axS, offset=self.tick_offset, trim=True)
        plt.tight_layout()
        figS.savefig(os.path.join(self.figure_folder, 'ScientificReports', 'abs_motion_energy_{}_controlITI{}.pdf'.format(IV,controlITI)))   
        
        dv = 'mean'
        ttests = sanity[['easy','correct']+[dv]]
        hard_error = ttests[(ttests['easy'] ==0) & (ttests['correct'] ==0)] # hard error
        hard_correct = ttests[(ttests['easy'] ==0) & (ttests['correct'] ==1)] # hard correct
        easy_error = ttests[(ttests['easy'] ==1) & (ttests['correct'] ==0)] # easy error
        easy_correct = ttests[(ttests['easy'] ==1) & (ttests['correct'] ==1)] # easy correct
    
        hard_error = np.array(hard_error[dv])
        hard_correct = np.array(hard_correct[dv])
        easy_error = np.array(easy_error[dv])
        easy_correct = np.array(easy_correct[dv])
        
        print('')
        print('2 sample perm tests')
        print('controlITI = ' + str(controlITI))
        print('hard_error vs. hard_correct')
        m,p = ocf.perm_2sample(hard_error, hard_correct)
        print('mean={}, std={}, pval={}'.format(m, np.std(hard_error-hard_correct), round(p,3)))
    
        print('')
        print('easy_error vs. easy_correct')
        m,p = ocf.perm_2sample(easy_error, easy_correct)
        print('mean={}, std={}, pval={}'.format(m, np.std(easy_error-easy_correct), round(p,3)))
    
        print('')
        print('hard_error vs. easy_error')
        m,p = ocf.perm_2sample(hard_error, easy_error)
        print('mean={}, std={}, pval={}'.format(m, np.std(hard_error-easy_error), round(p,3)))
    
        print('')
        print('hard_correct vs. easy_correct')
        m,p = ocf.perm_2sample(hard_correct, easy_correct)
        print('mean={}, std={}, pval={}'.format(m, np.std(hard_correct-easy_correct), round(p,3)))    
        
        print('')
        print('MAIN EFFECTS')
        print('hard vs. easy')
        hard = np.array(ttests[ttests['easy'] ==0][dv]) # hard
        easy = np.array(ttests[ttests['easy'] ==1][dv]) # easy
        m,p = ocf.perm_2sample(hard, easy)
        print('mean={}, std={}, pval={}'.format(m, np.std(hard-easy), round(p,3)))
        
        print('MAIN EFFECTS')
        print('error vs. correct')
        error = np.array(ttests[ttests['correct'] ==0][dv]) # error
        correct = np.array(ttests[ttests['correct'] ==1][dv]) # correct
        m,p = ocf.perm_2sample(error, correct)
        print('mean={}, std={}, pval={}'.format(m, np.std(error-correct), round(p,3)))
        
        print('success: pupil_results_motion_energy')

                
    def regress_pupil_motion_energy(self, controlITI, regressRT):
        ### RUN stats ###
        # linear regression on Error and Correct (separately)
        # can clean up hard coding here...
        
        dvs = self.pupil_dvs_PRE # RT in

        dec_locked = 'resp_locked'
        
        d = pd.read_csv(os.path.join(self.dataframe_folder,'pupil', 'subjects', 'pupil_subjects.csv'))
                
        for t,time_locked in enumerate([dec_locked]+['feed_locked']):
            
            dv = dvs[t] # which interval?
            save_betas_correct1 = []    # 'pupil ~ constant + abs(motion energy)'
            save_betas_error1 = []      
            
            save_betas_correct2 = []    # 'pupil ~ constant + abs(motion energy) + RT'
            save_betas_error2 = []
                        
            if controlITI: 
                if time_locked == 'feed_locked': # long ITIs only
                    D = d[d['long_ITI']]
                else: # long ISIs only decision locked
                    D = d[d['long_isi']]
                D.reset_index(inplace=True)
                D.drop(['index'],axis=1,inplace=True)
            else:
                D = deepcopy(d)
            
            
            for s,subj in enumerate(np.unique(D['subj_idx'])):
                ss = len(np.unique(D['subj_idx']))
                
                ################ MODEL: 'pupil ~ constant + abs(motion energy)'
                # ERROR
                this_subj_error = D[(D['subj_idx']==s) & (D['correct']==0)]
                Y = np.array(this_subj_error[dv]) # pupil
                ME = stats.zscore(np.abs(np.array(this_subj_error['motion_energy'])))
                X = np.column_stack((ME))
                betas = ocf.lin_regress_betas(Y, X)    # constant, ME, RT betas     
                save_betas_error1.append(betas[1]) # for ME, with RT orthogonalize
                # CORRECT
                this_subj_correct = D[(D['subj_idx']==s) & (D['correct']==1)]
                Y = np.array(this_subj_correct[dv]) # pupil
                ME = stats.zscore(np.abs(np.array(this_subj_correct['motion_energy'])))
                X = np.column_stack((ME))
                betas = ocf.lin_regress_betas(Y, X)    # constant, ME, RT betas     
                save_betas_correct1.append(betas[1]) # for ME, with RT orthogonalized
                ################
                                
                if regressRT:
                ################ MODEL: 'pupil ~ constant + abs(motion energy) + RT'
                    # ERROR
                    this_subj_error = D[(D['subj_idx']==s) & (D['correct']==0)]
                    Y = np.array(this_subj_error[dv]) # pupil
                    ME = stats.zscore(np.abs(np.array(this_subj_error['motion_energy'])))
                    RT = stats.zscore(np.log(np.array(this_subj_error['rt'])))
                    X = np.column_stack((ME,RT))
                    betas = ocf.lin_regress_betas(Y, np.transpose(X))    # constant, ME, RT betas
                    save_betas_error2.append(betas[1]) # for ME, with RT orthogonalized
                    # CORRECT
                    this_subj_correct = D[(D['subj_idx']==s) & (D['correct']==1)]
                    Y = np.array(this_subj_correct[dv]) # pupil
                    ME = stats.zscore(np.abs(np.array(this_subj_correct['motion_energy'])))
                    RT = stats.zscore(np.log(np.array(this_subj_correct['rt'])))
                    X = np.column_stack((ME,RT))
                    betas = ocf.lin_regress_betas(Y, np.transpose(X))    # constant, ME, RT betas
                    save_betas_correct2.append(betas[1]) # for ME, with RT orthogonalized
                ################
            
            print('')     
            print('controlITI = ' + str(controlITI))       
            # reg model 1
            print('pupil ~ constant + abs(motion energy)')
            save_betas_correct1 = np.array(save_betas_correct1)
            save_betas_error1 = np.array(save_betas_error1)
            DIFF = save_betas_error1 - save_betas_correct1 # interaction term
        
            print('SLOPE STATS')
            print('ERROR slope')
            print(time_locked)
            print(dv)
            print('Mean beta= ' + str(np.mean(save_betas_error1)))
            print('STD beta= ' + str(np.std(save_betas_error1)))
            p = ocf.exact_mc_perm_test(save_betas_error1, np.repeat(0,ss)) 
            print('pval= ' + str(p))
            print('')
            print('SLOPE STATS')
            print('CORRECT slope')
            print(time_locked)
            print(dv)
            print('Mean beta= ' + str(np.mean(save_betas_correct1)))
            print('STD beta= ' + str(np.std(save_betas_correct1)))
            p = ocf.exact_mc_perm_test(save_betas_correct1, np.repeat(0,ss)) 
            print('pval= ' + str(p))
            print('')
            
            print('INTERACTION TERM STATS')
            print(time_locked)
            print(dv)
            print('Mean beta= ' + str(np.mean(DIFF)))
            print('STD beta= ' + str(np.std(DIFF)))
            print('error-correct betas for ME')
            p = ocf.exact_mc_perm_test(DIFF, np.repeat(0,ss)) 
            print('pval= ' + str(p))
            print('')
            
            if regressRT:
                # reg model 2
                print('pupil ~ constant + abs(motion energy) + RT')
                save_betas_correct2 = np.array(save_betas_correct2)
                save_betas_error2 = np.array(save_betas_error2)
                DIFF = save_betas_error2 - save_betas_correct2 # interaction term
        
                print('SLOPE STATS')
                print('ERROR slope')
                print(time_locked)
                print(dv)
                print('Mean beta= ' + str(np.mean(save_betas_error2)))
                print('STD beta= ' + str(np.std(save_betas_error2)))
                p = ocf.exact_mc_perm_test(save_betas_error2, np.repeat(0,ss)) 
                print('pval= ' + str(p))
                print('')
                print('SLOPE STATS')
                print('CORRECT slope')
                print(time_locked)
                print(dv)
                print('Mean beta= ' + str(np.mean(save_betas_correct2)))
                print('STD beta= ' + str(np.std(save_betas_correct2)))
                p = ocf.exact_mc_perm_test(save_betas_correct2, np.repeat(0,ss)) 
                print('pval= ' + str(p))
                print('')
            
                print('INTERACTION TERM STATS')
                print(time_locked)
                print(dv)
                print('Mean beta= ' + str(np.mean(DIFF)))
                print('STD beta= ' + str(np.std(DIFF)))
                print('error-correct betas for ME')
                p = ocf.exact_mc_perm_test(DIFF, np.repeat(0,ss)) 
                print('pval= ' + str(p))
                print('')
        print('success: regress_pupil_motion_energy')    

        
    def pupil_event_related_betas(self, controlITI, regressRT):     
        # plots the difference in error-correct beta values for regresion of motion energy onto pupil 
        # m1 with RT in, m2 with RT also regressed out
        # subplot 1 original response, subplot 2 RT regressed out of resp_locked
        # NOTE: original resp_locked array with -5 seconds wrt choice, while stim & feed -2 s wrt event
        # First cut out the signals of interest, pad break, then plot
        
        fig = plt.figure(figsize=(3,2))    
        ax = fig.add_subplot(111)
        
        nperms = 10000
        corr = False
        
        dec_locked = 'resp_locked' # or 'stim_locked'
        dec_event = 'Choice'  # or 'Cue'
        dec_event_s = ['choice','feedback']# or 'cue'
        
        name = ['Time from event (s)']
        entire_course = []
        
        # Get color scheme, labels
        scheme = ocf.get_colors(factor='interact') # returns [labels, colors, alphas]
        labels = scheme[0]
        colors = scheme[1]
        alphas = scheme[2]
        
        cond = 'correct'
        fac = ['correct'] # for higher level dataframes
        
        # get event related dataframe
        if controlITI:
            if regressRT:
                postFix1 = '_isi_rRT'
            else:
                postFix1 = '_isi'
            postFix2 = '_ITI'
        else:
            if regressRT:
                postFix1 = '_rRT'
            else:
                postFix1 = ''
            postFix2 = ''
    
        downsample_rate = 20 # 20 Hz
        downsample_factor = int(self.sample_rate / downsample_rate) # 50, needs to be an integer
        interval = self.interval # determines size of kernel when * with sample rate
        k = self.interval*downsample_rate # length of kernel
     
        pupil_step_lim = [[-5,10],[-2,13]] # resp, feed
        pupil_xlim = [[-1.5,7.5],[-1.5,0]]

        add_break = 1
        add_xlim = pupil_xlim[1][1] - pupil_xlim[1][0]
        time2add = pupil_xlim[0][1] + add_break # end of resp + how many seconds? - beg of feed
            
        ##################
        #### RESP LOCKED
        cdata1 = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}.csv'.format('resp_locked','motion_energy',postFix1)))
        cdata2 = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}.csv'.format('feed_locked_b2','motion_energy',postFix2)))  # continuation of decision interval
        cdata1 = cdata1.drop(['Unnamed: 0'], axis=1, inplace=False)
        cdata2 = cdata2.drop(['Unnamed: 0'], axis=1, inplace=False)
        
        ## COMBINE cdata1 and cdata2 into one time course for the RESP locked signal
        # downsample subject level pupil data
        conditions = cdata1[['correct']] # drop the names of the conditions to make np array
        pdata1 = cdata1.drop(['correct','subj_idx'], axis=1, inplace=False)
        pdata1 = np.array(pdata1)
        pdata2 = cdata2.drop(['correct','subj_idx'], axis=1, inplace=False)
        pdata2 = np.array(pdata2)
        
        # Set time_locked parameters RESP
        step_lim_t1 = pupil_step_lim[0] # [-5,10]  # pupil_step_lim[0]
        xlim_t1 = pupil_xlim[0] # [-1.5,7.5]   # pupil_xlim[0]
        step_t1 = pd.Series(np.linspace(step_lim_t1[0], step_lim_t1[1], k))
        xlim_indices_t1 = np.array(step_t1 >= xlim_t1[0]) * np.array(step_t1 <= xlim_t1[1])
        # Set time_locked parameters FEED2
        step_lim_t2 = pupil_step_lim[1] # [-2,13]  # pupil_step_lim[1]
        xlim_t2 =  pupil_xlim[1] # [-1.5,0]     # pupil_xlim[1]
        step_t2 = pd.Series(np.linspace(step_lim_t2[0], step_lim_t2[1], k))
        xlim_indices_t2 = np.array(step_t2 >= xlim_t2[0]) * np.array(step_t2 <= xlim_t2[1])
        
        # pad break between choice and feedlocked with NaNs
        padding = np.zeros([pdata1.shape[0], downsample_rate*add_break])
        padding[:] = nan
        pdata = np.concatenate((pdata1[:,xlim_indices_t1],padding,pdata2[:,xlim_indices_t2]),axis=-1)
                
        entire_course.append(pdata)
        
        ##################
        #### FEED LOCKED
        cdata3 = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}.csv'.format('feed_locked','motion_energy',postFix2)))
        cdata3 = cdata3.drop(['Unnamed: 0'], axis=1, inplace=False)
        
        #### PAD cdata3 to same size as RESP locked signal
        # downsample subject level pupil data
        conditions = cdata3[['correct']] # drop the names of the conditions to make np array
        pdata3 = cdata3.drop(['correct','subj_idx'], axis=1, inplace=False)
        pdata3 = np.array(pdata3)
        
        # Set time_locked parameters RESP
        step_lim_t3 = pupil_step_lim[1] # [-2,13]  # pupil_step_lim[1]
        xlim_t3 = pupil_xlim[0] # [-1.5,7.5]   # pupil_xlim[0]
        step_t3 = pd.Series(np.linspace(step_lim_t3[0], step_lim_t3[1], k))
        # Step size for x axis:
        xlim_indices_t3 = np.array(step_t3 >= xlim_t3[0]) * np.array(step_t3 <= xlim_t3[1])
        
        # pad break between choice and feedlocked with NaNs
        padding = np.zeros([pdata3.shape[0], int(downsample_rate*(add_break+add_xlim))])
        padding[:] = nan
        pdata = np.concatenate((pdata3[:,xlim_indices_t3],padding),axis=-1)
                
        entire_course.append(pdata)
        # Plot cue, feedback interaction term
        
        ### DEFINE xlim for concatenated time course
        xlim = [pupil_xlim[0][0], pupil_xlim[0][1]+add_break+add_xlim]
        xlim_indices = pd.Series(np.linspace(xlim[0], xlim[1], entire_course[0].shape[1] ))
        
        # Plot cue, feedback interaction term
        total_interact = []
        for t,pdata in enumerate(entire_course):
            
            this_sig = pd.DataFrame(entire_course[t])
            this_sig[fac] = conditions

            ###########################
            # INTERACTION TERM SUBPLOT
            ###########################
            # compute "difference of differences"
            # Error - Correct
            c_name1 = fac[0] # correct
            cond1 = this_sig[(this_sig[c_name1] ==0)] #  error
            cond2 = this_sig[(this_sig[c_name1] ==1) ] # correct
            cond1.drop(fac, axis=1, inplace=True)
            cond2.drop(fac, axis=1, inplace=True)
            cond1 = np.array(cond1)
            cond2 = np.array(cond2)
            DIFF = cond1-cond2 # error-correct
            save_DIFF = DIFF # to cut off at 0 for stats
            
            # Plot
            sns.tsplot(DIFF, time=xlim_indices, condition=dec_event_s[t], value='Interaction term \n(beta coeff.)', color=colors[t], alpha=alphas[t], ci=66, lw=1, ls='-', ax=ax)
            # stats
            ocf.cluster_sig_bar_1samp(array=DIFF, x=np.array(xlim_indices), yloc=t+2, color=colors[t], ax=ax, threshold=0.05, nrand=nperms, cluster_correct=corr)
            total_interact.append(DIFF)
        
        # difference intervals                             
        ocf.cluster_sig_bar_1samp(array=total_interact[0]-total_interact[1], x=np.array(xlim_indices), yloc=6, color='black', ax=ax, threshold=0.05, nrand=nperms, cluster_correct=corr)
                             
        # Shade time of interest in grey
        ax.axvline(0, lw=1, alpha=1, color = 'k') # Add vertical line at t=0
        ax.axhline(0, lw=1, alpha=1, color = 'k') # Add horizontal line at t=0
        ax.axvspan(3, 6, facecolor='k', alpha=0.1)
        ax.axvspan(xlim[1]-0.5, xlim[1], facecolor='k', alpha=0.1) # 500 ms before feedback

        # Figure parameters        
        ax.set_xticks([0,3,6, xlim[1]-1,xlim[1]]) # mark 1 sec back from feedback
        ax.set_xticklabels([ 0,3,6, -1,0])
        ax.set_xlim(xlim)
        ax.set_ylim([-2,2])
        
        ax.legend(loc='best')
            
        sns.despine(offset=10, trim=True)
        plt.tight_layout()
        fig.savefig(os.path.join(self.figure_folder, 'ScientificReports', 'pupil_event_related_betas_regressRT{}_controlITI{}.pdf'.format(regressRT,controlITI)))        
        print('success: pupil_event_related_betas')    
    

        
    def pupil_results(self, controlITI, regressRT):
        # Figure with 6 panels all pupil results
        
        dec_locked = 'resp_locked' # or 'stim_locked'
        dec_event = 'Choice'  # or 'Cue
        dec_event_s = 'choice' # or 'cue'
        pupil_step_lim = [[-5,10],[-2,13]]
        pupil_xlim = [-1,7.5] # irf only goes back to 1 s
        
        if regressRT:
            postFixRT = ['_rRT','']
        else:
            postFixRT = ['','']
            
        nperms = 10000
        corr = True
        
        downsample_rate = 20 # 20 Hz
        downsample_factor = self.sample_rate / downsample_rate # 50
        interval = self.interval # determines size of kernel when * with sample rate
        k = self.interval*downsample_rate # length of kernel
        
        fig = plt.figure(figsize=(7,4)) 
        
        #######################
        # A mean IRFs
        #######################
        ax = fig.add_subplot(231)
        ax.axhline(0, lw=1, alpha=1, color = 'k') # Add horizontal line at t=0        
        ax.axvline(0, lw=1, alpha=1, color = 'k') # Add vertical line at t=0        
        
        # add deconvolved IRF, 'all' event-related for cue & feedback
        # cluster test IRF against 0
        # Read in dataframe
        if controlITI:
            cue_data = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}{}.csv'.format(dec_locked,'all','_isi',postFixRT[0])))
            feed_data = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}{}.csv'.format('feed_locked','all','_ITI',postFixRT[1])))
        else:
            cue_data = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}.csv'.format(dec_locked,'all',postFixRT[0])))
            feed_data = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}.csv'.format('feed_locked','all',postFixRT[1])))
            
        # IRF time series starts -1 second before cue, others start -2 sec
        if dec_locked == 'stim_locked':
            this_irf = dec_locked
        else:
            this_irf = 'resp_locked'
        irf_data = pd.read_csv(os.path.join(self.dataframe_folder_IRF,'pupil','higher','deconvolution_IRF_{}.csv'.format(this_irf)))
        irf_data.drop('Unnamed: 0', axis=1, inplace=True)
        irf_data = np.array(irf_data)
                
        # downsample cue & feed data
        cue_data = cue_data.drop(['subj_idx'], axis=1, inplace=False)
        cue_data = np.array(cue_data)
        feed_data = feed_data.drop(['subj_idx'], axis=1, inplace=False)
        feed_data = np.array(feed_data)
        
        if not regressRT: # regressed signal downsampled already to save computational time
            cue_data = sp.signal.decimate(cue_data, downsample_factor, ftype='fir')
        feed_data = sp.signal.decimate(feed_data, downsample_factor, ftype='fir')
        
        # for task evoked responses
        xlabel = 'Time from event (s)'
        xlim = pupil_xlim # stays same for all events
        
        step_lim_cue = pupil_step_lim[0]
        step_cue = pd.Series(np.linspace(step_lim_cue[0], step_lim_cue[1], k), name=xlabel)
        # Step size for x axis:
        xlim_indices_cue = np.array(step_cue >= xlim[0]) * np.array(step_cue <= xlim[1])
        
        step_lim_feed = pupil_step_lim[1]
        step_feed = pd.Series(np.linspace(step_lim_feed[0], step_lim_feed[1], k), name=xlabel)
        # Step size for x axis:
        xlim_indices_feed = np.array(step_feed >= xlim[0]) * np.array(step_feed <= xlim[1])
        
        # for IRF
        step_lim_irf = [-1,14]
        step_irf = pd.Series(np.linspace(step_lim_irf[0], step_lim_irf[1], k), name=xlabel)
        # Step size for x axis:
        xlim_indices_irf = np.array(step_irf >= xlim[0]) * np.array(step_irf <= xlim[1])
        
        # cut xlim
        cue_data = cue_data[:,xlim_indices_cue]
        feed_data = feed_data[:,xlim_indices_feed]
        irf_data = irf_data[:,xlim_indices_irf]
                
        # plot
        sns.tsplot(cue_data, time=step_cue[xlim_indices_cue], condition=dec_event, color='blue', alpha=0.6, lw=1, ls='-', ax=ax)
        sns.tsplot(feed_data, time=step_feed[xlim_indices_feed], condition='Feedback', color='purple', alpha=0.6, lw=1, ls='-', ax=ax)
        
        # subplot parameters
        ax.set_ylabel('Pupil response (psc)')
        ax.set_ylim(-3,10)
        # Shade time of interest in grey
        ax.legend(loc='best')      
        sns.despine(ax=ax, left=False, right=True, offset=self.tick_offset, trim=True)  

        # different y-scale for IRF
        color = 'tab:grey'
        ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
        ax2.yaxis.tick_right()
        ax2.tick_params(axis='y', color=color, labelcolor=color)
        sns.tsplot(irf_data, time=step_irf[xlim_indices_irf], condition='IRF', color='gray', alpha=0.8, lw=1, ls='-', ax=ax2)
        ax2.set_ylabel('IRF (psc)', color=color)  # we already handled the x-label with ax1
        ax2.spines['right'].set_color(color)
        ax2.set_ylim(-1,3)
        
        # Shade time of interest in grey
        ax2.legend_.remove()
        sns.despine(ax=ax2, left=True, right=False, offset=self.tick_offset, trim=True)  
        
        #######################
        # B correct vs. error resp phase (locked to feedback)
        #######################
        # plots the response-locked and feed-locked time courses on the same figure (see Urai et al Nature Comm. paper)
        # baseline with respect to stimulus onset
        ax = fig.add_subplot(232)
        
        cond = 'correct'
        factors = ['correct']
            
        downsample_rate = 20 # 20 Hz
        downsample_factor = int(self.sample_rate / downsample_rate) # 50, needs to be an integer
        interval = self.interval # determines size of kernel when * with sample rate
        k = self.interval*downsample_rate # length of kernel
        
        ylim = (0,12)
    
        pupil_step_limB = [[-5,10],[-2,13]] # resp, feed
        pupil_xlimB = [[-1.5,7.5],[-1.5,0]]
        
        name = ['Time from choice (s)', 'Time from feedback (s)']    
        
        # where do I want the feedback response to start? 
        fstart = pupil_xlimB[0][1] + 1 # end of resp + how many seconds?   
        time2add = fstart - pupil_xlimB[1][0] # end of resp + how many seconds? - beg of feed
        
        # Get median RT
        rtdata = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_higher_all.csv'))
        rt_mean = rtdata['rt_med'].mean()
        
        regressRT = False
        t1 = 'resp_locked'
        t2 = 'feed_locked_b2' # continuation of decision interval
        
        # get event related dataframe
        if controlITI:
            if regressRT:
                postFix1 = '_isi_rRT'
            else:
                postFix1 = '_isi'
            postFix2 = '_ITI'
        else:
            if regressRT:
                postFix1 = '_rRT'
            else:
                postFix1 = ''
            postFix2 = ''
        cdata1 = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}.csv'.format(t1,cond,postFix1)))
        cdata2 = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}.csv'.format(t2,cond,postFix2)))
        
        # Set time_locked parameters RESP
        step_lim_t1 = pupil_step_limB[0]
        xlim_t1 = pupil_xlimB[0]
        xlabel_t1 = name[0]
        step_t1 = pd.Series(np.linspace(step_lim_t1[0], step_lim_t1[1], k))
        # Step size for x axis:
        xlim_indices_t1 = np.array(step_t1 >= xlim_t1[0]) * np.array(step_t1 <= xlim_t1[1])
        # Set time_locked parameters FEED
        step_lim_t2 = pupil_step_limB[1]
        xlim_t2 = pupil_xlimB[1]
        xlabel_t2 = name[1]
        step_t2 = pd.Series(np.linspace(step_lim_t2[0], step_lim_t2[1], k))
        # Step size for x axis:
        xlim_indices_t2 = np.array(step_t2 >= xlim_t2[0]) * np.array(step_t2 <= xlim_t2[1])
                                        
        # Get color scheme, labels
        scheme = ocf.get_colors(factor=cond) # returns [labels, colors, alphas]
        labels = scheme[0]
        colors = scheme[1]
        alphas = scheme[2]  
                                                                                                 
        # Shade time of interest in grey
        ax.axvline(0, lw=1, alpha=1, color = 'k') # Add vertical line at t=0
        ax.axhline(0, lw=1, alpha=1, color = 'k') # Add horizontal line at t=0
        ax.axvline(time2add, lw=1, alpha=1, color = 'k') # Add vertical line at t=8.5, when feedback starts
        ax.axvspan(time2add-0.5, time2add, facecolor='k', alpha=0.25) # 500 ms before feedback
        
        # Compute means, sems for all conditions of interest
        conditions = cdata1[factors]
        grouped1 = cdata1.groupby(factors+['subj_idx']).mean()
        grouped2 = cdata2.groupby(factors+['subj_idx']).mean()
        
        # for each interval, get means for each of the 4 conditions
        save_pdata = [] 
        for c,cdata in enumerate([cdata1,cdata2]): 
            save_cond = []
            for value, grouped_df in cdata.groupby(factors):
                print(value)
                # easy*correct
                # (0, 0)
                # (0, 1)
                # (1, 0)
                # (1, 1)
                # shell()
                grouped_df.drop(factors+['subj_idx'], axis=1, inplace=True)
                pdata = np.array(grouped_df)
            
                if not (c==0 and regressRT): # for t1 only, RT regressed data already downsampled
                    # downsample subject level pupil data
                    pdata = sp.signal.decimate(pdata, downsample_factor, ftype='fir') 
                # save for interaction 
                save_cond.append(pdata)
            save_pdata.append(save_cond)
        
        save_cond1 = []  # for plotting difference stats
        save_cond2 = []            
        for l in range(len(save_pdata[0])): # accuracy: 2 conditions
            
            # cut both time courses
            p1 = save_pdata[0][l][:,xlim_indices_t1] # resp
            p2 = save_pdata[1][l][:,xlim_indices_t2] # feed
                                
            sns.tsplot(p1, time=step_t1[xlim_indices_t1], value='Pupil response (psc)', color=colors[l], alpha=alphas[l], lw=1, ls='-', ax=ax)
            sns.tsplot(p2, time=step_t2[xlim_indices_t2]+time2add, condition=labels[l], value='Pupil response (psc)', color=colors[l], alpha=alphas[l], lw=1, ls='-', ax=ax)
            
            save_cond1.append(p1)
            save_cond2.append(p2)
            
        # DIFFERENCE TERM
        DIFF1 = np.array(save_cond1[0])-np.array(save_cond1[1])
        ocf.cluster_sig_bar_1samp(array=DIFF1, x=np.array(step_t1[xlim_indices_t1]), yloc=1, color='black', ax=ax, threshold=0.05, nrand=nperms, cluster_correct=corr)
        DIFF2 = np.array(save_cond2[0])-np.array(save_cond2[1])
        ocf.cluster_sig_bar_1samp(array=DIFF1, x=np.array(step_t2[xlim_indices_t2]), yloc=1, color='black', ax=ax, threshold=0.05, nrand=nperms, cluster_correct=corr)
        
        # Figure parameters
        ax.set_ylim(ylim)     
        ax.set_xlim([pupil_xlimB[0][0],pupil_xlimB[1][1]+time2add])
        ax.set_xticks([0,3,6, time2add])
        ax.set_xticklabels([ 0,3,6, 0])
        ax.set_title('Pre-feedback interval')
        ax.legend(loc='best')
        sns.despine(ax=ax, offset=self.tick_offset, trim=True)
        
        #######################
        # C correct vs. error feedback phase
        #######################
        factors = [['correct']]
        csv_names = ['correct']
        dv_title = 'Post-feedback interval'
        
        t = 1
        time_locked = 'feed_locked'
        
        ax = fig.add_subplot(2,3,3)
        # Shade time of interest in grey
        ax.axvspan(3,6, facecolor='k', alpha=0.25)
        ax.axvline(0, lw=1, alpha=1, color = 'k') # Add vertical line at t=0
        ax.axhline(0, lw=1, alpha=1, color = 'k')
        # Add a line for mean RT
        if time_locked == 'stim_locked':
            ax.axvline(rt_mean, ls='--', lw=1, alpha=1, color = 'k')
        
        # Set time_locked parameters
        name = ['Time from ' + dec_event_s +' (s)', 'Time from feedback (s)']        
        step_lim = pupil_step_lim[t]
        xlim = pupil_xlim
        xlabel = name[t]
        step = pd.Series(np.linspace(step_lim[0], step_lim[1], k), name=xlabel)
        # Step size for x axis:
        xlim_indices = np.array(step >= xlim[0]) * np.array(step <= xlim[1])
    
        # Loop across factors of interest
        for c,cond in enumerate(csv_names):    
            print cond     
            
            if controlITI:
                if time_locked == 'feed_locked':
                    postFix = '_ITI'
                else: # stim, resp
                    postFix = '_isi'
            else: # controlITI False
                postFix = ''
                
            # Read in dataframe
            cdata = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}{}.csv'.format(time_locked,cond,postFix,postFixRT[t])))
                                            
            # Get color scheme, labels
            scheme = ocf.get_colors(factor=cond) # returns [labels, colors, alphas]
            labels = scheme[0]
            colors = scheme[1]
            alphas = scheme[2]  
                                                                                                                        
            conditions = cdata[factors[c]]
            grouped = cdata.groupby(factors[c]+['subj_idx']).mean()

            save_cond = []
            for value, grouped_df in cdata.groupby(factors[c]):
                l = value
                grouped_df.drop(factors[c]+['subj_idx'], axis=1, inplace=True)
                pdata = np.array(grouped_df)
                
                # downsample subject level pupil data
                if (time_locked=='feed_locked') or ((time_locked==dec_locked) and (not regressRT)):
                    pdata = sp.signal.decimate(pdata, downsample_factor, ftype='fir')
                pdata = pdata[:,xlim_indices]
                # save for interaction 
                save_cond.append(pdata)
                sns.tsplot(pdata, time=step[xlim_indices], condition=labels[l], value='Pupil response (psc))', color=colors[l], alpha=alphas[l], lw=1, ls='-', ax=ax)
                print(value)
                print(labels[l])
            # DIFFERENCE TERM
            DIFF = np.array(save_cond[0])-np.array(save_cond[1])
            ocf.cluster_sig_bar_1samp(array=DIFF, x=np.array(step[xlim_indices]), yloc=1, color='black', ax=ax, threshold=0.05, nrand=nperms, cluster_correct=corr)
            
            # Figure parameters
            ax.set_xlim(xlim)
            # ax.set_ylim(ylim[t])
            ax.legend(loc='upper right')
            ax.set_xlabel(xlabel)
            ax.set_title(dv_title)
            sns.despine(ax=ax, offset=self.tick_offset, trim=True)  
        
        #######################
        # D interaction cue vs. feedback
        #######################  
        ax = fig.add_subplot(2,3,4)
    
        # interaction term
        ax.axvline(0, lw=1, alpha=1, color = 'k') # Add vertical line at t=0
        ax.axhline(0, lw=1, alpha=1, color = 'k') # Add horizontal line at t=0
        
        ylim = (-4,4)
        pupil_xlim_D = [-1.5,7.5]
        entire_course = []
        fac = ['easy','correct']
        cond = 'easy*correct'
        ttest = []
        total_interact = []
        nperms = 10000
        corr = True
        
        dec_locked = 'resp_locked' # or 'stim_locked'
        dec_event = 'Choice'  # or 'Cue'
        dec_event_s = ['choice','feedback']# or 'cue'
        name = ['Time from event (s)']
        entire_course = []
        
        # Get color scheme, labels
        scheme = ocf.get_colors(factor='interact') # returns [labels, colors, alphas]
        labels = scheme[0]
        colors = scheme[1]
        alphas = scheme[2]
        
        # get event related dataframe
        if controlITI:
            if regressRT:
                postFix1 = '_isi_rRT'
            else:
                postFix1 = '_isi'
            postFix2 = '_ITI'
        else:
            if regressRT:
                postFix1 = '_rRT'
            else:
                postFix1 = ''
            postFix2 = ''
    
        downsample_rate = 20 # 20 Hz
        downsample_factor = int(self.sample_rate / downsample_rate) # 50, needs to be an integer
        interval = self.interval # determines size of kernel when * with sample rate
        k = self.interval*downsample_rate # length of kernel
     
        pupil_step_lim = [[-5,10],[-2,13]] # resp, feed
        pupil_xlim = [[-1.5,7.5],[-1.5,0]]

        add_break = 1
        add_xlim = pupil_xlim[1][1] - pupil_xlim[1][0]
        time2add = pupil_xlim[0][1] + add_break # end of resp + how many seconds? - beg of feed
            
        ##################
        #### RESP LOCKED
        cdata1 = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}.csv'.format('resp_locked',cond,postFix1)))
        cdata2 = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}.csv'.format('feed_locked_b2',cond,postFix2)))  # continuation of decision interval
        
        ## COMBINE cdata1 and cdata2 into one time course for the RESP locked signal
        # downsample subject level pupil data
        conditions = cdata1[['easy','correct']] # drop the names of the conditions to make np array
        pdata1 = cdata1.drop(['easy','correct','subj_idx'], axis=1, inplace=False)
        pdata1 = np.array(pdata1)
        pdata2 = cdata2.drop(['easy','correct','subj_idx'], axis=1, inplace=False)
        pdata2 = np.array(pdata2)
        
        if not regressRT:
            pdata1 = sp.signal.decimate(pdata1, downsample_factor, ftype='fir')
            pdata2 = sp.signal.decimate(pdata2, downsample_factor, ftype='fir')
        
        # Set time_locked parameters RESP
        step_lim_t1 = pupil_step_lim[0] # [-5,10]  # pupil_step_lim[0]
        xlim_t1 = pupil_xlim[0] # [-1.5,7.5]   # pupil_xlim[0]
        step_t1 = pd.Series(np.linspace(step_lim_t1[0], step_lim_t1[1], k))
        xlim_indices_t1 = np.array(step_t1 >= xlim_t1[0]) * np.array(step_t1 <= xlim_t1[1])
        # Set time_locked parameters FEED2
        step_lim_t2 = pupil_step_lim[1] # [-2,13]  # pupil_step_lim[1]
        xlim_t2 =  pupil_xlim[1] # [-1.5,0]     # pupil_xlim[1]
        step_t2 = pd.Series(np.linspace(step_lim_t2[0], step_lim_t2[1], k))
        xlim_indices_t2 = np.array(step_t2 >= xlim_t2[0]) * np.array(step_t2 <= xlim_t2[1])
        
        # pad break between choice and feedlocked with NaNs
        padding = np.zeros([pdata1.shape[0], downsample_rate*add_break])
        padding[:] = nan
        pdata = np.concatenate((pdata1[:,xlim_indices_t1],padding,pdata2[:,xlim_indices_t2]),axis=-1)
                
        entire_course.append(pdata)
        
        ##################
        #### FEED LOCKED
        cdata3 = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}.csv'.format('feed_locked',cond,postFix2)))
        
        #### PAD cdata3 to same size as RESP locked signal
        # downsample subject level pupil data
        conditions = cdata3[['easy','correct']] # drop the names of the conditions to make np array
        pdata3 = cdata3.drop(['easy','correct','subj_idx'], axis=1, inplace=False)
        pdata3 = np.array(pdata3)
        pdata3 = sp.signal.decimate(pdata3, downsample_factor, ftype='fir')
        
        # Set time_locked parameters RESP
        step_lim_t3 = pupil_step_lim[1] # [-2,13]  # pupil_step_lim[1]
        xlim_t3 = pupil_xlim[0] # [-1.5,7.5]   # pupil_xlim[0]
        step_t3 = pd.Series(np.linspace(step_lim_t3[0], step_lim_t3[1], k))
        xlim_indices_t3 = np.array(step_t3 >= xlim_t3[0]) * np.array(step_t3 <= xlim_t3[1])
        
        # pad break between choice and feedlocked with NaNs
        padding = np.zeros([pdata3.shape[0], int(downsample_rate*(add_break+add_xlim))])
        padding[:] = nan
        pdata = np.concatenate((pdata3[:,xlim_indices_t3],padding),axis=-1)
                
        entire_course.append(pdata)
        # Plot cue, feedback interaction term
        
        ### DEFINE xlim for concatenated time course
        xlim = [pupil_xlim[0][0], pupil_xlim[0][1]+add_break+add_xlim]
        xlim_indices = pd.Series(np.linspace(xlim[0], xlim[1], entire_course[0].shape[1] ))
        
        # Plot cue, feedback interaction term
        total_interact = []
        for t,pdata in enumerate(entire_course):
            
            this_sig = pd.DataFrame(entire_course[t])
            this_sig[fac] = conditions

            ###########################
            # INTERACTION TERM SUBPLOT
            ###########################
            # compute "difference of differences"
            # get interaction term
            c_name1 = fac[0]
            c_name2 = fac[1]
            cond1a = this_sig[(this_sig[c_name1] ==0) & (this_sig[c_name2] ==0)] # hard error
            cond1b = this_sig[(this_sig[c_name1] ==0) & (this_sig[c_name2] ==1)] # hard correct
            cond2a = this_sig[(this_sig[c_name1] ==1) & (this_sig[c_name2] ==0)] # easy error
            cond2b = this_sig[(this_sig[c_name1] ==1) & (this_sig[c_name2] ==1)] # easy correct
            cond1a.drop(fac, axis=1, inplace=True)
            cond1b.drop(fac, axis=1, inplace=True)
            cond2a.drop(fac, axis=1, inplace=True)
            cond2b.drop(fac, axis=1, inplace=True)
            cond1a = np.array(cond1a)
            cond2a = np.array(cond2a)
            cond1b = np.array(cond1b)
            cond2b = np.array(cond2b)
    
            ###########################
            # INTERACTION TERM SUBPLOT
            ###########################
            # compute "difference of differences"
            # Easy(Error-Correct) > Hard(Error-Correct)
            d1 = cond2a-cond2b # easy(error-correct)
            d2 = cond1a-cond1b # hard(error-correct)
            DIFF = d1-d2 # iteraction term
            
            # Plot
            sns.tsplot(DIFF, time=xlim_indices, condition=dec_event_s[t], value='Interaction term \n(beta coeff.)', color=colors[t], alpha=alphas[t], ci=66, lw=1, ls='-', ax=ax)
            # stats
            ocf.cluster_sig_bar_1samp(array=DIFF, x=np.array(xlim_indices), yloc=t+2, color=colors[t], ax=ax, threshold=0.05, nrand=nperms, cluster_correct=corr)
            total_interact.append(DIFF)
        
        # difference intervals                             
        ocf.cluster_sig_bar_1samp(array=total_interact[0]-total_interact[1], x=np.array(xlim_indices), yloc=6, color='black', ax=ax, threshold=0.05, nrand=nperms, cluster_correct=corr)
                                                                                                     
        # Shade time of interest in grey
        ax.axvline(0, lw=1, alpha=1, color = 'k') # Add vertical line at t=0
        ax.axhline(0, lw=1, alpha=1, color = 'k') # Add horizontal line at t=0

        # Figure parameters        
        ax.set_xticks([0,3,6, xlim[1]-1,xlim[1]]) # mark 1 sec back from feedback
        ax.set_xticklabels([ 0,3,6, -1,0])
        
        ax.legend(loc='best')
        
        # Figure parameters
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.legend(loc='upper left')
        ax.set_xlabel(xlabel)
        ax.set_ylim(-4,4)
        ax.set_yticks([-3,0,3])
        ax.set_yticklabels([-3,0,3])
        sns.despine(ax=ax, offset=self.tick_offset, trim=True)  
        
        #######################
        # E,F scalars decision phase
        #######################
        ylim = [(4,9.5),(-2,1)]         
        
        if dec_locked == 'stim_locked':
            if regressRT:
                dvs = ['pupil_d_clean','pupil_d_feed_clean']
            else:
                dvs = ['pupil_d_clean_RT','pupil_d_feed_clean'] # RT in the cue-locked scalars!
        else: # resp_locked     
            if regressRT: # USE FEEDBACK BASELINE FOR PRE-FEEDBACK INTERVAL, STIM baseline and RT REMOVED
                dvs = self.pupil_dvs_PRE_rRT
            else: # USE FEEDBACK BASELINE - STIM BASELINE FOR PRE-FEEDBACK INTERVAL
                dvs = self.pupil_dvs_PRE # RT in the scalars!
                
        cond = 'easy*correct'
        fig_part = ['e','f']
        dv_title = ['Pre-feedback interval','Post-feedback interval']
        
        for n,dv in enumerate(dvs):
                
            ax = fig.add_subplot(2,3,n+5)
            
            ylabel = 'Pupil response (psc))'          
            dv = dv+'_mean' # _mean or _med
            
            if controlITI: 
                if 'feed' in dv: # long ITIs only
                    postFix = '_ITI'
                else: # long ISIs only
                    postFix = '_isi'
            else: # use all trials
                postFix = ''

            # grab the corresponding higher level file    
            cdata = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_higher_{}{}.csv'.format(cond,postFix)))

            # Add statistics
            try:
                aov = pd.read_csv(os.path.join(self.dataframe_folder,'anova_output','csv','rm_anova_{}_{}{}.csv'.format(dv,cond,postFix)))
            except:
                pass
            # number of subjects
            ss = len(np.unique(cdata['subj_idx']))
            # Compute means, sems for all conditions of interest
            MEANS = pd.DataFrame(cdata.groupby(['easy','correct'])[dv].mean().reset_index())
            stds = cdata.groupby(['easy','correct'])[dv].std()
            stds = np.array(stds)
            SEMS = stds/np.sqrt(ss)
            
            fac = ['easy','correct']

            ### LINE GRAPH ###
            ind = [0.3,0.5]
            xlim = [0.275,0.575]
            # get xlabels and color scheme for two conditions
            ls = fac[1] # corresponding to lines
            scheme = ocf.get_colors(factor=ls)
            leg_label = scheme[0]
            colors = scheme[1]
            alphas = scheme[2]
            s2 = ocf.get_colors(factor=fac[0]) # corresponding to xticks
            xticklabels = s2[0]

            # Plot by looping through 'keys' in grouped dataframe
            x=0 # count 'groups'
            for key,grp in MEANS.groupby(ls):
                # print(key)
                print(grp)
                ax.errorbar(ind,grp[dv],yerr=SEMS[x], label=leg_label[x], color=colors[x], alpha=alphas[x])
                x=x+1

            # Figure parameters
            ax.set_xticks(ind)
            ax.set_xticklabels(xticklabels)    
            ax.legend(loc='best')
            ax.set_ylabel(ylabel)
            # set figure parameters
            ax.set_title(dv_title[n])
            sns.despine(ax=ax, offset=self.tick_offset, trim=True)  
            
            # STATS FOR PLOTTING
            print('controlITI {} '.format(controlITI))
            print(dv)
            aov.drop(['Unnamed: 0'],axis=1,inplace=True)
            print(aov) # order of effects: Easy, Correct, Interaction
        
            ttests = cdata[['easy','correct']+[dv]]
            hard_error = ttests[(ttests['easy'] ==0) & (ttests['correct'] ==0)] # hard error
            hard_correct = ttests[(ttests['easy'] ==0) & (ttests['correct'] ==1)] # hard correct
            easy_error = ttests[(ttests['easy'] ==1) & (ttests['correct'] ==0)] # easy error
            easy_correct = ttests[(ttests['easy'] ==1) & (ttests['correct'] ==1)] # easy correct
        
            hard_error = np.array(hard_error[dv])
            hard_correct = np.array(hard_correct[dv])
            easy_error = np.array(easy_error[dv])
            easy_correct = np.array(easy_correct[dv])
        
            print('')
            print('2 sample perm tests')
            print('hard_error vs. hard_correct')
            m,p = ocf.perm_2sample(hard_error, hard_correct)
            print('mean={} , std={},  pval={}'.format(m, np.std(hard_error-hard_correct), round(p,3)))
        
            print('')
            print('easy_error vs. easy_correct')
            m,p = ocf.perm_2sample(easy_error, easy_correct)
            print('mean={} , std={}, pval={}'.format(m, np.std(easy_error-easy_correct), round(p,3)))
        
            print('')
            print('hard_error vs. easy_error')
            m,p = ocf.perm_2sample(hard_error, easy_error)
            print('mean={} , std={}, pval={}'.format(m, np.std(hard_error-easy_error), round(p,3)))
        
            print('')
            print('hard_correct vs. easy_correct')
            m,p = ocf.perm_2sample(hard_correct, easy_correct)
            print('mean={} , std={}, pval={}'.format(m, np.std(hard_correct-easy_correct), round(p,3)))
            
            print('')
            print('MAIN EFFECTS')
            print('hard vs. easy')
            hard = np.array(ttests[ttests['easy'] ==0][dv]) # hard
            easy = np.array(ttests[ttests['easy'] ==1][dv]) # easy
            m,p = ocf.perm_2sample(hard, easy)
            print('mean={}, std={}, pval={}'.format(m, np.std(hard-easy), round(p,3)))
        
            print('MAIN EFFECTS')
            print('error vs. correct')
            error = np.array(ttests[ttests['correct'] ==0][dv]) # error
            correct = np.array(ttests[ttests['correct'] ==1][dv]) # correct
            m,p = ocf.perm_2sample(error, correct)
            print('mean={}, std={}, pval={}'.format(m, np.std(error-correct), round(p,3)))
                    
        plt.tight_layout()
        if regressRT:
            fig.savefig(os.path.join(self.figure_folder, 'ScientificReports', 'pupil_results_{}_controlITI_{}_rRT.pdf'.format(dec_locked,controlITI)))        
        else:
            fig.savefig(os.path.join(self.figure_folder, 'ScientificReports', 'pupil_results_{}_controlITI_{}.pdf'.format(dec_locked,controlITI)))        
        print('success: pupil_results')    
            
    def plot_sdt_models_fits_motion_energy(self, controlITI, binME):
        # fits the subject-specific models to the pupil data based on motion energy
        # four levels (Pearson correlation)
        # correlation coefficents at group level tested with permutation test
        # for Belief State model (model1) and Stimulus State model (model2)
        
        IV = 'motion_energy'
        mdv = ['uncertainty','pe_inv'] # dvs of interest from model, get average per ev_level
        # resp_locked baseline wrt choice
        pdv = self.pupil_dvs_PRE # locked to feedback in pre-interval
        nbins = 6
        
        # single subject noise estimates
        sigmas = pd.read_csv(os.path.join(self.figure_folder, 'ScientificReports','model_subjects',IV,'sigmas_subjects_{}.csv'.format(IV)))
        sigmas = np.array(sigmas.iloc[:,1]) # get 2nd column
        
        # load pupil data
        sdata = pd.read_csv(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_subjects.csv'))
        sdata.drop(['Unnamed: 0'], axis=1, inplace=True)
                
        save_model_r = [] # model1+stim, model1+feed, model2+stim, model2+feed
        for m in ['model1', 'model2']:
            
            for t,time_locked in enumerate(self.time_locked):
                # for each model, interval plot the Spearman correlations
                figS = plt.figure(figsize=(10,10))
                # color = ['blue','purple']
                color = ['grey','grey']
                # loop over subjects
                save_interval_r = []
                save_model_interaction = []
                save_pupil_interaction = []
                
                if controlITI: 
                    if time_locked == 'feed_locked': # long ITIs only
                        D = sdata[sdata['long_ITI']]
                    else: # long ISIs only decision locked
                        D = sdata[sdata['long_isi']]
                    D.reset_index(inplace=True)
                    D.drop(['index'],axis=1,inplace=True)
                else:
                    D = deepcopy(sdata)

                for s,subj in enumerate(sigmas):
                    mdata = [] # clear variable
                    
                    mdata = pd.read_csv(os.path.join(self.figure_folder, 'ScientificReports','model_subjects',IV,'{}_subj{}_{}.csv'.format(m,s,IV)))
                    mdata.drop(['Unnamed: 0'], axis=1, inplace=True)

                    d = D[D['subj_idx']==s]
                    d.reset_index(inplace=True)
                    d.drop(['index'], axis=1, inplace=True)
                   
                    # Because selecting controlITI trials, the motion energy values will differ slightly
                    ME_fits = np.round(d['abs_motion_energy'],3) # Rounding important for matching values!
                    d['ME'] = ME_fits
                    ME_fits = np.round(mdata['ev_levels'],3) 
                    mdata['ME'] = ME_fits
                    
                    # get model estimations for ME levels of this subject    
                    me = mdata[mdata['ME'].isin(np.array(d['ME']))]
                    
                    fac = 'ME'
                    # get dvs per EV
                    model_dvs = me.groupby(['correct',fac])[mdv[t]].mean()
                    model_dvs = pd.DataFrame(model_dvs).reset_index()
                    model_dvs['correct'] = np.array(model_dvs['correct'], dtype=int)
                    # pupil_dvs = d.groupby(['correct',fac])[pdv[t]].count()
                    pupil_dvs = d[[fac,'correct',pdv[t]]] 
                    
                    # sanity = me.groupby(['correct',fac])[mdv[t]].count()
                    
                    # for each pupil trial, get the correct model parameter depending on the accuracy of that trial
                    T1 = pd.merge(pupil_dvs,
                                     model_dvs, 
                                     how = 'left',
                                     on=[fac,'correct']
                                     )
                                     
                    sanity = sum(d.correct==T1.correct) == len(d.correct) # accuracy correctly matched model vs. pupil
                    sanity2 = np.unique(T1[pdv[t]]).shape[0] == len(d.correct) # all unique pupil values
                    
                    # ERRORS only
                    T = T1[T1['correct']==0]
                    # T = T1
                    
                    if binME:
                        BIN_BY = np.array(T[mdv[t]]) # bin by model parameters, not motion energy
                        bin_labels = range(1,nbins+1)
                        bins = pd.qcut(BIN_BY, nbins, labels=bin_labels, retbins=True, duplicates='drop')
                        T['bins'] = np.array(bins[0])
                        T_grouped = T.groupby(['bins'])[mdv[t],pdv[t]].mean()
                        print(T.groupby(['bins'])[mdv[t],pdv[t]].count())
                        
                        ME_grouped = pd.DataFrame(T.groupby(['bins'])[fac].mean())
                        
                        y = np.array(T_grouped[pdv[t]]) # pupil
                        x = np.array(T_grouped[mdv[t]]) # model
                        c = np.array(ME_grouped[fac])
                    else:
                        y = np.array(T[pdv[t]]) # pupil
                        x = np.array(T[mdv[t]]) # model
                        c = np.array(T[fac])
                                                            
                    coeff,pval = sp.stats.pearsonr(x, y) 
                    save_interval_r.append(coeff)
                                  
                    ## generate correlation plots for correlations
                    axS = figS.add_subplot(4,4,s+1)
                    axS.set_title(m + ' '+ time_locked +' subj '+ str(s) + '\nr=' + str(np.round(coeff,3)) + ' p=' + str(np.round(pval,4)) )
                    
                    if binME:                                       
                        z = axS.scatter(x,y,s=150, c=c, cmap='RdBu_r') # color is motion energy or uncertainty bin
                    else:
                        z = axS.scatter(x,y,s=30, c=c, cmap='RdBu_r') # color is motion energy or uncertainty bin

                    r = np.polyfit(x, y, 1) # linear , [slope, intercept]
                    axS.plot(x, r[0]*np.array(x)+r[1], 'r-', label='linear fit')
                    
                    axS.set_xlabel('model '+ mdv[t]) # model dvs.0
                    axS.set_ylabel(pdv[t]) # pupil dvs
                    if s==1:
                        axS.legend(loc='best',fontsize=4)
                        plt.colorbar(z,ax=axS)
                    else:
                        axS.legend().set_visible(False)
                    
                # save plots for each model for each interval
                plt.tight_layout()
                figS.savefig(os.path.join(self.figure_folder, 'ScientificReports', 'Model_fits_{}_{}_{}_controlITI{}_{}_Corr.pdf'.format(pdv[0],m,time_locked,controlITI,IV)))
                    
                # save coefficients for this model
                save_model_r.append(save_interval_r) # model1 dec, model1 feed, model2 dec, model2 feed
                
        ### STATS AND PLOTTING ###
        print('sigmas = [' + str(np.round(min(sigmas),2)) + ',' + str(np.round(max(sigmas),2)) + ']' )

        fig = plt.figure(figsize=(2,2))
        ax = fig.add_subplot(111)
        ax.axhline(0, lw=1, alpha=1, color = 'k') # Add horizontal line at t=0
        # for interaction plots
        ind = [0.3,0.35,0.5,0.55]
        xlim = [0.275,0.575]
        bar_width = 0.05

        xticklabels = ['Belief State (Pre)','Stimulus State (Pre)','Belief State (Post)','Stimulus State (Post)']
        colors = ['blue','blue','purple','purple']
        alphas = [1,0.8,1,0.8]

        # order save_model_r = model1 dec, model1 feed, model2 dec, model2 feed
        # want model1 dec, model2 dec, model1 feed, model2 feed
        reorder_m = [save_model_r[0],save_model_r[2],save_model_r[1],save_model_r[3]]
        # test model1dec vs. model2dec
        # test model1feed vs. model2feed

        for r,rhos in enumerate(range(len(reorder_m))): # model1 dec, model1 feed, model2 dec, model2 feed
            # FISCHER TRANSFORM r coefficients
            reorder_m[r] = ocf.fischer_transform(np.array(reorder_m[r]))

            MEAN = np.mean(reorder_m[r])
            STE = np.std(reorder_m[r]) / np.sqrt(len(reorder_m[r]))
            # plot
            ax.bar(ind[r], MEAN, width=bar_width, yerr=STE, color=colors[r], alpha=alphas[r])
            # plot subject points
            # for i in range(len(save_model_r[r])):

            P = ocf.exact_mc_perm_test(np.array(reorder_m[r]), np.repeat(0,len(reorder_m[r]))) # significantly different from 0?
            
            # corrected for multiple comparisons
            survive, adjustedp = mne.stats.fdr_correction(P, alpha=0.05, method='indep')
            P = adjustedp

            locstar = MEAN + 0.01 # put star a bit above bar
            if P < 0.001:
                ax.text(ind[r]-0.00, locstar, '***', fontsize=6)
            elif P < 0.01:
                ax.text(ind[r]-0.00, locstar, '**', fontsize=6)
            elif P < 0.05:
                ax.text(ind[r]-0.00, locstar, '*', fontsize=6)

        # MODEL COMPARISONS
        # test model1dec vs. model2dec
        # test model1feed vs. model2feed
        PRE = np.array(reorder_m[0]) - np.array(reorder_m[1])
        P1 = ocf.exact_mc_perm_test(PRE, np.repeat(0,len(PRE)))
        POST = np.array(reorder_m[2]) - np.array(reorder_m[3])
        P2 = ocf.exact_mc_perm_test(POST, np.repeat(0,len(POST)))

        for i,P in enumerate([P1,P2]):
            pind = [0,2]
            locstar = MEAN + 0.01 # put star a bit above bar
            if P < 0.001:
                ax.text(ind[pind[i]]+(bar_width/2), locstar, '***', fontsize=6, color='red')
            elif P < 0.01:
                ax.text(ind[pind[i]]+(bar_width/2), locstar, '**', fontsize=6, color='red')
            elif P < 0.05:
                ax.text(ind[pind[i]]+(bar_width/2), locstar, '*', fontsize=6, color='red')

            print('MODEL DIFFERENCES')
            print('interval {}'.format(i))
            print('p = {}'.format(P))

        # set figure parameters
        ax.set_ylabel('Pearson r \nZ-score')
        ax.set_xticks(ind)
        sns.despine(offset=10, trim=True)
        ax.set_xticklabels(xticklabels,rotation=90,fontsize=4) # has to go after despine
        plt.tight_layout()
        fig.savefig(os.path.join(self.figure_folder, 'ScientificReports', 'Model_fits_{}_controlITI{}_{}.pdf'.format(pdv[0],controlITI,IV)))
        print('success: plot_sdt_models_fits_motion_energy')        
