from flask import render_template, request, redirect
from app import app
import subprocess

@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Dr. Evil'} # fake user
    posts = [  # fake array of posts
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', user=user, posts=posts)


@app.route("/login/", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        name = request.form['login']
        password = request.form['password']
        return redirect(url_for('test', name=name, password=password))
    else:
        return render_template('login.html')


@app.route("/test/", methods=['POST'])
def test():
    name = request.form['login']
    password = request.form['password']
    input = ['/home/tgadola/AlanParsonsProject/app/test.py', name, password]
    a = subprocess.Popen(input, stdout = subprocess.PIPE,
                            stderr=subprocess.PIPE,
                           stdin=subprocess.PIPE)
    out = a.communicate()
    return out
