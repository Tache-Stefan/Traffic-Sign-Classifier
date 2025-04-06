from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableDict
db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class UserStatistics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_predictions = db.Column(db.Integer, default=0)
    correct_predictions = db.Column(db.Integer, default=0)
    label_predictions = db.Column(MutableDict.as_mutable(JSON), nullable=True, default=dict)

    def update_label_statistics(self, label, correct):
        if not isinstance(self.label_predictions, dict):
            self.label_predictions = {}

        if label not in self.label_predictions:
            self.label_predictions[label] = {"total": 0, "correct": 0}

        self.label_predictions[label]["total"] += 1
        if correct:
            self.label_predictions[label]["correct"] += 1

        if self.total_predictions is None:
            self.total_predictions = 0
        if self.correct_predictions is None:
            self.correct_predictions = 0

        self.total_predictions += 1
        if correct:
            self.correct_predictions += 1

        db.session.commit()

    def get_label_statistics_summary(self):
        summary = []
        for label, stats in self.label_predictions.items():
            label = int(label)
            summary.append({
                "label": label,
                "total": stats.get("total", 0),
                "correct": stats.get("correct", 0),
            })
        return summary
