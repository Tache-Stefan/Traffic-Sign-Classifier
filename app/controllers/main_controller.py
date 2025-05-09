from flask import Blueprint, render_template, request, send_from_directory, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
import os
from app.models.user import UserStatistics, db
from app.utils.classifier import predict_image
from app.utils.config import GTSRB_labels
from werkzeug.utils import secure_filename


main_bp = Blueprint('main', __name__)


@main_bp.route("/", methods=["GET", "POST"])
@main_bp.route("/home", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        model_name = request.form.get("model")

        if not file or file.filename == "":
            return "No file uploaded"
        if not model_name:
            return "No model provided"
        if not file.content_type.startswith("image/"):
            return "Uploaded file is not an image."

        filename = secure_filename(file.filename)
        upload_folder = current_app.config["UPLOAD_FOLDER"]

        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        prediction = predict_image(filepath, model_name)
        return render_template("index.html", filename=filename,
                               prediction=prediction, label=GTSRB_labels[prediction])
    return render_template("index.html")


@main_bp.route("/uploads/<filename>")
def uploaded_file(filename):
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    return send_from_directory(upload_folder, filename)


@main_bp.route("/feedback", methods=["POST"])
@login_required
def feedback():
    label = request.form.get("label")
    feedback = request.form.get("feedback")

    if label is None or feedback not in ["correct", "incorrect"]:
        flash("Invalid feedback received.", "danger")
        return redirect(url_for('main.index'))

    stats = UserStatistics.query.filter_by(user_id=current_user.id).first()
    if not stats:
        stats = UserStatistics(user_id=current_user.id)
        db.session.add(stats)

    correct = feedback == "correct"
    stats.update_label_statistics(label, correct)

    return redirect(url_for('main.index'))


@main_bp.route("/<username>")
@login_required
def profile(username):
    stats = UserStatistics.query.filter_by(user_id=current_user.id).first()
    label_stats = stats.get_label_statistics_summary() if stats else []
    return render_template("profile.html", user=current_user, stats=stats,
                                             label_stats=label_stats, GTSRB_labels=GTSRB_labels)

@main_bp.route("/about")
def about():
    return render_template("about.html")
