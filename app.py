import json
import os
import sqlite3
import secrets

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory


# ============================================================
# CONFIGURATION
# ============================================================

BASE = os.path.dirname(os.path.abspath(__file__))

# Always load .env from the same folder as app.py
load_dotenv(os.path.join(BASE, ".env"))

DB_PATH = os.path.join(BASE, "team.db")

app = Flask(
    __name__,
    static_folder=os.path.join(BASE, "static"),
    static_url_path="/static"
)


# ============================================================
# DATABASE
# ============================================================

def conn():
    c = sqlite3.connect(DB_PATH)

    # Original/shared team task table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS team (
            id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            created REAL DEFAULT (strftime('%s','now'))
        )
        """
    )

    # Teams
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS teams (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created REAL DEFAULT (strftime('%s','now'))
        )
        """
    )

    # Tasks belonging to a specific team
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS team_tasks (
            id TEXT PRIMARY KEY,
            team_code TEXT NOT NULL,
            data TEXT NOT NULL,
            created REAL DEFAULT (strftime('%s','now'))
        )
        """
    )

    # Members who have joined each team.
    # A new member record is created when a device creates or joins a team.
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS team_members (
            id TEXT PRIMARY KEY,
            team_code TEXT NOT NULL,
            created REAL DEFAULT (strftime('%s','now'))
        )
        """
    )

    return c


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/")
def index():
    return send_from_directory(
        app.static_folder,
        "index.html"
    )


# ============================================================
# GEMINI AI
# ============================================================

@app.post("/api/ai")
def ai():

    key = os.getenv("GEMINI_API_KEY")

    if not key:
        return jsonify(
            error="Set GEMINI_API_KEY in your .env file to use AI features."
        ), 503

    data = request.get_json(silent=True) or {}

    prompt = (data.get("prompt") or "")[:30000]

    if not prompt.strip():
        return jsonify(
            error="Empty prompt"
        ), 400

    try:

        from google import genai

        client = genai.Client(
            api_key=key
        )

        response = client.models.generate_content(
            model=os.getenv(
                "GEMINI_MODEL",
                "gemini-3.8-flash"
            ),
            contents=prompt
        )

        return jsonify(
            text=response.text or ""
        )

    except Exception as e:

        print("GEMINI ERROR:", repr(e))

        return jsonify(
            error=str(e)
        ), 502


# ============================================================
# TEAM CODE GENERATOR
# ============================================================

# Avoid confusing characters such as O/0 and I/1
TEAM_ALPHABET = (
    "ABCDEFGHJKLMNPQRSTUVWXYZ"
    "23456789"
)


def generate_team_code():

    return "".join(
        secrets.choice(TEAM_ALPHABET)
        for _ in range(6)
    )


# ============================================================
# TEAM MEMBER COUNT
# ============================================================

def add_team_member(c, code, member_id=None):
    """Register a browser/device as a team member.

    The member_id is generated once in the browser and reused so refreshing
    or joining the same team again does not create duplicate members.
    """
    member_id = (member_id or "").strip()

    if not member_id:
        member_id = "m" + secrets.token_hex(8)

    c.execute(
        """
        INSERT OR IGNORE INTO team_members
        (id, team_code)
        VALUES (?, ?)
        """,
        (member_id, code)
    )

    return member_id


def get_member_count(c, code):
    row = c.execute(
        """
        SELECT COUNT(*)
        FROM team_members
        WHERE team_code=?
        """,
        (code,)
    ).fetchone()

    return row[0] if row else 0


# ============================================================
# CREATE TEAM
# ============================================================

