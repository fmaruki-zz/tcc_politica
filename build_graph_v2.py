import json
import csv
from collections import defaultdict

class GenerateId(object):
    def __init__(self):
        self.id = 0
    def __call__(self):
        self.id += 1
        return self.id
generateId = GenerateId()


class ConnectNode(object):
    def __init__(self):
        self.connections = []

    def __call__(self, node1, node2, desc):
        if node1 and node2:
            self.connections.append((node1[0], node2[0], desc))

    def make_unique(self):
        connection_set = set(self.connections)
        self.connections = []
        for conn in connection_set:
            self.connections.append((conn[0], conn[1], conn[2], generateId()))

    def create_dicts(self):
        self.make_unique()
        by1 = defaultdict(list)
        by2 = defaultdict(list)
        for connection in self.connections:
            by1[connection[0]].append(connection)
            by2[connection[1]].append(connection)
        return (by1, by2)
connectNode = ConnectNode()


class NodeGen(object):
    def __init__(self, nodetype, key, columns, header_index):
        self.array = {}
        self.nodetype = nodetype
        if type(columns) == list:
            self.index = [header_index[c[key]] for c in columns]
            self.create = self.create_multi
            self.column_names = ["type"] + columns[0].keys()
            self.column_indexes = [[header_index.get(column) for column in c.values()] for c in columns]
        else:
            if key:
                self.index = header_index[columns[key]]
            else:
                self.create = self.create_no_key
                self.array = []
            self.column_names = ["type"] + columns.keys()
            self.column_indexes = [header_index.get(column) for column in columns.values()]

    def __iter__(self):
        return self.array.__iter__

    def __len__(self):
        return self.array.__len__

    def create(self, data):
        key = data[self.index]
        if not key:
            return None
        if key in self.array:
            node = self.array[key]
        else:
            node = [(data[index].decode("latin1").encode("utf-8") if index != None else "") for index in self.column_indexes]
            node.insert(0, generateId())
            self.array[key] = node
        return node

    def create_multi(self, data):
        node = [None for i in self.column_indexes]
        for i,cc in enumerate(self.column_indexes):
            key = data[self.index[i]]
            if not key:
                continue
            if key in self.array:
                node[i] = self.array[key]
            else:
                node[i] = [(data[index].decode("latin1").encode("utf-8") if index != None else "") for index in cc]
                node[i].insert(0, generateId())
                self.array[key] = node[i]
        return node

    def create_no_key(self, data):
        node = [(data[index].decode("latin1").encode("utf-8") if index != None else "") for index in self.column_indexes]
        node.insert(0, generateId())
        self.array.append(node)
        return node

    def print_node(self, node, cOut, cIn):
        id = node[0]
        values = [self.nodetype] + node[1:]
        obj = {
            "id": id,
            "label": "vertex",
            "properties": {name: [{"id": generateId(), "value": value}]
                for name, value in zip(self.column_names, node)
            }
        }

        nodes_out = cOut.get(id)
        nodes_in = cIn.get(id)
        if nodes_out:
            obj['outE'] = {}
            for node1, node2, link_name, link_id in nodes_out:
                if link_name not in obj['outE']:
                    obj['outE'][link_name] = []
                obj['outE'][link_name].append({
                    "id": link_id,
                    "inV": node2,
                })
        if nodes_in:
            obj['inE'] = {}
            for node1, node2, link_name, link_id in nodes_in:
                if link_name not in obj['inE']:
                    obj['inE'][link_name] = []
                obj['inE'][link_name].append({
                    "id": link_id,
                    "outV": node1,
                })
        return json.dumps(obj)

f1 = open("tse/cand_2010_replace.csv")
reader1 = csv.reader(f1, delimiter=";")
f2 = open("tse/cand_2012.csv")
reader2 = csv.reader(f2, delimiter=";")
f3 = open("tse/cand_2014.csv")
reader3 = csv.reader(f3, delimiter=";")
headers = reader1.next()
reader2.next()
reader3.next()
index = {h: i for i,h in enumerate(headers)}

