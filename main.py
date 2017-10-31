from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, owner):
        self.name = name
        self.completed = False
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(40))
    tasks = db.relationship('Task', backref='owner')

    def __init__(self, email, password, username):
        self.email = email
        self.password = password
        self.username = username

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120))
    content = db.Column(db.Text())
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    def __init__(self,name, owner_id, content):
        self.name = name 
        self.owner_id = owner_id
        self.content=content

@app.before_request
def require_login():
    allowed_routes = ['login','blog','signup']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def index():

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        task_name = request.form['task']
        new_task = Task(task_name, owner)
        db.session.add(new_task)
        db.session.commit()

    tasks = Task.query.filter_by(completed=False,owner=owner).all()
    completed_tasks = Task.query.filter_by(completed=True,owner=owner).all()
    return render_template('todos.html',title="Get It Done!", 
        tasks=tasks, completed_tasks=completed_tasks)

    # blogs = Blog.query.all()
    # return render_template('blogposts.html',title="Blogs!", 
    #     blogs=blogs)


@app.route('/newblog', methods=['POST', 'GET'])
def newblog():

    no_name=""
    no_content=""
    no_anything=""

    if request.method == 'POST':
        blog_name = request.form['new_blog_title']
        blog_content = request.form['new_blog_post']
        new_blog = Blog(blog_name, blog_content)

    

        if blog_name=="":
            no_name = "Please enter a title"
        if blog_content=="":
            no_content="Please make a blog to go with your beautiful title"

        if not no_name and not no_content:
            db.session.add(new_blog)
            db.session.commit()
            id=new_blog.id
            print(id)
            return redirect ('/blog?blogid='+str(id))
        else:
            return render_template('newblogpost.html', no_name=no_name, no_content=no_content)

    else:
        return render_template ('newblogpost.html', title="New Blog Post")
         

@app.route('/blog', methods=['POST','GET'])
def blog():
    
    if (id=request.args.get ('blogid')):
      blogs=Blog.query.filter_by(id=id).first()
      return render_template('blog.html',blogpost=blogs)
    else:
      return redirect('/')  

@app.route('/user', methods=['POST','GET'])
def users():
    
    if (id=request.args.get ('userid')):
      users=User.query.filter_by(id=id).first()
      return render_template('blog.html',blogpost=blogs)
    else:
      return redirect('/')  


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/newpost')
        elif not user:
            flash('this user does not exist','error')
            return render_template('login.html')
            
        elif user:
            flash('User password incorrect, or user does not exist', 'error')
            return render_template('login.html')
        else:
            return redirect('/signup')



@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        verify = request.form['verify']
        email_fail = false
        username_fail = false
        password_fail = false
        test = re.compile('^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$',re.I)              
        if not test.search(email):
            email_fail = true
            flash('This email address is invalid.')
        test = re.compile('[A-Za-z_0-9]{3,20}',re.I)
        if not test.search(username):
            username_fail = true
            flash('username is invalid. Please enter a username between three(3) and twenty (20) characters using only A-Z, a-z, 0-9, and _')
        test = re.compile('[A-Za-z_0-9]{3,20}',re.I)
        if (password != verify) or not test.search(password):
            password_fail = true
            flash('password is invalid, it must be at least 3 characters, and no more than 40')
        if (username_fail or password_fail or email_fail):
            return redirect('/signup')

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password, username)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['email']
    del session['username']
    return redirect('/')


@app.route('/delete-task', methods=['POST'])
def delete_task():

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()






