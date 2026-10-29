from datetime import datetime
from functools import wraps
from games import games_bp, configure_game_database
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

app = Flask(__name__)

app.register_blueprint(games_bp)
app.config["SECRET_KEY"] = "change-this-secret-key-before-production"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cyber_awareness.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


# ============================================================
# DATABASE MODELS
# ============================================================

class Participant(UserMixin, db.Model):
    __tablename__ = "participants"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(120), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(255), nullable=False)

    organization = db.Column(db.String(150), nullable=True)

    participant_type = db.Column(
        db.String(50),
        nullable=False,
        default="Student"
    )

    points = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    attempts = db.relationship(
        "MissionAttempt",
        backref="participant",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Mission(db.Model):
    __tablename__ = "missions"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    slug = db.Column(db.String(150), unique=True, nullable=False)

    description = db.Column(db.Text, nullable=False)

    icon = db.Column(db.String(20), nullable=False, default="🛡️")

    points = db.Column(db.Integer, nullable=False, default=100)

    active = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    attempts = db.relationship(
        "MissionAttempt",
        backref="mission",
        lazy=True,
        cascade="all, delete-orphan"
    )


class MissionAttempt(db.Model):
    __tablename__ = "mission_attempts"

    id = db.Column(db.Integer, primary_key=True)

    participant_id = db.Column(
        db.Integer,
        db.ForeignKey("participants.id"),
        nullable=False
    )

    mission_id = db.Column(
        db.Integer,
        db.ForeignKey("missions.id"),
        nullable=False
    )

    score = db.Column(db.Integer, nullable=False, default=0)

    completed = db.Column(db.Boolean, nullable=False, default=False)

    completed_at = db.Column(
        db.DateTime,
        nullable=True
    )


# ============================================================
# LOGIN MANAGER
# ============================================================

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Participant, int(user_id))


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def create_default_missions():
    missions = [
        {
            "name": "Spot the Phish",
            "slug": "phishing",
            "description": (
                "Learn how to identify suspicious emails, messages, "
                "links and online scams."
            ),
            "icon": "🎣",
            "points": 100
        },
        {
            "name": "Protect Your Account",
            "slug": "account-security",
            "description": (
                "Learn about strong passwords, multi-factor authentication "
                "and account protection."
            ),
            "icon": "🔐",
            "points": 100
        },
        {
            "name": "Secure Your Device",
            "slug": "device-security",
            "description": (
                "Discover practical ways to protect phones, computers "
                "and other digital devices."
            ),
            "icon": "📱",
            "points": 100
        },
        {
            "name": "Browse Safely",
            "slug": "web-safety",
            "description": (
                "Learn how to recognize unsafe websites, suspicious links "
                "and dangerous downloads."
            ),
            "icon": "🌐",
            "points": 100
        },
        {
            "name": "Cyber Detective",
            "slug": "cyber-detective",
            "description": (
                "Investigate a fictional cyber incident and discover "
                "what happened."
            ),
            "icon": "🕵️",
            "points": 150
        },
        {
            "name": "Capture the Flag",
            "slug": "ctf",
            "description": (
                "Take part in beginner-friendly cybersecurity challenges "
                "and find hidden flags."
            ),
            "icon": "🚩",
            "points": 250
        },
        {
            "name": "AI Cyber Challenge",
            "slug": "ai-challenge",
            "description": (
                "Use an interactive AI-powered cybersecurity scenario "
                "to practice making safe decisions."
            ),
            "icon": "🤖",
            "points": 150
        },
        {
            "name": "Final Cyber Challenge",
            "slug": "final-challenge",
            "description": (
                "Test what you learned throughout Cyber Awareness Month."
            ),
            "icon": "🧠",
            "points": 200
        }
    ]

    for item in missions:
        existing = Mission.query.filter_by(slug=item["slug"]).first()

        if not existing:
            mission = Mission(
                name=item["name"],
                slug=item["slug"],
                description=item["description"],
                icon=item["icon"],
                points=item["points"]
            )

            db.session.add(mission)

    db.session.commit()
configure_game_database(
    db,
    Mission,
    MissionAttempt
)

with app.app_context():
    db.create_all()
    create_default_missions()


# ============================================================
# PUBLIC ROUTES
# ============================================================

@app.route("/")
def index():
    missions = Mission.query.filter_by(active=True).all()

    return render_template(
        "index.html",
        missions=missions
    )


# ============================================================
# REGISTRATION
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()

        email = request.form.get("email", "").strip().lower()

        password = request.form.get("password", "")

        organization = request.form.get(
            "organization",
            ""
        ).strip()

        participant_type = request.form.get(
            "participant_type",
            "Student"
        ).strip()

        if not full_name or not email or not password:
            flash(
                "Please complete all required fields.",
                "error"
            )

            return redirect(url_for("register"))

        if len(password) < 8:
            flash(
                "Password must contain at least 8 characters.",
                "error"
            )

            return redirect(url_for("register"))

        existing_user = Participant.query.filter_by(
            email=email
        ).first()

        if existing_user:
            flash(
                "An account with this email already exists.",
                "error"
            )

            return redirect(url_for("login"))

        participant = Participant(
            full_name=full_name,
            email=email,
            organization=organization,
            participant_type=participant_type
        )

        participant.set_password(password)

        db.session.add(participant)
        db.session.commit()

        login_user(participant)

        flash(
            "Welcome to Cyber Awareness Month!",
            "success"
        )

        return redirect(url_for("dashboard"))

    return render_template("register.html")


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        participant = Participant.query.filter_by(
            email=email
        ).first()

        if participant and participant.check_password(password):

            login_user(participant)

            next_page = request.args.get("next")

            if next_page and next_page.startswith("/"):
                return redirect(next_page)

            return redirect(url_for("dashboard"))

        flash(
            "Invalid email or password.",
            "error"
        )

    return render_template("login.html")


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("index"))


# ============================================================
# PARTICIPANT DASHBOARD
# ============================================================

@app.route("/dashboard")
@login_required
def dashboard():

    missions = Mission.query.filter_by(
        active=True
    ).order_by(Mission.id).all()

    completed_attempts = MissionAttempt.query.filter_by(
        participant_id=current_user.id,
        completed=True
    ).all()

    completed_mission_ids = {
        attempt.mission_id
        for attempt in completed_attempts
    }

    total_missions = len(missions)

    completed_count = len(completed_mission_ids)

    if total_missions > 0:
        progress = round(
            (completed_count / total_missions) * 100
        )
    else:
        progress = 0

    return render_template(
        "dashboard.html",
        missions=missions,
        completed_mission_ids=completed_mission_ids,
        completed_count=completed_count,
        total_missions=total_missions,
        progress=progress
    )


# ============================================================
# LEADERBOARD
# ============================================================

@app.route("/leaderboard")
def leaderboard():

    participants = Participant.query.order_by(
        Participant.points.desc(),
        Participant.created_at.asc()
    ).limit(100).all()

    return render_template(
        "leaderboard.html",
        participants=participants
    )


# ============================================================
# MISSION PLACEHOLDER
# ============================================================

@app.route("/mission/<slug>")
@login_required
def mission(slug):

    mission_data = Mission.query.filter_by(
        slug=slug,
        active=True
    ).first_or_404()

    return render_template(
        "dashboard.html",
        missions=Mission.query.filter_by(
            active=True
        ).order_by(Mission.id).all(),
        completed_mission_ids=set(),
        completed_count=0,
        total_missions=Mission.query.filter_by(
            active=True
        ).count(),
        progress=0,
        selected_mission=mission_data
    )


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "base.html",
        error_message="The page you requested could not be found."
    ), 404


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )