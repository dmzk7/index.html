from datetime import date
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from .auth import login_required, verify_csrf
from .database import get_db


dashboard_bp = Blueprint("dashboard", __name__)


def get_checkin_status(user_id):
    db = get_db()
    row = db.execute(
        "SELECT date FROM checkins WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    return row["date"] if row else None


@dashboard_bp.route("/")
def home():
    return render_template("index.html", title="MoneyHub | Recompensas e Monetização")


@dashboard_bp.route("/dashboard")
@login_required
def user_dashboard():
    db = get_db()
    user_id = g.user["id"]
    last_checkin = get_checkin_status(user_id)
    can_checkin = last_checkin != date.today().isoformat()

    ranking = db.execute(
        "SELECT name, points FROM users ORDER BY points DESC LIMIT 5"
    ).fetchall()
    referrals = db.execute(
        "SELECT referred_email, created_at FROM referrals WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
        (user_id,),
    ).fetchall()
    stats = {
        "total_users": db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "daily_checkins": db.execute("SELECT COUNT(*) FROM checkins WHERE date = ?", (date.today().isoformat(),)).fetchone()[0],
        "referral_count": db.execute("SELECT COUNT(*) FROM referrals WHERE user_id = ?", (user_id,)).fetchone()[0],
    }

    return render_template(
        "dashboard.html",
        title="Painel | MoneyHub",
        can_checkin=can_checkin,
        last_checkin=last_checkin,
        ranking=ranking,
        referrals=referrals,
        stats=stats,
    )


@dashboard_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db = get_db()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        bio = request.form.get("bio", "").strip()
        token = request.form.get("csrf_token")
        if not verify_csrf(token):
            flash("Falha na verificação CSRF.", "danger")
            return redirect(url_for("dashboard.profile"))

        if len(name) < 3:
            flash("O nome deve ter pelo menos 3 caracteres.", "danger")
        else:
            db.execute(
                "UPDATE users SET name = ?, bio = ? WHERE id = ?",
                (name, bio, g.user["id"]),
            )
            db.commit()
            flash("Perfil atualizado com sucesso.", "success")
            return redirect(url_for("dashboard.profile"))

    return render_template("profile.html", title="Perfil | MoneyHub")


@dashboard_bp.route("/checkin", methods=["POST"])
@login_required
def checkin():
    db = get_db()
    today = date.today().isoformat()
    last_checkin = get_checkin_status(g.user["id"])
    token = request.form.get("csrf_token")
    if not verify_csrf(token):
        flash("Falha na verificação CSRF.", "danger")
        return redirect(url_for("dashboard.user_dashboard"))

    if last_checkin == today:
        flash("Você já realizou o check-in diário hoje.", "warning")
    else:
        db.execute(
            "INSERT INTO checkins (user_id, date, reward) VALUES (?, ?, ?)",
            (g.user["id"], today, 25),
        )
        db.execute(
            "UPDATE users SET points = points + 25 WHERE id = ?",
            (g.user["id"],),
        )
        db.commit()
        flash("Check-in diário concluído! +25 pontos adicionados.", "success")

    return redirect(url_for("dashboard.user_dashboard"))
