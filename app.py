from flask import Flask, render_template, request, redirect, url_for, session

# Cria a aplicação Flask.
app = Flask(__name__)

# Chave usada pelo Flask para proteger os dados da session.
# A session mantém o usuário logado entre as páginas.
app.secret_key = "chave-secreta-do-projeto"


# Usuário fixo usado para acessar o sistema.
# Em uma aplicação real, esses dados viriam de um banco de dados.
USUARIO_TESTE = {
    "nome": "Administrador",
    "email": "admin@loja.com",
    "senha": "123"
}


# Lista de usuários cadastrados durante a execução do sistema.
# Em uma aplicação real, esses dados seriam salvos em um banco de dados.
usuarios = [
    USUARIO_TESTE.copy()
]


# Lista de produtos usada no dashboard.
produtos = [
    {"id": 1, "nome": "Camiseta Básica", "preco": 49.90, "estoque": 15},
    {"id": 2, "nome": "Calça Jeans", "preco": 119.90, "estoque": 8},
    {"id": 3, "nome": "Tênis Esportivo", "preco": 229.90, "estoque": 5}
]


# ROTA PRINCIPAL
# Função responsável por abrir a página inicial.
@app.route("/")
def index():
    return redirect(url_for("login"))


# LOGIN
# Mostra o formulário e verifica os dados enviados.
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


# DASHBOARD
# Mostra a tela principal e os produtos cadastrados.
@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        usuario=session["usuario"],
        produtos=produtos
    )


# CADASTRO DE USUÁRIO
# Mostra o formulário e adiciona o usuário à lista.
@app.route("/usuarios/cadastrar", methods=["GET", "POST"])
def cadastrar_usuario():
    if "usuario" not in session:
        return redirect(url_for("login"))

    mensagem = None

    if request.method == "POST":

        # Pega os dados preenchidos no formulário.
        novo_usuario = {
            "nome": request.form.get("nome"),
            "email": request.form.get("email"),
            "celular": request.form.get("celular"),
            "nascimento": request.form.get("nascimento"),
            "cpf": request.form.get("cpf"),
            "nivel": request.form.get("nivel"),
            "cep": request.form.get("cep"),
            "endereco": request.form.get("endereco"),
            "numero": request.form.get("numero"),
            "complemento": request.form.get("complemento"),
            "cidade": request.form.get("cidade"),
            "estado": request.form.get("estado")
        }

        # Adiciona o novo usuário à lista.
        usuarios.append(novo_usuario)

        mensagem = (
            f"Cadastro de {novo_usuario['nome']} "
            f"({novo_usuario['email']}) realizado com sucesso."
        )

    return render_template(
        "cadastro_usuario.html",
        usuario=session["usuario"],
        mensagem=mensagem
    )


# LISTAGEM DE USUÁRIOS
# Mostra todos os usuários cadastrados no sistema.
@app.route("/usuarios")
def listar_usuarios():

    # Impede que alguém acesse a página sem estar logado.
    if "usuario" not in session:
        return redirect(url_for("login"))

    # Envia a lista de usuários para o HTML.
    return render_template(
        "listar_usuarios.html",
        usuario=session["usuario"],
        usuarios=usuarios
    )


# LOGOUT
# Encerra a sessão do usuário e volta para o login.
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# Inicia o servidor Flask quando este arquivo é executado diretamente.
if __name__ == "__main__":
    app.run(debug=True)