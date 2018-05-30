import web
from web import form
import os
from os.path import join, isfile, exists
from os import getcwd, makedirs, walk
from bs4 import BeautifulSoup
import pandas as pd
import io

#=============================================================================
gdt_dir = join(getcwd(),'gdt/')

def load_imports(path):
    """
        Import all modules from gdt
    """
    files = os.listdir(path)
    imps = []

    for i in range(len(files)):
        name = files[i].split('.')
        if len(name) > 1:
            if name[1] == 'py' and name[0] != '__init__':
               name = name[0]
               imps.append(name)
               
    file = open(path+'__init__.py','w')
    toWrite = '__all__ = ' + str(imps)
    file.write(toWrite)
    file.close()

load_imports(gdt_dir)    
from gdt import problem_set as pbs
from gdt import rubrics as rub
from gdt import grade as gd
from gdt import users
#=============================================================================

templates_dir = join(getcwd(),'templates/')
data_dir = join(getcwd(),'data/') 
users_dir = join(getcwd(),'users/') 

urls = ('/', 'index',
        '/static/(.*)', 'serve_files',
        '/welcome_prof', 'welcome_prof',
        '/welcome_stud', 'welcome_stud',
        '/build_course', 'build_course',
        '/join_course', 'join_course',
        '/view_grade', 'view_grade',
        '/grading_setup', 'grading_setup',
        '/score_brkdown', 'score_brkdown',
        '/rubrics', 'build_rubrics',
        '/grading', 'gradePset',
        '/grading/gradeProblem','gradeProblem',
        '/graded', 'finished',
        '/export', 'download'
        )

#web.config.debug = False

# When using the web.py app reloader in local debug mode, session data may disappear 
# since the session object will not persit between reloads.
# Hack to make session play nice with the reloader (in debug mode)
# if web.config.get('_session') is None:
#     session = web.session.Session(app, db.SessionDBStore())
#     web.config._session = session
# else:
#     session = web.config._session
    
app = web.application(urls, globals())

this_session = web.session.Session(app, web.session.DiskStore('sessions'), \
               initializer={'user_name': None,'first_name': None, 'last_name': None,\
               'is_new_course': False, 'new_course': None, 'assignm_dir': None, \
               'user_dir': None, 'course_dir': None, 'num_prob': 0, 'max_grade': 0, \
                'probs_defined': False, 'prof_found': False, 'joined_course': False, \
                'searched_course': False, 'signed_up': False, 'logged_in': False
               })
session = this_session._initializer          

render = web.template.render('templates/', base='layout', globals={ 'str': str })

class index(object):
    
    def GET(self):
        return render.login()

    def POST(self):
        userinput = web.input()
        if 'sign_up' in userinput:
            # Signing up
            username = userinput['user_name']
            usertype = userinput['user_type']
            userinput.pop('sign_up')
            # Create folder for user
            if usertype == 'professor':
                folder_user = users_dir + 'professors/' + username + '/'
                page_user = '/welcome_prof'
            else:
                folder_user = users_dir + 'students/' + username + '/'
                page_user = '/welcome_stud'
            makedirs(folder_user)
            # Save user ID
            file_user = folder_user + 'id.csv'
            df_user = pd.DataFrame(list(userinput.items()))
            df_user.to_csv(file_user,index=False)
            session['user_name']= username
            session['first_name'] = userinput['first_name']
            session['signed_up'] = True
            raise web.seeother(page_user)
        else:
            # Login in
            usertype = userinput['user_type']
            if usertype == 'professor':
                user = users.professor(userinput['user_name'])
                usertype_dir = 'professors/'
                page_user = '/welcome_prof'
            else:
                user = users.student(userinput['user_name'])
                usertype_dir = 'students/'
                page_user = '/welcome_stud'
            user.first_name = user.get_ID(users_dir + usertype_dir,'first_name')
            user.last_name = user.get_ID(users_dir + usertype_dir,'last_name')
            session['user_name'] = user.user_name
            session['first_name'] = user.first_name
            session['last_name'] = user.last_name
            session['logged_in'] = True
            raise web.seeother(page_user)
            
