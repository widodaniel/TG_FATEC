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
from collections import Counter
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

# Constantes e variáveis globais
NUMERO_QUESTOES = 10
QUESTOES_DISPONIVEIS = list(range(2, 20))

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
        session['usuario_id'] = usuario.id
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
    

@app.route('/atualizar_senha', methods=['POST'])
@login_required
def atualizar_senha():
    senha_antiga = request.form['senhaAntiga']
    senha_nova = request.form['senhaNova']
    usuario = Usuario.query.get(current_user.id)
    
    if not usuario.verify_password(senha_antiga):
        return jsonify({'success': False, 'messageTitle': 'Senha incorreta', 'messageText': 'Sua senha está incorreta, tente novamente!!'})

    if usuario.verify_password(senha_nova):
        return jsonify({'success': False, 'messageTitle': 'Senha idêntica', 'messageText': 'Sua senha está igual a anterior, tente novamente!!'})
    
    usuario.senha = generate_password_hash(senha_nova)
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'messageTitle': 'Senha alterada', 'messageText': 'Sua senha foi alterada com sucesso'})
    except Exception as e:
        print(f"Erro ao atualizar a senha: {e}")
        return jsonify({'success': False, 'messageTitle': 'Erro ao atualizar a senha', 'messageText': 'Houve uma falha ao atualizar sua senha!!'})


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
    professor = Professor.query.filter_by(codProfessor=current_user.id).first()
    questoes = Questao.query.filter_by(codProfessor=professor.codProfessor).all()
    
    for questao in questoes:
        respostas = Resposta.query.filter_by(codQuestao = questao.codQuestao).all()
    return render_template('editarQuestoes.html', questoes = questoes, respostas = respostas)

@app.route("/get_respostas/<int:codQuestao>", methods=['GET'])
@login_required
def get_respostas(codQuestao):
    questao = Questao.query.filter_by(codQuestao=codQuestao).first()
    respostas = Resposta.query.filter_by(codQuestao=codQuestao).all()
    tipoQuestao = TipoQuestao.query.filter_by(codTipo=questao.codTipo).first()
    respostas_data = [{'descricao': resposta.descricaoResposta, 'correta': resposta.respCorreta} for resposta in respostas]
    return jsonify({
            'descricaoQuestao': questao.descricaoQuestao,
            'codDificuldade': questao.codDificuldade,
            'codTipo': tipoQuestao.descricaoTipo,
            'respostas': respostas_data
        })

from sqlalchemy.exc import SQLAlchemyError

@app.route("/removeQuestao/<int:codQuestao>", methods=['GET'])
@login_required
def remove_questao(codQuestao):
    try:
        questao = Questao.query.filter_by(codQuestao=codQuestao).first()
        if questao:
            # Exclui todas as respostas da questão
            Resposta.query.filter_by(codQuestao=codQuestao).delete()
            # Exclui a questão
            db.session.delete(questao)
            db.session.commit()
            return "Questão removida com sucesso!", 200
        else:
            return "Questão não encontrada.", 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return f"Erro ao remover a questão: {str(e)}", 500
    
@app.route("/alterarProva", methods=['POST'])
def alterar_prova():
    if request.method == 'POST':
        codQuestao = request.form['codQuestao']  # Obtém o código da questão a ser alterada
        descricaoQuestao = request.form['questao-descricao']
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

        questao = Questao.query.get(codQuestao)  # Obtém a questão existente a ser alterada
        if not questao:
            return "Questão não encontrada", 404

        questao.descricaoQuestao = descricaoQuestao
        questao.codDificuldade = dificuldade.codDificuldade
        questao.codTipo = tipo_questao.codTipo
        db.session.commit()

        # Atualiza as respostas da questão
        respostas_questao = Resposta.query.filter_by(codQuestao=codQuestao).all()
        for index, resposta in enumerate(respostas_questao):
            resposta.descricaoResposta = respostas[index]
            resposta.respCorreta = index in respostas_corretas
        db.session.commit()

        return redirect(url_for('editar_questoes'))


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
    
    # Obtém o tipo de questão
    tipo_questao = Questao.query.get(id_questao_atual).codTipo

    # Obtém a descrição do tipo de questão
    descricao_tipo_questao = TipoQuestao.query.get(tipo_questao).descricaoTipo

    # Verifica se a resposta selecionada é correta
    correta = resposta_selecionada == resposta_correta

    # Salva a resposta e a informação se estava correta ou não
    respostas.append({'resposta': resposta_selecionada, 'correta': correta, 'tipo': tipo_questao, 'descricao_tipo': descricao_tipo_questao})
    contador += 1

    print(contador)
    if len(respostas) == 10:
        return redirect(url_for('resultado'))
    return redirect(url_for('questao', id_questao=contador))


