import flask
import db_interaction as db_interaction
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
import datetime
import re
import os
import pickle
import college_majors as college_majors
import json
import pdfkit
import random
import form_db
import itertools
from time import gmtime, strftime


app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = "/home/jamespetullo/mysite/wkhtmltopdin"


def create_pdf(pdf_data):
    pdf = StringIO()
    pisa.CreatePDF(StringIO(pdf_data.encode('utf-8')), pdf)
    return pdf
############Styling TODO:##################
#TODO: change position and background of signup and login menus
#TODO: style user confirmation email body
##############################
##############Administration TODO:################
#TODO: find best company name
#TODO: create email with domain name
#SkillHost
#NOTE: serialized student skills are located in 'studentskills.txt'
#NEED: navigation bar
#TODO: add settings page where user can change name, password, etc
#TODO:put a "already have an account? Login" feature on signup page
#TODO: create filter menu on search page
#TODO: make sure that any instances of User __setitem__ has been forced to global
#TODO: create a better search algorithm
class User:
    def __init__(self, name):
        self.name = "3424245" if name is None else name
        self.email = None
        self._form_name = "3424245"

    @property
    def username(self):
        return self._form_name
    @username.setter
    def username(self, value):
        self._form_name = value

    @username.getter
    def username(self):
        return self._form_name


    def __getitem__(self, token):
        if token in self.__dict__:
            return self.__dict__[token]

        raise KeyError("Please check variable '{}'".format(token))

    def __setitem__(self, k, v):
        self.__dict__[k] = v

    def cleanup(self):
        self.__dict__ = {a:b for a, b in self.__dict__.items() if a == "name" and b == "3424245"}



    def __str__(self):
        return self.name if "name" in self.__dict__ else self.username



user = User(None)
class Pdf:

    def render_pdf(self, html):

        from xhtml2pdf import pisa
        from StringIO import StringIO

        pdf = StringIO()
        #print "the____html", html
        #print "the____html_type", type(html)
        pisa.CreatePDF(StringIO(html[0]), pdf)

        return pdf.getvalue()
app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False, #used to be False
    MAIL_USERNAME = 'jpetullo14@gmail.com',
    MAIL_PASSWORD = 'Gobronxbombers2#',
    WKHTMLTOPDF_USE_CELERY = True,
    WKHTMLTOPDF_BIN_PATH ='/Users/jamespetullo/Downloads/wkhtmltox-0.12.4_osx-carbon-i386.pkg',
    PDF_DIR_PATH =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'pdf')
))
mail = Mail(app)
ts = URLSafeTimedSerializer("secretkey")
#mail.init_app(app)


@app.route('/confirm/<token>')
def confirm_email(token):

    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)


        #print "confired!!!, welcome", email
        #BUG: redirecting to account_issue.html when "login" is preceeded with forward slash
    except:
        return flask.render_template("account_issue.html")
    db_interaction.set_verified(email)

    return flask.redirect(flask.url_for("login"))

@app.route('/forms/ask', methods=['GET', 'POST'])
def ask_question():
    headers = ['title', 'content', 'tags', 'email', 'id', 'date', 'isop']
    if user.username == "3424245":
        return flask.redirect('/forms')

    if flask.request.method=="POST":
        title = flask.request.form["question_title"]
        question_content = flask.request.form['question']
        tags = flask.request.form.getlist('tags')

        if not title:
            return flask.render_template('ask_question.html', error1 = 'Title must be filled in', error2='', error3 = '', tags = ['grades', 'scores', 'tests', 'applications', 'SAT', 'ACT', 'college-search', 'admissions', 'colleges'])
        if not question_content:
            return flask.render_template('ask_question.html', error1 = '', error2='Question cannot be left blank', error3 = '', tags = ['grades', 'scores', 'tests', 'applications', 'SAT', 'ACT', 'college-search', 'admissions', 'colleges'])
        if not tags:
            return flask.render_template('ask_question.html', error1 = '', error2='', error3 = 'Please add at least one tag that describes the question content', tags = ['grades', 'scores', 'tests', 'applications', 'SAT', 'ACT', 'college-search', 'admissions', 'colleges'])

        new_id = 1 if not form_db.get_post_ids() else max(form_db.get_post_ids())+1
        form_db.add_post(**dict(zip(headers, [title, question_content, ','.join(tags), user['email'], new_id, strftime("%Y-%m-%d %H:%M:%S", gmtime()), 1])))
        return flask.redirect("/forms/question/{}".format(new_id))
        #process, then redirect to question layout
    return flask.render_template('ask_question.html', error1 = '', error2='', tags = ['grades', 'scores', 'tests', 'applications', 'SAT', 'ACT', 'college-search', 'admissions', 'colleges'])

