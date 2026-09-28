from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import re

app = Flask(__name__)

DATABASE = "database/study.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = get_db()

    notes = conn.execute(
        "SELECT * FROM notes ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        notes=notes
    )


@app.route("/add-note", methods=["POST"])
def add_note():

    subject = request.form["subject"]
    title = request.form["title"]
    content = request.form["content"]

    conn = get_db()

    conn.execute(
        """
        INSERT INTO notes (subject, title, content)
        VALUES (?, ?, ?)
        """,
        (subject, title, content)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


@app.route("/delete-note/<int:note_id>")
def delete_note(note_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM notes WHERE id = ?",
        (note_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


@app.route("/ask", methods=["POST"])
def ask():

    question = request.form.get("question", "").strip()

    answer = generate_answer(question)

    return render_template(
        "index.html",
        answer=answer,
        notes=get_notes()
    )


def get_notes():

    conn = get_db()

    notes = conn.execute(
        "SELECT * FROM notes ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return notes


def generate_answer(question):

    if not question:
        return "Please enter a question."

    question_lower = question.lower()

    answers = {

        "python":
        "Python is a high-level programming language used for web development, automation, data science and artificial intelligence.",

        "machine learning":
        "Machine Learning is a branch of AI where computers learn patterns from data and use those patterns to make predictions or decisions.",

        "artificial intelligence":
        "Artificial Intelligence is the field of creating computer systems that can perform tasks that normally require human intelligence.",

        "html":
        "HTML is used to create the structure of web pages using elements such as headings, paragraphs, buttons and forms.",

        "css":
        "CSS is used to style web pages. It controls colors, layouts, fonts, spacing, animations and responsive design.",

        "javascript":
        "JavaScript is a programming language used to make web pages interactive and dynamic.",

        "database":
        "A database is an organized collection of data that allows applications to store, retrieve and manage information."
    }

    for keyword, answer in answers.items():

        if keyword in question_lower:
            return answer

    return (
        "I found your question, but this basic version does not "
        "have an answer for that topic yet. You can add more topics "
        "to the AI knowledge base."
    )


@app.route("/summary", methods=["POST"])
def summary():

    text = request.form.get("text", "").strip()

    if not text:
        result = "Please enter some text to summarize."

    else:
        sentences = re.split(r"(?<=[.!?])\s+", text)

        if len(sentences) <= 3:
            result = text
        else:
            result = " ".join(sentences[:3])

    return render_template(
        "index.html",
        summary=result,
        notes=get_notes()
    )


@app.route("/quiz")
def quiz():

    questions = [
        {
            "question": "What does HTML stand for?",
            "answer": "HyperText Markup Language"
        },
        {
            "question": "Which language is commonly used for AI development?",
            "answer": "Python"
        },
        {
            "question": "What is CSS used for?",
            "answer": "Styling web pages"
        },
        {
            "question": "What is Machine Learning?",
            "answer": "A method where computers learn patterns from data"
        }
    ]

    return render_template(
        "index.html",
        quiz=questions,
        notes=get_notes()
    )


if __name__ == "__main__":

    create_database()

    app.run(debug=True)