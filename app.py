from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "chave-secreta-do-projeto"

# Usuário de teste para acessar o sistema.
USUARIO_TESTE = {
    "nome": "Administrador",
    "email": "admin@loja.com",
    "senha": "123"
}

# Lista de usuários cadastrados.
usuarios = [
    USUARIO_TESTE.copy()
]

# Produtos iniciais da loja.
produtos = [
    {"id": 1, "nome": "Camiseta Básica", "preco": 49.90, "estoque": 15},
    {"id": 2, "nome": "Calça Jeans", "preco": 119.90, "estoque": 8},
    {"id": 3, "nome": "Tênis Esportivo", "preco": 229.90, "estoque": 5}
]


# Página inicial: redireciona para o login.
@app.route("/")
def index():
    return redirect(url_for("login"))


# Login do sistema.
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


# Dashboard com os produtos e indicadores.
@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))

    total_unidades = sum(produto["estoque"] for produto in produtos)

    valor_estoque = sum(
        produto["preco"] * produto["estoque"]
        for produto in produtos
    )

    estoque_baixo = sum(
        1 for produto in produtos if produto["estoque"] <= 5
    )

    return render_template(
        "dashboard.html",
        usuario=session["usuario"],
        produtos=produtos,
        total_unidades=total_unidades,
        valor_estoque=valor_estoque,
        estoque_baixo=estoque_baixo
    )


# Cadastro de produtos.
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
            # Aceita preço com vírgula ou ponto decimal.
            preco = float(preco_texto.replace(",", "."))
            estoque = int(estoque_texto)

            if not nome:
                erro = "Informe o nome do produto."
            elif preco < 0:
                erro = "O preço não pode ser negativo."
            elif estoque < 0:
                erro = "A quantidade em estoque não pode ser negativa."
            else:
                novo_produto = {
                    "id": max(
                        (produto["id"] for produto in produtos),
                        default=0
                    ) + 1,
                    "nome": nome,
                    "preco": preco,
                    "estoque": estoque
                }

                produtos.append(novo_produto)
                mensagem = f"Produto '{nome}' cadastrado com sucesso."

        except ValueError:
            erro = "Informe um preço válido e uma quantidade inteira."

    return render_template(
        "cadastro_produto.html",
        usuario=session["usuario"],
        erro=erro,
        mensagem=mensagem
    )


# Cadastro de usuários.
@app.route("/usuarios/cadastrar", methods=["GET", "POST"])
def cadastrar_usuario():
    if "usuario" not in session:
        return redirect(url_for("login"))

    mensagem = None

    if request.method == "POST":
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


# Listagem de usuários.
@app.route("/usuarios")
def listar_usuarios():
    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "listar_usuarios.html",
        usuario=session["usuario"],
        usuarios=usuarios
    )


# Logout.
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)