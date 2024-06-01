from flask import render_template, flash, request, redirect, url_for, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import app, db, login_manager
from app.models.forms import LoginForm, EditarPerfil
from app.models.tables import *
import random
import re
from datetime import date, datetime


questoes_disponiveis = [id_questoes for id_questoes in range(1, 10)]
random.shuffle(questoes_disponiveis)
questoes_selecionadas = []
respostas = []  # Lista para armazenar as respostas
contador = 1


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
    return render_template('index.html', professor=professor, aluno=aluno)


@app.route("/instrucoes")
def instrucoes():
    return render_template('instrucoes.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        email = email.lower()
        senha = form.senha.data

        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario or not usuario.verify_password(senha):
            return redirect(url_for('login'))

        login_user(usuario)
        return redirect(url_for('index'))

    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/cadastrar", methods=['GET', 'POST'])
def cadastrar():
    random_clico = random.randint(1, 10)
    for _ in range(13):
        random_number = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        ra = "143048" + random_number
    if request.method == 'POST':
        cpf = request.form['cpf'].upper()
        cpf = re.sub(r'\D', '', cpf)
        nome = request.form['nome'].upper()
        email = request.form['email'].lower()
        senha = request.form['senha']

        usuario = Usuario(cpf, nome, email, senha)
        db.session.add(usuario)
        db.session.commit()

        # Exemplo funcional - ForeignKeys

        codUsuario = Usuario.query.filter_by(cpf=usuario.cpf).first().id

        aluno = Aluno(codUsuario, ra, random_clico)
        db.session.add(aluno)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('cadastro.html')


def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.acessoUsuario != 'A':
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


@app.route('/admin', methods=['GET'])
@admin_required
def admin_route():
    return jsonify({"message": "Welcome, Admin!"})


@app.route("/perfil/aluno", methods=['GET', 'POST'])
@login_required
def perfil_aluno():
    usuario = Usuario.query.filter_by(id=current_user.id).first()
    return render_template('configuracoes_cliente_aluno.html', usuario=usuario)


@app.route('/atualizar_dados_professor', methods=['POST'])
def atualizar_dados_professor():
    if request.method == 'POST':
        if request.method == 'POST':
            novo_nome = request.form['input_dadosPessoasNome'].upper()
            novo_email = request.form['input_dadosPessoasEmail'].lower()
            usuario = Usuario.query.get(current_user.id)
            usuario.nome = novo_nome
            usuario.email = novo_email
            try:
                db.session.commit()
                # Retorna uma resposta JSON indicando sucesso
                return jsonify({'success': True})
            except:
                # Retorna uma resposta JSON indicando falha
                return jsonify({'success': False})


@app.route('/atualizar_dados_aluno', methods=['POST'])
def atualizar_dados_aluno():
    if request.method == 'POST':
        novo_nome = request.form['input_dadosPessoasNome'].upper()
        novo_email = request.form['input_dadosPessoasEmail'].lower()
        usuario = Usuario.query.get(current_user.id)
        usuario.nome = novo_nome
        usuario.email = novo_email
        try:
            db.session.commit()
            # Retorna uma resposta JSON indicando sucesso
            return jsonify({'success': True})
        except:
            # Retorna uma resposta JSON indicando falha
            return jsonify({'success': False})


@app.route("/perfil/professor", methods=['GET', 'POST'])
@login_required
def perfil_professor():
    return render_template('configuracoes_cliente_professor.html')


@app.route("/cadastro_questoes", methods=['GET', 'POST'])
@login_required
def cadastro_questoes():
    return render_template('cadastroQuestoes.html')


@app.route("/perfil/editar/<int:id>", methods=['GET', 'POST'])
@login_required
def editar_perfil(id):
    email = None
    senha = None
    form = EditarPerfil()
    aluno = Aluno.query.filter_by(id=id).first()

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

    return render_template('editar_configuracao_cliente.html', email=email,
                           senha=senha,
                           form=form)


@app.route("/questao/<int:id_questao>", methods=['GET', 'POST'])
# @login_required
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
        Questao.query.filter_by(codQuestao=id_questao_selecionada).first(),
        'respostas':
        Resposta.query.filter_by(codQuestao=id_questao_selecionada).all(),
        'resposta_correta':
        Resposta.query.filter_by(
            codQuestao=id_questao_selecionada).first().respCorreta
    }

    questoes_selecionadas.append(objeto)

    return render_template(f'Q{id_questao}a.html',
                           questoes=objeto['questao'],
                           respostas=objeto['respostas'], contador=contador)


