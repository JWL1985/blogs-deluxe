from flask import Flask, request, redirect, render_template, session, flash 
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://build-a-blog:Bulova23@localhost:8889/build-a-blog"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
app.secret_key = "secret-key"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route("/blog")
def index():
    title = "Build A Blog"
    return render_template("base.html", title=title)

@app.route("/blogpost", methods=["POST", "GET"])
#blog_id = request.form["blog-id"]
def blog_post(): #TODO- set up so blog_post() blog_id as an argument
    if request.method == "POST":
        blog_title = request.form["blog_title"]
        blog_body = request.form["blog_body"]
        blog = Blog(blog_title, blog_body)
        db.session.add(blog)
        db.session.commit()

        blog_id = blog.id 


    
    return render_template("display_blog.html", blog_title=blog_title, blog_body=blog_body)

@app.route("/newpost")
def new_post():
    return render_template("new_post.html")

if __name__ == "__main__":
    app.run()


