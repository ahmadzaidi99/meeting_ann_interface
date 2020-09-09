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

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("annotate", __name__)


def get_meeting(meeting_id):
    with open('flaskr/data/codes.json', 'r') as json_file:
        codes = json.load(json_file)
        json_file.close()
    file = codes['ICSI'].get(str(meeting_id))

    if meeting_id < 200:
        with open(os.path.join('flaskr/data/ICSI_json/', file), 'r') as json_file:
            meeting = json.load(json_file)
            json_file.close()
    return meeting


def topic_segmentation(meeting_id, topics, k, m):
    meeting = get_meeting(meeting_id)
    if m == 0:
        m = len(meeting['turns'])
    genq = "/annotate/" + str(session["annotation_id"]) + "/genq/"
    speq = "/annotate/" + str(session["annotation_id"]) + "/speq/"

    return render_template('topic_seg2.html', topics=topics, meeting=meeting, k=k, m=m, gen_q=genq, spe_q=speq)

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

    return render_template("meeting_list.html", codes=ICSI_codes)


@bp.route("/meeting/<int:meeting_id>/annotate/", methods=("GET", "POST"))
@login_required
def annotate(meeting_id):
    db = get_db()

    existing_annotations = db.execute(
        "SELECT annotation_name FROM annotations WHERE meeting_id = ?", (meeting_id,)
    ).fetchall()

    if request.method == "POST":
        name = request.form["name"]
        db.execute(
            "INSERT INTO annotations (annotator_id, meeting_id, annotation_name) VALUES (?, ?, ?)",
            (g.user["id"], meeting_id, name),
        )
        db.commit()

        annotation = db.execute(
            "SELECT * FROM annotations WHERE annotation_name = ?", (name,)
        ).fetchone()

        session["annotation_id"] = annotation["id"]
        return redirect("/annotate/" + str(annotation["id"]) + "/topics/")

    return render_template("annotate_meeting.html", existing_annotations=existing_annotations)


@bp.route("/annotate/<int:annotation_id>/topics/", methods=("GET", "POST"))
@login_required
def topic_annotation(annotation_id):
    db = get_db()
    meeting_id = db.execute("SELECT meeting_id, id FROM annotations WHERE"
                            " id = ?", (annotation_id,)).fetchone()

    def get_topics(annotation_id):
        db = get_db()
        topics = db.execute("SELECT topic, the_range, annotation_id FROM topics "
                            "WHERE annotation_id = ? ORDER BY first_mention DESC", (annotation_id,)).fetchall()
        return topics

    if request.method == "POST":
        topic = request.form["topic"]
        range = request.form["range"]
        db = get_db()
        db.execute(
            "INSERT INTO topics (annotation_id, topic, the_range, first_mention)"
            "VALUES (?, ?, ?, ?)",
            (annotation_id, topic, range, 1),
        )
        db.commit()

    # if request.method == "POST":
    #     line = request.form["line"]
    #     return redirect(request.path + "#" + str(int(line) - 1))

    return topic_segmentation(meeting_id["meeting_id"], get_topics(annotation_id), 0, 0)


@bp.route("/test/")
@login_required
def test():
    return request.path


@bp.route("/annotate/<int:annotation_id>/genq/", methods=("GET", "POST"))
@login_required
def gen_queries(annotation_id):
    db = get_db()
    meeting_id = db.execute("SELECT meeting_id, id "
                            "FROM annotations WHERE id = ?", (annotation_id,)).fetchone()["meeting_id"]

    meeting = get_meeting(meeting_id)

    num_turns = len(meeting["turns"])

    if request.method == "POST":
        query = request.form["query"]

        db = get_db()
        db.execute(
            "INSERT INTO queries (topic_id, the_query, specific)"
            "VALUES (?, ?, ?)",
            (annotation_id, query, 0),
        )
        db.commit()

    return render_template("gen_queries.html", meeting=meeting, k=num_turns)
