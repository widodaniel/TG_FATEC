from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.filter_by(id=user_id).first()

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cpf = db.Column(db.String(11), nullable=False, unique=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(256), nullable=False)

    alunos = db.relationship('Aluno', backref='usuario', lazy=True)
    professores = db.relationship('Professor', backref='usuario', lazy=True)

    def __init__(self, cpf, nome, email, senha):
        self.cpf = cpf
        self.nome = nome
        self.email = email
        self.senha = generate_password_hash(senha)

    def verify_password(self, senha):
        return check_password_hash(self.senha, senha)

    def __repr__(self):
        return f"<Usuario {self.nome}>"

class Aluno(db.Model):
    __tablename__ = 'aluno'

    id = db.Column(db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
    ra = db.Column(db.String(30), nullable=False)
    ciclo_finalizado = db.Column(db.String(1), nullable=False)

class Professor(db.Model):
    __tablename__ = 'professor'

    id = db.Column(db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
    rp = db.Column(db.String(30))
    acesso = db.Column(db.String(1))

class Prova(db.Model):
    __tablename__ = 'prova'

    codProva = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    quantidadeCorreta = db.Column(db.Integer)
    dt_emissao = db.Column(db.Date)
    tempo_prova = db.Column(db.DateTime)

class Caderno(db.Model):
    __tablename__ = 'caderno'

    codCaderno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricaoCaderno = db.Column(db.String(20))

class AnoProva(db.Model):
    __tablename__ = 'anoprova'

    codAnoProva = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ano = db.Column(db.Integer)

class Dificuldade(db.Model):
    __tablename__ = 'dificuldade'

    codDificuldade = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grau = db.Column(db.String(1))

class Questao(db.Model):
    __tablename__ = 'questoes'

    codQuestao = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.Integer, db.ForeignKey('professor.id'))
    descricaoQuest = db.Column(db.String(600))
    codCaderno = db.Column(db.Integer, db.ForeignKey('caderno.codCaderno'))
    codAnoProva = db.Column(db.Integer, db.ForeignKey('anoprova.codAnoProva'))
    codDificuldade = db.Column(db.Integer, db.ForeignKey('dificuldade.codDificuldade'))
    tipo = db.Column(db.String(30))

class Resposta(db.Model):
    __tablename__ = 'respostas'

    codResposta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codQuestao = db.Column(db.Integer, db.ForeignKey('questoes.codQuestao'))
    descricaoResposta = db.Column(db.String(600))
    respCorreta = db.Column(db.Boolean)

class QuestoesProva(db.Model):
    __tablename__ = 'questoesprova'

    codquestao = db.Column(db.Integer, db.ForeignKey('questoes.codQuestao'), primary_key=True)
    codprova = db.Column(db.Integer, db.ForeignKey('prova.codProva'), primary_key=True)

class TipoQuestao(db.Model):
    __tablename__ = 'tipoquestao'

    codTipo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricaoTipo = db.Column(db.String(60))
