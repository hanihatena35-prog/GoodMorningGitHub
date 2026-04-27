from flask import Flask, render_template, request, redirect, session, flash
from datetime import datetime, timedelta
import re

app = Flask(__name__)
app.secret_key = "secret_key"

# 仮のユーザーデータ（本来はDB）
user_data = {
    "username": "testuser",
    "password": "Testpass1",
    "password_updated": datetime.now() - timedelta(days=80)  # 80日前に更新 → 期限間近
}

PASSWORD_EXPIRE_DAYS = 90
PASSWORD_WARNING_DAYS = 7


def is_valid_password(pw):
    """パスワードのバリデーション"""
    if len(pw) < 8:
        return False
    if not re.match(r"^[A-Za-z0-9]+$", pw):
        return False
    return True


def check_password_expiry():
    """パスワード期限チェック"""
    last_update = user_data["password_updated"]
    expire_date = last_update + timedelta(days=PASSWORD_EXPIRE_DAYS)
    warning_date = expire_date - timedelta(days=PASSWORD_WARNING_DAYS)

    return datetime.now(), warning_date, expire_date


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username != user_data["username"] or password != user_data["password"]:
            flash("ユーザー名またはパスワードが違います")
            return render_template("login.html")

        now, warn, expire = check_password_expiry()

        session["username"] = username

        # 有効期限切れ
        if now > expire:
            flash("パスワードの有効期限が切れています。変更してください。")
            return redirect("/change_password")

        # 期限1週間前
        if now >= warn:
            flash("パスワードの有効期限が1週間以内です。変更を推奨します。")
            return redirect("/home")

        return redirect("/home")

    return render_template("login.html")


@app.route("/home")
def home():
    if "username" not in session:
        return redirect("/")
    return render_template("home.html")


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "username" not in session:
        return redirect("/")

    if request.method == "POST":
        new_pw = request.form["new_password"]

        if not is_valid_password(new_pw):
            flash("パスワードは8文字以上で英大文字・英小文字・数字のみ使用できます")
            return render_template("change_password.html")

        user_data["password"] = new_pw
        user_data["password_updated"] = datetime.now()

        flash("パスワードを変更しました")
        return redirect("/home")

    return render_template("change_password.html")


if __name__ == "__main__":
    app.run(debug=True)
