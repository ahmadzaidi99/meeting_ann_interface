from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.exceptions import abort
import os
import json
from os.path import isfile, join
from itertools import chain

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("annotate", __name__)


def parse_range(rng):
    parts = rng.split('-')
    if 1 > len(parts) > 2:
        raise ValueError("Bad range: '%s'" % (rng,))
    parts = [int(i) for i in parts]
    start = parts[0]
    end = start if len(parts) == 1 else parts[1]
    if start > end:
        end, start = start, end
    return range(start, end + 1)


def parse_range_list(rngs):
    return sorted(set(chain(*[parse_range(rng) for rng in rngs.split(',')])))


def annotation_queries(annotation_id):
    db = get_db()
    queries = db.execute("SELECT id, the_query, annotation_id, topic_id, specific, created FROM queries "
                             "WHERE annotation_id = ? ORDER BY created", (annotation_id,)).fetchall()
    return queries


def get_meeting(meeting_id):
    with open('flaskr/data/codes.json', 'r') as json_file:
        codes = json.load(json_file)
        json_file.close()



    if meeting_id < 200:
        file = codes['ICSI'].get(str(meeting_id))
        with open(os.path.join('flaskr/data/ICSI_json/', file), 'r') as json_file:
            meeting = json.load(json_file)
            json_file.close()

    if meeting_id >= 200:
        file = codes['com'].get(str(meeting_id))
        with open(os.path.join('flaskr/data/com/', file), 'r') as json_file:
            meeting = json.load(json_file)
            json_file.close()

    return meeting





def get_topics(annotation_id):
    db = get_db()
    topics = db.execute("SELECT id, topic, the_range, annotation_id FROM topics "
                            "WHERE annotation_id = ? ORDER BY first_mention DESC", (annotation_id,)).fetchall()
    return topics


def get_sums(query_id):
    db = get_db()
    summary = db.execute("SELECT id, query_id, summary, range FROM summaries "
                        "WHERE query_id = ?", (query_id,)).fetchall()
    return summary


@bp.route("/meeting/list", methods=("GET", "POST"))
@login_required
def list_meetings():
    def get_codes():
        with open('flaskr/data/codes.json', 'r') as json_file:
            codes = json.load(json_file)
            json_file.close()
        return codes

    codes = get_codes()

    ICSI_codes = codes["ICSI"]
    com_codes = codes["com"]

    return render_template("meeting_list.html", codes=ICSI_codes, com_codes=com_codes)


@bp.route("/meeting/<int:meeting_id>/annotate/", methods=("GET", "POST"))
@login_required
def annotate(meeting_id):
    db = get_db()

    existing_annotations = db.execute(
        "SELECT annotation_name, id FROM annotations WHERE meeting_id = ?", (meeting_id,)
    ).fetchall()

    if request.method == "POST":
        name = request.form["name"]
        db.execute(
            "INSERT INTO annotations (annotator_id, meeting_id, annotation_name) VALUES (?, ?, ?)",
            (g.user["id"], meeting_id, name),
        )
        db.commit()

        annotation = db.execute(
            "SELECT MAX(id) AS the_id FROM annotations",
        ).fetchone()

        session["annotation_id"] = annotation["the_id"]
        return redirect("/annotate/" + str(annotation["the_id"]) + "/topics/")

    return render_template("annotate_meeting.html", existing_annotations=existing_annotations)


@bp.route("/", methods=("GET", "POST"))
def start():
    return render_template("landing.html")


@bp.route("/annotate/<int:annotation_id>/topics/", methods=("GET", "POST"))
@login_required
def topic_annotation(annotation_id):
    db = get_db()
    meeting_id = db.execute("SELECT meeting_id, id FROM annotations WHERE"
                            " id = ?", (annotation_id,)).fetchone()["meeting_id"]

    meeting = get_meeting(meeting_id)

    genq = "/annotate/" + str(session["annotation_id"]) + "/genq/"

    if request.method == "POST":
        topic = request.form["topic"]
        range_list = parse_range_list(request.form["range"])
        range = request.form["range"]
        earliest = min(range_list)
        db = get_db()
        db.execute(
            "INSERT INTO topics (annotation_id, topic, the_range, first_mention)"
            "VALUES (?, ?, ?, ?)",
            (annotation_id, topic, range, earliest),
        )
        db.commit()

    # if request.method == "POST":
    #     line = request.form["line"]
    #     return redirect(request.path + "#" + str(int(line) - 1))

    return render_template('topic_seg2.html', topics=get_topics(annotation_id), meeting=meeting, k=0, m=len(meeting['turns']), gen_q=genq)


