from flask import Flask, render_template, request, jsonify
from services.file_service import save_file, process_download, generate_qr

app = Flask(__name__)


# Home page (GET only)
@app.route("/")
def index():
    return render_template("index.html")


# ================= DOWNLOAD =================

@app.route("/download", methods=["POST"])
def download():
    code = request.form.get("code")
    response, error = process_download(code)

    if error:
        return render_template("index.html", error=error)

    return response


@app.route("/download_direct/<code>")
def download_direct(code):
    response, error = process_download(code)

    if error:
        return error

    return response


# ================= AJAX UPLOAD =================

@app.route("/upload_ajax", methods=["POST"])
def upload_ajax():

    files = request.files.getlist("file")

    if not files:
        return jsonify({"error": "No file selected!"}), 400

    codes = []

    for file in files:
        code, error = save_file(file)

        if error:
            return jsonify({"error": error}), 400

        download_url = request.url_root + "download_direct/" + code
        generate_qr(download_url, code)

        codes.append(code)

    return jsonify({
        "success": True,
        "codes": codes
    })


if __name__ == "__main__":
    app.run()
