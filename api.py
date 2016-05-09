import time
import flask
from init import app, db
import models


@app.route('/api/upvote', methods=['POST'])
def upvote():
    if 'auth_user' not in flask.session:
        flask.abort(403)
    user_id = models.Users.query.filter_by(name=flask.session.get('auth_user')).first().id
    if flask.request.form['_csrf_token'] != flask.session['csrf_token']:
        flask.abort(400)

    answer_id = flask.request.form['answer_id']
    want_star = flask.request.form['want_star'] == 'true'
    answer = models.Answers.query.filter_by(id=answer_id).first()
    star = models.Votes.query.filter_by(answer_id=answer_id,
                                        voter_id=user_id).first()
    if star is None:
        star = models.Votes()
        star.up_vote = 1
        star.voter_id = user_id
        star.answer_id = answer_id
        answer.total_up_vote += 1
        db.session.add(star)
        db.session.commit()
        return flask.jsonify({'result': 'ok'})
    else:
        if want_star:
            if star.up_vote is None and star.down_vote is None:
                star.up_vote = 1
                answer.total_up_vote += 1
                db.session.commit()
                return flask.jsonify({'result': 'ok'})
            elif star.up_vote is None and star.down_vote == 1:
                return flask.jsonify({'result': 'already-vote-down'})
        else:
            star.up_vote = None
            answer.total_up_vote -= 1
            db.session.commit()
            return flask.jsonify({'result': 'ok'})


@app.route('/api/downvote', methods=['POST'])
def downvote():
    if 'auth_user' not in flask.session:
        flask.abort(403)
    user_id = models.Users.query.filter_by(name=flask.session.get('auth_user')).first().id
    if flask.request.form['_csrf_token'] != flask.session['csrf_token']:
        flask.abort(400)
    answer_id = flask.request.form['answer_id']
    want_star = flask.request.form['want_star'] == 'true'
    answer = models.Answers.query.filter_by(id=answer_id).first()
    star = models.Votes.query.filter_by(answer_id=answer_id,
                                        voter_id=user_id).first()
    if star is None:
        star = models.Votes()
        star.down_vote = 1
        star.voter_id = user_id
        star.answer_id = answer_id
        answer.total_down_vote += 1
        db.session.add(star)
        db.session.commit()
        return flask.jsonify({'result': 'ok'})
    else:
        if want_star:
            if star.down_vote is None and star.up_vote is None:
                star.down_vote = 1
                answer.total_down_vote += 1
                db.session.commit()
                return flask.jsonify({'result': 'ok'})
            elif star.down_vote is None and star.up_vote == 1:
                return flask.jsonify({'result': 'already-vote-up'})
        else:
            star.down_vote = None
            answer.total_down_vote -= 1
            db.session.commit()
            return flask.jsonify({'result': 'ok'})
