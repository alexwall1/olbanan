import json
import urllib
import random

from flask import Flask, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from config import profile, key, DATABASE_URI, DEBUG, PROJECT_DIR

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
db = SQLAlchemy(app)


class Bar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eniro_id = db.Column(db.Integer, nullable=False)
    vote = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    facebook = db.Column(db.String(255), nullable=True)
    homepage = db.Column(db.String(255), nullable=True)
    company_reviews = db.Column(db.String(255), nullable=True)
    station = db.Column(db.String(255), nullable=False)
    line = db.Column(db.String(255), nullable=False)
    zone = db.Column(db.Integer, nullable=False)


def build_query(latitude, longitude, search_word='restaurang', max_distance='300'):
    return urllib.urlencode({
        'profile': profile,
        'key': key,
        'country': 'se',
        'version': '1.1.3',
        'search_word': search_word,
        'geo_area': 'stockholm',
        'latitude': latitude,
        'longitude': longitude,
        'max_distance': max_distance})


@app.route("/")
def root():
    return render_template('base.html')


@app.route("/bar")
def bar():
    zone = request.args.get('zone')
    if not zone:
        abort(404)
    bar_found = None
    with open(PROJECT_DIR + 'stations.json') as f:
        all_stations = json.load(f)
        stations = [x for x in all_stations if x['zone'] == zone]
        n = len(stations)
        c = 0
        while c < 3 and not bar_found:
            c += 1
            r1 = random.randrange(0, n)
            params = build_query(stations[r1]["latitude"], stations[r1]["longitude"])
            u = urllib.urlopen("https://api.eniro.com/cs/proximity/basic?%s" % params)
            data = u.read()
            obj = json.loads(data)
            hits = obj['totalHits']
            if hits > 0:
                r2 = random.randrange(0, min(hits, 25))
                bar_found = obj['adverts'][r2]
                bar_found['station'] = stations[r1]
        if not bar_found:
            abort(404)
    return json.dumps(bar_found, indent=4)


@app.route("/vote", methods=["POST"])
def vote():
    _eniro_id = request.form.get("eniroId") or abort(400)
    _vote = request.form.get("vote") or abort(400)

    vote = 0
    if _vote == "1":
        vote = 1
    elif _vote == "-1":
        vote = -1
    else:
        abort(400)

    r = Bar.query.filter_by(eniro_id=_eniro_id).first()
    if r:
        r.vote += vote
    else:
        b = Bar()
        b.vote = vote
        b.eniro_id = _eniro_id
        b.name = request.form.get('name')
        b.facebook = request.form.get('facebook')
        b.homepage = request.form.get('homepage')
        b.company_reviews = request.form.get('companyReviews')
        b.station = request.form.get('station')
        b.line = request.form.get('line')
        b.zone = int(request.form.get('zone'))
        db.session.add(b)
    db.session.commit()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == "__main__":
    app.run(debug=DEBUG)
