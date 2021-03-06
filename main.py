from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcs&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_body = db.Column(db.String(300))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pub_date = db.Column(db.DateTime)

    def __init__(self, blog_title, blog_body, owner, pub_date=None):
        self.blog_title = blog_title
        self.blog_body = blog_body
        self.owner = owner
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

@app.before_request
def require_login():
    allowed_routes = ['login', 'main-blog-listings', 'index', 
    'signup', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():

    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/blog', methods=['POST', 'GET']) 
def blog_listing():
    new_id = request.args.get('id')
    new_user = request.args.get('user')

    if not new_id and not new_user:
        blogs = Blog.query.order_by(Blog.pub_date).all() #view all blogs by all users
        return render_template("main-blog-listings.html", 
        blogs=blogs, title="Build A Blog!")
    
    if not new_user:  #view one blog by one user
        blog = Blog.query.filter_by(id=new_id).first()
        my_user = User.query.filter_by(id=blog.owner_id).first()
        return render_template('single_blog_view.html', 
        blog=blog, user=my_user)
    
    else:   #view all blogs by one user
        
        u_id = User.query.filter_by(username=new_user).first()
        blogs = Blog.query.filter_by(owner_id=u_id.id).all()
        return render_template('view_users_blogs.html', 
        blogs=blogs, user=u_id)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if len(username) <= 3:
            flash('Invalid username, must be at least 3 characters')
            return redirect('/signup')

        if len(password) <= 3:
            flash('Invalid password, must be at least 3 characters')
            return redirect('/signup')

        if password != verify:
            flash('Passwords do not match')
            return redirect('/signup')

        existing_user = User.query.filter_by(username=username).first()

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost') 

        else:
            flash('That username already exists')
            return redirect('/signup')

    return render_template('signup.html')



@app.route('/login', methods=['POST', 'GET'])
def login():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user.username != username:
            flash('No such username', 'error')
            return redirect('/login')
                        
        if not check_pw_hash(password, user.pw_hash):
            flash('Incorrect password')
            return redirect('/login')  

        else:
            session['username'] = username
            flash("Logged In")
            return redirect('/newpost')


    return render_template('login.html')



@app.route('/newpost', methods=['POST', 'GET']) #create a blog
def new_post():

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']

        this_id = User.query.filter_by(username=session['username']).first()

        blog_title_error = ""
        blog_body_error = ""

        if blog_title == "":
            blog_title_error = "Please fill in the title"

        if blog_body == "":
            blog_body_error = "Please fill in the body"

        if not blog_title_error and not blog_body_error:


            new_blog = Blog(blog_title, blog_body, this_id)
            db.session.add(new_blog)
            db.session.commit()

            new_id = new_blog.id

            return redirect('/blog?id={0}'.format(new_id))
        
        else:
            return render_template("add-new-blog.html", 
            blog_title_error=blog_title_error, 
            blog_body_error=blog_body_error,
            title="New Entry")

    return render_template('add-new-blog.html', title="New Entry")

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')











if __name__ == '__main__':
    app.run()