@app.post("/api/team/create")
def create_team():

    data = request.get_json(
        silent=True
    ) or {}

    name = (
        data.get("name") or ""
    ).strip()

    if not name:

        return jsonify(
            error="Team name is required."
        ), 400

    if len(name) > 60:

        return jsonify(
            error="Team name must be 60 characters or less."
        ), 400

    member_id = (data.get("member_id") or "").strip()

    if not member_id:
        return jsonify(
            error="Member ID is required."
        ), 400

    with conn() as c:

        code = None

        # Generate a unique code
        for _ in range(20):

            candidate = generate_team_code()

            exists = c.execute(
                """
                SELECT 1
                FROM teams
                WHERE code=?
                """,
                (candidate,)
            ).fetchone()

            if not exists:

                code = candidate
                break

        if not code:

            return jsonify(
                error="Could not generate a team code. Try again."
            ), 500

        c.execute(
            """
            INSERT INTO teams
            (code, name)
            VALUES (?, ?)
            """,
            (
                code,
                name
            )
        )

        # The creator is the first member.
        member_id = add_team_member(c, code, data.get("member_id"))
        member_count = get_member_count(c, code)

    print(
        f"TEAM CREATED: {name} [{code}] - members: {member_count}"
    )

    return jsonify(
        ok=True,
        team={
            "name": name,
            "code": code,
            "member_id": member_id,
            "member_count": member_count
        }
    )


# ============================================================
# JOIN TEAM
# ============================================================

@app.post("/api/team/join")
def join_team():

    data = request.get_json(
        silent=True
    ) or {}

    code = (
        data.get("code") or ""
    ).strip().upper()

    if not code:

        return jsonify(
            error="Team code is required."
        ), 400

    member_id = (data.get("member_id") or "").strip()

    if not member_id:
        return jsonify(
            error="Member ID is required."
        ), 400

    with conn() as c:

        row = c.execute(
            """
            SELECT code, name
            FROM teams
            WHERE code=?
            """,
            (code,)
        ).fetchone()

        if not row:
            return jsonify(
                error="Invalid team code. Check the code and try again."
            ), 404

        # Register this joining device/member.
        member_id = add_team_member(c, code, data.get("member_id"))
        member_count = get_member_count(c, code)

    print(
        f"TEAM JOINED: {row[1]} [{row[0]}] - members: {member_count}"
    )

    return jsonify(
        ok=True,
        team={
            "name": row[1],
            "code": row[0],
            "member_id": member_id,
            "member_count": member_count
        }
    )



# ============================================================
# LEAVE TEAM
# ============================================================

@app.post("/api/team/<code>/leave")
def leave_team(code):

    code = code.strip().upper()

    data = request.get_json(silent=True) or {}
    member_id = (data.get("member_id") or "").strip()

    if not member_id:
        return jsonify(
            error="Member ID is required."
        ), 400

    with conn() as c:

        team = c.execute(
            """
            SELECT 1
            FROM teams
            WHERE code=?
            """,
            (code,)
        ).fetchone()

        if not team:
            return jsonify(
                error="Team not found."
            ), 404

        c.execute(
            """
            DELETE FROM team_members
            WHERE id=?
            AND team_code=?
            """,
            (member_id, code)
        )

        member_count = get_member_count(c, code)

    print(
        f"TEAM LEFT: [{code}] member={member_id} members={member_count}"
    )

    return jsonify(
        ok=True,
        member_count=member_count
    )


# ============================================================
# GET TEAM TASKS
# ============================================================

@app.get("/api/team/<code>/tasks")
def get_team_tasks(code):

    code = code.strip().upper()

    with conn() as c:

        team = c.execute(
            """
            SELECT name
            FROM teams
            WHERE code=?
            """,
            (code,)
        ).fetchone()

        if not team:

            return jsonify(
                error="Team not found."
            ), 404

        member_count = get_member_count(c, code)

        rows = c.execute(
            """
            SELECT id, data
            FROM team_tasks
            WHERE team_code=?
            ORDER BY created
            """,
            (code,)
        ).fetchall()

    tasks = []

    for task_id, data in rows:

        task = json.loads(data)

        task["id"] = task_id

        tasks.append(task)

    return jsonify(
        team={
            "name": team[0],
            "code": code,
            "member_count": member_count
        },
        tasks=tasks
    )


# ============================================================
# ADD TEAM TASK
# ============================================================

