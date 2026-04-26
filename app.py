"""
Social Board - 研究团队社交看板
支持头像上传、个人详情页、编辑与删除
"""

import html
import os
import secrets
import sqlite3
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, g
from werkzeug.utils import secure_filename

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "social.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                research TEXT,
                interests TEXT,
                contact TEXT,
                bio TEXT,
                avatar TEXT,
                mbti TEXT,
                company TEXT,
                location TEXT,
                website TEXT,
                github TEXT,
                skills TEXT,
                edit_token TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cols = {row[1] for row in db.execute("PRAGMA table_info(people)")}
        migrations = [
            ("avatar", "TEXT"),
            ("bio", "TEXT"),
            ("mbti", "TEXT"),
            ("company", "TEXT"),
            ("location", "TEXT"),
            ("website", "TEXT"),
            ("github", "TEXT"),
            ("skills", "TEXT"),
            ("edit_token", "TEXT"),
        ]
        for col, dtype in migrations:
            if col not in cols:
                db.execute(f"ALTER TABLE people ADD COLUMN {col} {dtype}")
        db.commit()


@app.template_filter("nl2br")
def nl2br_filter(value):
    if not value:
        return value
    escaped = html.escape(value)
    return escaped.replace("\n", "<br>").replace("\\n", "<br>")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/person/<int:person_id>")
def person_page(person_id):
    db = get_db()
    row = db.execute(
        "SELECT * FROM people WHERE id = ?", (person_id,)
    ).fetchone()
    if not row:
        return render_template("person.html", person=None), 404
    return render_template("person.html", person=dict(row))


@app.route("/api/people", methods=["GET"])
def get_people():
    db = get_db()
    rows = db.execute(
        """
        SELECT id, name, research, interests, contact, bio, avatar,
               mbti, company, location, website, github, skills, created_at
        FROM people ORDER BY created_at DESC
        """
    ).fetchall()
    people = [dict(row) for row in rows]
    return jsonify({"people": people})


@app.route("/api/people/<int:person_id>", methods=["GET"])
def get_person(person_id):
    db = get_db()
    row = db.execute(
        """
        SELECT id, name, research, interests, contact, bio, avatar,
               mbti, company, location, website, github, skills, created_at
        FROM people WHERE id = ?
        """,
        (person_id,),
    ).fetchone()
    if not row:
        return jsonify({"error": "Not found"}), 404
    return jsonify(dict(row))


@app.route("/api/people", methods=["POST"])
def add_person():
    name = (request.form.get("name") or "").strip()
    research = (request.form.get("research") or "").strip()
    interests = (request.form.get("interests") or "").strip()
    contact = (request.form.get("contact") or "").strip()
    bio = (request.form.get("bio") or "").strip()
    mbti = (request.form.get("mbti") or "").strip().upper()
    company = (request.form.get("company") or "").strip()
    location = (request.form.get("location") or "").strip()
    website = (request.form.get("website") or "").strip()
    github = (request.form.get("github") or "").strip()
    skills = (request.form.get("skills") or "").strip()

    if not name:
        return jsonify({"error": "Name is required."}), 400

    avatar_path = None
    file = request.files.get("avatar")
    if file and file.filename and allowed_file(file.filename):
        ext = secure_filename(file.filename).rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)
        avatar_path = f"/static/uploads/{filename}"

    edit_token = secrets.token_urlsafe(16)

    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO people
        (name, research, interests, contact, bio, avatar,
         mbti, company, location, website, github, skills, edit_token, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (name, research, interests, contact, bio, avatar_path,
         mbti, company, location, website, github, skills, edit_token, datetime.now().isoformat()),
    )
    db.commit()

    row = db.execute(
        """
        SELECT id, name, research, interests, contact, bio, avatar,
               mbti, company, location, website, github, skills, created_at
        FROM people WHERE id = ?
        """,
        (cursor.lastrowid,),
    ).fetchone()
    data = dict(row)
    data["edit_token"] = edit_token
    return jsonify(data), 201


@app.route("/api/people/<int:person_id>/edit", methods=["POST"])
def edit_person(person_id):
    token = (request.form.get("edit_token") or "").strip()
    if not token:
        return jsonify({"error": "Missing edit token."}), 403

    db = get_db()
    existing = db.execute("SELECT edit_token, avatar FROM people WHERE id = ?", (person_id,)).fetchone()
    if not existing:
        return jsonify({"error": "Not found."}), 404
    if existing["edit_token"] != token:
        return jsonify({"error": "Invalid edit token."}), 403

    name = (request.form.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Name is required."}), 400

    research = (request.form.get("research") or "").strip()
    interests = (request.form.get("interests") or "").strip()
    contact = (request.form.get("contact") or "").strip()
    bio = (request.form.get("bio") or "").strip()
    mbti = (request.form.get("mbti") or "").strip().upper()
    company = (request.form.get("company") or "").strip()
    location = (request.form.get("location") or "").strip()
    website = (request.form.get("website") or "").strip()
    github = (request.form.get("github") or "").strip()
    skills = (request.form.get("skills") or "").strip()

    avatar_path = existing["avatar"]
    file = request.files.get("avatar")
    if file and file.filename and allowed_file(file.filename):
        ext = secure_filename(file.filename).rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)
        avatar_path = f"/static/uploads/{filename}"

    db.execute(
        """
        UPDATE people SET
        name=?, research=?, interests=?, contact=?, bio=?, avatar=?,
        mbti=?, company=?, location=?, website=?, github=?, skills=?
        WHERE id=?
        """,
        (name, research, interests, contact, bio, avatar_path,
         mbti, company, location, website, github, skills, person_id),
    )
    db.commit()

    row = db.execute(
        """
        SELECT id, name, research, interests, contact, bio, avatar,
               mbti, company, location, website, github, skills, created_at
        FROM people WHERE id = ?
        """,
        (person_id,),
    ).fetchone()
    return jsonify(dict(row))


@app.route("/api/people/<int:person_id>", methods=["DELETE"])
def delete_person(person_id):
    token = request.headers.get("X-Edit-Token", "").strip()
    if not token:
        return jsonify({"error": "Missing edit token."}), 403

    db = get_db()
    existing = db.execute("SELECT edit_token FROM people WHERE id = ?", (person_id,)).fetchone()
    if not existing:
        return jsonify({"error": "Not found."}), 404
    if existing["edit_token"] != token:
        return jsonify({"error": "Invalid edit token."}), 403

    db.execute("DELETE FROM people WHERE id = ?", (person_id,))
    db.commit()
    return jsonify({"deleted": True})


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=False, host="0.0.0.0", port=port)
else:
    init_db()
