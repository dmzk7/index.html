from datetime import date
from flask import Blueprint, g, jsonify, request
from .auth import login_required
from .database import get_db

api_bp = Blueprint("api", __name__)


@api_bp.route("/stats")
@login_required
def api_stats():
    db = get_db()
    user_id = g.user["id"]
    total_users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    top_users = db.execute("SELECT name, points FROM users ORDER BY points DESC LIMIT 5").fetchall()
    referrals = db.execute("SELECT COUNT(*) FROM referrals WHERE user_id = ?", (user_id,)).fetchone()[0]
    daily_checkins = db.execute("SELECT COUNT(*) FROM checkins WHERE date = ?", (date.today().isoformat(),)).fetchone()[0]

    return jsonify(
        success=True,
        stats={
            "total_users": total_users,
            "top_users": [{"name": row["name"], "points": row["points"]} for row in top_users],
            "referrals": referrals,
            "daily_checkins": daily_checkins,
        },
    )


@api_bp.route("/user")
@login_required
def api_user():
    user = g.user
    return jsonify(
        success=True,
        user={
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "points": user["points"],
            "referral_code": user["referral_code"],
            "bio": user["bio"],
            "created_at": user["created_at"],
        },
    )


@api_bp.route("/leaderboard")
@login_required
def api_leaderboard():
    db = get_db()
    rows = db.execute("SELECT name, points FROM users ORDER BY points DESC LIMIT 10").fetchall()
    return jsonify(success=True, leaderboard=[{"name": row["name"], "points": row["points"]} for row in rows])
