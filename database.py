import sqlite3
import re
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "college.db"

SAMPLE_FAQS = [
    ("How can I apply for admission?", "Students can apply through the college admissions office or the official admissions portal. Replace this sample answer with your college's verified admission procedure.", "Admissions"),
    ("What documents are required for admission?", "Commonly requested documents may include previous academic mark sheets, transfer certificate, identity proof and passport-size photographs. Confirm the exact list with the admissions office.", "Admissions"),
    ("Where can I find course details?", "Course names, eligibility criteria and curriculum details should be obtained from the official department or college prospectus. Replace this answer with verified college information.", "Courses"),
    ("How do I pay my tuition fees?", "Please use only the official payment methods communicated by the college accounts office. Contact the accounts office for the current fee schedule and payment instructions.", "Fees"),
    ("How can I contact the examination cell?", "Please contact the college examination cell through the official college contact details for exam timetables, hall tickets and results.", "Examinations"),
    ("Does the college provide placement support?", "The placement cell coordinates career guidance, training and recruitment activities. Contact the placement office for current company visits and eligibility details.", "Placements"),
    ("What library facilities are available?", "For library timings, membership rules and available resources, please check with the college library. Add your college's verified details here.", "Facilities"),
    ("Where can I find the academic calendar?", "The academic calendar is published by the college or respective department. Contact your department office for the latest approved calendar.", "Academics"),
]


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT DEFAULT 'General'
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        count = conn.execute("SELECT COUNT(*) FROM faqs").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO faqs(question, answer, category) VALUES (?, ?, ?)",
                SAMPLE_FAQS
            )


STOP_WORDS = {
    "a", "an", "the", "is", "are", "do", "does", "did",
    "i", "my", "me", "we", "you", "what", "how", "where",
    "when", "can", "could", "would", "should", "please",
    "for", "to", "of", "in", "on", "and", "or", "get",
    "your", "our", "their", "this", "that", "find", "information", "info", "details", "exact"
}

SYNONYMS = {
    "papers": "documents",
    "paper": "documents",
    "document": "documents",
    "certificates": "documents",
    "certificate": "documents",
    "admitted": "admission",
    "admit": "admission",
    "apply": "admission",
    "applying": "admission",
    "timetable": "schedule",
    "time": "schedule",
    "exam": "examinations",
    "exams": "examinations",
    "tuition": "fees",
    "fee": "fees",
    "payment": "fees",
    "payments": "fees",
    "placement": "placements",
}


def tokenize(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    normalized = set()

    for word in words:
        if word in STOP_WORDS:
            continue
        normalized.add(SYNONYMS.get(word, word))

    return normalized


def search_faqs(question, limit=5):
    query_words = tokenize(question)
    if not query_words:
        return []

    with connect() as conn:
        rows = conn.execute(
            "SELECT id, question, answer, category FROM faqs"
        ).fetchall()

    scored = []
    query_lower = question.lower()

    for row in rows:
        # Match primarily against the FAQ question and category.
        faq_words = tokenize(row["question"] + " " + row["category"])
        overlap = len(query_words & faq_words)
        if not overlap:
            continue

        score = overlap / len(query_words)
        faq_text = (
            row["question"] + " " + row["answer"] + " " + row["category"]
        ).lower()

        # Do not treat a generic fee FAQ as an exact BCA fee answer.
        if "bca" in query_lower and "bca" not in faq_text:
            score *= 0.3

        if score >= 0.25:
            scored.append((score, dict(row)))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [item for score, item in scored[:limit]]


def save_message(role, message):
    with connect() as conn:
        conn.execute(
            "INSERT INTO chat_messages(role, message) VALUES (?, ?)",
            (role, message)
        )


def get_recent_messages(limit=20):
    with connect() as conn:
        rows = conn.execute(
            "SELECT role, message, created_at FROM chat_messages ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(row) for row in reversed(rows)]


def get_all_faqs():
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, question, answer, category FROM faqs ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def add_faq(question, answer, category):
    with connect() as conn:
        conn.execute(
            "INSERT INTO faqs (question, answer, category) VALUES (?, ?, ?)",
            (question, answer, category)
        )


def update_faq(faq_id, question, answer, category):
    with connect() as conn:
        conn.execute(
            """UPDATE faqs
               SET question = ?, answer = ?, category = ?
               WHERE id = ?""",
            (question, answer, category, faq_id)
        )


def delete_faq(faq_id):
    with connect() as conn:
        conn.execute(
            "DELETE FROM faqs WHERE id = ?",
            (faq_id,)
        )
