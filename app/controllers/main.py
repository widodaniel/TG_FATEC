from flask import render_template, flash, request, redirect, url_for, jsonify, abort,session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import app, db, login_manager
from app.models.forms import LoginForm, EditarPerfil
from app.models.tables import Usuario, Professor, Aluno, Questao, Resposta, TipoQuestao, Dificuldade, AnoProva, Prova
import random
import re
import time
from datetime import datetime,timedelta,timezone

# Constantes e variáveis globais
NUMERO_QUESTOES = 10
QUESTOES_DISPONIVEIS = list(range(2, 12))

DURATION = 60 * 60

random.shuffle(QUESTOES_DISPONIVEIS)
questoes_selecionadas = []
respostas = []
contador = 1


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login'))


@app.route("/")
@app.route("/index")
def index():
    global respostas, contador
    global start_time
    respostas = []
    contador = 1
    session['start_time'] = time.time()

    if current_user.is_authenticated:
        email = current_user.email
        usuario = Usuario.query.filter_by(email=email).first()
        professor = Professor.query.filter_by(codProfessor=usuario.id).first()
        aluno = Aluno.query.filter_by(codAluno=usuario.id).first()
    else:
        usuario = professor = aluno = None

    return render_template('index.html', professor=professor, aluno=aluno)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.lower()
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
    if request.method == 'POST':
        cpf = re.sub(r'\D', '', request.form['cpf'].upper())
        nome = request.form['nome'].upper()
        email = request.form['email'].lower()
        senha = request.form['senha']

        usuario_por_cpf = Usuario.query.filter_by(cpf=cpf).first()
        if usuario_por_cpf:
            flash('CPF já cadastrado.', 'cpf_error')
            return redirect(url_for('cadastrar'))

        # Verificar se o e-mail já está cadastrado
        usuario_por_email = Usuario.query.filter_by(email=email).first()
        if usuario_por_email:
            flash('E-mail já cadastrado.', 'email_error')
            return redirect(url_for('cadastrar'))

        usuario = Usuario(cpf=cpf, nome=nome, email=email, senha=senha)
        db.session.add(usuario)
        db.session.commit()

        codUsuario = Usuario.query.filter_by(cpf=cpf).first().id
        ra = f"143048{''.join([str(random.randint(0, 9)) for _ in range(7)])}"
        random_clico = random.randint(1, 10)
        aluno = Aluno(codAluno=codUsuario, ra=ra, ciclo_finalizado=random_clico)
        db.session.add(aluno)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('cadastro.html')


def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.acessoUsuario != 'A':
            abort(403)
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


@app.route('/atualizar_dados', methods=['POST'])
@login_required
def atualizar_dados():
    novo_nome = request.form['input_dadosPessoasNome'].upper()
    novo_email = request.form['input_dadosPessoasEmail'].lower()
    usuario = Usuario.query.get(current_user.id)
    usuario.nome = novo_nome
    usuario.email = novo_email
    try:
        db.session.commit()
        return jsonify({'success': True})
    except:
        return jsonify({'success': False})


@app.route("/perfil/professor", methods=['GET', 'POST'])
@login_required
def perfil_professor():
    return render_template('configuracoes_cliente_professor.html')


@app.route("/cadastro_questoes", methods=['GET', 'POST'])
@login_required
def cadastro_questoes():
    return render_template('cadastroQuestoes.html')

@app.route("/editar_questoes", methods=['GET', 'POST'])
@login_required
def editar_questoes():
    return render_template('editarQuestoes.html')


@app.route("/perfil/editar/<int:id>", methods=['GET', 'POST'])
@login_required
def editar_perfil(id):
    form = EditarPerfil()
    aluno = Aluno.query.filter_by(id=id).first()

    if form.validate_on_submit():
        if form.senha.data:
            aluno.senha = generate_password_hash(form.senha.data)
        if form.email.data:
            aluno.email = form.email.data

        db.session.add(aluno)
        db.session.commit()
        flash('Formulário enviado com sucesso!', 'success')
        return redirect(url_for('perfil'))

    return render_template('editar_configuracao_cliente.html', form=form)


@app.route("/questao/<int:id_questao>", methods=['GET', 'POST'])
def questao(id_questao):
    global contador
    if not QUESTOES_DISPONIVEIS:
        reset()
    id_questao_selecionada = QUESTOES_DISPONIVEIS.pop()

    questao_obj = Questao.query.filter_by(codQuestao=id_questao_selecionada).first()
    respostas_obj = Resposta.query.filter_by(codQuestao=id_questao_selecionada).all()
    resposta_correta_obj = Resposta.query.filter_by(codQuestao=id_questao_selecionada, respCorreta=True).first()

    if questao_obj is None or resposta_correta_obj is None:
        return "Questão ou resposta não encontrada", 404

    objeto = {
        'id': id_questao_selecionada,
        'questao': questao_obj,
        'respostas': respostas_obj,
        'resposta_correta': resposta_correta_obj.descricaoResposta,
    }
    questoes_selecionadas.append(objeto)

    return render_template(f'Q{id_questao}a.html', questoes=objeto['questao'], respostas=objeto['respostas'], contador=contador)


