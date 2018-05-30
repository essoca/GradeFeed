#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from os.path import isfile

class GradingRubric(object):
    
    def __init__(self,global_dir,data_dir,**kargs):

        if kargs['global_rubric'] is True:
            self.rubrics = pd.read_csv(global_dir+'rubrics_global.csv')
            self.rubrics.to_csv(data_dir+'rubrics.csv',index=False)
            self.numelems_global = len(self.rubrics.index) 
            self.numelems = self.numelems_global
        else:
            self.rubrics = pd.read_csv(data_dir+'rubrics.csv')
            global_rubrics = pd.read_csv(global_dir+'rubrics_global.csv')
            self.numelems_global = len(global_rubrics.index)
            self.numelems = len(self.rubrics.index)

    def render(self,template,first_name,**kargs):
        """
            Render global rubrics, or add elements, or commit changes
        """
        if kargs['action'] == 'global':
            return template(self.rubrics,first_name,self.numelems,self.numelems_global,'global')
        elif kargs['action'] == 'add':
            return template(self.rubrics,first_name,self.numelems,self.numelems_global,'add')
        else:
            return template(self.rubrics,first_name,self.numelems,self.numelems_global,'commit')
    
    def isAdded(self,inputdata):
        """
            True if a rubric non-empty rubric has been added 
        """
        key_added = 'e_' + str(self.numelems+1) + '_2'
        if key_added in inputdata:
            if inputdata[key_added] != ' ':
                return True
            else:
                return False    
        else:
            return False
        
    
    def save_csv(self,file_rubrics,user_input):
        """ 
            Save the deductions provided by user to csv file
        """
        # Save the modifications to % in the global rubrics
        for row in range(self.numelems_global):
            self.rubrics.ix[row,1] = user_input['e'+str(row+1)+'2']
        
        if self.isAdded(user_input):
            # Save added rubrics    
            row2append = []
            for col in range(2):
                key = 'e_' + str(self.numelems+1)+ '_' + str(col+1)
                row2append.append(user_input[key])
                
            colnames = self.rubrics.columns.values 
            df_row2append = pd.DataFrame([row2append],columns=colnames)
            self.rubrics = self.rubrics.append(df_row2append, ignore_index=True)
            # The number of elements in the rubrics increases by one
            self.numelems += 1
        self.rubrics.to_csv(file_rubrics,index=False)
        
 
        


    