from flaskr.db import get_db

def get_topics(annotation_id):
    db = get_db()
    topics = db.execute("SELECT id, topic, the_range, annotation_id FROM topics "
                        "WHERE annotation_id = ? ORDER BY first_mention DESC", (annotation_id,)).fetchall()
    return topics


topics = get_topics(103)

print(topics.index(1))