people = NodeGen("pessoa", "cpf", dict(
    raca="DESCRICAO_COR_RACA",
    cpf="CPF_CANDIDATO",
    data_nascimento="DATA_NASCIMENTO",
    nacionalidade="DESCRICAO_NACIONALIDADE",
    sexo="DESCRICAO_SEXO",
    nome="NOME_CANDIDATO",
    titulo_eleitoral="NUM_TITULO_ELEITORAL_CANDIDATO",
), index)

candidatures = NodeGen("candidatura", None, dict(
    ano="ANO_ELEICAO",
    situacao="DES_SITUACAO_CANDIDATURA",
    resultado="DESC_SIT_TOT_TURNO",
    nome_eleicao="DESCRICAO_ELEICAO",
    estado_civil="DESCRICAO_ESTADO_CIVIL",
    grau_instrucao="DESCRICAO_GRAU_INSTRUCAO",
    despesa_max="DESPESA_MAX_CAMPANHA",
    idade="IDADE_DATA_ELEICAO",
    email="NM_EMAIL",
    nome_urna="NOME_URNA_CANDIDATO",
    turno="NUM_TURNO",
    numero="NUMERO_CANDIDATO",
    seq="SEQUENCIAL_CANDIDATO",
), index)

posts = NodeGen("cargo", "nome", dict(
    nome="DESCRICAO_CARGO",
), index)

jobs = NodeGen("ocupacao", "nome", dict(
    nome="DESCRICAO_OCUPACAO",
), index)

states = NodeGen("estado", "sigla", [
    dict(sigla="SIGLA_UF"),
    dict(sigla="SIGLA_UF_NASCIMENTO"),
], index)

cities = NodeGen("cidade", "nome", [
    dict(nome="DESCRICAO_UE"),
    dict(nome="NOME_MUNICIPIO_NASCIMENTO"),
], index)

parties = NodeGen("partido", "sigla", dict(
    nome="NOME_PARTIDO",
    sigla="SIGLA_PARTIDO",
    numero="NUMERO_PARTIDO",
), index)

blocs = NodeGen("coligacao", "codigo", dict(
    nome="NOME_LEGENDA",
    sigla="SIGLA_LEGENDA",
    codigo="CODIGO_LEGENDA",
    composicao="COMPOSICAO_LEGENDA",
), index)

for reader in (reader1, reader2, reader3):
    for line in reader:
        person = people.create(line)
        candidature = candidatures.create(line)
        post = posts.create(line)
        job = jobs.create(line)
        bloc = blocs.create(line)
        party = parties.create(line)
        state = states.create(line)
        city = cities.create(line)
        connectNode(candidature, post, "cargo")
        connectNode(candidature, job, "ocupacao")
        if line[index["SIGLA_UE"]] != line[index["SIGLA_UF"]]:
            connectNode(candidature, city[0], "local")
        else:
            city[0] = None
            connectNode(candidature, state[0], "local")
        connectNode(candidature, party, "partido")
        connectNode(candidature, bloc, "coligacao")
        connectNode(person, candidature, "candidatura")
        connectNode(bloc, party, "partido")
        connectNode(city[0], state[0], "estado")
        connectNode(city[1], state[1], "estado")
        connectNode(person, city[1], "nascimento")

by1, by2 = connectNode.create_dicts()

with open("output_objs.json", "w") as f:
    print "person"
    for person in people.array.values():
        obj = people.print_node(person, by1, by2)
        print >>f, obj
    people = None

    print "candidature"
    for candidature in candidatures.array:
        obj = candidatures.print_node(candidature, by1, by2)
        print >>f, obj
    candidatures = None

    print "post"
    for post in posts.array.values():
        obj = posts.print_node(post, by1, by2)
        print >>f, obj
    posts = None

    print "job"
    for job in jobs.array.values():
        obj = jobs.print_node(job, by1, by2)
        print >>f, obj
    jobs = None

    print "bloc"
    for bloc in blocs.array.values():
        obj = blocs.print_node(bloc, by1, by2)
        print >>f, obj
    blocs = None

    print "party"
    for party in parties.array.values():
        obj = parties.print_node(party, by1, by2)
        print >>f, obj
    parties = None

    print "state"
    for state in states.array.values():
        obj = states.print_node(state, by1, by2)
        print >>f, obj
    states = None

    print "city"
    for city in cities.array.values():
        obj = cities.print_node(city, by1, by2)
        print >>f, obj
    cities = None

