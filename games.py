from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user


games_bp = Blueprint(
    "games",
    __name__,
    url_prefix="/games"
)


# Database references supplied by app.py
db = None
Mission = None
MissionAttempt = None


def configure_game_database(
    database,
    mission_model,
    mission_attempt_model
):
    global db
    global Mission
    global MissionAttempt

    db = database
    Mission = mission_model
    MissionAttempt = mission_attempt_model

# ============================================================
# GAME DATA
# ============================================================

GAMES = {

    "spot-the-phish": {
        "title": "Spot the Phish",
        "icon": "🕵️",
        "description": (
            "Can you identify suspicious messages before they trick you?"
        ),
        "category": "Beginner",

        # Connected to the Mission table in app.py
        "mission_slug": "phishing",

        "questions": [

            {
                "question": (
                    "You receive an email saying: "
                    "'URGENT! Your account will be closed today. "
                    "Click here immediately.' What is the biggest warning sign?"
                ),

                "choices": [
                    "The email has a greeting",
                    "It creates urgency and pressures you to click",
                    "The email contains text",
                    "The message has a subject"
                ],

                "answer": 1,

                "explanation": (
                    "Creating panic or urgency is a common phishing trick."
                )
            },

            {
                "question": (
                    "A message asks you to enter your password using a link "
                    "you were not expecting. What should you do?"
                ),

                "choices": [
                    "Click quickly before the link expires",
                    "Send your password to the sender",
                    "Verify the request using an official channel",
                    "Forward your password to a friend"
                ],

                "answer": 2,

                "explanation": (
                    "Unexpected password requests should be verified "
                    "through an official channel."
                )
            },

            {
                "question": (
                    "Which sender address would be most suspicious for "
                    "an organization called Secure Bank?"
                ),

                "choices": [
                    "support@securebank.com",
                    "help@securebank.com",
                    "security@securebank.com",
                    "security@secure-bank-login.example"
                ],

                "answer": 3,

                "explanation": (
                    "A strange or unrelated domain can be a major "
                    "phishing warning sign."
                )
            },

            {
                "question": (
                    "A message says you have won a prize but you never "
                    "entered a competition. What should you do?"
                ),

                "choices": [
                    "Click the prize link",
                    "Provide your information",
                    "Treat it as suspicious and verify it",
                    "Send it to everyone"
                ],

                "answer": 2,

                "explanation": (
                    "Unexpected prizes are commonly used to make people "
                    "click malicious links."
                )
            },

            {
                "question": (
                    "Which action is safest when you receive a suspicious link?"
                ),

                "choices": [
                    "Open it to see what happens",
                    "Verify the website independently",
                    "Send it to another person",
                    "Enter your login details first"
                ],

                "answer": 1,

                "explanation": (
                    "Use a trusted route to reach the real website instead "
                    "of clicking a suspicious link."
                )
            }
        ]
    },


    # ========================================================
    # PASSWORD DEFENDER
    # ========================================================

    "password-defender": {

        "title": "Password Defender",

        "icon": "🔐",

        "description": (
            "Protect accounts by making smart password decisions."
        ),

        "category": "Beginner",

        "mission_slug": "account-security",

        "questions": [

            {
                "question": "Which password practice is safest?",

                "choices": [
                    "Use the same password everywhere",
                    "Use unique passwords for important accounts",
                    "Share passwords with friends",
                    "Use your name as your password"
                ],

                "answer": 1,

                "explanation": (
                    "Unique passwords reduce the damage if one account "
                    "is compromised."
                )
            },

            {
                "question": "What adds an extra layer of protection to an account?",

                "choices": [
                    "Dark mode",
                    "Two-factor authentication",
                    "A profile picture",
                    "A longer username"
                ],

                "answer": 1,

                "explanation": (
                    "Two-factor authentication requires an additional "
                    "verification step."
                )
            },

            {
                "question": (
                    "Why should you avoid using personal information "
                    "in passwords?"
                ),

                "choices": [
                    "It makes websites slower",
                    "It is easier for others to guess",
                    "It prevents you from logging in",
                    "It changes your username"
                ],

                "answer": 1,

                "explanation": (
                    "Information such as names, birthdays, or school names "
                    "can be easier to guess."
                )
            },

            {
                "question": (
                    "Someone asks you for your account password so they "
                    "can 'help' you. What should you do?"
                ),

                "choices": [
                    "Give it immediately",
                    "Post it privately",
                    "Keep it private",
                    "Send it through a public group"
                ],

                "answer": 2,

                "explanation": (
                    "Passwords should remain private, even when someone "
                    "claims they need them."
                )
            },

            {
                "question": (
                    "What should you do if you think your password "
                    "has been exposed?"
                ),

                "choices": [
                    "Keep using it",
                    "Change it and secure the account",
                    "Share it with someone",
                    "Post a warning containing the password"
                ],

                "answer": 1,

                "explanation": (
                    "Change the exposed password and use additional "
                    "security such as 2FA."
                )
            }
        ]
    },


    # ========================================================
    # FIND THE RED FLAGS
    # ========================================================

    "find-the-red-flags": {

        "title": "Find the Red Flags",

        "icon": "🔎",

        "description": (
            "Look carefully and identify cybersecurity warning signs."
        ),

        "category": "Medium",

        "mission_slug": "web-safety",

        "questions": [

            {
                "question": (
                    "A public computer is asking you whether to save "
                    "your password. What is the safest choice?"
                ),

                "choices": [
                    "Save it",
                    "Save it for later",
                    "Do not save it",
                    "Write it on the screen"
                ],

                "answer": 2,

                "explanation": (
                    "Other people may use a public computer after you."
                )
            },

            {
                "question": (
                    "You connect to Wi-Fi at a public place. Which action "
                    "provides better protection for sensitive activity?"
                ),

                "choices": [
                    "Use an unprotected connection for everything",
                    "Use appropriate security protections such as a trusted VPN",
                    "Disable every security feature",
                    "Share your account password"
                ],

                "answer": 1,

                "explanation": (
                    "Security protections can help reduce risks when "
                    "using public networks."
                )
            },

            {
                "question": (
                    "An app asks for access to information that does not "
                    "appear necessary for its function. What should you do?"
                ),

                "choices": [
                    "Approve everything automatically",
                    "Review the permission and decide carefully",
                    "Give the app your password",
                    "Install more copies of the app"
                ],

                "answer": 1,

                "explanation": (
                    "Review app permissions and only grant access "
                    "that is appropriate."
                )
            },

            {
                "question": (
                    "Your computer suddenly shows many unexpected warnings "
                    "asking you to install unknown software. What should you do?"
                ),

                "choices": [
                    "Install everything",
                    "Ignore the warnings and keep clicking",
                    "Stop and investigate the source",
                    "Enter your password into every warning"
                ],

                "answer": 2,

                "explanation": (
                    "Unexpected security warnings can be deceptive. "
                    "Verify the source before taking action."
                )
            },

            {
                "question": (
                    "Which is a warning sign that a website may not "
                    "be trustworthy?"
                ),

                "choices": [
                    "It has a normal navigation menu",
                    "It uses HTTPS",
                    "The address is strange or impersonates another organization",
                    "It has a footer"
                ],

                "answer": 2,

                "explanation": (
                    "A suspicious or impersonating domain is an important "
                    "warning sign."
                )
            }
        ]
    },


    # ========================================================
    # CYBER SHIELD
    # ========================================================

    "cyber-shield": {

        "title": "Cyber Shield",

        "icon": "🛡️",

        "description": (
            "Choose the security action that best protects the situation."
        ),

        "category": "Medium",

        "mission_slug": "device-security",

        "questions": [

            {
                "question": (
                    "Your operating system has an important security "
                    "update available. What should you do?"
                ),

                "choices": [
                    "Ignore updates forever",
                    "Install updates from trusted sources",
                    "Disable security updates",
                    "Delete the operating system"
                ],

                "answer": 1,

                "explanation": (
                    "Security updates often fix vulnerabilities."
                )
            },

            {
                "question": (
                    "Which security control can help block unwanted "
                    "network traffic?"
                ),

                "choices": [
                    "Firewall",
                    "Calculator",
                    "Wallpaper",
                    "Music player"
                ],

                "answer": 0,

                "explanation": (
                    "Firewalls can control network traffic according "
                    "to security rules."
                )
            },

            {
                "question": "Why are backups important?",

                "choices": [
                    "They make passwords shorter",
                    "They can help recover data after loss or an incident",
                    "They remove every cyber threat",
                    "They replace all security controls"
                ],

                "answer": 1,

                "explanation": (
                    "Backups provide a way to recover important information."
                )
            },

            {
                "question": "What is encryption mainly used for?",

                "choices": [
                    "Making data unreadable to unauthorized people",
                    "Making computers physically larger",
                    "Removing the need for passwords",
                    "Increasing screen brightness"
                ],

                "answer": 0,

                "explanation": (
                    "Encryption transforms data so unauthorized people "
                    "cannot easily read it."
                )
            },

            {
                "question": (
                    "Which action can help protect an account "
                    "from unauthorized access?"
                ),

                "choices": [
                    "Using two-factor authentication",
                    "Sharing the password",
                    "Using the same password everywhere",
                    "Disabling account security"
                ],

                "answer": 0,

                "explanation": (
                    "Two-factor authentication adds another "
                    "verification layer."
                )
            }
        ]
    }
}


