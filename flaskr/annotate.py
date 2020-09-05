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
    return render_template('topic_seg2.html', topics=topics, meeting=meeting, k=k, m=m)


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
        return redirect("/" + str(meeting_id) + "/annotate/topics/" + str(annotation["id"]))

    return render_template("annotate_meeting.html", existing_annotations=existing_annotations)


@bp.route("/<int:meeting_id>/annotate/topics/<int:annotation_id>", methods=("GET", "POST"))
@login_required
def show_topics(meeting_id, annotation_id):
    def get_topics(annotation_id):
        topics = db.execute("SELECT topic, range, annotation_id FROM topics "
                            "WHERE annotation_id = ? ORDER BY first_mention DESC", (annotation_id,)).fetchall()
        return topics

    if request.method == "POST":
        topic = request.form["topic"]
        range = request.form["range"]
        # annotation_id = request.form["annotation_id"]
        db = get_db()
        db.execute(
            "INSERT INTO topics (annotation_id, topic, range, first_mention)"
            "VALUES (?, ?, ?, ?)",
            (annotation_id, topic, range, 1),
        )
        db.commit()

    return topic_segmentation(meeting_id, get_topics(annotation_id), 0, 0)