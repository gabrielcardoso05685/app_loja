import os

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or "chave-secreta-do-projeto"

usuarios = [{
    "nome": "Gabriel",
    "email": "admin@loja.com",
    "nivel": "Administrador",
    "senha": "123",
}]

produtos = [
    {"id": 1, "nome": "Camiseta Basica", "preco": 49.90, "estoque": 15},
    {"id": 2, "nome": "Calca Jeans", "preco": 119.90, "estoque": 8},
    {"id": 3, "nome": "Tenis Esportivo", "preco": 229.90, "estoque": 5},
]
perfis = []


@app.route("/")
@app.route("/index")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        usuario = next((u for u in usuarios
                        if u.get("email", "").strip().lower() == email
                        and u.get("senha") == senha), None)
        if usuario:
            session["usuario"] = usuario["nome"]
            return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    total_unidades = sum(p["estoque"] for p in produtos)
    valor_estoque = sum(p["preco"] * p["estoque"] for p in produtos)
    estoque_baixo = sum(1 for p in produtos if p["estoque"] <= 5)
    return render_template("dashboard.html", usuario=session.get("usuario", "Administrador"),
                           produtos=produtos, total_unidades=total_unidades,
                           valor_estoque=valor_estoque, estoque_baixo=estoque_baixo)


@app.route("/produtos")
def listar_produtos():
    return render_template("produtos/listar_produtos.html", produtos=produtos)


@app.route("/produtos/cadastrar", methods=["GET", "POST"])
def cadastrar_produto():
    if request.method == "POST":
        produtos.append({"id": len(produtos) + 1,
                         "nome": request.form.get("nome", ""),
                         "preco": float(request.form.get("preco", "0").replace(",", ".")),
                         "estoque": int(request.form.get("estoque", "0"))})
        return redirect(url_for("listar_produtos"))
    return render_template("produtos/cadastro_produto.html")


@app.route("/usuarios/cadastrar", methods=["GET", "POST"])
def cadastrar_usuario():
    if request.method == "POST":
        usuarios.append({"nome": request.form.get("nome", ""),
                         "email": request.form.get("email", ""),
                         "celular": request.form.get("celular", ""),
                         "nascimento": request.form.get("nascimento", ""),
                         "cpf": request.form.get("cpf", ""),
                         "nivel": request.form.get("nivel", "Usuario"),
                         "senha": request.form.get("senha", ""),
                         "cep": request.form.get("cep", ""),
                         "endereco": request.form.get("endereco", ""),
                         "numero": request.form.get("numero", ""),
                         "complemento": request.form.get("complemento", ""),
                         "cidade": request.form.get("cidade", ""),
                         "estado": request.form.get("estado", "")})
        return redirect(url_for("listar_usuarios"))
    return render_template("usuarios/cadastro_usuario.html")


@app.route("/usuarios")
def listar_usuarios():
    return render_template("usuarios/listar_usuarios.html", usuarios=usuarios)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/perfis/inserir", methods=["GET", "POST"])
def inserir_perfil():
    if request.method == "POST":
        perfis.append({"nome": request.form.get("nome", ""),
                       "descricao": request.form.get("descricao", "")})
        return redirect(url_for("listar_perfis"))
    return render_template("perfis/perfil-form.html")


@app.route("/perfis/listar")
def listar_perfis():
    return render_template("perfis/perfis-listar.html", perfis=perfis)


@app.errorhandler(404)
def pagina_nao_encontrada(erro):
    return render_template("404.html"), 404


@app.errorhandler(500)
def erro_no_servidor(erro):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
