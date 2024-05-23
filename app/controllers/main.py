from flask import render_template, flash, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import app, db, login_manager
from app.models.forms import LoginForm, EditarPerfil
from app.models.tables import *
import random
import re

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login'))


@app.route("/index")
@app.route("/")
def index():
    global respostas
    respostas = []
    print(respostas)

    if contador > 1:
      reset()

    if current_user.is_authenticated:
        email = current_user.email
        usuario = Usuario.query.filter_by(email=email).first()
        professor = Professor.query.filter_by(codProfessor=usuario.id).first()
        aluno = Aluno.query.filter_by(codAluno=usuario.id).first()
    else:
        # Lidar com o caso onde o usuário não está autenticado
        usuario = None
        professor = None
        aluno = None
    return render_template('index.html', professor = professor, aluno = aluno)

@app.route("/instrucoes")
def instrucoes():
    return render_template('instrucoes.html')
    

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data
        senha = form.senha.data

        usuario = Usuario.query.filter_by(email=email).first()
        print(usuario.verify_password(senha))
        print(senha)
        if not usuario or not usuario.verify_password(senha):
            return redirect(url_for('login'))
        
        login_user(usuario)
        return redirect(url_for('index'))

    return render_template('login.html', form = form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/cadastrar", methods=['GET','POST'])
def cadastrar():
    if request.method == 'POST':
        cpf = request.form['cpf'].upper()
        cpf = re.sub(r'\D', '', cpf)
        nome = request.form['nome'].upper()
        email = request.form['email']
        senha = request.form['senha']
        
    
        usuario = Usuario(cpf,nome,email,senha)
        db.session.add(usuario)
        db.session.commit()
        
        # Exemplo funcional - ForeignKeys

        # codUsuario = Usuario.query.filter_by(cpf = usuario.cpf).first().id
        
        # aluno = Aluno(codUsuario,"373737","6")
        # db.session.add(aluno)
        # db.session.commit()

        return redirect(url_for('login'))
        
    return render_template('cadastro.html')


@app.route("/perfil/cliente", methods=['GET','POST'])
@login_required
def perfil_cliente():
    return render_template('configuracoes_cliente_aluno.html')

@app.route("/perfil/professor", methods=['GET','POST'])
@login_required
def perfil_professor():
    return render_template('configuracoes_cliente_professor.html')


@app.route("/perfil/editar/<int:id>", methods=['GET', 'POST'])
@login_required
def editar_perfil(id):
    email = None
    senha = None
    form = EditarPerfil()
    aluno = Aluno.query.filter_by(id = id).first()

    if form.validate_on_submit():
            email = form.email.data
            senha = form.senha.data

            if senha and senha != None:
                aluno.senha = generate_password_hash(senha)

            if email and email != None:
                aluno.email = email
                
            db.session.add(aluno)
            db.session.commit()
            flash('Formulário enviado com sucesso!', 'success')
            return redirect(url_for('perfil'))

    return render_template('editar_configuracao_cliente.html', email = email,
                           senha = senha,
                           form = form)
questoes_disponiveis = [id_questoes for id_questoes in range(1,1)]
# random.shuffle(questoes_disponiveis)
questoes_selecionadas = []

@app.route("/questao/<int:id_questao>", methods=['GET','POST'])
@login_required
def questao(id_questao):
  global contador
  if not questoes_disponiveis:
    reset()
  id_questao_selecionada = questoes_disponiveis.pop()
  print(id_questao_selecionada)
  objeto = {
    'id':
    id_questao_selecionada,
    'questao':
    Questao.query.filter_by(id=id_questao_selecionada).first(),
    'respostas':
    Resposta.query.filter_by(questao_id=id_questao_selecionada).all(),
    'resposta_correta':
    Questao.query.filter_by(id=id_questao_selecionada).first().respostaCorreta
  }

  questoes_selecionadas.append(objeto)

  return render_template(f'Q{id_questao}a.html',
                         questoes=objeto['questao'],
                         respostas=objeto['respostas'], contador = contador)

respostas = []  # Lista para armazenar as respostas
contador = 1
@app.route('/salvar_resposta', methods=['POST'])
def salvar_resposta():
    global contador
    resposta = request.form['resposta']  # Obtém a resposta enviada pelo formulário
    respostas.append(resposta)  # Adiciona a resposta à lista
    contador += 1
    return redirect(url_for('questao', id_questao = contador))  # Redireciona para a próxima página do questionário

@app.route("/resultado")
def resultado():
    selecionadas = [selecionada for selecionada in questoes_selecionadas]
   
    # Valida as respostas e gera o contador de respostas corretas
    contador_corretas = 0
    resultados = []
    for i, resposta in enumerate(respostas):
        resultado = resposta == selecionadas[i]['resposta_correta']
        resultados.append(resultado)
        if resultado:
            contador_corretas += 1
    print(respostas)
    return render_template('resultado.html', respostas=respostas, resultados=resultados, contador_corretas=contador_corretas)


@app.route("/cadastrarQuestao", methods=['GET','POST'])
def cadastrarQuestao():
    
    if request.method == 'POST':
        descricao = request.form['descricao']

        questao = Questao(descricao)
        db.session.add(questao)
        db.session.commit()
        return redirect(url_for('cadastrarQuestao'))

    return render_template('cadastroQuestoes.html')

     

@app.route("/cadastrarResposta", methods=['GET','POST'])
def cadastrarResposta():
    
    if request.method == 'POST':
        descricaoResposta = request.form['descricaoResposta']
        questao_id = request.form['questao_id']

        if 'respostaCorreta' in request.form:
            respostaCorreta = True
        else:
            respostaCorreta = False

        resposta = Resposta(descricaoResposta, respostaCorreta, questao_id)
        db.session.add(resposta)
        db.session.commit()

    
        return redirect(url_for('cadastrarResposta'))
    return render_template('cadastroRespostas.html')

@app.errorhandler(404)
def page_not_found(error):
    return "Página não encontrada", 404


def reset():
    global contador
    contador = 1
    resetQuestoes = [questaoNova for questaoNova in range(1,1)]
    for resetQuest in resetQuestoes:
        questoes_disponiveis.append(resetQuest)
    return "Todas as questões foram utilizadas"

