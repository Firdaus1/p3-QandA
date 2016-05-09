import flask
import base64
import os
import models
import bcrypt
import datetime
from sqlalchemy.orm import joinedload
from init import app, db

###########################################################################################################
#       User section!!!
#
###########################################################################################################
@app.before_request
def setup_user():
    if 'auth_user' in flask.session:
        user = models.Users.query.get(flask.session['auth_user'])
        # save the user in `flask.g`, which is a set of globals for this request
        flask.g.user = user


@app.route('/log', methods=['POST'])
def login():
    user = flask.request.form['user']
    password = flask.request.form['password']
    userinfo = models.Users.query.filter_by(name=user).first()
    if userinfo:
        p = bcrypt.hashpw(password.encode('utf8'), userinfo.pw_hash)
        if userinfo.pw_hash == p:
            flask.session['auth_user'] = user
            return flask.redirect(flask.request.form['url'], code=303)
        else:
            return flask.render_template('index.html', check=2)
    else:
        return flask.render_template('index.html', check=1)


@app.route('/sign')
def sign():
    return flask.render_template('createuser.html')


@app.route('/createuser', methods=['POST'])
def createuser():
    user = flask.request.form['user']
    if user == '':
        return flask.render_template('createuser.html', check=0)
    password = flask.request.form['password']
    confirm = flask.request.form['confirm']
    finduser = models.Users.query.filter_by(name=user).first()
    if finduser:
        return flask.render_template('createuser.html', check=1, username=user)
    if password != confirm:
        return flask.render_template('createuser.html', check=2)
    new_user = models.Users()
    new_user.name = user
    new_user.pw_hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(15))
    db.session.add(new_user)
    db.session.commit()

    flask.session['auth_user'] = user
    return flask.redirect('/', code=303)


@app.route('/logout')
def logout():
    del flask.session['auth_user']
    return flask.redirect(flask.request.args.get('url', '/'))


###########################################################################################################
#       Error section!!!
#
###########################################################################################################
@app.errorhandler(404)
def not_found(err):
    return (flask.render_template('404.html', path=flask.request.path), 404)


###########################################################################################################
#       Index page section!!!
#
###########################################################################################################
@app.route('/')
def mainpage():
    if 'csrf_token' not in flask.session:
        flask.session['csrf_token'] = base64.b64encode(os.urandom(32)).decode('ascii')
    auth_user = flask.session.get('auth_user', None)
    questions = models.Questions.query.all()
    pages = len(questions)
    index = 0
    resp = flask.make_response(flask.render_template('index.html', auth_user=auth_user,
                                                     csrf_token=flask.session['csrf_token'],
                                                     questions=questions, pageindex=index,
                                                     pages=pages))
    return resp


@app.route('/<int:page>')
def pageindex(page):
    index = page
    questions = models.Questions.query.all()
    pages = len(questions)
    return flask.render_template('index.html', csrf_token=flask.session['csrf_token'],
                                 questions=questions, pageindex=index, pages=pages)


###########################################################################################################
#       Create questions section!!!
#
###########################################################################################################
@app.route('/askquestion')
def askquestion():
    return flask.render_template('addquestion.html', _csrf_token=flask.session['csrf_token'])


@app.route('/addquestion', methods=['POST'])
def addquestion():
    question = models.Questions()
    if 'auth_user' not in flask.session:
        app.logger.warn('unauthorized user tried to question')
        flask.abort(401)
    if flask.request.form['_csrf_token'] != flask.session['csrf_token']:
        app.logger.debug('invalid CSRF token in question form')
        flask.abort(400)

    title = flask.request.form['title']
    content = flask.request.form['content']
    alltags = flask.request.form['tags']

    if title == '' or content == '':
        return flask.render_template('addquestion.html', _csrf_token=flask.session['csrf_token'],
                                     errorms=1)
    checkquestion = models.Questions.query.filter_by(title=title).first()
    if checkquestion:
        return flask.render_template('addquestion.html', _csrf_token=flask.session['csrf_token'],
                                     errorms=2, content=content)

    for tag in alltags.split(','):
        if not tag.strip():
            continue
        tags = models.QuestionTag()
        tags.tag = tag.strip()
        question.tags.append(tags)

    question.title = title
    question.content = content
    question.time = datetime.datetime.today().replace(microsecond=0)

    author_id = models.Users.query.filter_by(name=flask.session.get('auth_user')).first().id
    question.author_id = author_id
    db.session.add(question)
    db.session.commit()

    return flask.redirect(flask.url_for('question', qid=question.id), code=303)


###########################################################################################################
#       Question detail page!!!
#
###########################################################################################################
@app.route('/question/<int:qid>')
def question(qid):
    question = models.Questions.query.get(qid)
    if 'auth_user' not in flask.session:
        user_id = None

    else:
        user_id = models.Users.query.filter_by(name=flask.session.get('auth_user')).first().id

    #answers = models.Answers.query.join(models.Votes, models.Answers.id == models.Votes.answer_id).
    # filter_by(question_id=question.id)
    allanswers = []
    answers = models.Answers.query.filter_by(question_id=question.id)
    for answer in answers:
        if user_id is None:
            upvote = False
            downvote = False
        else:
            status = models.Votes.query.filter_by(answer_id=answer.id, voter_id=user_id).first()
            if status is None:
                upvote = False
                downvote = False
            else:
                upvote = status.up_vote is not None
                downvote = status.down_vote is not None

        allanswers.append({"answer": answer, "upvote": upvote, "downvote": downvote,
                           "totalvote": answer.total_up_vote - answer.total_down_vote})

        allanswers = sorted(allanswers, key=lambda r: r['totalvote'])

    return flask.render_template('questionpage.html', question=question, answers=allanswers,
                                 _csrf_token=flask.session['csrf_token'],user_id=user_id)


@app.route('/addanswer', methods=['POST'])
def addanswer():

    if 'auth_user' not in flask.session:
        app.logger.warn('unauthorized user tried to question')
        flask.abort(401)
    if flask.request.form['_csrf_token'] != flask.session['csrf_token']:
        app.logger.debug('invalid CSRF token in question form')
        flask.abort(400)

    qid = flask.request.form['question_id']
    content = flask.request.form['content']

    if not content:
        return flask.redirect(flask.url_for('question', qid=qid), code=303)

    answer = models.Answers()
    answer.content = content
    answer.time = datetime.datetime.today().replace(microsecond=0)
    answer.total_up_vote = 0
    answer.total_down_vote = 0
    answer.question_id = int(qid)

    author = flask.session.get('auth_user', None)
    answer.author_id = models.Users.query.filter_by(name=author).first().id
    models.Questions.query.filter_by(id=qid).first().n_answer += 1

    db.session.add(answer)
    db.session.commit()

    return flask.redirect(flask.url_for('question', qid=qid), code=303)

###########################################################################################################
#       Tag page!!!
#
###########################################################################################################
@app.route('/tags/<tag>')
def tagpage(tag):
    q = models.QuestionTag.query.options(joinedload(models.QuestionTag.question))
    alltags = q.filter_by(tag=tag).all()
    questions = [at.question for at in alltags]
    return flask.render_template('tag.html', tag=tag, questions=questions)
