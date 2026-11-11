
import os

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, url_for, request, session
from flask_wtf.csrf import CSRFProtect

from db import execute_one

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Liga a proteção CSRF: todo formulário POST do sistema vai precisar do token
CSRFProtect(app)


# ==============================================================================
# PÁGINAS PRINCIPAIS
# ==============================================================================

@app.route('/')
def index():
    # A raiz não mostra nada: só leva para a tela de login
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    # Conta as linhas de cada tabela para os cartões da Home
    perfis = execute_one('SELECT COUNT(*) AS total FROM perfis')
    usuarios = execute_one('SELECT COUNT(*) AS total FROM usuarios')
    produtos = execute_one('SELECT COUNT(*) AS total FROM produtos')

    return render_template('dashboard.html', titulo='Sistema de Gestão',
                           total_perfis=perfis['total'],
                           total_usuarios=usuarios['total'],
                           total_produtos=produtos['total'])


if __name__ == '__main__':
    app.run(debug=True)

# Chave utilizada para manter a sessão do usuário.
app.secret_key = "chave-secreta-do-projeto"


# --------------------------------------------------
# DADOS DE TESTE
# --------------------------------------------------

# Dados iniciais. Tudo fica na memória e é apagado ao fechar o servidor.

app.config["WTF_CSRF_ENABLED"] = False

usuarios = [
    {
        "nome": "Administrador",
        "email": "admin@loja.com",
        "nivel": "Administrador"
    }
]

produtos = [
    {"id": 1, "nome": "Camiseta Básica", "preco": 49.90, "estoque": 15},
    {"id": 2, "nome": "Calça Jeans", "preco": 119.90, "estoque": 8},
    {"id": 3, "nome": "Tênis Esportivo", "preco": 229.90, "estoque": 5}
]

perfis = []

@app.route("/index")
def index():
    return redirect(url_for("index.html"))

@app.route("/login")
def login():
    if request.method == "POST":
        session["usuario"] = request.form.get("email", "") or "Administrador"
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    total_unidades = sum(produto["estoque"] for produto in produtos)
    valor_estoque = sum(produto["preco"] * produto["estoque"] for produto in produtos)
    estoque_baixo = sum(1 for produto in produtos if produto["estoque"] <= 5)
    return render_template(
        "dashboard.html",
        usuario=session.get("usuario", "Administrador"),
        produtos=produtos,
        total_unidades=total_unidades,
        valor_estoque=valor_estoque,
        estoque_baixo=estoque_baixo
    )


app.view_functions["index"] = index
app.view_functions["login"] = login
app.view_functions["dashboard"] = dashboard
app.add_url_rule("/login", endpoint="login_post", view_func=login, methods=["POST"])


@app.route("/produtos")
def listar_produtos():
    return render_template("produtos/listar_produtos.html", produtos=produtos)


@app.route("/produtos/cadastrar", methods=["GET", "POST"])
def cadastrar_produto():
    if request.method == "POST":
        produtos.append({
            "id": len(produtos) + 1,
            "nome": request.form.get("nome", ""),
            "preco": float(request.form.get("preco", "0").replace(",", ".")),
            "estoque": int(request.form.get("estoque", "0"))
        })
        return redirect(url_for("listar_produtos"))
    return render_template("produtos/cadastro_produto.html")


@app.route("/usuarios/cadastrar", methods=["GET", "POST"])
def cadastrar_usuario():
    if request.method == "POST":
        usuarios.append({
            "nome": request.form.get("nome", ""),
            "email": request.form.get("email", ""),
            "celular": request.form.get("celular", ""),
            "nascimento": request.form.get("nascimento", ""),
            "cpf": request.form.get("cpf", ""),
            "nivel": request.form.get("nivel", "Usuário"),
            "cep": request.form.get("cep", ""),
            "endereco": request.form.get("endereco", ""),
            "numero": request.form.get("numero", ""),
            "complemento": request.form.get("complemento", ""),
            "cidade": request.form.get("cidade", ""),
            "estado": request.form.get("estado", "")
        })
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
        perfis.append({"nome": request.form.get("nome", ""), "descricao": request.form.get("descricao", "")})
        return redirect(url_for("listar_perfis"))
    return render_template("perfis/perfil-form.html")


@app.route("/perfis/listar")
def listar_perfis():
    return render_template("perfis/perfis-listar.html", perfis=perfis)

# ==============================================================================
# TELAS DE ERROS
# ==============================================================================

@app.errorhandler(404)
def pagina_nao_encontrada(erro):
    return render_template('404.html'), 404


@app.errorhandler(500)
def erro_no_servidor(erro):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(debug=True)
