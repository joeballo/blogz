from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8888/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_body = db.Column(db.String(300))

    def __init__(self, blog_title):
        self.blog_title = blog_title



@app.route('/') #first visit
def index():

    return render_template('add-new-blog.html')


@app.route('/newpost', methods=['POST', 'GET']) #create a blog
def index():


    db.session.add()
    db.session.commit()
    
    return render_template('add-new-blog.html')


@app.route('/blog') # view blogs
def blog_listing():


    return render_template ('main-blog-listing.html')







if __name__ == '__main__':
    app.run()