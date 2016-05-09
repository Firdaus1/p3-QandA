from init import db, app


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20))
    pw_hash = db.Column(db.String(64))


class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50))
    content = db.Column(db.String(50))
    time = db.Column(db.DateTime)
    n_answer = db.Column(db.Integer, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('Users', backref='questions')


class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(100))
    time = db.Column(db.DateTime)
    total_up_vote = db.Column(db.Integer)
    total_down_vote = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    author = db.relationship('Users', backref='answers')
    question = db.relationship('Questions', backref='answers')

class QuestionTag(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag = db.Column(db.String(50))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    question = db.relationship('Questions', backref='tags')

class Votes(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    up_vote = db.Column(db.Integer)
    down_vote = db.Column(db.Integer)
    voter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'))
    voter = db.relationship('Users', backref='votes')
    answer = db.relationship('Answers', backref='votes')

db.create_all(app=app)
