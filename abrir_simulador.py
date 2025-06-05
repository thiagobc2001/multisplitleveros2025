import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from requests_oauthlib import OAuth2Session
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# ====== FLASK CONFIGURAÇÃO ======
app = Flask(__name__, static_folder='static')
app.secret_key = os.getenv('FLASK_SECRET_KEY')


# ====== OAUTH CONFIG ======
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"
REDIRECT_URI = "https://multisplitleveros2025.onrender.com/callback"
SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

# ====== BANCO DE DADOS ======
DATABASE_URL = os.getenv("DATABASE_URL")  # <-- A URL que você copiou no Render

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    rating = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ====== MIDDLEWARE LOGIN ======
def login_required(view_func):
    def wrapped_view(*args, **kwargs):
        if "email" not in session or not session["email"].endswith("@leveros.com.br"):
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    wrapped_view.__name__ = view_func.__name__
    return wrapped_view

@app.route("/")
def index():
    if "email" in session and session["email"].endswith("@leveros.com.br"):
        return redirect(url_for("selecionar_fornecedor"))
    return redirect(url_for("login"))

@app.route("/login")
def login():
    google = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPE)
    authorization_url, state = google.authorization_url(
        AUTHORIZATION_BASE_URL,
        access_type="offline",
        prompt="select_account"
    )
    session["oauth_state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    google = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, state=session.get("oauth_state"))
    token = google.fetch_token(
        TOKEN_URL,
        client_secret=CLIENT_SECRET,
        authorization_response=request.url
    )
    session["oauth_token"] = token
    userinfo = google.get(USER_INFO_URL).json()
    
    email = userinfo.get("email", "")
    if not email.endswith("@leveros.com.br"):
        return "Acesso restrito a usuários @leveros.com.br", 403

    session["email"] = email
    return redirect(url_for("selecionar_fornecedor"))

@app.route("/selecionar", methods=["GET", "POST"])
@login_required
def selecionar_fornecedor():
    fornecedores = ['LG', 'Fujitsu', 'Daikin', 'TCL', 'Gree', 'Midea']
    if request.method == 'POST':
        session['fornecedor'] = request.form.get('fornecedor', 'LG')
        return redirect(url_for('simulador'))
    return render_template('login.html', fornecedores=fornecedores)

@app.route("/simulador")
@login_required
def simulador():
    fornecedor = session.get('fornecedor', 'LG')
    caminho_json = f'/static/data/{fornecedor}/'
    return render_template('simulador.html', caminho_json=caminho_json, fornecedor=fornecedor)

@app.route("/submit_feedback", methods=["POST"])
@login_required
def submit_feedback():
    email = session["email"]
    rating = request.json.get("rating")

    db = SessionLocal()
    feedback = db.query(Feedback).filter(Feedback.email == email).first()
    if not feedback:
        novo_feedback = Feedback(email=email, rating=rating)
        db.add(novo_feedback)
        db.commit()
    db.close()
    return jsonify({"message": "Feedback registrado!"})

@app.route("/feedback_status")
@login_required
def feedback_status():
    email = session["email"]
    db = SessionLocal()
    feedback = db.query(Feedback).filter(Feedback.email == email).first()
    db.close()
    if feedback:
        return jsonify({"has_feedback": True})
    else:
        return jsonify({"has_feedback": False})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
