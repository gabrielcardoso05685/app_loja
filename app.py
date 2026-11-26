import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFProtect
from mysql.connector import Error
from db import execute_insert, execute_one, execute_query
from validacoes.validacoes_perfil import validar_perfil

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

CSRFProtect(app)

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/perfis')
def listar_perfis():
    perfis = execute_query(
        'SELECT id_perfil, nome, descricao, criado_em FROM perfis ORDER BY nome',
        fetch=True
    )
    return render_template('perfis/perfis_listar.html', perfis=perfis)

@app.route('/produtos')
def listar_produtos():
    produtos = execute_query(
        'SELECT id_produto, nome, descricao, preco, estoque FROM produtos ORDER BY nome',
        fetch=True
    )
    return render_template('produtos/produtos_listar.html', produtos=produtos)


@app.route('/perfis/inserir', methods=['GET', 'POST'])
def inserir_perfil():

    nome = ''
    descricao = ''

    if request.method == 'POST':
       nome = request.form.get('nome', '').strip()
       descricao = request.form.get('descricao', '').strip()

    try:
        novo_id = execute_insert(
        'INSERT INTO perfis (nome, descricao) VALUES (%s, %s)',(nome, descricao))
        flash(f'Pefil {nome} cadastrado com o ID {novo_id}.', 'success')
        return redirect(url_for("listar_perfis"))
    
    except Error as erro:
        if erro.errno == 1062:
            flash(f'Já existe um perfil com este nome', 'danger')
        else:
            raise
       
    return render_template('perfis/perfil_form.html', nome=nome, descricao=descricao)



@app.route('/produtos/inserir', methods=['GET', 'POST'])
def inserir_produto():

    nome = ''
    descricao = ''
    preco = ''
    estoque = ''

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        descricao = request.form.get('descricao', '').strip()
        preco = request.form.get('preco', '').strip()
        estoque = request.form.get('estoque', '').strip()

        try:
            novo_produto = execute_insert(
                    'INSERT INTO produtos (nome, descricao, preco, estoque) '
                    'VALUES (%s, %s, %s, %s)',
                    (nome, descricao, preco, estoque)
                )
            flash('Produto foi cadastrado com sucesso.', 'success')
        except Error as erro:
            flash('Erro ao cadastrar produto.', 'danger')

    return render_template(
        'produtos/produto_form.html',
        nome=nome,
        descricao=descricao,
        preco=preco,
        estoque=estoque
    )

# ==============================================================================
# TELAS DE ERROS
# ==============================================================================

@app.errorhandler(404)
def pagina_nao_encontrada(erro):
    return render_template('404.html'), 404


@app.errorhandler(500)
def erro_no_servidor(erro):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