class serve_files(object):
    
    def GET(self,name):
        ext = name.split(".")[-1]
        cType = {
            "png":"static/png",
            "jpg":"static/jpeg",
            "gif":"static/gif",
            "css":"static/css",
            "js":"static/js"
            }
        if name in os.listdir('static'):
            web.header("Content-Type", cType[ext])
            return open('static/{}'.format(name),"rb").read()
        else:
            raise web.notfound()    
        

################################## Professors ##################################
class welcome_prof(object): 
    
    def GET(self):
        user = users.professor(session['user_name'])
        user.first_name = session['first_name']
        return user.welcome(render.welcome_prof,user,session)
        
    def POST(self):
        userinput = web.input()
        if userinput['task'] == 'build_course':
           raise web.seeother('/build_course')
        else:
           raise web.seeother('/grading_setup')
            
class build_course(object):
    
    def GET(self):
        return render.build_course(session['first_name'])
        
    def POST(self):
        userinput = web.input()
        folder_course = users_dir + 'professors/' + session['user_name'] 
        folder_course += '/' + userinput['courseId'] + '/'
        if not exists(folder_course):
            makedirs(folder_course)
        df_roster = pd.read_csv(io.BytesIO(userinput['file_roster']))
        file_roster = folder_course + 'roster_' + userinput['courseId'] + '.csv'
        df_roster.to_csv(file_roster,index=False)   
        session['is_new_course'] = True
        session['new_course'] = userinput['courseId']
        raise web.seeother('/welcome_prof')
        
class grading_setup(object):
    
    def GET(self):
        user = users.professor(session['user_name'])
        user.first_name = session['first_name']
        # List the current courses owned by user
        user_dir = users_dir + 'professors/' + session['user_name'] + '/'
        user.userdir = user_dir
        courses =  [x[0] for x in user.list_courses()]
        del courses[0]
        courses = [x.split('/')[-1] for x in courses]
        # These will appear as options to choose when grading
        #return render.pset_setup(courses)
        return render.pset_setup(courses,user)
        
    def POST(self):
        userinput = web.input()
        session['num_prob'] = int(userinput['num_prob'])
        session['max_grade'] = float(userinput['maxgrade'])
        # Save data for the course and assignment graded in the current session
        course = userinput['course']
        assignm_id = userinput['assignment_id']
        user_dir = users_dir + 'professors/' + session['user_name'] + '/'
        assignm_dir = user_dir + course + '/' + assignm_id + '/'
        session['user_dir'] = user_dir
        session['course_dir'] = user_dir + course + '/'
        session['assignm_dir'] = assignm_dir
        if not exists(session['assignm_dir']):
            makedirs(session['assignm_dir'])
        raise web.seeother('/score_brkdown')

class score_brkdown(object):
    
    def GET(self):
        pset = pbs.ProblemSet(session['num_prob'], session['max_grade'], score=False)
        if session['probs_defined']:
            pset.prob_score = pd.read_csv(session['assignm_dir']+'prob_score.csv')
        return pset.render_select(render.score_brk0,session['probs_defined'],session['first_name'])

    def POST(self): 
        userinput = web.input()
        pset = pbs.ProblemSet(session['num_prob'],session['max_grade'], score=True)
        if "got_prob_labels" in userinput:
            pset.save_labels_nitems(userinput,session['assignm_dir'])
            session['probs_defined'] = True
        if "grade_distr" in userinput:
            pset.prob_score = pd.read_csv(session['assignm_dir']+'prob_score.csv')
            pset.score_brkdown(userinput["grade_distr"],session['assignm_dir'])
            sum_score_brkdown = pset.prob_score['Score'].sum()
            if userinput['grade_distr'] == "manual":
                # Show the table of score breakdown until sum_score_brkdown == max_grade
                while abs(sum_score_brkdown - pset.max_grade) >= 0.01:
                    return pset.render(render.score_brk,sum_score_brkdown,session['first_name'],manual_distr=True,reset=False)  
            else:
                return pset.render(render.score_brk,sum_score_brkdown,session['first_name'],manual_distr=False,reset=False)  
        elif "reset" in userinput:
            raise web.seeother('/score_brkdown')
        elif "continue" in userinput:
            # Generate table of maximum scores per problem on the roster
            pset.gen_maxScore_table(session['course_dir'],session['assignm_dir'])
            # Go to add rubrics
            raise web.seeother('/rubrics')
        
