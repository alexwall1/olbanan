# -*- coding: utf-8 -*-

import json
import urllib
import random
import os

from flask import Flask, render_template, request, abort
from database import db_session
from models import Bar
from config import profile, key

app = Flask(__name__)

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

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


@app.route("/ranking")
def ranking():
    bars = Bar.query.order_by(Bar.vote.desc()).all()
    return render_template('ranking.html', bars=bars)


@app.route("/")
def root():
    return render_template('generate.html')


@app.route("/bar")
def bar():
    zone = request.args.get('zone')
    if not zone or not request.args.get('line'):
        abort(400)

    line = ["Alla", "Gröna", "Röda", "Blå"][int(request.args.get('line')) - 1]

    bar_found = None
    bad_bars = [x for (x,) in db_session.query(Bar.eniro_id).filter(Bar.vote < 0).all()]

    with open(os.path.join(PROJECT_DIR,'stations.json')) as f:
        all_stations = json.load(f)
        stations = [x for x in all_stations if x["zone"] == zone and (line == "Alla" or line.decode('utf-8') in x["line"])]
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
                eniro_id = long(bar_found['eniroId'])
                if eniro_id not in bad_bars:
                    bar_found['station'] = stations[r1]
                else:
                    bar_found = None
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
        b.zone = int(request.form.get('zone'))
        db_session.add(b)
    db_session.commit()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == "__main__":
    app.run()