# ============================================================
# GAME LIST
# ============================================================

@games_bp.route("/")
@login_required
def games_home():

    return render_template(
        "games.html",
        games=GAMES
    )


# ============================================================
# PLAY GAME
# ============================================================

@games_bp.route("/<game_id>")
@login_required
def play_game(game_id):

    game = GAMES.get(game_id)

    if not game:
        return "Game not found", 404

    return render_template(
        "play_game.html",
        game_id=game_id,
        game=game
    )


# ============================================================
# GAME DATA API
# ============================================================

@games_bp.route("/api/<game_id>")
@login_required
def game_api(game_id):

    game = GAMES.get(game_id)

    if not game:

        return jsonify({
            "success": False,
            "message": "Game not found"
        }), 404

    return jsonify({
        "success": True,
        "title": game["title"],
        "questions": game["questions"]
    })


# ============================================================
# SAVE GAME SCORE
# ============================================================

@games_bp.route(
    "/api/<game_id>/score",
    methods=["POST"]
)
@login_required
def save_game_score(game_id):

    # --------------------------------------------------------
    # Find game
    # --------------------------------------------------------

    game = GAMES.get(game_id)

    if not game:

        return jsonify({
            "success": False,
            "message": "Game not found."
        }), 404


    # --------------------------------------------------------
    # Get submitted score
    # --------------------------------------------------------

    data = request.get_json(silent=True) or {}

    try:

        score = int(data.get("score", 0))

    except (
        TypeError,
        ValueError
    ):

        return jsonify({
            "success": False,
            "message": "Invalid score."
        }), 400


    # --------------------------------------------------------
    # Protect the score
    # --------------------------------------------------------

    question_count = len(
        game["questions"]
    )

    max_score = question_count * 10

    if score < 0:
        score = 0

    if score > max_score:
        score = max_score


    # --------------------------------------------------------
    # Find the connected mission
    # --------------------------------------------------------

    mission_slug = game.get(
        "mission_slug"
    )

    mission = Mission.query.filter_by(
        slug=mission_slug,
        active=True
    ).first()


    if not mission:

        return jsonify({
            "success": False,
            "message": "The mission connected to this game was not found."
        }), 404


    # --------------------------------------------------------
    # Find previous attempt
    # --------------------------------------------------------

    attempt = MissionAttempt.query.filter_by(
        participant_id=current_user.id,
        mission_id=mission.id
    ).first()


    # --------------------------------------------------------
    # Calculate percentage
    # --------------------------------------------------------

    percentage = 0

    if max_score > 0:

        percentage = round(
            (score / max_score) * 100
        )


    # A participant is considered to have completed
    # the mission at 70% or higher.

    completed = percentage >= 70


    # --------------------------------------------------------
    # Calculate points
    # --------------------------------------------------------

    earned_points = round(
        (score / max_score) * mission.points
    )


    # --------------------------------------------------------
    # FIRST ATTEMPT
    # --------------------------------------------------------

    if attempt is None:

        attempt = MissionAttempt(
            participant_id=current_user.id,
            mission_id=mission.id,
            score=score,
            completed=completed
        )

        if completed:

            from datetime import datetime

            attempt.completed_at = datetime.utcnow()

        db.session.add(attempt)

        current_user.points += earned_points


    # --------------------------------------------------------
    # EXISTING ATTEMPT
    #
    # Only a higher score can increase leaderboard points.
    # --------------------------------------------------------

    else:

        old_score = attempt.score

        old_points = round(
            (old_score / max_score) * mission.points
        )

        if score > old_score:

            attempt.score = score

            attempt.completed = completed

            if completed and attempt.completed_at is None:

                from datetime import datetime

                attempt.completed_at = datetime.utcnow()

            new_points = earned_points

            point_difference = (
                new_points - old_points
            )

            if point_difference > 0:

                current_user.points += point_difference


    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    db.session.commit()


    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return jsonify({

        "success": True,

        "game": game["title"],

        "score": score,

        "max_score": max_score,

        "percentage": percentage,

        "earned_points": earned_points,

        "total_points": current_user.points,

        "completed": completed,

        "message": (
            "Game completed and score saved."
            if completed
            else
            "Score saved. Reach 70% or higher to complete this mission."
        )
    })

