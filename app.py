import os
from flask import Flask, render_template, request, jsonify
from config import MAX_FILE_SIZE, SECRET_KEY, DEBUG
from database import init_db
from services.file_service import save_files, process_download, generate_qr


# ================= APP INIT =================
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE
app.config["SECRET_KEY"] = SECRET_KEY


# ================= INITIALIZE DATABASE =================
init_db()


# ================= HOME =================
@app.route("/")
def index():
    return render_template("index.html")


# ================= HEALTH CHECK (Render Required) =================
@app.route("/health")
def health():
    return jsonify({"status": "OK"}), 200


# ================= DOWNLOAD =================
@app.route("/download", methods=["POST"])
def download():
    code = request.form.get("code", "").strip().upper()

    if not code or len(code) != 6:
        return render_template("index.html", error="Invalid download code.")

    response, error = process_download(code)

    if error:
        return render_template("index.html", error=error)

    return response


@app.route("/download_direct/<code>")
def download_direct(code):
    code = code.strip().upper()

    response, error = process_download(code)

    if error:
        return error, 404

    return response


# ================= AJAX MULTIPLE UPLOAD =================
@app.route("/upload_ajax", methods=["POST"])
def upload_ajax():

    files = request.files.getlist("file")

    if not files or files[0].filename == "":
        return jsonify({
            "success": False,
            "error": "No files uploaded"
        })

    # 🔥 Save all files under ONE code
    code, error = save_files(files)

    if error:
        return jsonify({
            "success": False,
            "error": error
        })

    # Generate QR
    download_url = request.url_root + "download_direct/" + code
    generate_qr(download_url, code)

    return jsonify({
        "success": True,
        "code": code
    })


# ================= ERROR HANDLERS =================
@app.errorhandler(413)
def file_too_large(e):
    return jsonify({"error": "File too large! Max 20MB allowed."}), 413


@app.errorhandler(404)
def not_found(e):
    return render_template("index.html", error="Page not found."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("index.html", error="Internal server error."), 500


# ================= RUN SERVER =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=DEBUG)