@app.route('/salvar_resposta', methods=['POST'])
def salvar_resposta():
    global contador
    # Obtém a resposta enviada pelo formulário
    resposta = request.form['resposta']
    respostas.append(resposta)  # Adiciona a resposta à lista
    contador += 1
    # Redireciona para a próxima página do questionário
    return redirect(url_for('questao', id_questao=contador))


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


@app.route("/cadastrarProva", methods=['POST'])
def cadastrarProva():
    professor = Professor.query.filter_by(codProfessor=current_user.id).first()
    codProfessor = professor.codProfessor

    if request.method == 'POST':
        descricaoQuestao = request.form['questao']
        descricaoTipo = request.form['assunto']
        grauDificuldade = request.form['dificuldade']

        # Lista de respostas
        respostas = request.form.getlist('respostas[]')

        # Verificando quais respostas foram marcadas como corretas
        respostas_corretas = [
            int(index) for index in request.form.getlist('correta')]

        # Validação e obtenção de codTipo
        tipo_questao = TipoQuestao.query.filter_by(
            descricaoTipo=descricaoTipo).first()
        if not tipo_questao:
            return "Tipo de Questão inválido", 400  # Retornar um erro apropriado
        codTipo = tipo_questao.codTipo

        # Validação e obtenção de codDificuldade
        dificuldade = Dificuldade.query.filter_by(grau=grauDificuldade).first()
        if not dificuldade:
            return "Dificuldade inválida", 400  # Retornar um erro apropriado
        codDificuldade = dificuldade.codDificuldade

        # Obtendo o ano atual
        ano_atual = datetime.now().year

        # Verificando se o ano da prova já existe, senão criar um novo
        anoProva = AnoProva.query.filter_by(ano=ano_atual).first()
        if not anoProva:
            anoProva = AnoProva(ano=ano_atual)
            db.session.add(anoProva)
            db.session.commit()

        # Criando a nova questão
        questao = Questao(codProfessor=codProfessor, descricaoQuestao=descricaoQuestao,
                          codAnoProva=anoProva.codAnoProva, codDificuldade=codDificuldade, codTipo=codTipo)

        # Adicionando a questão ao banco de dados
        db.session.add(questao)
        db.session.commit()

        # Cadastrar respostas
        cadastrarResposta(questao, respostas, respostas_corretas)

        # Redirecionar para uma página apropriada após a inserção
        return redirect(url_for('cadastro_questoes'))

    # Renderizar um template apropriado se a solicitação não for POST
    return render_template('cadastrarProva.html')


def cadastrarResposta(questao, respostas, respostas_corretas):
    for index, resposta in enumerate(respostas):
        # Verificar se a resposta é correta
        correta = index in respostas_corretas

        # Criar a resposta no banco de dados
        nova_resposta = Resposta(
            codQuestao=questao.codQuestao, descricaoResposta=resposta, respCorreta=correta)
        db.session.add(nova_resposta)

    # Commit das respostas no banco de dados
    db.session.commit()


@app.errorhandler(404)
def page_not_found(error):
    return "Página não encontrada", 404


def reset():
    global contador
    contador = 1
    resetQuestoes = [questaoNova for questaoNova in range(1, 1)]
    for resetQuest in resetQuestoes:
        questoes_disponiveis.append(resetQuest)
    return "Todas as questões foram utilizadas"
