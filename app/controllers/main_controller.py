from flask import Blueprint, render_template, request, send_from_directory, current_app
import os
from app.utils.classifier import predict_image
from app.utils.config import GTSRB_labels


main_bp = Blueprint('main', __name__)


@main_bp.route("/", methods=["GET", "POST"])
@main_bp.route("/home", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            return "No file uploaded"
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)
        prediction = predict_image(filepath)
        return render_template("index.html", filename=file.filename,
                               prediction=prediction, label=GTSRB_labels[prediction])
    return render_template("index.html")


@main_bp.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
