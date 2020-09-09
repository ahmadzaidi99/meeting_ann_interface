-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS topics;
DROP TABLE IF EXISTS queries;
DROP TABLE IF EXISTS annotations;
DROP TABLE IF EXISTS summaries;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  email TEXT NOT NULL
);

CREATE TABLE annotations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  annotator_id INTEGER NOT NULL,
  meeting_id INTEGER NOT NULL,
  annotation_name TEXT NOT NULL,
  prev INT,
  FOREIGN KEY (annotator_id) REFERENCES user (id)
);

CREATE TABLE topics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  annotation_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  topic TEXT NOT NULL,
  the_range TEXT NOT NULL,
  first_mention INTEGER NOT NULL,
  comments TEXT,
  prev INT,
  FOREIGN KEY (annotation_id) REFERENCES annotations (id)
);

CREATE TABLE queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    specific INT NOT NULL,
    the_query TEXT NOT NULL,
    comments TEXT,
    prev INT,
    FOREIGN KEY (topic_id) REFERENCES topics (id)
);

CREATE TABLE summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_id INTEGER NOT NULL,
    summary TEXT NOT NULL,
    range TEXT NOT NULL,
    comments TEXT,
    prev INT,
    FOREIGN KEY (query_id) REFERENCES queries (id)
);