@app.post("/api/team/<code>/tasks")
def add_team_task(code):

    code = code.strip().upper()

    data = request.get_json(
        silent=True
    ) or {}

    with conn() as c:

        team = c.execute(
            """
            SELECT 1
            FROM teams
            WHERE code=?
            """,
            (code,)
        ).fetchone()

        if not team:

            return jsonify(
                error="Team not found."
            ), 404

        task_id = (
            "t" +
            secrets.token_hex(6)
        )

        c.execute(
            """
            INSERT INTO team_tasks
            (id, team_code, data)
            VALUES (?, ?, ?)
            """,
            (
                task_id,
                code,
                json.dumps(data)
            )
        )

    return jsonify(
        ok=True,
        id=task_id
    )


# ============================================================
# UPDATE TEAM TASK
# ============================================================

@app.patch("/api/team/<code>/tasks/<task_id>")
def update_team_task(
    code,
    task_id
):

    code = code.strip().upper()

    patch = request.get_json(
        silent=True
    ) or {}

    with conn() as c:

        row = c.execute(
            """
            SELECT data
            FROM team_tasks
            WHERE id=?
            AND team_code=?
            """,
            (
                task_id,
                code
            )
        ).fetchone()

        if not row:

            return jsonify(
                error="Task not found."
            ), 404

        old_data = json.loads(
            row[0]
        )

        new_data = {
            **old_data,
            **patch
        }

        c.execute(
            """
            UPDATE team_tasks
            SET data=?
            WHERE id=?
            AND team_code=?
            """,
            (
                json.dumps(new_data),
                task_id,
                code
            )
        )

    return jsonify(
        ok=True
    )


# ============================================================
# DELETE TEAM TASK
# ============================================================

@app.delete("/api/team/<code>/tasks/<task_id>")
def delete_team_task(
    code,
    task_id
):

    code = code.strip().upper()

    with conn() as c:

        c.execute(
            """
            DELETE FROM team_tasks
            WHERE id=?
            AND team_code=?
            """,
            (
                task_id,
                code
            )
        )

    return jsonify(
        ok=True
    )


# ============================================================
# OLD TEAM API
# ============================================================

# Keeping these routes so your existing frontend
# doesn't immediately break if it still calls them.

@app.get("/api/team")
def team_list():

    with conn() as c:

        rows = c.execute(
            """
            SELECT id, data
            FROM team
            ORDER BY created
            """
        ).fetchall()

    return jsonify([
        {
            **json.loads(data),
            "id": task_id
        }
        for task_id, data in rows
    ])


@app.put("/api/team/<tid>")
def team_set(tid):

    data = request.get_json(
        silent=True
    ) or {}

    with conn() as c:

        c.execute(
            """
            INSERT OR REPLACE
            INTO team (id, data)
            VALUES (?, ?)
            """,
            (
                tid,
                json.dumps(data)
            )
        )

    return jsonify(
        ok=True
    )


@app.patch("/api/team/<tid>")
def team_update(tid):

    patch = request.get_json(
        silent=True
    ) or {}

    with conn() as c:

        row = c.execute(
            """
            SELECT data
            FROM team
            WHERE id=?
            """,
            (tid,)
        ).fetchone()

        if not row:

            return jsonify(
                error="Not found"
            ), 404

        merged = {
            **json.loads(row[0]),
            **patch
        }

        c.execute(
            """
            UPDATE team
            SET data=?
            WHERE id=?
            """,
            (
                json.dumps(merged),
                tid
            )
        )

    return jsonify(
        ok=True
    )


@app.delete("/api/team/<tid>")
def team_delete(tid):

    with conn() as c:

        c.execute(
            """
            DELETE FROM team
            WHERE id=?
            """,
            (tid,)
        )

    return jsonify(
        ok=True
    )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host=os.getenv(
            "HOST",
            "0.0.0.0"
        ),
        port=int(
            os.getenv(
                "PORT",
                "5000"
            )
        ),
        debug=False
    )