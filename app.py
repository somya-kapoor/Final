"""Flask Login Example"""

from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, create_engine, Table
import json
import hashlib
import uuid
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class User(db.Model):
    """ Create user table"""

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80))
    password = db.Column(db.String(1024))
    password_salt = db.Column(db.String(1024))

    def __init__(self, username, password, password_salt):
        self.username = username
        self.password = password
        self.password_salt = password_salt


class Story(db.Model):
    """ Create story table"""

    id = db.Column(db.Integer, primary_key=True)

    story_title = db.Column(db.String(80))
    story_body = db.Column(db.String(8000))
    story_reader_list = db.Column(db.String(80000))

    def __init__(self, story_title, story_body, story_reader_list):
        self.story_title = story_title
        self.story_body = story_body
        self.story_reader_list = story_reader_list


def convert_story_to_json(story):
    read_count = 0
    if story.story_reader_list != "null":
        read_count = len(set(json.loads(story.story_reader_list)))
    return {
        "story_link": "/story/" + str(story.id),
        "story_key": "room-" + str(story.id),
        "story_title": story.story_title,
        "story_body": story.story_body,
        "story_read_count": read_count
    }


def get_stories():
    stories = Story.query.limit(100).all()
    stories_json = [
        convert_story_to_json(el)
        for el in stories
    ]
    return stories_json


def get_story(story_id, for_user):
    story = Story.query.filter_by(id=story_id).first()
    user_reader_list = story.story_reader_list

    if user_reader_list == "null" or user_reader_list is None:
        user_reader_list = [for_user]
    else:
        user_reader_list = json.loads(user_reader_list)
        user_reader_list.extend([for_user])
    
    user_reader_list = list(set(user_reader_list))
    story.story_reader_list = json.dumps(user_reader_list)
    # save to db
    db.session.commit()
    return convert_story_to_json(story)


@app.route('/', methods=['GET', 'POST'])
def home():
    """ Session control"""
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return render_template('index.html', data=get_stories())


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Form"""
    if request.method == 'GET':
        return render_template('login.html')
    else:
        try:
            name = request.form['username']
            passw = request.form['password']
            data = User.query.filter_by(username=name).first()
            if data is not None:
                hashed_password = generate_hashed_password(
                    passw, data.password_salt)
                if hashed_password == data.password:
                    session['logged_in'] = True
                    session['logged_user'] = name
                    return redirect(url_for('home'))

        except:
            logging.warn("something went wrong while logging in")
            return "Unable to log you in"
    return 'Unable to log you in'


@app.route('/story/<story_id>', methods=['GET'])
def get_story_render(story_id):
    """ Session control"""
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return render_template('story.html', data=get_story(story_id, session['logged_user']))


def generate_hashed_password(password, password_salt):
    return hashlib.sha512((password + password_salt).encode('utf-8')).hexdigest()


@app.route('/register/', methods=['GET', 'POST'])
def register():
    """Register Form"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first() is not None:
            return "username already exists"
        password_salt = uuid.uuid4().hex
        hashed_password = generate_hashed_password(password, password_salt)
        new_user = User(
            username=request.form['username'],
            password=hashed_password,
            password_salt=password_salt
        )  
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html')
    return render_template('register.html')


@app.route("/logout")
def logout():
    """Logout Form"""
    session['logged_in'] = False
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.debug = True
    db.create_all()
    app.secret_key = "42342354"
    app.run(host='0.0.0.0')
