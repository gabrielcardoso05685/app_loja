
import os

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, url_for, request, session, math
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

# Conta utilizada para acessar o sistema.
USUARIO_TESTE = {
    "nome": "Administrador",
    "email": "admin@loja.com",
    "senha": "123",
    "nivel": "Administrador"
}

# Os dados ficam armazenados na memória.
# Eles serão perdidos quando o servidor for reiniciado.
usuarios = [USUARIO_TESTE.copy()]

produtos = [
    {
        "id": 1,
        "nome": "Camiseta Básica",
        "preco": 49.90,
        "estoque": 15
    },
    {
        "id": 2,
        "nome": "Calça Jeans",
        "preco": 119.90,
        "estoque": 8
    },
    {
        "id": 3,
        "nome": "Tênis Esportivo",
        "preco": 229.90,
        "estoque": 5
    }
]


# --------------------------------------------------
# USUÁRIOS
# --------------------------------------------------

@app.route("/")
def index():
    # Encaminha o usuário para a tela de login.
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    # Se já estiver autenticado, vai diretamente ao dashboard.
    if "usuario" in session:
        return redirect(url_for("dashboard"))

    erro = None

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")

        # Verifica as credenciais da conta de teste.
        if (
            email == USUARIO_TESTE["email"]
            and senha == USUARIO_TESTE["senha"]
        ):

            session["usuario"] = USUARIO_TESTE["nome"]

            # Após o login, redireciona para o dashboard.
            return redirect(url_for("dashboard"))

        else:
            erro = "E-mail ou senha inválidos."

    return render_template(
        "login.html",
        erro=erro
    )


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():

    # Impede o acesso de usuários não autenticados.
    if "usuario" not in session:
        return redirect(url_for("login"))

    # Calcula a quantidade total de unidades em estoque.
    total_unidades = sum(
        produto["estoque"] for produto in produtos
    )

    # Calcula o valor total dos produtos em estoque.
    valor_estoque = sum(
        produto["preco"] * produto["estoque"]
        for produto in produtos
    )

    # Conta quantos produtos possuem estoque baixo.
    estoque_baixo = sum(
        1 for produto in produtos
        if produto["estoque"] <= 5
    )

    return render_template(
        "dashboard.html",
        usuario=session["usuario"],
        produtos=produtos,
        total_unidades=total_unidades,
        valor_estoque=valor_estoque,
        estoque_baixo=estoque_baixo
    )


# --------------------------------------------------
# PRODUTOS
# --------------------------------------------------

@app.route("/produtos")
def listar_produtos():

    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "produtos/listar_produtos.html",
        usuario=session["usuario"],
        produtos=produtos
    )


@app.route("/produtos/cadastrar", methods=["GET", "POST"])
def cadastrar_produto():

    if "usuario" not in session:
        return redirect(url_for("login"))

    erro = None
    mensagem = None

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        preco_texto = request.form.get("preco", "").strip()
        estoque_texto = request.form.get("estoque", "").strip()

        try:

            # Aceita vírgula ou ponto como separador decimal.
            preco = float(preco_texto.replace(",", "."))
            estoque = int(estoque_texto)

            # Valida os dados recebidos.
            if not nome:
                erro = "Informe o nome do produto."

            elif not math.isfinite(preco):
                erro = "Informe um preço válido."

            elif preco < 0:
                erro = "O preço não pode ser negativo."

            elif estoque < 0:
                erro = "O estoque não pode ser negativo."

            else:

                # Gera um ID automaticamente.
                novo_id = max(
                    (produto["id"] for produto in produtos),
                    default=0
                ) + 1

                # Adiciona o produto à lista.
                produtos.append({
                    "id": novo_id,
                    "nome": nome,
                    "preco": preco,
                    "estoque": estoque
                })

                # Retorna para a listagem após cadastrar.
                return redirect(url_for("listar_produtos"))

        except ValueError:
            erro = "Informe um preço válido e uma quantidade inteira."

    return render_template(
        "produtos/cadastro_produto.html",
        usuario=session["usuario"],
        erro=erro,
        mensagem=mensagem
    )


# --------------------------------------------------
# USUÁRIOS
# --------------------------------------------------

@app.route("/usuarios/cadastrar", methods=["GET", "POST"])
def cadastrar_usuario():

    if "usuario" not in session:
        return redirect(url_for("login"))

    mensagem = None

    if request.method == "POST":

        # Recebe os dados enviados pelo formulário.
        novo_usuario = {
            "nome": request.form.get("nome", "").strip(),
            "email": request.form.get("email", "").strip(),
            "celular": request.form.get("celular", "").strip(),
            "nascimento": request.form.get("nascimento", ""),
            "cpf": request.form.get("cpf", "").strip(),
            "nivel": request.form.get("nivel", "Usuário"),
            "cep": request.form.get("cep", "").strip(),
            "endereco": request.form.get("endereco", "").strip(),
            "numero": request.form.get("numero", "").strip(),
            "complemento": request.form.get("complemento", "").strip(),
            "cidade": request.form.get("cidade", "").strip(),
            "estado": request.form.get("estado", "")
        }

        # Adiciona o usuário à lista.
        usuarios.append(novo_usuario)

        mensagem = (
            f"Cadastro de {novo_usuario['nome']} "
            "realizado com sucesso."
        )

    return render_template(
        "usuarios/cadastro_usuario.html",
        usuario=session["usuario"],
        mensagem=mensagem
    )


@app.route("/usuarios")
def listar_usuarios():

    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "usuarios/listar_usuarios.html",
        usuario=session["usuario"],
        usuarios=usuarios
    )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    # Encerra a sessão atual.
    session.clear()

    return redirect(url_for("login"))


# --------------------------------------------------
# INICIALIZAÇÃO DO SERVIDOR
# --------------------------------------------------

#=================================================
# PERFIL
#=================================================
@app.route('/perfis/inserir', methods=['GET', 'POST'])
def inserir_perfil():

    if request.method == 'POST':
        return redirect(url_for('listar_perfis'))
    return render_template('perfis/perfil-form.html')

@app.route('/perfis/listar')
def listar_perfis():
    return render_template('perfis/perfis-listar.html')

























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
