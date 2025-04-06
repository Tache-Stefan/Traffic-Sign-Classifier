from flask import Blueprint, render_template, request, send_from_directory, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
import os
from app.models.user import UserStatistics, db
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