@app.route("/forms/question/<id>", methods=['GET', 'POST'])
def display_questions(id):
    #headers = ['title', 'content', 'tags', 'email', 'id', 'date', 'isop']
    posts = form_db.get_posts(int(id))
    form_db.update_views(int(id), viewer = "3424245@3424245" if not user['email'] else user['email'])
    people = [' '.join(db_interaction.get_person(i[-4])[0]) for i in posts]
    op_tags = [i.split(',')[0] for i in db_interaction.get_certain_tags(posts[0][-4])[0]]
    if int(id) not in form_db.get_post_ids():
        return flask.render_template('post_not_found.html')
    if flask.request.method == "POST":
        answer = flask.request.form['response']

        if not answer:
            return flask.render_template('form_post_responses.html', user_type = user['name'], op=list(posts[0])+[people[0]], op_tags=op_tags, responses = [list(a)+[b] for a, b in zip(posts[1:], people[1:])], error='Response cannot be left blank')

        form_db.add_post(title = posts[0][0], content = answer, tags=posts[0][2], email=user['email'], id=posts[0][-3], date=strftime("%Y-%m-%d %H:%M:%S", gmtime()), isop=0)
        return flask.redirect("/forms/question/{}".format(posts[0][-3]))
    #posts = form_db.get_posts(int(id))
    #TODO: once enabled on pythonanywhere, add link to profile for each user who posts on a thread
    #headers = ['title', 'content', 'tags', 'email', 'id', 'date', 'isop']
    posts = form_db.get_posts(int(id))

    people = [' '.join(db_interaction.get_person(i[-4])[0]) for i in posts]
    responses = [list(a)+[b] for a, b in zip(posts[1:], people[1:])]
    responder_tags = [[b.split(',')[0] for b in db_interaction.get_certain_tags(post[-4])[0]] for post in posts[1:]]


    return flask.render_template('form_post_responses.html', user_type = user['name'], op=list(posts[0])+[people[0]], op_tags=op_tags, responses = [list(a)+[b]+c for a, b, c in zip(posts[1:], people[1:], responder_tags)], error='')

@app.route("/settings")
def settings():
    if user["name"] == "3424245":
        return flask.redirect("/login")

    return flask.render_template("account_settings.html")

@app.route("/delete")
def delete_account():
    global user
    if user["name"] == "3424245":
        return flask.redirect("/login")
    #print "right here with user['email']", user["email"]
    db_interaction.delete_user(user["email"])

    user["name"] = "3424245"
    user.cleanup()
    return flask.redirect("/")


