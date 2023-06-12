from flask import render_template, flash, request, redirect, url_for
from flask_login import login_user, logout_user
from app import app, db
from app.models.forms import LoginForm, EditarPerfil
from app.models.tables import Aluno, Prova, Questao, Resposta
import random

@app.route("/index")
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data
        senha = form.senha.data

        aluno = Aluno.query.filter_by(email=email).first()

        if not aluno or not aluno.verify_password(senha):
            return redirect(url_for('login'))
        
        login_user(aluno)
        return redirect(url_for('index'))

    return render_template('login.html', form = form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/cadastrar", methods=['GET','POST'])
def cadastrar():
    
    if request.method == 'POST':
        cpf = request.form['cpf'].upper()
        nome = request.form['nome'].upper()
        instituicao_ensino = request.form['instituicaoEnsino'].upper()
        email = request.form['email']
        senha = request.form['senha']

    
        aluno = Aluno(cpf,nome, instituicao_ensino,email,senha)
        db.session.add(aluno)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('cadastro.html')

@app.route("/perfil", methods=['GET','POST'])
def perfil():
    return render_template('configuracoes_cliente.html')

@app.route("/perfil/editar", methods=['GET', 'POST'])
def editar_perfil():
    email = None
    senha = None
    form = EditarPerfil()

    if form.validate_on_submit():
            email = form.email.data
            senha = form.senha.data
            form.email.data = ''
            form.senha.data = ''

    return render_template('editar_configuracao_cliente.html', email = email,
                           senha = senha,
                           form = form)

@app.route("/questao/<int:id_questao>")
def questao(id_questao):

    numeros = random.sample(range(1, 3), 2)

    for numero in numeros:
        gera_questao = numero

    questoes = Questao.query.filter_by(id = gera_questao).first()
    respostas = Resposta.query.filter_by(questao_id = gera_questao).all()

    return render_template('Q{}a.html'.format(id_questao), questoes = questoes, respostas = respostas)


@app.route("/cadastrarQuestao", methods=['GET','POST'])
def cadastrarQuestao():
    
    if request.method == 'POST':
        descricao = request.form['descricao']

        questao = Questao(descricao)
        db.session.add(questao)
        db.session.commit()
        return redirect(url_for('cadastrarResposta'))

    return render_template('cadastroQuestoes.html')

     

@app.route("/cadastrarResposta", methods=['GET','POST'])
def cadastrarResposta():
    
    if request.method == 'POST':
        descricaoResposta = request.form['descricaoResposta']
        questao_id = request.form['questao_id']

        resposta = Resposta(descricaoResposta, questao_id)
        db.session.add(resposta)
        db.session.commit()

    
        return redirect(url_for('cadastrarResposta'))
    return render_template('cadastroRespostas.html')