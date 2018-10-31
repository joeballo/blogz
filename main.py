from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_body = db.Column(db.String(300))

    def __init__(self, blog_title, blog_body):
        self.blog_title = blog_title
        self.blog_body = blog_body

@app.route('/blog') 
def blog_listing():
    num = request.args.get('id')
    if not num:
        blogs = Blog.query.all() #view all blogs
        return render_template("main-blog-listings.html", blogs=blogs, title="Build A Blog!")
    else:
            #view single blog
        blog = Blog.query.filter_by(id=num).first()
        return render_template('single_blog_view.html', 
        blog=blog)


@app.route('/newpost', methods=['POST', 'GET']) #create a blog
def new_post():

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']

        blog_title_error = ""
        blog_body_error = ""

        if blog_title == "":
            blog_title_error = "Please fill in the title"

        if blog_body == "":
            blog_body_error = "Please fill in the body"

        if not blog_title_error and not blog_body_error:


            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()

            #blogs = Blog.query.filter_by(id).first()
            new_id = new_blog.id

            return redirect('/blog?id={0}'.format(new_id))
        
        else:
            return render_template("add-new-blog.html", 
            blog_title_error=blog_title_error, 
            blog_body_error=blog_body_error,
            title="New Entry")

    return render_template('add-new-blog.html', title="New Entry")












if __name__ == '__main__':
    app.run()