import csv
import sys
from connect import Pessoa, Candidatura, Partido, Legenda, engine
from sqlalchemy.orm import sessionmaker
from collections import defaultdict

Session = sessionmaker(bind=engine)
session = Session()

filename = sys.argv[1]
f = open(filename)
reader = csv.DictReader(f, delimiter=";")
registries = list(reader)

def populate(obj, dictionary, fields):
    for obj_name, dict_name in fields.items():
        setattr(obj, obj_name, dictionary.get(dict_name, "").decode("latin1").encode("utf-8"))

counter = 0
titulos = set()
for line in registries:
    counter += 1
    print "pessoa-{}".format(counter)
    if line["NUM_TITULO_ELEITORAL_CANDIDATO"] in titulos:
        continue
    else:
        titulos.add(line["NUM_TITULO_ELEITORAL_CANDIDATO"])
    pessoa = Pessoa()
    populate(pessoa, line, dict(
        nome = "NOME_CANDIDATO",
        cpf = "CPF_CANDIDATO",
        titulo_eleitoral = "NUM_TITULO_ELEITORAL_CANDIDATO",
        sexo = "DESCRICAO_SEXO",
        grau_instrucao = "DESCRICAO_GRAU_INSTRUCAO",
        raca = "DESCRICAO_COR_RACA",
        nacionalidade = "CODIGO_NACIONALIDADE",
        uf = "SIGLA_UF_NASCIMENTO",
        cod_municipio = "CODIGO_MUNICIPIO_NASCIMENTO",
        municipio = "NOME_MUNICIPIO_NASCIMENTO",
    ))
    session.add(pessoa)
    print "ok"
session.commit()



counter = 0
partido_ano = set()
for line in registries:
    counter += 1
    print "partidos-{}".format(counter)
    if (line["NOME_PARTIDO"], line["ANO_ELEICAO"]) in partido_ano:
        continue
    else:
        partido_ano.add((line["NOME_PARTIDO"], line["ANO_ELEICAO"]))
    #
    partido = session.query(Partido).filter_by(nome=line['NOME_PARTIDO'].decode("latin1").encode("utf-8")).first()
    if not partido:
        partido = Partido()
        populate(partido, line, dict(
            nome="NOME_PARTIDO",
            numero="NUMERO_PARTIDO",
        ))
        session.add(partido)

    #
    legenda = session.query(Legenda).filter_by(ano=line['ANO_ELEICAO'].decode("latin1").encode("utf-8"), codigo=line['CODIGO_LEGENDA'].decode("latin1").encode("utf-8")).first()
    if not legenda:
        legenda = Legenda()
        populate(legenda, line, dict(
            ano='ANO_ELEICAO',
            codigo='CODIGO_LEGENDA',
            sigla='SIGLA_LEGENDA',
            nome='NOME_LEGENDA',
            composicao='COMPOSICAO_LEGENDA',
        ))
        legenda.ano_cod = legenda.ano + legenda.codigo
    legenda.partidos.append(partido)
    session.add(legenda)
    print "ok"
session.commit()



counter = 0
for line in registries:
    counter += 1
    print "candidatura-{}".format(counter)
    #
    cand = Candidatura()
    populate(cand, line, dict(
        ano="ANO_ELEICAO",
        turno="NUM_TURNO",
        cargo="DESCRICAO_CARGO",
        numero="NUMERO_CANDIDATO",
        nome="NOME_URNA_CANDIDATO",
        situacao="DES_SITUACAO_CANDIDATURA",
        ocupacao="DESCRICAO_OCUPACAO",
        estado_civil="DESCRICAO_ESTADO_CIVIL",
        resultado="DESC_SIT_TOT_TURNO",
        email="NM_EMAIL",
        pessoa_id="NUM_TITULO_ELEITORAL_CANDIDATO",
        partido_id="NOME_PARTIDO",
    ))
    cand.legenda_id = cand.ano + line["CODIGO_LEGENDA"].decode("latin1").encode("utf-8")
    if line['SIGLA_UF'] == line['SIGLA_UE']:
        populate(cand, line, dict(uf="SIGLA_UF"))
    else:
        populate(cand, line, dict(
            cod_cidade="SIGLA_UE",
            cidade="DESCRICAO_UE",
        ))
    session.add(cand)
    print "ok"
session.commit()
