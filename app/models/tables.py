from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Aluno.query.filter_by(id=user_id).first()


class Aluno(db.Model, UserMixin):
    __tablename__ = "alunos"

    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(14), nullable=False, unique=True)
    nome = db.Column(db.String(80), nullable=False)
    instituicao_ensino = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(40), nullable=False,unique=True)
    senha = db.Column(db.String(128), nullable=False)

    provas = db.relationship('Prova', backref='alunos')

    def __init__(self, cpf, nome, instituicao_ensino, email, senha):
        self.cpf = cpf
        self.nome = nome
        self.instituicao_ensino = instituicao_ensino
        self.email = email
        self.senha = generate_password_hash(senha)

    def verify_password(self, senha):
        return check_password_hash(self.senha, senha)


    def __repr__(self) -> str:
        return "<Aluno %r>" % self.nome

class Prova(db.Model):
    __tablename__ = "provas"

    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'))

    def __init__(self, aluno_id):
        self.aluno_id = aluno_id

    def __repr__(self) -> str:
        return "<Prova %r>" % self.id

class Questao(db.Model):
    __tablename__ = "questoes"

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text)
    repostaCorreta = db.Column(db.String(1))
    respostas = db.relationship('Resposta', backref='questoes')

    def __init__(self, descricao):
        self.descricao = descricao

    def __repr__(self) -> str:
        return "<Questoes %r>" % self.id


class Resposta(db.Model):
    __tablename__ = "respostas"

    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text)
    questao_id = db.Column(db.Integer, db.ForeignKey('questoes.id'))

    def __init__(self, descricao, questao_id):
        self.descricao = descricao
        self.questao_id = questao_id

    def __repr__(self) -> str:
        return "<Respostas %r>" % self.id




