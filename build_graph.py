import json

class ListOfNodes(object):
    def __init__(self, *args):
        self.innerList = []
        self.keys = args

    def __getitem__(self, index):
        return self.innerList[index]

    def __setitem__(self, index, value):
        self.innerList[index] = value

    def __delitem__(self, index):
        del self.innerList[index]

    def __iter__(self):
        return iter(self.innerList)

    def __len__(self):
        return len(self.innerList)

    def find(self, *args):
        for item in self.innerList:
            properties = item['properties']
            for index, key in enumerate(self.keys):
                if args[index] == properties[key][0]['value']:
                    return item
        return None

    def append(self, item):
        self.innerList.append(item)

people = ListOfNodes("cpf")
candidatures = ListOfNodes("ano", "turno", "nome_urna")
posts = ListOfNodes("nome")
jobs = ListOfNodes("nome")
states = ListOfNodes("sigla")
cities = ListOfNodes("nome")
parties = ListOfNodes("sigla")
blocs = ListOfNodes("codigo")


class GenerateId(object):
    def __init__(self):
        self.id = 0
    def __call__(self):
        self.id += 1
        return self.id
generateId = GenerateId()


def createNode(**kwargs):
    return {
        "id": generateId(),
        "label": "vertex",
        "properties": {name: [{"id": generateId(), "value": value}]
            for name, value in kwargs.items()
        }
    }

def connectNode(node1, node2, name):
    if "outE" not in node1:
        node1['outE'] = {}
    if name not in node1["outE"]:
        node1['outE'][name] = []
    elif node2 in node1['outE'][name]:
        return

    id = generateId()
    node1['outE'][name].append({
        "id": id,
        "inV": node2['id']
    })

    if 'inE' not in node2:
        node2['inE'] = {}
    if name not in node2["inE"]:
        node2['inE'][name] = []
    node2['inE'][name].append({
        "id": id,
        "outV": node1['id']
    })


def createPersonNode(data):
    node = people.find(data.get("CPF_CANDIDATO"))
    if not node:
        node = createNode(
            type="pessoa",
            raca=data.get("DESCRICAO_COR_RACA"),
            cpf=data.get("CPF_CANDIDATO"),
            data_nascimento=data.get("DATA_NASCIMENTO"),
            nacionalidade=data.get("DESCRICAO_NACIONALIDADE"),
            sexo=data.get("DESCRICAO_SEXO"),
            nome=data.get("NOME_CANDIDATO"),
            titulo_eleitoral=data.get("NUM_TITULO_ELEITORAL_CANDIDATO"),
        )
        people.append(node)
    candidature = createCandidature(data)
    location = createBirthLocation(data)
    connectNode(node, candidature, "candidatura")
    connectNode(node, location, "nascimento")
    return node


def createCandidature(data):
    node = candidatures.find(data.get("ANO_ELEICAO"), data.get("NUM_TURNO"), data.get("NOME_URNA_CANDIDATO"))
    if not node:
        node = createNode(
            type="candidatura",
            ano=data.get("ANO_ELEICAO"),
            situacao=data.get("DES_SITUACAO_CANDIDATURA"),
            resultado=data.get("DESC_SIT_TOT_TURNO"),
            nome_eleicao=data.get("DESCRICAO_ELEICAO"),
            estado_civil=data.get("DESCRICAO_ESTADO_CIVIL"),
            grau_instrucao=data.get("DESCRICAO_GRAU_INSTRUCAO"),
            despesa_max=data.get("DESPESA_MAX_CAMPANHA"),
            idade=data.get("IDADE_DATA_ELEICAO"),
            email=data.get("NM_EMAIL"),
            nome_urna=data.get("NOME_URNA_CANDIDATO"),
            turno=data.get("NUM_TURNO"),
            numero=data.get("NUMERO_CANDIDATO"),
            seq=data.get("SEQUENCIAL_CANDIDATO"),
        )
        candidatures.append(node)
    post = createPost(data)
    job = createJob(data)
    location = createLocation(data)
    party = createParty(data)
    bloc = createBloc(data)
    connectNode(node, post, "cargo")
    connectNode(node, job, "ocupação")
    connectNode(node, location, "local")
    connectNode(node, party, "partido")
    connectNode(node, bloc, "coligação")
    connectNode(bloc, party, "partido")
    return node

def createPost(data):
    node = posts.find(data.get("DESCRICAO_CARGO"))
    if not node:
        node = createNode(
            type="cargo",
            nome=data.get("DESCRICAO_CARGO"),
        )
        posts.append(node)
    return node

def createJob(data):
    node = jobs.find(data.get("DESCRICAO_OCUPACAO"))
    if not node:
        node = createNode(
            type="ocupação",
            nome=data.get("DESCRICAO_OCUPACAO"),
        )
        jobs.append(node)
    return node

def createLocation(data):
    if data.get("SIGLA_UE") == data.get("SIGLA_UF"):
        # é um estado
        node = states.find(data.get("SIGLA_UF"))
        if not node:
            node = createNode(
                type="estado",
                sigla=data.get("SIGLA_UF"),
            )
            states.append(node)
    else:
        # é uma cidade
        node = cities.find(data.get("DESCRICAO_UE"))
        if not node:
            state = states.find(data.get("SIGLA_UF"))
            if not state:
                state = createNode(
                    type="estado",
                    sigla=data.get("SIGLA_UF"),
                )
                states.append(state)
            node = createNode(
                type="cidade",
                nome=data.get("DESCRICAO_UE"),
            )
            cities.append(node)
            connectNode(node, state, "estado")
    return node

