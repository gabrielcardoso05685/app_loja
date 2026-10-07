from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)


USUARIO_TESTE = {
    "nome": "Administrador",
    "email": "admin@loja.com",
    "senha": "123"
}

produtos = [
    {"id": 1, "nome": "Camiseta Básica", "preco": 49.90, "estoque": 15},
    {"id": 2, "nome": "Calça Jeans", "preco": 119.90, "estoque": 8},
    {"id": 3, "nome": "Tênis Esportivo", "preco": 229.90, "estoque": 5}
]


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        if email == USUARIO_TESTE["email"] and senha == USUARIO_TESTE["senha"]:
            session["usuario"] = USUARIO_TESTE["nome"]
            return redirect(url_for("dashboard"))

        erro = "E-mail ou senha inválidos."

    return render_template("login.html", erro=erro)


@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        usuario=session["usuario"],
        produtos=produtos
    )


@app.route("/usuarios/cadastrar", methods=["GET", "POST"])
def cadastrar_usuario():
    if "usuario" not in session:
        return redirect(url_for("login"))

    mensagem = None

    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        mensagem = f"Cadastro de {nome} ({email}) simulado com sucesso."

    return render_template(
        "cadastro_usuario.html",
        usuario=session["usuario"],
        mensagem=mensagem
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
