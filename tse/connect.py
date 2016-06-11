# import psycopg2 as psql

# conn = psql.connect(dbname="tse", user="tseuser", host="tseinstance.chidn7ywooak.us-west-2.rds.amazonaws.com", password="tsepassword")
# psql -h tseinstance.chidn7ywooak.us-west-2.rds.amazonaws.com -p 5432 -U tseuser tse

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

engine = create_engine("postgresql+psycopg2://tseuser:tsepassword@tseinstance.chidn7ywooak.us-west-2.rds.amazonaws.com:5432/tse")
Base = declarative_base()

class Pessoa(Base):
    __tablename__ = "pessoas"
    titulo_eleitoral = Column(String, primary_key=True)
    nome = Column(String)
    cpf = Column(String)
    sexo = Column(String)
    grau_instrucao = Column(String)
    raca = Column(String)
    nacionalidade = Column(String)
    uf = Column(String)
    cod_municipio = Column(String)
    municipio = Column(String)


leg_part = Table("partidos_legendas", Base.metadata,
    Column("partido", ForeignKey("partidos.nome"), primary_key=True),
    Column("legenda", ForeignKey("legendas.ano_cod"), primary_key=True),
)

class Partido(Base):
    __tablename__ = "partidos"
    nome = Column(String, primary_key=True)
    numero = Column(String)
    legendas = relationship("Legenda", secondary=leg_part, back_populates="partidos")


class Legenda(Base):
    __tablename__ = "legendas"
    ano_cod = Column(String, primary_key=True)
    ano = Column(String)
    codigo = Column(String)
    sigla = Column(String)
    nome = Column(String)
    composicao = Column(String)
    partidos = relationship("Partido", secondary=leg_part, back_populates="legendas")


class Candidatura(Base):
    __tablename__ = "candidaturas"
    id = Column(Integer, primary_key=True)
    ano = Column(String)
    turno = Column(String)
    uf = Column(String)
    cod_cidade = Column(String)
    cidade = Column(String)
    cargo = Column(String)
    numero = Column(String)
    nome = Column(String)
    situacao = Column(String)
    ocupacao = Column(String)
    estado_civil = Column(String)
    resultado = Column(String)
    email = Column(String)
    pessoa_id = Column(String, ForeignKey("pessoas.titulo_eleitoral"))
    pessoa = relationship("Pessoa", back_populates="candidaturas")
    partido_id = Column(String, ForeignKey("partidos.nome"))
    partido = relationship("Partido", back_populates="candidaturas")
    legenda_id = Column(String, ForeignKey("legendas.ano_cod"))
    legenda = relationship("Legenda", back_populates="candidaturas")

Pessoa.candidaturas = relationship("Candidatura", back_populates="pessoa")
Partido.candidaturas = relationship("Candidatura", back_populates="partido")
Legenda.candidaturas = relationship("Candidatura", back_populates="legenda")

if __name__ == "__main__":
    Base.metadata.create_all(engine)