def createBirthLocation(data):
    node = cities.find(data.get("NOME_MUNICIPIO_NASCIMENTO"))
    if not node:
        state = states.find(data.get("SIGLA_UF_NASCIMENTO"))
        if not state:
            state = createNode(
                type="estado",
                sigla=data.get("SIGLA_UF_NASCIMENTO"),
            )
            states.append(state)
        node = createNode(
            type="cidade",
            nome=data.get("NOME_MUNICIPIO_NASCIMENTO"),
        )
        cities.append(node)
        connectNode(node, state, "estado")
    return node

def createParty(data):
    node = parties.find(data.get("SIGLA_PARTIDO"))
    if not node:
        node = createNode(
            type="partido",
            nome=data.get("NOME_PARTIDO"),
            sigla=data.get('SIGLA_PARTIDO'),
            numero=data.get("NUMERO_PARTIDO"),
        )
        parties.append(node)
    return node

def createBloc(data):
    node = blocs.find(data.get("CODIGO_LEGENDA"))
    if not node:
        node = createNode(
            type="coligação",
            nome=data.get("NOME_LEGENDA"),
            codigo=data.get("CODIGO_LEGENDA"),
            sigla=data.get("SIGLA_LEGENDA"),
            composicao=data.get("COMPOSICAO_LEGENDA"),
        )
        blocs.append(node)
    return node

if __name__ == "__main__":
    with open("tse/cand_2012.json") as f:
        index = 0
        for line in f:
            index += 1
            print(index)
            obj = json.loads(line)
            createPersonNode(obj)
    import pdb;pdb.set_trace()
    with open("tse/output_graph.json", "w") as f:
        for category in (people, candidatures, posts, jobs, states, cities, parties, blocs):
            for obj in category:
                txt = json.dumps(obj)
                f.writeln(txt)

# Coligação {
#     "NOME_LEGENDA": "PARTIDO ISOLADO",
#     "CODIGO_LEGENDA": "230000000007",
#     "COMPOSICAO_LEGENDA": "PRP",
#     "SIGLA_LEGENDA": "#NULO#",
# }

# Partido {
#     "NOME_PARTIDO": "PARTIDO REPUBLICANO PROGRESSISTA",
#     "NUMERO_PARTIDO": "44",
#     "SIGLA_PARTIDO": "PRP",
# }

# Local {
#     "DESCRICAO_UE": "RORAIMA",
#     "SIGLA_UE": "RR"
#     "SIGLA_UF": "RR",
# }

# Local_Nascimento {
#     "SIGLA_UF_NASCIMENTO": "PA",
#     "CODIGO_MUNICIPIO_NASCIMENTO": "-3",
#     "NOME_MUNICIPIO_NASCIMENTO": "ITAITUBA",
# }

# Ocupação {
#     "CODIGO_OCUPACAO": "176",
#     "DESCRICAO_OCUPACAO": "COZINHEIRO",
# }

# Cargo {
#     "CODIGO_CARGO": "7",
#     "DESCRICAO_CARGO": "DEPUTADO ESTADUAL",
# }

# Pessoa {
#     "CODIGO_COR_RACA": "03",
#     "CODIGO_NACIONALIDADE": "1",
#     "CODIGO_SEXO": "4",
#     "CPF_CANDIDATO": "72967625272",
#     "DATA_NASCIMENTO": "26/10/1983",
#     "DESCRICAO_COR_RACA": "PARDA",
#     "DESCRICAO_NACIONALIDADE": "BRASILEIRA NATA",
#     "DESCRICAO_SEXO": "FEMININO",
#     "NOME_CANDIDATO": "ELIETE SOUSA DE OLIVEIRA",
#     "NUM_TITULO_ELEITORAL_CANDIDATO": "044514191309",
# }

# Candidatura {
#     "ANO_ELEICAO": "2014",
#     "DES_SITUACAO_CANDIDATURA": "DEFERIDO",
#     "DESC_SIT_TOT_TURNO": "SUPLENTE",
#     "DESCRICAO_ELEICAO": "Elei\u00e7\u00f5es Gerais 2014",
#     "DESCRICAO_ESTADO_CIVIL": "SOLTEIRO(A)",
#     "DESCRICAO_GRAU_INSTRUCAO": "L\u00ca E ESCREVE",
#     "DESPESA_MAX_CAMPANHA": "1000000",
#     "IDADE_DATA_ELEICAO": "30",
#     "NM_EMAIL": "ELIETEOLIVEIRA@HOTMAIL.COM",
#     "NOME_URNA_CANDIDATO": "DI\u00c9SY",
#     "NUM_TURNO": "1",
#     "NUMERO_CANDIDATO": "44550",
#     "SEQUENCIAL_CANDIDATO": "230000000060",
#     "COD_GRAU_INSTRUCAO": "2",
#     "COD_SIT_TOT_TURNO": "5",
#     "COD_SITUACAO_CANDIDATURA": "2",
#     "CODIGO_ESTADO_CIVIL": "1",
# }
