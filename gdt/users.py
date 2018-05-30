import pandas as pd
import os

class professor(object):
    
    def __init__(self,user_name):
        self.user_name = user_name
        
    def welcome(self,template,user,session_data):
        return template(user.first_name,session_data)
        
    def get_ID(self,prof_dirs,which):
        """
            Find the folder assigned to the professor and retrive properties
            from id.csv
        """
        file_id = prof_dirs + self.user_name + '/id.csv'
        df_prof = pd.read_csv(file_id)
        which_idx = df_prof.index[df_prof['0']==which].tolist()[0]
        return df_prof.ix[which_idx,1]
        
    def list_courses(self):
        """
            Returns a generator listing the dirs of the courses owned by user
        """
        return walklevel(self.userdir)
        
class student(object):
    
    def __init__(self,user_name,*args):
        self.user_name = user_name
        if len(args) != 0:
            first_name, last_name = args
            self.first_name = first_name
            self.last_name = last_name
        
    def welcome(self,template,user,session_data):
        return template(user,session_data)
        
    def get_ID(self,prof_dirs,which):
        """
            Find the folder assigned to the professor and retrive properties
            from id.csv
        """
        file_id = prof_dirs + self.user_name + '/id.csv'
        df_prof = pd.read_csv(file_id)
        which_idx = df_prof.index[df_prof['0']==which].tolist()[0]
        return df_prof.ix[which_idx,1]
        
    def search_professor(self,last_name,profs_dir):   
        """
            Search the professor by last name
        """
        profs = []
        profs_unames = []
        courses = []
        for profs_username in walklevel(profs_dir):
            if profs_username[0]+'/' == profs_dir:
                # Building list of professors
                df_profID = pd.read_csv(profs_dir + profs_username[1][0] + '/id.csv')
                idx_fname = df_profID.index[df_profID.iloc[:,0]=='first_name'].tolist()[0]
                idx_lname = df_profID.index[df_profID.iloc[:,0]=='last_name'].tolist()[0]
                fname, lname = df_profID.ix[idx_fname,1], df_profID.ix[idx_lname,1]
                if lname == last_name:
                    profs.append(fname + ' ' + lname)
                    profs_unames.append(profs_username[1][0])
                # Building their list of courses    
            else:
                courses.append(','.join(profs_username[1]))
        return profs, profs_unames, courses   
        
    def is_in_course(self,users_dir,userinput):
        """
            Search whether student belong to the roster of claimed course
        """
        prof_username = userinput['prof_username']
        course = userinput['course']
        course_dir = users_dir + 'professors/' + prof_username +'/'+ course +'/'
        roster = pd.read_csv(course_dir + 'roster_' + course + '.csv')
        idx_lname = roster['Last Name'].index[roster['Last Name']==self.last_name].tolist()
        idx_fname = roster['First Name'].index[roster['First Name']==self.first_name].tolist()
        if len(idx_lname) == 0:
            return False
        else:    
            if idx_fname[0] == idx_lname[0]:
                return True
            else:
                return False
                
    def find_grades(self,data_dir):
        """
            Search the folder of a professor for grades
        """
        grades = {} 
        stats = {}
        for root, dirs in walklevel(data_dir,0):
            for k in range(len(dirs)):
                assignm = str(dirs[k])
                roster_g = pd.read_csv(data_dir+ assignm +'/roster_graded.csv')
                stats_g = pd.read_csv(data_dir+ assignm +'/stats.csv')
                idx_lname = roster_g.index[roster_g['Last Name']==self.last_name].tolist()[0]
                idx_fname = roster_g.index[roster_g['First Name']==self.first_name].tolist()[0]
                if idx_lname == idx_fname:
                    grades[assignm] = [roster_g.ix[idx_lname,2]]
                    stats[assignm] = [stats_g.ix[2,1]]
                else:
                    print('Student not in roster')
                    
        df_grades = pd.DataFrame(grades)  
        df_grades = df_grades.append(pd.DataFrame(stats),ignore_index=True)
        return df_grades
        
    def render(self,template,prof_found,*args):
        """
            Render the list of professors matching last name and their courses
        """
        return template(prof_found,*args)
        
    def render_grades(self,template,course,grades):
        """
            Render the grades of the student and the medians of the course
        """
        return template(course,grades)
    
def walklevel(some_dir, level=1):
    """
        Generator to list directories inmediately below some_dir
    """
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        #yield root, dirs, files
        yield root, dirs
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]    
            