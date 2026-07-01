from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from .auth import admin_required, login_required, verify_csrf
from .database import get_db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
@admin_required
def admin_home():
    db = get_db()
    users = db.execute(
        "SELECT id, name, email, points, referral_code, created_at FROM users ORDER BY created_at DESC LIMIT 20"
    ).fetchall()
    stats = {
        "total_users": db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "total_checkins": db.execute("SELECT COUNT(*) FROM checkins").fetchone()[0],
        "total_referrals": db.execute("SELECT COUNT(*) FROM referrals").fetchone()[0],
    }
    return render_template("admin.html", title="Admin | MoneyHub", users=users, stats=stats)


@admin_bp.route("/user/<int:user_id>/points", methods=["POST"])
@login_required
@admin_required
def update_user_points(user_id):
    db = get_db()
    amount = request.form.get("points", "0").strip()
    token = request.form.get("csrf_token")
    if not verify_csrf(token):
        flash("Falha na verificação CSRF.", "danger")
        return redirect(url_for("admin.admin_home"))

    try:
        points = int(amount)
        db.execute("UPDATE users SET points = ? WHERE id = ?", (points, user_id))
        db.commit()
        flash("Pontos do usuário atualizados com sucesso.", "success")
    except ValueError:
        flash("Valor de pontos inválido.", "danger")
    return redirect(url_for("admin.admin_home"))
