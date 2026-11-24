
import os
import hmac
from functools import wraps

from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, session, flash
)
from dotenv import load_dotenv

from database import (
    init_db, search_faqs, save_message,
    get_recent_messages, get_all_faqs,
    add_faq, update_faq, delete_faq
)
from ai_service import generate_answer

load_dotenv()

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.secret_key = os.getenv(
    "FLASK_SECRET_KEY", "development-secret-change-before-deployment"
)

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")


def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return function(*args, **kwargs)
    return wrapper


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("message") or "").strip()

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    if len(question) > 600:
        return jsonify({"error": "Please keep your question under 600 characters."}), 400

    save_message("user", question)
    faqs = search_faqs(question, limit=5)

    if not faqs:
        answer = (
            "I couldn't find verified information about that in the "
            "college FAQ database. Please contact the college office "
            "for confirmation."
        )
    else:
        answer = generate_answer(question, faqs)

    save_message("assistant", answer)

    return jsonify({
        "answer": answer,
        "sources": [item["question"] for item in faqs]
    })


@app.get("/api/history")
def history():
    return jsonify(get_recent_messages(20))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        password = request.form.get("password", "")

        if not ADMIN_PASSWORD:
            flash("Please configure ADMIN_PASSWORD in your .env file.")
        elif hmac.compare_digest(password, ADMIN_PASSWORD):
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Incorrect password. Please try again.")

    return render_template("admin_login.html")


@app.get("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.get("/admin")
@admin_required
def admin_dashboard():
    return render_template("admin.html", faqs=get_all_faqs())


@app.post("/admin/add")
@admin_required
def admin_add():
    question = request.form.get("question", "").strip()
    answer = request.form.get("answer", "").strip()
    category = request.form.get("category", "General").strip() or "General"

    if question and answer:
        add_faq(question, answer, category)
        flash("FAQ added successfully.")
    else:
        flash("Question and answer are required.")

    return redirect(url_for("admin_dashboard"))


@app.post("/admin/update/<int:faq_id>")
@admin_required
def admin_update(faq_id):
    question = request.form.get("question", "").strip()
    answer = request.form.get("answer", "").strip()
    category = request.form.get("category", "General").strip() or "General"

    if question and answer:
        update_faq(faq_id, question, answer, category)
        flash("FAQ updated successfully.")
    else:
        flash("Question and answer cannot be empty.")

    return redirect(url_for("admin_dashboard"))


@app.post("/admin/delete/<int:faq_id>")
@admin_required
def admin_delete(faq_id):
    delete_faq(faq_id)
    flash("FAQ deleted.")
    return redirect(url_for("admin_dashboard"))


# Initialize the database when the application is imported by Gunicorn or run locally.
init_db()


if __name__ == "__main__":
    app.run(debug=True)
