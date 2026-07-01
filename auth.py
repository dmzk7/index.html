import re
import secrets
from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from .database import get_db

auth_bp = Blueprint("auth", __name__)

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(16)
    return session["csrf_token"]


def verify_csrf(token):
    return token and session.get("csrf_token") == token


def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
        return
    db = get_db()
    g.user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def login_required(view):
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Faça login para continuar.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    wrapped_view.__name__ = view.__name__
    return wrapped_view


def admin_required(view):
    def wrapped_view(*args, **kwargs):
        if g.user is None or not g.user["is_admin"]:
            flash("Acesso administrativo necessário.", "danger")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    wrapped_view.__name__ = view.__name__
    return wrapped_view


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        token = request.form.get("csrf_token")
        if not verify_csrf(token):
            flash("Falha na verificação CSRF.", "danger")
            return redirect(url_for("auth.login"))

        db = get_db()
        error = None
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user is None:
            error = "E-mail ou senha incorretos."
        elif not check_password_hash(user["password_hash"], password):
            error = "E-mail ou senha incorretos."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            flash(f"Bem-vindo de volta, {user['name']}!", "success")
            return redirect(url_for("dashboard.home"))

        flash(error, "danger")

    return render_template("login.html", title="Login | MoneyHub")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        referral_code = request.form.get("referral_code", "").strip().upper()
        token = request.form.get("csrf_token")

        if not verify_csrf(token):
            flash("Falha na verificação CSRF.", "danger")
            return redirect(url_for("auth.register"))

        error = None
        if len(name) < 3:
            error = "Informe seu nome completo."
        elif not EMAIL_PATTERN.match(email):
            error = "Informe um e-mail válido."
        elif len(password) < 8:
            error = "A senha deve ter ao menos 8 caracteres."

        db = get_db()
        if db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone() is not None:
            error = "Este e-mail já está registrado."

        referred_by = None
        reward = 0
        if referral_code:
            sponsor = db.execute(
                "SELECT id FROM users WHERE referral_code = ?", (referral_code,)
            ).fetchone()
            if sponsor is None:
                error = "Código de indicação inválido."
            else:
                referred_by = sponsor["id"]
                reward = 50

        if error is None:
            password_hash = generate_password_hash(password)
            invitation_code = secrets.token_hex(3).upper()
            db.execute(
                "INSERT INTO users (name, email, password_hash, referral_code, referred_by, points) VALUES (?, ?, ?, ?, ?, ?)",
                (name, email, password_hash, invitation_code, referred_by, 100 + reward),
            )
            db.commit()

            if referred_by:
                db.execute(
                    "INSERT INTO referrals (user_id, referred_email) VALUES (?, ?)",
                    (referred_by, email),
                )
                db.execute(
                    "UPDATE users SET points = points + 50 WHERE id = ?", (referred_by,)
                )
                db.commit()

            flash("Cadastro realizado com sucesso. Faça login para continuar.", "success")
            return redirect(url_for("auth.login"))

        flash(error, "danger")

    return render_template("register.html", title="Cadastro | MoneyHub")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada com sucesso.", "info")
    return redirect(url_for("auth.login"))
