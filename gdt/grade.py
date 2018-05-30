import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from os.path import isfile

class GradePset(object):

    def __init__(self,data_dir):
        # Unnecessary use of memory?
        self.rubrics = pd.read_csv(data_dir+'rubrics.csv')
        
    def render(self,template,first_name,data_dir): 
        """
            Render the editable table to grade
        """
        roster_mxg = pd.read_csv(data_dir+'roster_maxScores.csv')
        roster_g = pd.read_csv(data_dir+'roster_scores.csv')
        return template(first_name,roster_mxg,roster_g)
        
        
class GradeProblem(object):

    def __init__(self,**kargs):
        # Object instantiated when selecting deductions
        if ('which' in kargs) and len(kargs.values()) == 1:
            self.which = kargs['which']
        
        if 'nothandedin' in kargs:
            nothandedin = kargs['nothandedin']
            #ps = nothandedin['not_handed_in'].split(',') 
            # Index of problem to grade and student in roster
            data_dir = kargs['dirsave']
            probscore = pd.read_csv(data_dir+'prob_score.csv')
            self.numProb = len(probscore.index)
            #self.student = int(ps[3])
            self.student = int(nothandedin['student'])
            
        # Object instantiated when grading
        if ('deductions' in kargs) and ('dirsave' in kargs):
            deductions = kargs['deductions']
            data_dir = kargs['dirsave']
            ps = deductions['which'].split(',')
            # Index of problem to grade and student in roster
            self.problem = int(ps[1])
            self.student = int(ps[3])
            # remove 'which' key:value from selected_deductions
            deductions.pop('which',None)
            # Reconstruct deductions applied to each item
            probscore = pd.read_csv(data_dir+'prob_score.csv')
            rubrics = pd.read_csv(data_dir+'rubrics.csv')
            nItems = probscore.ix[self.problem-2,1]
            nElemRub = len(rubrics.index)
            
            dict_manual = {'item'+list(key)[-1]: value for key, value in \
                            deductions.items() if 'manual' in key}
            dict_rs_manual = {'item'+list(key)[-1]: value for key, value in \
                               deductions.items() if 'reason' in key}   
            dict_asw_manual = {'item'+list(key)[-1]: value for key, value in \
                   deductions.items() if 'answer' in key}                    
            items_manual = [int(list(key)[-1]) for key in dict_manual.keys()]                 
            
            dict_rub = {}
            for n in range(nItems):
                if not n+1 in items_manual:
                    rub_deduct = [int(list(key)[2]) for key in deductions.keys() \
                            if not 'manual' in key and not 'reason' in key \
                            and not 'answer' in key and int(list(key)[1])-1 == n ] 
                    dict_rub['item'+str(n+1)] = rub_deduct 
            
            self.nItems = nItems
            self.nElemRub = nElemRub
            self.manual_deduct = dict_manual
            self.manual_reasons = dict_rs_manual
            self.manual_answers = dict_asw_manual
            self.rub_deduct = dict_rub

    def render_select(self,template,first_name,data_dir):
        """
            Render the selection of deductions to apply
        """
        # Identify student and problem to grade
        stud_id = int(self.which.split('_')[1])
        prob_id = int(self.which.split('_')[2])
        roster_mxg = pd.read_csv(data_dir+'roster_maxScores.csv')
        probs = list(roster_mxg.columns.values)
        prob = probs[prob_id-1]
        fname = roster_mxg.ix[stud_id-1,1]
        lname = roster_mxg.ix[stud_id-1,0]
        # Extract the number of items of the problem
        probscore = pd.read_csv(data_dir+'prob_score.csv')
        nItems_idx = probscore.Problem[probscore.Problem == prob].index.tolist()[0]
        nItems = probscore.iloc[nItems_idx,1]
        # Read the rubrics
        rubrics = pd.read_csv(data_dir+'rubrics.csv')
        # Separate concepts evaluated for each item 
        
        evaluating = probscore.Evaluating[prob_id-3]
        if ")" in evaluating:
            eval_items = evaluating.split(")")
            evaluating = []
            del eval_items[0]
            for k in range(len(eval_items)): 
                eval_item = list(eval_items[k])
                if eval_item[-1].isalnum() and not eval_item[-2].isalnum():
                    evaluating.append(''.join(eval_item[:-2]))
                else:
                    evaluating.append(''.join(eval_item))
        else:
            evaluating = [evaluating]
        return template(first_name,stud_id,prob_id,prob,fname,lname,nItems,rubrics,evaluating)
        
        
    def not_handed_in(self,data_dir,userinput):
        """
            Put zeros to all problems of given student
        """
        studscore = pd.read_csv(data_dir+'roster_scores.csv')
        if userinput['not_handed_in'] == 'all':
            # Put zeros to all problems
            for k in range(self.numProb):
                studscore.ix[self.student,k+2] = 0
        elif '-' in userinput['not_handed_in']:        
            # Put zeros to all problems from a given one
            from_prob = userinput['not_handed_in'].split('-')[0]
            probscore = pd.read_csv(data_dir+'prob_score.csv')
            prob_idx = probscore.Problem[probscore['Problem']==from_prob].index.tolist()[0]
            for k in range(self.numProb-prob_idx):
                studscore.ix[self.student,2+prob_idx+k] = 0
        studscore.to_csv(data_dir+'roster_scores.csv',index=False)
        
        
    def grade(self,data_dir):
        """
            Grade problem given the selected deductions
        """
        probscore = pd.read_csv(data_dir+'prob_score.csv')
        rubrics = pd.read_csv(data_dir+'rubrics.csv')
        max_score = probscore.Score[self.problem-2]
        nItems = self.nItems
        # Assume equal score per item
        score_item = max_score/nItems
        score_left_m = 0
        score_left_r = 0
        reasons_deductions = ""
        student_answer = ""
        
        for item, value in self.manual_deduct.items():
            # Manual scoring
            reduct = float(value)/100
            score_left_m += (1-reduct) * score_item
        
        for item, value in self.manual_reasons.items():
            # Reason for deductions
            # Scape commas (-> _) not to interfere with csv when saving 
            reasons_deductions += item + ':' + value.replace(",","_") +'|' 
        
        for item, value in self.manual_answers.items():
            # Student's answer
            # Scape commas (-> _) not to interfere with csv when saving 
            student_answer += item + ':' + value.replace(",","_") +'|'     
        
        for item, value in self.rub_deduct.items():
            # Grade using rubrics
            rub_deducted = score_item
            for r in range(len(value)):
                reduct = rubrics.ix[value[r],1]/100
                rub_deducted -= reduct * score_item
                reasons_deductions += item +':'+ rubrics.ix[value[r],0] + '|'
            score_left_r += rub_deducted    
        
        grade_prob = score_left_m + score_left_r 
        # In case the grade is the maximum, modify roster_maxScore for this prob
        # This is done to render the problem as graded
        if grade_prob == max_score:
           mxgscore = pd.read_csv(data_dir+'roster_maxScores.csv') 
           mxgscore.ix[self.student,self.problem] = max_score - 0.1
           mxgscore.to_csv(data_dir+'roster_maxScores.csv',index=False) 
        # Add the score to the roster_scores file
        studscore = pd.read_csv(data_dir+'roster_scores.csv')
        studscore.ix[self.student,self.problem] = round(grade_prob,2)
        studscore.to_csv(data_dir+'roster_scores.csv',index=False)
        # Write student's answer to file
        stud_answer = pd.read_csv(data_dir+'roster_answers.csv')  
        stud_answer.ix[self.student,self.problem] = student_answer
        stud_answer.to_csv(data_dir+'roster_answers.csv',index=False)
        # Write reasons for deduction to file
        stud_deductions = pd.read_csv(data_dir+'roster_deductions.csv')  
        stud_deductions.ix[self.student,self.problem] = reasons_deductions
        stud_deductions.to_csv(data_dir+'roster_deductions.csv',index=False)