@app.route("/forms", methods=['GET', 'POST'])
def forms_home():
    global user
    user.username = user['name']
    posts = form_db.get_posts()
    #print datetime.datetime.now(), datetime.datetime.strptime(posts[0][-2], "%Y-%m-%d %H:%M:%S")
    new_datime = datetime.datetime.now()-datetime.datetime.strptime(posts[0][-2], "%Y-%m-%d %H:%M:%S")
    #print new_datime.days, new_datime.seconds//3600 #works for hours
    new_posts = [list(i)+[datetime.datetime.now()-datetime.datetime.strptime(i[-2], "%Y-%m-%d %H:%M:%S")] for i in posts]
    #print [[i[-1].time().days, i[-1].time().hour, i[-1].time().minute, i[-1].time().seconds] for i in new_posts]
    converter = {0:"days", 1:"hours", 2:"minutes", 3:'seconds'}
    #print [[i[-1].days, i[-1].days * 24 + i[-1].seconds//3600, (i[-1].seconds % 3600)//60, i[-1].seconds % 60] for i in new_posts]
    #final_posts = [i[:-1]+[[i[-1].days, i[-1].seconds//3600, i[-1].seconds//60, i[-1].seconds]] for i in new_posts]
    final_posts = [i[:-1]+[[i[-1].days, i[-1].days * 24 + i[-1].seconds//3600, (i[-1].seconds % 3600)//60, i[-1].seconds % 60]] for i in new_posts]
    print final_posts
    second_posts = [i[:-1]+["{} {}".format([(c, d) for c, d in enumerate(i[-1]) if d > 0][0][-1], converter[[(c, d) for c, d in enumerate(i[-1]) if d > 0][0][0]])] for i in final_posts]

    new_final_posts = [i[:-1]+["{} {}".format(1, re.findall('(?<=\s)\w+$', i[-1])[0][:-1])] if re.findall('^1\s', i[-1]) else i[:-1]+[i[-1]] for i in second_posts]
    people = [' '.join(db_interaction.get_person(i[-5])[0]) for i in new_final_posts]
    final_posts1 = [a+[b]+[form_db.get_view_number(a[-4])] for a, b in zip(new_final_posts, people)]

    tags = ['grades', 'scores', 'tests', 'applications', 'SAT', 'ACT', 'college-search', 'admissions', 'colleges']
    tags_frequencies = {tag:[len([post for post in final_posts1 if post[6] and tag.lower() in post[2].lower()]), len([post for post in final_posts1 if not post[6] and tag.lower() in post[2].lower()])] for tag in tags}
    #answers_with_tags = {tag:len([post for post in final_posts1 if not post[6] and tag.lower() in post[2].lower()]) for tag in tags}
    print "--------"
    print tags_frequencies
    print "--------"
    return flask.render_template("form_home.html", user_name1 = user['name'], user=user.username, newest=[i for i in final_posts1 if i[-3]], activity = final_posts1, tag_data = tags_frequencies.items())


@app.route('/forms/profile', methods=['GET', 'POST'])
def form_profile():
    if user['name'] == "3424245":
        return flask.redirect('/login')

    global user
    print "++++++++++++"
    print form_db.get_user_form_listing('jpetullo14@gmail.com')
    print "++++++++++++"
    user.username = user['name']
    posts = form_db.get_posts()
    #print datetime.datetime.now(), datetime.datetime.strptime(posts[0][-2], "%Y-%m-%d %H:%M:%S")
    new_datime = datetime.datetime.now()-datetime.datetime.strptime(posts[0][-2], "%Y-%m-%d %H:%M:%S")
    #print new_datime.days, new_datime.seconds//3600 #works for hours
    new_posts = [list(i)+[datetime.datetime.now()-datetime.datetime.strptime(i[-2], "%Y-%m-%d %H:%M:%S")] for i in posts]
    #print [[i[-1].time().days, i[-1].time().hour, i[-1].time().minute, i[-1].time().seconds] for i in new_posts]
    converter = {0:"days", 1:"hours", 2:"minutes", 3:'seconds'}
    #print [[i[-1].days, i[-1].days * 24 + i[-1].seconds//3600, (i[-1].seconds % 3600)//60, i[-1].seconds % 60] for i in new_posts]
    #final_posts = [i[:-1]+[[i[-1].days, i[-1].seconds//3600, i[-1].seconds//60, i[-1].seconds]] for i in new_posts]
    final_posts = [i[:-1]+[[i[-1].days, i[-1].days * 24 + i[-1].seconds//3600, (i[-1].seconds % 3600)//60, i[-1].seconds % 60]] for i in new_posts]

    second_posts = [i[:-1]+["{} {}".format([(c, d) for c, d in enumerate(i[-1]) if d > 0][0][-1], converter[[(c, d) for c, d in enumerate(i[-1]) if d > 0][0][0]])] for i in final_posts]

    new_final_posts = [i[:-1]+["{} {}".format(1, re.findall('(?<=\s)\w+$', i[-1])[0][:-1])] if re.findall('^1\s', i[-1]) else i[:-1]+[i[-1]] for i in second_posts]
    people = [' '.join(db_interaction.get_person(i[-5])[0]) for i in new_final_posts]
    final_posts1 = [a+[b]+[form_db.get_view_number(a[-4])] for a, b in zip(new_final_posts, people)]

    print set(itertools.chain(*[[b.capitalize() for b in i[2].split(',')] for i in final_posts1 if i[3] == user['email']]))
    return flask.render_template('user_form_profile.html', username = user.username, tags = set(itertools.chain(*[[b.capitalize().upper() if b.lower() == "sat" or b.lower() == "act" else b.capitalize() for b in i[2].split(',')] for i in final_posts1 if i[3] == user['email']])), answers = [i for i in final_posts1 if not i[-4]], posts = [i for i in final_posts1 if i[-4]])

@app.route("/change_password<token>", methods=["GET", "POST"])
def change_password(token):
    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)


        #print "confired!!!, welcome", email
        #BUG: redirecting to account_issue.html when "login" is preceeded with forward slash
    except:
        return flask.render_template("account_issue.html")
    if flask.request.method=="POST":
        new_password = flask.request.form["password1"]
        confirm_password = flask.request.form["password2"]
        #print new_password, confirm_password, email
        if not re.findall('\W+', new_password):
            return flask.render_template("change_password.html", invalid_form="password must contain at least one non alphanumeric character")
        if len(new_password) < 8:
            return flask.render_template("change_password.html", invalid_form = "password must be at least eight characters")
        if new_password != confirm_password:
            return flask.render_template("change_password.html", invalid_form = "passwords do not match")
        #print "email used here:--------------"
        #print email
        #print new_password
        #print "------------------------------"

        db_interaction.update_password(email, new_password)
        #print(db_interaction.get_full_users())
        #print "------------------------------"
        return flask.redirect("/")
    return flask.render_template("change_password.html", invalid_form='')

@app.route("/changepassword")
def change():
    token = ts.dumps(user["email"], salt='email-confirm-key')

    confirm_url = flask.url_for('change_password', token=token, _external=True)
    reset_password(user["name"], user["email"], confirm_url)
    return flask.render_template("prompt_password_confirm.html")

@app.route("/forgotpassword", methods=["GET", "POST"])
def forgot_password():
    if flask.request.method=="POST":
        name = flask.request.form["name"]
        email = flask.request.form["email"]
        if not re.findall('^[\w\W]+@[\w\W]+$', email):
            return flask.render_template("forgot_password.html", invalid_form = "Invalid email form")
        token = ts.dumps(email, salt='email-confirm-key')

        confirm_url = flask.url_for('change_password', token=token, _external=True)
        reset_password(user["name"], email, confirm_url)

        return flask.render_template("prompt_password_confirm.html")
    return flask.render_template("forgot_password.html", invalid_form = '')
@app.route("/signout", methods=["GET", "POST"])
def sign_out():
    global user
    user["name"] = "3424245"
    user.username = "3424245"
    return flask.redirect("/")

    #db_interaction.set_verified(email)
@app.route("/searcherror", methods=["GET", "POST"])
def search_error():
    '''
    if user["name"] == "3424245":
        return flask.redirect("/login")
    '''
    if flask.request.method=="POST":
        new_search = flask.request.form["search"]
        #print "new_search", new_search
        return flask.redirect("/students/{}".format(re.sub("\W+", '', new_search).lower()))


    return flask.render_template("no_results.html")


@app.errorhandler(404)
def page_not_found(e):

    return flask.render_template("404.html")

@app.route("/about")
def about():
    return flask.render_template("about.html")


def send_confirmation_email(name, email, user_linkup):


    msg = Message(subject="Studenthost Account Confirmation", sender="jpetullo14@gmail.com", recipients=[email])
    msg.html = flask.render_template("account_confirmation.html", confirm_url=user_linkup)
    mail.send(msg)

def reset_password(name, email, user_linkup):
    msg = Message(subject="Password Change Request", sender="jpetullo14@gmail.com", recipients=[email])
    msg.html = flask.render_template("change_password_email.html", confirm_url=user_linkup)
    mail.send(msg)

def create_pdf(pdf_data):
    from xhtml2pdf import pisa
    from StringIO import StringIO
    '''
    pdf = StringIO()
    pisa.CreatePDF(StringIO(pdf_data.encode("utf-8")), pdf.getvalue())
    return
    '''
    pdf = StringIO()
    pisa.CreatePDF(StringIO(pdf_data), pdf)
    return pdf

@app.route("/printprofile/<email>")
def print_profile(email):

    data = db_interaction.get_user_listing_by_email(email)
    #pdfkit.from_url("http://127.0.0.1:5000/printprofile/{}".format(email), "{}.pdf".format(data[0][0]), options = {'page-size': 'A4', "dpi":400})
    vals = ["name","personal_statement", "grade", "colleges", "majors", "skills", "activities"]

    #return flask.render_template("profile.html", name=, grade="12th", personal_statement="I am love programming, math, and aglorithms", colleges=["WPI", "Assumption College", "Worcester State", "MIT", "Holy Cross", "Olin College"], majors=["Computer Science", "Mathematics", "Finance"], skills=["Hard work", "enthusiasm", "tenacity"], activities=["Civil Air Patrol", "Knights of the Altar", "Programming"])
    return flask.render_template("plain_profile.html", **{a:b.split(",") if a =="colleges" or a=="majors" or a == "skills" or a == "activities" else b for a, b in zip(vals, data[0][1:])})

@app.route("/printmyprofile")
def print_student_profile():
    if user["name"] == "3424245":
        return flask.redirect("/login")
    data = db_interaction.get_user_listing_by_email(user["email"])
    vals = ["name","personal_statement", "grade", "colleges", "majors", "skills", "activities"]

    #pdf = create_pdf(flask.render_template('plain_profile.html', **{a:b.split(",") if a =="colleges" or a=="majors" or a == "skills" or a == "activities" else b for a, b in zip(vals, data[0][1:])}))
    html = flask.render_template('plain_profile.html', **{a:b.split(",") if a =="colleges" or a=="majors" or a == "skills" or a == "activities" else b for a, b in zip(vals, data[0][1:])})
    #config = pdfkit.configuration(wkhtmltopdf="/home/jamespetullo/mysite/wkhtmltox-0.13.0-alpha-7b36694_linux-trusty-amd64.deb")
    #pdfkit.from_string(html, 'wkhtmltopdin/{}.pdf'.format(data[0][1]), options = {'page-size': 'A4', "dpi":300}, configuration=config)
    the_pdf = render_pdf(HTML(string=html))
    return the_pdf
    #return HTML(string=html).write_pdf("{}.pdf".format(data[0][1]))
    #return flask.redirect("/")
    #this works!!!!!
    #return flask.send_from_directory("/Users/jamespetullo/Downloads/MainSite-master2/wkhtmltopdin", "{}.pdf".format(data[0][1]), as_attachment=True)
@app.route("/students/<studentname>", methods=["GET", "POST"])
def search_for_student(studentname):
    '''
    if user["name"] == "3424245":
        return flask.redirect("/login")
    '''
    print("studentname", studentname)
    #user_data = db_interaction.get_user_listing(studentname)
    user_data = db_interaction.get_full_user_listing()
    print user_data
    user_data = [i for i in user_data if studentname in i[0].lower()]
    print("userdata", user_data)
    data = pickle.load(open('college_list.txt'))
    student_skills = pickle.load(open('studentskills.txt')) #/home/jamespetullo/mysite/
    student_activities = pickle.load(open('studentactivities.txt'))
    new_data = [i for i in data if len(i) != 1 and i != "X-Y-Z"]
    if flask.request.method == "POST":
        full_users = list(db_interaction.get_full_user_listing())

        first_name = flask.request.form["FirstName"]
        lastname = flask.request.form["LastName"]
        grades = flask.request.form.getlist("grade")
        schools = flask.request.form.getlist("colleges")
        majors1 = flask.request.form.getlist("majors")
        skills = flask.request.form.getlist("skill")
        activities = flask.request.form.getlist("activity")
        vals = [first_name+lastname, grades, schools, majors1, skills, activities]
        headers = ["name", "grades", "schools", "majors", "skills", "activities"]
        #vals = map(lambda x:"FALSE" if not x else x, vals)
            #print all(b in a if not isinstance(b, list) else any(c in a for c in b) for a, b in zip(i, vals))
        vals1 = {a:b for a, b in zip(headers, vals) if b}

        #possible_users = [i for i in full_users if any(b in a if not isinstance(b, list) else any(c in a for c in b) for a, b in zip(i, vals))]
        user_listing = [{a:b for a, b in zip(["name", "personalstatement", "grades", "schools", "majors", "skills", "activities"], i)} for i in db_interaction.get_full_user_listing()]

        options = [[i[c] for c in headers] for i in user_listing if any(any(d in b for d in vals1.get(a, ' ')) if isinstance(vals1.get(a, ' '), list) else vals1.get(a, 'NOTFOUND') in b in b for a, b in i.items())]



        #final_listing = [i.values() for i in user_listing if ]
        possible_users = options

        #print [[i[0],re.sub("\W+", '', i[0]).lower()+str(c+1) ,i[2], i[3].split(",")[0], i[4].split(",")[0], i[5].split(",")[0], i[6].split(",")[0]] for c, i in enumerate(possible_users)]
        if not any(all(b for b in i) if isinstance(i, list) and len(i) > 0 else i for i in vals):
            return flask.render_template("search_results.html", user_data = [[i[0],re.sub("\W+", '', i[0]).lower()+str(c+1) ,i[1], i[2].split(",")[0], i[3].split(",")[0], i[4].split(",")[0], i[5].split(",")[0]] for c, i in enumerate(possible_users)], number = len(possible_users), original_search = studentname, studentskills = student_skills, activities=student_activities, name=user["name"], colleges=new_data, majors = college_majors.majors, advanced_search_error="Please enter at least one search entry")

        if not possible_users:
            return flask.redirect("/searcherror")
        else:
            return flask.render_template("search_results.html", user_data = [[i[0],re.sub("\W+", '', i[0]).lower()+str(c+1) ,i[1], i[2].split(",")[0], i[3].split(",")[0], i[4].split(",")[0], i[5].split(",")[0]] for c, i in enumerate(possible_users)], number = len(possible_users), original_search = studentname, studentskills = student_skills, activities=student_activities, name=user["name"], colleges=new_data, majors = college_majors.majors)



    print("user_data", user_data)
     #added for test purposes only
    if not user_data:
        return flask.redirect("/searcherror")
    if len(user_data) > 1:
        #print "all the data here", [[i[0],re.sub("\W+", '', i[0]).lower() ,i[2], i[3].split(",")[0], i[4].split(",")[0], i[5].split(",")[0], i[6].split(",")[0]] for i in user_data]

        return flask.render_template("search_results.html", user_data = [[i[0],re.sub("\W+", '', i[0]).lower()+str(c+1) ,i[2], i[3].split(",")[0], i[4].split(",")[0], i[5].split(",")[0], i[6].split(",")[0]] for c, i in enumerate(user_data)], number = len(user_data), original_search = studentname, studentskills = student_skills, activities=student_activities, name=user["name"], colleges=new_data, majors = college_majors.majors)




    return flask.redirect("/student/{}".format(re.sub("\W+", '', studentname).lower()))


@app.route("/", methods=["GET", "POST"])
def home_page():
    #user_data1 = db_interaction.get_profile_info(user["email"])
    if flask.request.method == "POST":
        search_result = flask.request.form["search"]
        print("search_result: {}".format(search_result))
        return flask.redirect("/students/{}".format(re.sub("\W+", '', search_result).lower()))
    else:
        if user["name"] == "3424245":

            return flask.render_template('home.html', is_logged_in = user["name"], user_name='')




        else:

            user_data1 = db_interaction.get_profile_info(user["email"])
            full_data = db_interaction.get_user_listing_by_email(user["email"])

            flag = False
            name = None
            try:
                name = full_data[0][1]
            except IndexError:
                flag = False

            else:
                flag = True

            if flag:
                #data = db_interaction.get_user_listing(''.join(re.split("\W+", name)).lower())
                data = db_interaction.get_user_listing_by_email(user["email"])



                vals = ["name", "grade", "personal_statement", "colleges", "majors", "skills", "activities"]
                #print "data listing", {a:b.split(",") if a =="colleges" or a=="majors" or a == "skills" or a == "activities" else b for a, b in zip(vals, data[0])}
                return flask.render_template("new_user_profile.html", first_name = user["name"], user_name = full_data[0][1], full_user_name=''.join(user_data1[0][0].split()).lower(), **{a:b.split(",") if a =="colleges" or a=="majors" or a == "skills" or a == "activities" else b for a, b in zip(vals, data[0][1:])})

            return flask.render_template("first_time_user.html", user_name = user["name"])

@app.route("/login_with_google", methods=["GET", "POST"])
def google_login():
    if flask.request.method == "POST":
        email = flask.request.form["email"]
        username = flask.request.form["username"]


        return flask.redirect("/")

    else:
        return flask.render_template("google_login.html")
@app.route("/login_with_facebook", methods=["GET", "POST"])
def facebook_login():
    if flask.request.method == "POST":
        pass

    else:
        return flask.render_template("facebook_login.html")

@app.route("/login_with_twitter", methods=["GET", "POST"])
def twitter_login():
    pass

@app.route("/test", methods=["GET", "POST"])
def test_form():
    if flask.request.method == "POST":


        return flask.redirect("/")
    else:
        data = pickle.load(open('/home/jamespetullo/mysite/college_list.txt'))
        new_data = [i for i in data if len(i) != 1 and i != "X-Y-Z"]
        return flask.render_template("test.html", colleges = new_data)


@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "POST":
        email = flask.request.form["email"]
        password = flask.request.form["password"]
        user_login_attempt = db_interaction.get_user_name(email, password)
        if not db_interaction.check_user(email):
            return flask.render_template("login.html", invalid_form='Account not created', account_confirmed = '')
        if not db_interaction.is_verified(email):
            return flask.render_template("login.html", invalid_form='', account_confirmed = '', not_verified="Your account has not been confirmed")

        if not user_login_attempt:
            return flask.render_template("login.html", invalid_form='Invalid email or password', account_confirmed = '')
        else:
            global user
            user["name"] = user_login_attempt[0]
            user["email"] = email

            #print "user['email']", user["email"]
            user["username"] = db_interaction.get_username(email, password)[0]
            return flask.redirect("/")
    else:
        return flask.render_template("login.html", invalid_form='', account_confirmed = '')

@app.route("/student/<name>", methods=["GET", "POST"]) #gets name in the form jamespetullo
def show_name(name):
    '''
    if user["name"] == "3424245":
        return flask.redirect("/login")
    '''
    new_name = bool(re.findall('\d+$', name))
    the_emails = db_interaction.get_user_listing_email(re.sub("\d+$", '', name)) if new_name else db_interaction.get_user_listing_email(name)


    #data = db_interaction.get_user_listing(''.join(re.split("\W+", name)).lower()) #used to be data = db_interaction.get_user_listing(name)
    data = db_interaction.get_user_listing_by_email(user["email"]) if not new_name else [db_interaction.get_user_listing_by_email(i)[0] for i in the_emails] #used to be data = db_interaction.get_user_listing(name)

    if not data:
        #pass #here, will return template the says "user not found"
        return flask.redirect("/searcherror")

    else:
        #db_interaction.set_profile(*[user["email"], full_name, user_summary, grade, schools, majors1, skills, activities])
        data = data if len(data) == 1 else [data[int(re.findall('\d+$', name)[0])-1]]
        vals = ["name","personal_statement", "grade", "colleges", "majors", "skills", "activities"]

        #return flask.render_template("profile.html", name=, grade="12th", personal_statement="I am love programming, math, and aglorithms", colleges=["WPI", "Assumption College", "Worcester State", "MIT", "Holy Cross", "Olin College"], majors=["Computer Science", "Mathematics", "Finance"], skills=["Hard work", "enthusiasm", "tenacity"], activities=["Civil Air Patrol", "Knights of the Altar", "Programming"])
        return flask.render_template("profile.html", **{a:b.split(",") if a =="colleges" or a=="majors" or a == "skills" or a == "activities" else b for a, b in zip(vals, data[0][1:])})
@app.route("/profile", methods=["GET", "POST"])
def create_profile():
    if user["name"] == "3424245":
        return flask.redirect("/login")
    elif flask.request.method == "POST":
        full_name = flask.request.form["user_name"]
        user_summary = flask.request.form["summary"]
        grade = flask.request.form["user_grade"]
        schools = ','.join(flask.request.form.getlist("colleges"))
        majors1 = ','.join(flask.request.form.getlist("majors"))
        skills = ','.join(flask.request.form.getlist("skill"))
        activities = ','.join(flask.request.form.getlist("activity"))
        optional_skills = flask.request.form.getlist('optional_skill')
        optional_activities = flask.request.form.getlist('optional_activity')

        if optional_skills[0]:

            skills += ','+optional_skills[0].capitalize() if len(re.split(',\s*', optional_skills[0])) == 1 else ','+','.join([i.capitalize() for i in re.split(',\s*', optional_skills[0])])

            #skills += ","+re.sub(',\s*', ',', optional_skills[0])
        if optional_activities[0]:

            activities += ','+optional_activities[0].capitalize() if len(re.split(',\s*', optional_activities[0])) == 1 else ','+','.join([i.capitalize() for i in re.split(',\s*', optional_activities[0])])
        responses = [full_name, grade, user_summary, schools, majors1, skills, activities]
        issues = ["name_issue", "grade_issue", "summary_issue", "college_issue", "major_issue", "skills_issue", "interest_issue"]

        if any(not i for i in responses):
            return flask.render_template("create_profile.html", name=user["name"], **{a:'' if b else "Field left blank" for a, b in zip(issues, responses)})

        if not db_interaction.get_profile_info(user["email"]):#used to be get_profile_info(user["email"])[0]


                        #db_interaction.set_profile(*[user["email"], grade, full_name, user_summary, schools, majors1, skills, activities])
            db_interaction.set_profile(*[user["email"], full_name, user_summary, grade, schools, majors1, skills, activities])
        else:
            #print "Got here"
            db_interaction.update_profile(*[user["email"], full_name, user_summary, grade, schools, majors1, skills, activities])

        #print db_interaction.get_profile_info(user["email"])




            #return flask.render_template("create_profile.html", name=user["name"], colleges=new_data, majors = college_majors.majors, major_issue="Please select three unique majors")
        #return flask.redirect("/student/{}".format(re.sub("\W+", '', full_name).lower())) #later, will redirect to main profile and dislay info on profile card
        return flask.redirect("/")
    else:
        data = pickle.load(open('/home/jamespetullo/mysite/college_list.txt'))
        student_skills = pickle.load(open('/home/jamespetullo/mysite/studentskills.txt'))
        student_activities = pickle.load(open('/home/jamespetullo/mysite/studentactivities.txt'))
        new_data = [i for i in data if len(i) != 1 and i != "X-Y-Z"]
        if not db_interaction.get_user_listing_by_email(user["email"]):

            return flask.render_template("create_profile.html", studentskills = student_skills, activities=student_activities, name=user["name"], colleges=new_data, majors = college_majors.majors, current_schools='', current_majors='', current_activities='', current_skills='', user_full_name = '', user_summary='', user_grade = '')

        user_data = db_interaction.get_user_listing_by_email(user["email"])[0]
        #current_schools='', current_majors='', current_activities='', current_skills='', user_full_name = '', user_summary='', user_grade = ''
        #vals = ["name", "grade", "personal_statement", "colleges", "majors", "skills", "activities"]
        vals = ["user_full_name", "user_grade", "user_summary", "current_schools", "current_majors", "current_skills", "current_activities"]
        data1 = {a:b.split(",") if a =="current_schools" or a=="current_majors" or a == "current_skills" or a == "current_activities" else b for a, b in zip(vals, user_data[1:])}
        #print "data1 here", data1
        #print "user's name", user["name"]
        return flask.render_template("create_profile.html", studentskills = student_skills, activities=student_activities, name=user["name"], colleges=new_data, majors = college_majors.majors, **{a:b.split(",") if a =="current_schools" or a=="current_majors" or a == "current_skills" or a == "current_activities" else b for a, b in zip(vals, user_data[1:])})

@app.route("/signup", methods=["GET", "POST"])
def user_signin():
    if flask.request.method == "POST":
        email = flask.request.form["email"]
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        name = flask.request.form["name"]
        age = flask.request.form["age"]
        lastname = flask.request.form["lastname"]
        password2 = flask.request.form['password2']
        full_listing = [email, username, password, password2, name, lastname]
        full_listing1 = [name, lastname, email, password, username, "no"]
        if not name.isalpha() or not lastname.isalpha():
            return flask.render_template("user_login.html", incorrect_username_type="First name and last name must consist of alphabetic characters only", username_taken = '',email_taken='', password_issue = '', age_issue="Please enter a number", incomplete="")

        if not age.isdigit():
            return flask.render_template("user_login.html", username_taken = '',email_taken='', password_issue = '', age_issue="Please enter a number", incomplete="")
        if len([i for i in full_listing if i]) != len(full_listing):
            return flask.render_template("user_login.html", username_taken = '', email_taken = '', password_issue = '', age_issue="", incomplete="Some forms are not filled out")

        if int(age) < 13 or int(age) > 20:
            return flask.render_template("user_login.html", username_taken = '', email_taken = '', password_issue = '', age_issue="You must be older than 13 years", incomplete="")

        if password != password2:
            return flask.render_template("user_login.html", username_taken = '', email_taken = '', password_issue = 'Passwords do not match', age_issue="", incomplete="")
        if not re.findall("^[\w\W]+@[a-zA-Z]+\.[a-zA-Z]+$", email):
            return flask.render_template("user_login.html", username_taken = '', invalid_email = "incorrect email format", email_taken = '', password_issue = '', age_issue="", incomplete="")
        if len(password) < 8 or len([i for i in password if i.isdigit()]) < 1 or len([i for i in password if i.isupper()]) < 1:
            return flask.render_template("user_login.html", username_taken = '', invalid_email = "", complexity="Password must consist of at least One uppercase letter, one digit, and be at least 8 characters long",email_taken = '', password_issue = '', age_issue="", incomplete="")

        if db_interaction.check_user(email):
            return flask.render_template("user_login.html", username_taken = '', email_taken = "email already taken", password_issue = '', age_issue="", incomplete="")
        db_interaction.add_user(*full_listing1)
        form_db.add_user(email)
        token = ts.dumps(email, salt='email-confirm-key')
        #print "token", token
        confirm_url = flask.url_for('confirm_email', token=token, _external=True)
        send_confirmation_email(name, email, confirm_url)
        return flask.render_template("/prompt_email_confirm.html")
    else:
        return flask.render_template("user_login.html", username_taken = '', email_taken = '', password_issue = '')

if __name__=="__main__":
	app.debug = True
app.run()
