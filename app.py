import os
import time

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session
)

from config import (
    MAX_FILE_SIZE,
    SECRET_KEY,
    DEBUG,
    ADMIN_USERNAME,
    ADMIN_PASSWORD
)

from database import init_db, get_connection

from services.file_service import (
    save_files,
    process_download,
    cleanup_expired_files
)

# ================= APP INIT =================
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE
app.config["SECRET_KEY"] = SECRET_KEY

init_db()


# ================= HOME =================
@app.route("/")
def index():
    return render_template("index.html")


# ================= AJAX UPLOAD =================
@app.route("/upload_ajax", methods=["POST"])
def upload_ajax():

    files = request.files.getlist("file")

    if not files or files[0].filename == "":
        return jsonify({
            "success": False,
            "error": "No files uploaded."
        })

    user_ip = request.remote_addr

    code, error = save_files(files, user_ip)

    if error:
        return jsonify({
            "success": False,
            "error": error
        })

    return jsonify({
        "success": True,
        "code": code
    })


# ================= DOWNLOAD (FORM) =================
@app.route("/download", methods=["POST"])
def download():

    code = request.form.get("code", "").strip().upper()

    if not code or len(code) != 6:
        return render_template(
            "index.html",
            error="Invalid download code."
        )

    user_ip = request.remote_addr

    response, error = process_download(code, user_ip)

    if error:
        return render_template(
            "index.html",
            error=error
        )

    return response


# ================= DIRECT DOWNLOAD =================
@app.route("/download_direct/<code>")
def download_direct(code):

    code = code.strip().upper()
    user_ip = request.remote_addr

    response, error = process_download(code, user_ip)

    if error:
        return "Invalid or expired code", 404

    return response


# ================= ADMIN LOGIN =================
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))

        return render_template(
            "admin_login.html",
            error="Invalid credentials"
        )

    return render_template("admin_login.html")


# ================= ADMIN LOGOUT =================
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


# ================= ADMIN DASHBOARD =================
@app.route("/admin")
def admin_dashboard():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    conn = get_connection()
    cursor = conn.cursor()

    current_time = int(time.time())

    # Total uploads
    cursor.execute("SELECT COUNT(*) FROM files")
    total_files = cursor.fetchone()[0]

    # Total downloads
    cursor.execute("SELECT SUM(downloads) FROM files")
    total_downloads = cursor.fetchone()[0] or 0

    # Active files
    cursor.execute(
        "SELECT COUNT(*) FROM files WHERE expires_at > ?",
        (current_time,)
    )
    active_files = cursor.fetchone()[0]

    # Expired files
    cursor.execute(
        "SELECT COUNT(*) FROM files WHERE expires_at < ?",
        (current_time,)
    )
    expired_files = cursor.fetchone()[0]

    # Most downloaded file
    cursor.execute("""
        SELECT code, downloads
        FROM files
        ORDER BY downloads DESC
        LIMIT 1
    """)
    most_downloaded = cursor.fetchone()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_files=total_files,
        total_downloads=total_downloads,
        active_files=active_files,
        expired_files=expired_files,
        most_downloaded=most_downloaded
    )


# ================= ERROR HANDLERS =================
@app.errorhandler(413)
def file_too_large(e):
    return jsonify({
        "success": False,
        "error": "File too large."
    }), 413


@app.errorhandler(500)
def server_error(e):
    return render_template(
        "index.html",
        error="Internal server error."
    ), 500


# ================= RUN SERVER =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=DEBUG
    )
