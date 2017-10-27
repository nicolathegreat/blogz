from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask (__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True 
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120))
    content = db.Column(db.Text())

    def __init__(self,name, content):
        self.name = name
        self.content=content

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
         



@app.route('/', methods=['POST', 'GET'])
def index():
    blogs = Blog.query.all()
    return render_template('blogposts.html',title="Blogs!", 
        blogs=blogs)

@app.route('/blog', methods=['POST','GET'])
def blog():
    
    id=request.args.get ('blogid')
    blogs=Blog.query.filter_by(id=id).first()
    return render_template('blog.html',blogpost=blogs)



if __name__ == '__main__':
    app.run()