class GradedPset(object):
    
    def __init__(self):
        pass
    
    def get_final_grades(self,data_dir):
        """
            Calculate the final grades of the problem set
        """
        studscore = pd.read_csv(data_dir+'roster_scores.csv')
        studscore["Grade"] = round(studscore.sum(axis=1),2)
        final_grades = studscore[['Last Name','First Name','Grade']]
        self.final_grades = final_grades
        best_grade = final_grades['Grade'].idxmax()
        self.stud_max_grade = final_grades.ix[best_grade,1]
        self.stud_max_grade += ' ' + final_grades.ix[best_grade,0]
        wrst_grade = final_grades['Grade'].idxmin()
        self.stud_min_grade = final_grades.ix[wrst_grade,1]
        self.stud_min_grade += ' ' + final_grades.ix[wrst_grade,0]
        ser_final_grades = final_grades['Grade'].replace(0.0,np.NaN)
        self.mean =  round(ser_final_grades.mean(),2)
        self.std =  round(ser_final_grades.std(),2)
        self.median =  round(ser_final_grades.median(),2)
        final_grades.to_csv(data_dir+'roster_graded.csv',index=False)
        # Save statistics
        df_stat = pd.DataFrame(columns=['Statistics','Value'])
        df_stat.loc[0] = ['mean', self.mean]
        df_stat.loc[1] = ['std', self.std]
        df_stat.loc[2] = ['median', self.median]
        df_stat.loc[3] = ['max_grade', self.stud_max_grade]
        df_stat.loc[4] = ['min_grade', self.stud_min_grade]
        df_stat.to_csv(data_dir+'stats.csv',index=False)
        
        
    def render(self,template,first_name,data_dir):
        """
            Render the final grade for the Problem set
        """
        roster_g = self.final_grades
        return template(first_name,data_dir,roster_g,self.mean,self.median,self.std,\
                        self.stud_max_grade,self.stud_min_grade)