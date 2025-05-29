import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
from flask import Flask, render_template, request, redirect, url_for, session
from requests_oauthlib import OAuth2Session

app = Flask(__name__, static_folder='static')
app.secret_key = 'b3b0d4523a3fdc6a91ee0f795ad78d33f7c394e2b8328e9c4dd478f97c9f4e7d'  # Altere para algo seguro

# ====== CONFIGURAÇÃO GOOGLE OAUTH ======
CLIENT_ID = "1067655818198-jl3lb93t5cskctck8jp5bh7sm2decf4s.apps.googleusercontent.com"
CLIENT_SECRET = "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"
AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"
REDIRECT_URI = "multisplitleveros2025.onrender.com/callback"
SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

# ====== FUNÇÃO PARA PROTEGER ROTAS ======
def login_required(view_func):
    def wrapped_view(*args, **kwargs):
        if "email" not in session or not session["email"].endswith("@leveros.com.br"):
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    wrapped_view.__name__ = view_func.__name__
    return wrapped_view

# ====== ROTA INICIAL ======
@app.route("/")
def index():
    if "email" in session and session["email"].endswith("@leveros.com.br"):
        return redirect(url_for("selecionar_fornecedor"))
    return redirect(url_for("login"))

# ====== LOGIN COM GOOGLE ======
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

# ====== CALLBACK DO GOOGLE ======
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

# ====== SELECIONAR FORNECEDOR ======
@app.route("/selecionar", methods=["GET", "POST"])
@login_required
def selecionar_fornecedor():
    fornecedores = ['LG', 'Fujitsu', 'Daikin', 'TCL', 'Gree']
    if request.method == 'POST':
        session['fornecedor'] = request.form.get('fornecedor', 'LG')
        return redirect(url_for('simulador'))
    return render_template('login.html', fornecedores=fornecedores)

# ====== SIMULADOR PROTEGIDO ======
@app.route("/simulador")
@login_required
def simulador():
    fornecedor = session.get('fornecedor', 'LG')
    caminho_json = f'/static/data/{fornecedor}/'
    return render_template('simulador.html', caminho_json=caminho_json, fornecedor=fornecedor)

# ====== LOGOUT ======
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
