from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "chave-secreta-do-projeto"

# Conta usada para acessar o sistema durante os testes.
USUARIO_TESTE = {
    "nome": "Administrador",
    "email": "admin@loja.com",
    "senha": "123"
}

# Os dados ficam na memória e são perdidos ao reiniciar o aplicativo.
usuarios = [USUARIO_TESTE.copy()]

produtos = [
    {"id": 1, "nome": "Camiseta Básica", "preco": 49.90, "estoque": 15},
    {"id": 2, "nome": "Calça Jeans", "preco": 119.90, "estoque": 8},
    {"id": 3, "nome": "Tênis Esportivo", "preco": 229.90, "estoque": 5}
]


# Encaminha o acesso inicial para a tela de login.
@app.route("/")
def index():
    return redirect(url_for("login"))


# Exibe o formulário e verifica as credenciais da conta de teste.
@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")

        if email == USUARIO_TESTE["email"] and senha == USUARIO_TESTE["senha"]:
            session["usuario"] = USUARIO_TESTE["nome"]
            return redirect(url_for("dashboard"))

        erro = "E-mail ou senha inválidos."

    return render_template("login.html", erro=erro)


# Mostra os indicadores calculados a partir dos produtos cadastrados.
@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))

    total_unidades = sum(p["estoque"] for p in produtos)
    valor_estoque = sum(p["preco"] * p["estoque"] for p in produtos)
    estoque_baixo = sum(1 for p in produtos if p["estoque"] <= 5)

    return render_template(
        "dashboard.html",
        usuario=session["usuario"],
        produtos=produtos,
        total_unidades=total_unidades,
        valor_estoque=valor_estoque,
        estoque_baixo=estoque_baixo
    )


# Exibe a listagem de produtos somente para usuários autenticados.
@app.route("/produtos")
def listar_produtos():
    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "listar_produtos.html",
        usuario=session["usuario"],
        produtos=produtos
    )


# Valida os dados, cadastra o produto e redireciona para a listagem.
@app.route("/produtos/cadastrar", methods=["GET", "POST"])
def cadastrar_produto():
    if "usuario" not in session:
        return redirect(url_for("login"))

    erro = None

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        preco_texto = request.form.get("preco", "").strip()
        estoque_texto = request.form.get("estoque", "").strip()

        try:
            # Aceita preços com vírgula ou ponto como separador decimal.
            preco = float(preco_texto.replace(",", "."))
            estoque = int(estoque_texto)

            if not nome:
                erro = "Informe o nome do produto."
            elif preco < 0:
                erro = "O preço não pode ser negativo."
            elif estoque < 0:
                erro = "O estoque não pode ser negativo."
            else:
                # Gera um identificador maior que os existentes.
                novo_id = max(
                    (p["id"] for p in produtos),
                    default=0
                ) + 1

                produtos.append({
                    "id": novo_id,
                    "nome": nome,
                    "preco": preco,
                    "estoque": estoque
                })

                return redirect(url_for("listar_produtos"))

        except ValueError:
            erro = "Informe um preço válido e uma quantidade inteira."

    return render_template(
        "cadastro_produto.html",
        usuario=session["usuario"],
        erro=erro
    )


# Recebe os dados do formulário e adiciona um usuário à lista.
@app.route("/usuarios/cadastrar", methods=["GET", "POST"])
def cadastrar_usuario():
    if "usuario" not in session:
        return redirect(url_for("login"))

    mensagem = None

    if request.method == "POST":
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

        usuarios.append(novo_usuario)
        mensagem = f"Cadastro de {novo_usuario['nome']} realizado com sucesso."

    return render_template(
        "cadastro_usuario.html",
        usuario=session["usuario"],
        mensagem=mensagem
    )


# Exibe os usuários cadastrados no sistema.
@app.route("/usuarios")
def listar_usuarios():
    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "listar_usuarios.html",
        usuario=session["usuario"],
        usuarios=usuarios
    )


# Encerra a sessão e retorna à tela de login.
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# Inicia o servidor de desenvolvimento quando este arquivo é executado.
if __name__ == "__main__":
    app.run(debug=True)