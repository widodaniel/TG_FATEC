"""empty message

Revision ID: cfae280a81ea
Revises: 
Create Date: 2024-04-17 17:16:56.894249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfae280a81ea'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('anoprova',
    sa.Column('codAnoProva', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('ano', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('codAnoProva')
    )
    op.create_table('caderno',
    sa.Column('codCaderno', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('descricaoCaderno', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('codCaderno')
    )
    op.create_table('dificuldade',
    sa.Column('codDificuldade', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('grau', sa.String(length=1), nullable=True),
    sa.PrimaryKeyConstraint('codDificuldade')
    )
    op.create_table('tipoquestao',
    sa.Column('codTipo', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('descricaoTipo', sa.String(length=60), nullable=True),
    sa.PrimaryKeyConstraint('codTipo')
    )
    op.create_table('usuario',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('cpf', sa.String(length=11), nullable=False),
    sa.Column('nome', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('senha', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cpf'),
    sa.UniqueConstraint('email')
    )
    op.create_table('aluno',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ra', sa.String(length=30), nullable=False),
    sa.Column('ciclo_finalizado', sa.String(length=1), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['usuario.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('professor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rp', sa.String(length=30), nullable=True),
    sa.Column('acesso', sa.String(length=1), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['usuario.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('prova',
    sa.Column('codProva', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('quantidadeCorreta', sa.Integer(), nullable=True),
    sa.Column('dt_emissao', sa.Date(), nullable=True),
    sa.Column('tempo_prova', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['aluno.id'], ),
    sa.PrimaryKeyConstraint('codProva')
    )
    op.create_table('questoes',
    sa.Column('codQuestao', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id', sa.Integer(), nullable=True),
    sa.Column('descricaoQuest', sa.String(length=600), nullable=True),
    sa.Column('codCaderno', sa.Integer(), nullable=True),
    sa.Column('codAnoProva', sa.Integer(), nullable=True),
    sa.Column('codDificuldade', sa.Integer(), nullable=True),
    sa.Column('tipo', sa.String(length=30), nullable=True),
    sa.ForeignKeyConstraint(['codAnoProva'], ['anoprova.codAnoProva'], ),
    sa.ForeignKeyConstraint(['codCaderno'], ['caderno.codCaderno'], ),
    sa.ForeignKeyConstraint(['codDificuldade'], ['dificuldade.codDificuldade'], ),
    sa.ForeignKeyConstraint(['id'], ['professor.id'], ),
    sa.PrimaryKeyConstraint('codQuestao')
    )
    op.create_table('questoesprova',
    sa.Column('codquestao', sa.Integer(), nullable=False),
    sa.Column('codprova', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['codprova'], ['prova.codProva'], ),
    sa.ForeignKeyConstraint(['codquestao'], ['questoes.codQuestao'], ),
    sa.PrimaryKeyConstraint('codquestao', 'codprova')
    )
    op.create_table('respostas',
    sa.Column('codResposta', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('codQuestao', sa.Integer(), nullable=True),
    sa.Column('descricaoResposta', sa.String(length=600), nullable=True),
    sa.Column('respCorreta', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['codQuestao'], ['questoes.codQuestao'], ),
    sa.PrimaryKeyConstraint('codResposta')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('respostas')
    op.drop_table('questoesprova')
    op.drop_table('questoes')
    op.drop_table('prova')
    op.drop_table('professor')
    op.drop_table('aluno')
    op.drop_table('usuario')
    op.drop_table('tipoquestao')
    op.drop_table('dificuldade')
    op.drop_table('caderno')
    op.drop_table('anoprova')
    # ### end Alembic commands ###