@app.route("/resultado")
def resultado():
    resultados_tipos = None
    contador_corretas = sum(1 for resposta in respostas if resposta['correta'])
    resultados = [{'resposta': resposta['resposta'], 'correta': resposta['correta']} for resposta in respostas]
    tipos_questoes = [resposta['descricao_tipo'] for resposta in respostas]
    contagem_tipos = Counter(tipos_questoes)

    tipos = list(contagem_tipos.keys())
    contagens = list(contagem_tipos.values())

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
        resultados_tipos = zip(resultados, tipos_questoes)
    return render_template('resultado.html', respostas=respostas, resultados=resultados, contador_corretas=contador_corretas, tempo_prova=tempo_prova_final, resultados_tipos=resultados_tipos, contagens=contagens, tipos=tipos)


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

    return render_template('cadastroQuestoes.html')


def cadastrarResposta(questao, respostas, respostas_corretas):
    for index, resposta in enumerate(respostas):
        correta = index in respostas_corretas
        nova_resposta = Resposta(codQuestao=questao.codQuestao, descricaoResposta=resposta, respCorreta=correta)
        db.session.add(nova_resposta)
    db.session.commit()


@app.errorhandler(404)
def page_not_found(error):
    return "Página não encontrada", 404


@app.route("/relatorios_professor", methods=['GET'])
def relatorios_professor():
    # Obter todos os alunos
    alunos = Aluno.query.all()

    # Criar uma lista para armazenar os objetos de relatório
    relatorios = []
    provas = []

    # Iterar sobre os alunos e obter a prova mais recente de cada um
    for aluno in alunos:
        prova = Prova.query.filter_by(codAluno=aluno.codAluno).order_by(desc(Prova.codProva)).first()
        if prova:
            usuario = Usuario.query.filter_by(id=aluno.codAluno).first()
            provas.append(prova)

            relatorio = {
                'codProva': prova.codProva,
                'raAluno': aluno.ra,
                'nomeAluno': usuario.nome,
                'quantidadeCorreta': prova.quantidadeCorreta,
                'tempo_prova': prova.tempo_prova
            }
            relatorios.append(relatorio)
            print(f'Adicionado relatório para a prova {prova.codProva} ao relatório')

    # Limitar a 10 provas mais recentes
    provas = sorted(provas, key=lambda x: x.codProva, reverse=True)[:10]

    # Obter os dados para o gráfico de barras duplas
    alunos, acertos, erros = grafico_barras(provas)

    return render_template('relatorios_professor.html', relatorios=relatorios, alunos=alunos, acertos=acertos, erros=erros)


@app.route("/relatorios_aluno", methods=['GET'])
@login_required
def relatorios_aluno():
    # Obter o id do aluno logado
    id_aluno_logado = current_user.id

    # Obter as 10 últimas provas do aluno logado
    provas = Prova.query.filter_by(codAluno=id_aluno_logado).order_by(desc(Prova.codProva)).limit(10).all()

    # Criar uma lista para armazenar os objetos de relatório
    relatorios = []

    # Iterar sobre as provas e criar um objeto de relatório para cada uma
    for prova in provas:
        relatorio = {
            'codProva': prova.codProva,
            'quantidadeCorreta': prova.quantidadeCorreta,
            'tempo_prova': prova.tempo_prova
        }
        relatorios.append(relatorio)

    return render_template('relatorios_aluno.html', relatorios=relatorios)


def grafico_barras(provas):
    # Criar listas para armazenar os códigos dos alunos, acertos e erros
    alunos = []
    acertos = []
    erros = []

    # Iterar sobre as provas e adicionar os dados às listas
    for prova in provas:
        aluno = Aluno.query.filter_by(codAluno=prova.codAluno).first()
        usuario = Usuario.query.filter_by(id=aluno.codAluno).first()

        alunos.append(usuario.nome)
        acertos.append(prova.quantidadeCorreta)
        erros.append(10 - prova.quantidadeCorreta)

    return alunos, acertos, erros




def reset():
    global contador, QUESTOES_DISPONIVEIS
    QUESTOES_DISPONIVEIS = list(range(2, 20))
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

@app.route('/profile')
def profile():
    if current_user.is_authenticated:
        return render_template('profile.html', user=current_user)
    else:
        return redirect(url_for('login'))