@bp.route("/test/")
@login_required
def test():
    return request.path


@bp.route("/annotate/<int:annotation_id>/genq/", methods=("GET", "POST"))
@login_required
def get_queries(annotation_id):
    db = get_db()
    meeting_id = db.execute("SELECT meeting_id, id "
                            "FROM annotations WHERE id = ?", (annotation_id,)).fetchone()["meeting_id"]

    topics = get_topics(annotation_id)
    topics_length = len(topics)

    meeting = get_meeting(meeting_id)

    num_turns = len(meeting["turns"])

    turns = range(num_turns)

    # print(topics[0]["id"])

    if request.method == "POST":
        form = request.form
        query = form["query"]
        topic = int(form.getlist("topic")[0])
        if topic == 0:
            specific = 0
            topic_id = None
        else:
            specific = 1
            topic_id = topics[topic - 1]["id"]

        db = get_db()
        db.execute(
            "INSERT INTO queries (topic_id, the_query, specific, annotation_id)"
            "VALUES (?, ?, ?, ?)",
            (topic_id, query, specific, annotation_id),
        )
        db.commit()

    return render_template("gen_queries.html", meeting=meeting,
                           turns=turns, topics=topics,
                           topics_length=topics_length, queries=annotation_queries(annotation_id),
                           annotation_id=annotation_id)


@bp.route("/annotate/<int:annotation_id>/summaries/<int:query_id>/", methods=("GET", "POST"))
@login_required
def summaries(annotation_id, query_id):
    db = get_db()
    meeting_id = db.execute("SELECT meeting_id, id "
                            "FROM annotations WHERE id = ?", (annotation_id,)).fetchone()["meeting_id"]

    meeting = get_meeting(meeting_id)

    the_query = db.execute("SELECT topic_id, specific, the_query FROM queries WHERE id = ?", (query_id,)).fetchone()

    if the_query["specific"] == 1:
        topic_range = db.execute("SELECT the_range, id FROM topics WHERE id = ?", (the_query["topic_id"],)).fetchone()
        turns = parse_range_list(topic_range["the_range"])
    else:
        turns = range(len(meeting["turns"]))

    if request.method == "POST":
        form = request.form
        summary = form["summary"]
        parsed = parse_range_list(form["range"])
        the_range = form["range"]
        for item in parsed:
            if item in turns:
                continue
            else:
                raise ValueError
        db = get_db()
        db.execute(
            "INSERT INTO summaries (query_id, summary, range)"
            "VALUES (?, ?, ?)",
            (query_id, summary, the_range),
        )
        db.commit()
        return redirect("/annotate/" + str(annotation_id) + "/genq/")

    summaries = get_sums(query_id)

    return render_template("summaries.html", meeting=meeting, turns=turns,
                           queries=annotation_queries(annotation_id), main_query=the_query,
                           annotation_id=annotation_id, summaries=summaries)


@bp.route("/annotation/<int:annotation_id>/", methods=("GET", "POST"))
@login_required
def view_annotation(annotation_id):
    db = get_db()

    meeting_id = db.execute("SELECT meeting_id, id FROM annotations WHERE"
                            " id = ?", (annotation_id,)).fetchone()["meeting_id"]

    meeting = get_meeting(meeting_id)

    num_turns = len(meeting["turns"])

    topics = get_topics(annotation_id)

    all_queries = annotation_queries(annotation_id)

    q_a = dict()

    for query in all_queries:
        sums = get_sums(query['id'])
        q_a[query["the_query"]] = sums

    return render_template("annotation.html", meeting=meeting, topics=topics,
                           num_turns=num_turns, sums=q_a)


@bp.route("/meeting/<int:meeting_id>/view", methods=("GET", "POST"))
def view_meeting(meeting_id):
    meeting = get_meeting(meeting_id)

    return render_template("view.html", meeting=meeting)