class build_rubrics(object):  
    
    def GET(self): 
        rub_global_dir = session['user_dir']
        rub_dir = session['assignm_dir']
        rubric = rub.GradingRubric(rub_global_dir,rub_dir, global_rubric = True)
        return rubric.render(render.rubrics,session['first_name'],action='global')
        
    def POST(self): 
        userinput = web.input()
        rub_global_dir = session['user_dir']
        rub_dir = session['assignm_dir']
        rubric = rub.GradingRubric(rub_global_dir,rub_dir, global_rubric = False)
        rubric.save_csv(session['assignm_dir']+'rubrics.csv',userinput)
        if 'add_deduction' in userinput:
            return rubric.render(render.rubrics,session['first_name'],action='add')
        if 'commit_changes' in userinput:
            return rubric.render(render.rubrics,session['first_name'],action='commit')
            
class gradePset(object):
    
    def GET(self):
        inputdata = web.input()
        grade = gd.GradePset(session['assignm_dir'])
        return grade.render(render.grade_pset,session['first_name'],session['assignm_dir'])
        
    def POST(self):
        inputdata = web.input()
        for key, value in inputdata.items():
            if value == 'grade':
                which = key
        select_deductions = gd.GradeProblem(which=which)
        return select_deductions.render_select(render.grade_prob,session['first_name'],session['assignm_dir'])


class gradeProblem(object):
    
    def POST(self):
        userinput = web.input()
        if len(userinput) == 0:
            print('Select deductions to apply to the problem')
            raise(ValueError)
        elif 'not_handed_in' in userinput:
            gradeProb = gd.GradeProblem(dirsave=session['assignm_dir'],nothandedin=userinput)
            gradeProb.not_handed_in(session['assignm_dir'],userinput)
            web.seeother('/grading')
        else:
            gradeProb = gd.GradeProblem(dirsave=session['assignm_dir'],deductions=userinput)
            gradeProb.grade(session['assignm_dir'])
            web.seeother('/grading')
            
class finished(object):
    
    def GET(self):
        gradedPset = gd.GradedPset()
        gradedPset.get_final_grades(session['assignm_dir'])
        return gradedPset.render(render.graded,session['first_name'],session['assignm_dir'])
        
class download(object):
    
    def GET(self):
        return open(session['assignm_dir']+'roster_graded.csv',"rb").read()
        
################################## Students ##################################    
class welcome_stud(object): 
    
    def GET(self):
        student = users.student(session['user_name'],session['first_name'],session['last_name'])
        return student.welcome(render.welcome_stud,student,session)
        
    def POST(self):
        userinput = web.input()
        if userinput['task'] == 'join_course':
           session['prof_found'] = False
           raise web.seeother('/join_course')
        else:
           raise web.seeother('/view_grade')
           
class join_course(object):
    
    def GET(self):
        student = users.student(session['user_name'],session['first_name'],session['last_name'])
        return student.render(render.join_course,session['prof_found'])
    
    def POST(self):
        userinput = web.input()
        student = users.student(session['user_name'],session['first_name'],session['last_name'])
        profs_dir = users_dir + 'professors/'
        profs, profs_unames, courses = student.search_professor(userinput['search'],profs_dir)
        if len(profs) != 0:
            session['prof_found'] = True
        if "course" in userinput:
            student_incourse = student.is_in_course(users_dir,userinput)
            session['new_course'] = userinput['course']
            if student_incourse:
                session['joined_course'] = True
                session['course_dir'] = users_dir +'professors/'+ userinput['prof_username'] +\
                                        '/' + userinput['course'] + '/'
                raise web.seeother('/welcome_stud')
            else:
                session['searched_course'] = True
                raise web.seeother('/welcome_stud')
        return student.render(render.join_course,session['prof_found'],
                profs,profs_unames,courses)

class view_grade(object):
    
    def GET(self):
        student = users.student(session['user_name'],session['first_name'],session['last_name'])
        grades = student.find_grades(session['course_dir'])
        return student.render_grades(render.view_grade,session['new_course'],grades)

if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()