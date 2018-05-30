#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

class ProblemSet(object):
    
    def __init__(self,nbp,mxg,**kargs):
        self.numproblems = int(nbp)
        self.max_grade = float(mxg)
        if kargs["score"]:
            # self.prob_score = pd.DataFrame(columns=['Problem','# Items','Score'])
            # for k in range(self.numproblems):
            #     self.prob_score.loc[k] = pd.Series({"Problem":'P'+str(k+1),\
            #         "# Items":1, "Score": 0
            #     })
            self.prob_score = pd.DataFrame(columns=['Problem','# Items','Evaluating','Score'])
            for k in range(self.numproblems):
                self.prob_score.loc[k] = pd.Series({"Problem":'P'+str(k+1),\
                    "# Items":1, "Evaluating": '', "Score": 0
                })
        else:
            # self.prob_score = pd.DataFrame(columns=['Problem','# Items'])
            # for k in range(self.numproblems):
            #     self.prob_score.loc[k] = pd.Series({"Problem":'P'+str(k+1),\
            #         "# Items":1
            #     })
            self.prob_score = pd.DataFrame(columns=['Problem','# Items','Evaluating'])
            for k in range(self.numproblems):
                self.prob_score.loc[k] = pd.Series({"Problem":'P'+str(k+1),\
                    "# Items":1, "Evaluating": ''
                })
    
    def save_labels_nitems(self,userinput,data_dir):
        """
            Save the labels given to the problems and the number of items for each.   
        """
        for row in range(self.numproblems):
            # for col in range(2):
            for col in range(3):
                key = 'e' + str(row+1) + str(col+1)
                if col == 2 and ',' in userinput[key]:
                    prob_info = userinput[key].replace(',','_')
                else:
                    prob_info = userinput[key]
                self.prob_score.iat[row,col] = prob_info
        self.prob_score.to_csv(data_dir + 'prob_score.csv',index=False)  

    def score_brkdown(self,grade_distr,data_dir):
        """
            Select the score breakdown for each problem (<100)
        """
        # Distribute the grade over the problems (even by default)
        mxg_prob = self.max_grade/self.numproblems
        for k in range(self.numproblems):
            self.prob_score.ix[k,3] = mxg_prob
        self.validate_sumScore(mxg_prob)
                
        if grade_distr == "weight_items":
            # Need to define percentage of the score per problem (when evenly
            # distributed) that will be added to multi-item problems
            perc = 0.3
            score_added = perc * mxg_prob
            # Find multi-item problems an add score_added
            mitm_idx = self.prob_score[self.prob_score['# Items'] != 1].index.tolist()
            itm1_idx = self.prob_score[self.prob_score['# Items'] == 1].index.tolist()
            num_mitm = len(mitm_idx)
            num_itm1 = len(itm1_idx)
            for k in range(num_mitm):
                self.prob_score.ix[mitm_idx[k],3] += score_added
            # The score added to multi-item problems must be subtracted from the others    
            total_score_added = num_mitm * score_added
            score_subtracted = total_score_added/num_itm1
            for k in range(num_mitm):
                self.prob_score.ix[mitm_idx[k],3] -= score_subtracted
            self.validate_sumScore(mxg_prob)    
        elif grade_distr == "manual":  
            self.prob_score['Score'] = 0
        # Round output score
        self.prob_score['Score'] = self.prob_score['Score'].round(2)
        self.prob_score.to_csv(data_dir + 'prob_score.csv',index=False)   
           
    def render_select(self,template,probs_defined,first_name):
        """
            Render the HTML table defining problems, # of items and how to breakdown
            the maximum grade over the problems
        """
        return template(self.numproblems,self.prob_score,probs_defined,first_name)
    
    def render(self,template,sum_score_brkdown,first_name,**kargs):
        """
            Render the HTML table defining prob_score
        """
        manual_distr = kargs["manual_distr"]
        reset = kargs["reset"]
        return template(sum_score_brkdown,self.numproblems,self.max_grade,
                self.prob_score,first_name,manual_distr,reset)
        
    def validate_sumScore(self,mxg_prob):
        """
            Make sure that the sum of all scores per problem give maximum grade
        """
        sum_score_brkdown = self.prob_score['Score'].sum() 
        # Check if sum_score_brkdown is max_grade 
        score_diff = sum_score_brkdown - self.max_grade
        if abs(score_diff) >= 0.01:
            # Randomly select a problem and add/substract score_diff from it
            from random import randint
            prob_idx = randint(0,self.numproblems-1)
            self.prob_score.ix[prob_idx,3] += score_diff
        
    def gen_maxScore_table(self,course_dir,data_dir):
        """
            Generate and save a table with the maximum score for each problem 
            (columns) attached to the roster of the class (rows)
        """
        course_name = course_dir.split('/')[-2]
        roster = pd.read_csv(course_dir+'roster_' + course_name + '.csv')
        roster_d = pd.read_csv(course_dir+'roster_' + course_name + '.csv')
        roster_a = pd.read_csv(course_dir+'roster_' + course_name + '.csv')
        df_probset = pd.read_csv(data_dir+'prob_score.csv')
        for k in range(len(df_probset.index)):
            label = df_probset.iloc[k,0]
            score = df_probset.iloc[k,3]
            roster[label]=pd.Series([score]*len(roster.index),index=roster.index) 
            roster_d[label]=pd.Series(["Not handed in"]*len(roster.index),index=roster.index)
            roster_a[label]=pd.Series(["None"]*len(roster.index),index=roster.index)
        roster.to_csv(data_dir + "roster_maxScores.csv",index=False) 
        # Generate file which will contain the graded problems
        roster.to_csv(data_dir + "roster_scores.csv",index=False)     
        # Generate the file which will contain the deductions applied
        # Those entries not modified is because student didn't hand in
        roster_d.to_csv(data_dir+'roster_deductions.csv',index=False)
        # Generate the file which will contain student answers
        # Those entries not modified is because student didn't answer or professor
        # did not write digitalized answer
        roster_a.to_csv(data_dir+'roster_answers.csv',index=False)
                  