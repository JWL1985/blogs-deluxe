from flask import Flask, request, redirect, render_template, session, flash 
from flask_sqlalchemy import SQLAlchemy 
import os 
import re 

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:Bulova23@localhost:8889/blogz"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
app.secret_key = "secret-key"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id")) 

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(25))
    email = db.Column(db.String(50), unique=True)
    blogs = db.relationship("Blog", backref = "owner")

    def __init__(self, username, email, password):
        self.username = username
        self.password = password
        self.email = email 

#def run(string):

def validate_login(username, email, password):
    username = username
    email = email
    password = password
    user = User.query.filter_by(email=email).first()
    if user.password == password:
        return True 
    else:
        flash("Incorrect password for username")
        return False


def validate_signup(username, email, password, verify):
    special_chars = re.compile("[!@#$%^&*()]")
    errors = {
        "username_error": "",
        "email_error": "",
        "password_error1": "",
        "password_error2": "",
        "verify_error": "",
    }
    if len(username) > 25 or len(username) < 5:
        errors["username_error"] = "Username must be between 5-25 characters"
        flash(errors["username_error"], "errors")
    if "." and "@" not in email:
        errors["email_error"] = "Please enter a valid email"
        flash(errors["email_error"], "errors")
    if (len(password) < 5 or len(password) > 25) or special_chars.search(password)==None:
        errors["password_error1"] = "Password must be between 5-25 characters and must contain at least one special character"
        flash(errors["password_error1"], "errors")
    if password != verify:
        errors["password_error2"] = "Please verify password"
        flash(errors["password_error2"], "errors")
    if errors:
        return redirect("/signup")
    else:
        return True


@app.before_request
def require_login():
    allowed_routes = ["login", "signup"]
    if request.endpoint not in allowed_routes and "email" not in session:
        return redirect("/login")

@app.route("/")
def index():
    del session["email"]
    return redirect("/login")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()
        if user:
            if validate_login(username, email, password):
                session["email"] = email 
                user_id = user.id 
                blogs = Blog.query.filter_by(owner_id=user_id).all()                
                return render_template("home_page.html", blogs=blogs)
                #TODO - route them to their user page (or /blog page)
            else:
                #flash("Incorrect Password")
                return redirect("/signup")
                #TODO - display errors and redirect to /login page


@app.route("/signup", methods = ["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        verify = request.form["verify-password"]
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()
        if user:
            if validate_login(username, email, password):
                session["email"] = email 
                user_id = user.id 
                blogs = Blog.query.filter_by(owner_id=user_id).all()                
                return render_template("home_page.html", blogs=blogs)
                #TODO - start session for user
                #TODO - route them to their user page (or /blog page)
            else:
                return render_template("/signup.html")
                #TODO - display errors and redirect to /login page
        else:
            if validate_signup(username, email, password, verify):
                user = User(username, email, password)
                db.session.add(user)
                db.session.commit()
                #user_id = user.id
                session["email"] = email #TODO - start session for user  
                user_id = user.id               
                blogs = Blog.query.filter_by(owner_id=user_id).all()
                return render_template("home_page.html", blogs=blogs)
    else:
        return render_template("/signup.html")

@app.route("/blog")
def blog():
    title = "Build A Blog"
    blogs = Blog.query.all()
    return render_template("home_page.html", title=title, blogs=blogs)

@app.route("/blogpost", methods=["POST", "GET"])
#blog_id = request.form["blog-id"]
def blog_post(): #TODO- set up so blog_post() blog_id as an argument
    
    if request.method == "GET":
        blog_id = request.args.get("blog_id")
        owner_id = request.args.get("owner_id")
        email = session["email"]
        blogs = Blog.query.filter_by(id=blog_id).all()
        return render_template("display_blog.html", blogs=blogs)
    else:
        return render_template("display_blog.html")

@app.route("/newpost")
def new_post():
    blog_title = request.args.get("blog_title")
    blog_body = request.args.get("blog_body")
    email = session["email"]
    owner = User.query.filter_by(email=email).first()
    if blog_title and blog_body:
        blog = Blog(blog_title, blog_body, owner)
        db.session.add(blog)
        db.session.commit()
        blog_id = str(blog.id)
        owner_id = str(owner.id) 
        #query_string = blog_title + blog_body + id
        return redirect("/blogpost?blog_id="+blog_id+"owner_id="+owner_id)
    else:
        #flash("Please enter valid Title & Blog Post")
        return render_template("new_post.html")

@app.route("/logout")
def logout():
    del session["email"]
    return redirect("/login")

#@app.route("/newpost-validate", methods = "POST")
#def validate_post():
#    blog_title = request.form["blog_title"]
#    blog_body = request.form["blog_body"]
#    if not blog_title or not blog_body:
#        flash("Please Enter A Valid Title & Blog Post", "error")
#        return render_template("new_post.html", title=blog_title, body=blog_body) 
#    else:
#        return True
        #blog = Blog(blog_title, blog_body,)
        #db.session.add(blog)
        #db.session.commit()
        #id = str(blog.id) 
        #query_string = blog_title + blog_body + id
        #return redirect("/blogpost?id="+id)
        #return redirect("/newpost?"+query_string)

if __name__ == "__main__":
    app.run()