@app.route('/salvar_resposta', methods=['POST'])
def salvar_resposta():
    global contador
    resposta_selecionada = request.form['resposta']
    id_questao_atual = request.form['id_questao']
    
    # Obtém a resposta correta para a questão atual
    resposta_correta_obj = Resposta.query.filter_by(codQuestao=id_questao_atual, respCorreta=True).first()
    
    if resposta_correta_obj is None:
        return "Erro ao verificar a resposta correta", 500
    
    resposta_correta = resposta_correta_obj.descricaoResposta
    
    # Verifica se a resposta selecionada é correta
    correta = resposta_selecionada == resposta_correta

    # Salva a resposta e a informação se estava correta ou não
    respostas.append({'resposta': resposta_selecionada, 'correta': correta})
    contador += 1

    if len(respostas) == 10:
        return redirect(url_for('resultado'))
    return redirect(url_for('questao', id_questao=contador))



@app.route("/resultado")
def resultado():
    
    contador_corretas = sum(1 for resposta in respostas if resposta['correta'])
    resultados = [{'resposta': resposta['resposta'], 'correta': resposta['correta']} for resposta in respostas]

    start_time = session.get('start_time', None)
    if start_time is not None:
        elapsed_time = time.time() - start_time
        tempo_prova = int(elapsed_time)
    else:
        tempo_prova = timedelta(seconds=0)
        
    tempo_prova_final = timedelta(seconds=tempo_prova)
    data_emissao=datetime.now().date()
    
    if current_user.is_authenticated:
        prova = Prova(codAluno=current_user.id, quantidadeCorreta=contador_corretas, dt_emissao=data_emissao, tempo_prova=tempo_prova_final)
        db.session.add(prova)
        db.session.commit()
    return render_template('resultado.html', respostas=respostas, resultados=resultados, contador_corretas=contador_corretas)


@app.route("/cadastrarProva", methods=['POST'])
def cadastrarProva():
    professor = Professor.query.filter_by(codProfessor=current_user.id).first()
    codProfessor = professor.codProfessor

    if request.method == 'POST':
        descricaoQuestao = request.form['questao']
        descricaoTipo = request.form['assunto']
        grauDificuldade = request.form['dificuldade']
        respostas = request.form.getlist('respostas[]')
        respostas_corretas = [int(index) for index in request.form.getlist('correta')]

        tipo_questao = TipoQuestao.query.filter_by(descricaoTipo=descricaoTipo).first()
        if not tipo_questao:
            return "Tipo de Questão inválido", 400

        dificuldade = Dificuldade.query.filter_by(grau=grauDificuldade).first()
        if not dificuldade:
            return "Dificuldade inválida", 400

        ano_atual = datetime.now().year
        anoProva = AnoProva.query.filter_by(ano=ano_atual).first()
        if not anoProva:
            anoProva = AnoProva(ano=ano_atual)
            db.session.add(anoProva)
            db.session.commit()

        questao = Questao(codProfessor=codProfessor, descricaoQuestao=descricaoQuestao, codAnoProva=anoProva.codAnoProva, codDificuldade=dificuldade.codDificuldade, codTipo=tipo_questao.codTipo)
        db.session.add(questao)
        db.session.commit()

        cadastrarResposta(questao, respostas, respostas_corretas)
        return redirect(url_for('cadastro_questoes'))

    return render_template('cadastrarProva.html')


def cadastrarResposta(questao, respostas, respostas_corretas):
    for index, resposta in enumerate(respostas):
        correta = index in respostas_corretas
        nova_resposta = Resposta(codQuestao=questao.codQuestao, descricaoResposta=resposta, respCorreta=correta)
        db.session.add(nova_resposta)
    db.session.commit()


@app.errorhandler(404)
def page_not_found(error):
    return "Página não encontrada", 404


def reset():
    global contador, QUESTOES_DISPONIVEIS
    contador = 1
    QUESTOES_DISPONIVEIS = list(range(2, 12))
    random.shuffle(QUESTOES_DISPONIVEIS)
    return "Todas as questões foram utilizadas"

@app.route('/get_time')
def get_time():
    start_time = session.get('start_time', None)
    if start_time is None:
        return jsonify({'time_left': DURATION})
    
    elapsed_time = time.time() - start_time
    time_left = max(0, DURATION - elapsed_time)
    return jsonify({'time_left': int(time_left)})