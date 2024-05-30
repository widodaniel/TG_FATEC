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
    acessoUsuario = db.Column(db.String(1), nullable=True)

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

    codAluno = db.Column(db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
    ra = db.Column(db.String(30), nullable=False)
    ciclo_finalizado = db.Column(db.String(1), nullable=False)

    def __init__(self, codAluno, ra, ciclo_finalizado):
        self.codAluno = codAluno
        self.ra = ra
        self.ciclo_finalizado = ciclo_finalizado
    
    def __repr__(self):
        return f"<Aluno {self.codAluno}>"
    
class Professor(db.Model):
    __tablename__ = 'professor'

    codProfessor = db.Column(db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
    rp = db.Column(db.String(30))
    acesso = db.Column(db.String(1))

    def __init__(self, codProfessor, rp, acesso):
        self.codProfessor = codProfessor
        self.rp = rp
        self.acesso = acesso
    
    def __repr__(self):
        return f"<Professor {self.codProfessor}>"
    

class Prova(db.Model):
    __tablename__ = 'prova'

    codProva = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codAluno = db.Column(db.Integer, db.ForeignKey('aluno.codAluno'), nullable=False)
    quantidadeCorreta = db.Column(db.Integer)
    dt_emissao = db.Column(db.Date)
    tempo_prova = db.Column(db.DateTime)

    def __init__(self, codAluno, quantidadeCorreta, dt_emissao,tempo_prova):
        self.codAluno = codAluno
        self.quantidadeCorreta = quantidadeCorreta
        self.dt_emissao = dt_emissao
        self.tempo_prova = tempo_prova
    
    def __repr__(self):
        return f"<Prova {self.codAluno}>"

class AnoProva(db.Model):
    __tablename__ = 'anoprova'

    codAnoProva = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ano = db.Column(db.Integer)

    def __init__(self, ano):
        self.ano = ano
    
    def __repr__(self):
        return f"<AnoProva {self.ano}>"

class Dificuldade(db.Model):
    __tablename__ = 'dificuldade'

    codDificuldade = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grau = db.Column(db.String(1))

    def __init__(self, grau):
        self.grau = grau
    
    def __repr__(self):
        return f"<Dificuldade {self.grau}>"

class Questao(db.Model):
    __tablename__ = 'questoes'

    codQuestao = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codProfessor = db.Column(db.Integer, db.ForeignKey('professor.codProfessor'))
    descricaoQuestao = db.Column(db.String(600))
    codAnoProva = db.Column(db.Integer, db.ForeignKey('anoprova.codAnoProva'))
    codDificuldade = db.Column(db.Integer, db.ForeignKey('dificuldade.codDificuldade'))
    codTipo = db.Column(db.Integer, db.ForeignKey('tipoquestao.codTipo'))

    def __init__(self, codProfessor, descricaoQuestao, codAnoProva, codDificuldade, codTipo):
        self.codProfessor = codProfessor
        self.descricaoQuestao = descricaoQuestao
        self.codAnoProva = codAnoProva
        self.codDificuldade = codDificuldade
        self.codTipo = codTipo
    
    def __repr__(self):
        return f"<Questao {self.descricaoQuestao}>"

class Resposta(db.Model):
    __tablename__ = 'respostas'

    codResposta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codQuestao = db.Column(db.Integer, db.ForeignKey('questoes.codQuestao'))
    descricaoResposta = db.Column(db.String(600))
    respCorreta = db.Column(db.Boolean)

    def __init__(self, codQuestao, descricaoResposta, respCorreta):
        self.codQuestao = codQuestao
        self.descricaoResposta = descricaoResposta
        self.respCorreta = respCorreta

    def __repr__(self):
        return f"<Resposta {self.descricaoResposta}>"
class QuestoesProva(db.Model):
    __tablename__ = 'questoesprova'

    codQuestao = db.Column(db.Integer, db.ForeignKey('questoes.codQuestao'), primary_key=True)
    codProva = db.Column(db.Integer, db.ForeignKey('prova.codProva'), primary_key=True)

    def __init__(self, codQuestao, codProva):
        self.codQuestao = codQuestao
        self.codProva = codProva

    def __repr__(self):
        return f"<QuestoesProva {self.codQuestao, self.codProva}>"

class TipoQuestao(db.Model):
    __tablename__ = 'tipoquestao'

    codTipo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricaoTipo = db.Column(db.String(60))

    def __init__(self, descricaoTipo):
        self.descricaoTipo = descricaoTipo

    def __repr__(self):
        return f"<TipoQuestao {self.descricaoTipo}>"