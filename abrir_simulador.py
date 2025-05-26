from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, static_folder='static')
app.secret_key = 'sua_chave_secreta_aqui'

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    fornecedores = ['LG', 'Fujitsu', 'Daikin', 'TCL', 'Gree']  # Adicione mais fornecedores aqui se precisar
    if request.method == 'POST':
        fornecedor_escolhido = request.form.get('fornecedor', 'LG')
        session['fornecedor'] = fornecedor_escolhido
        return redirect(url_for('simulador'))
    return render_template('login.html', fornecedores=fornecedores)

@app.route('/simulador')
def simulador():
    fornecedor = session.get('fornecedor', 'LG')
    caminho_json = f'/static/data/{fornecedor}/'
    return render_template('simulador.html', caminho_json=caminho_json, fornecedor=fornecedor)

if __name__ == "__main__":
    app.run(debug=True)
