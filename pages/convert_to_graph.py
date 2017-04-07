import pickle
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

    def __call__(self, node1, node2, desc, weight=None):
        if node1 and node2:
            self.connections.append((node1[0], node2[0], desc, weight))

    def make_unique(self):
        connection_set = set(self.connections)
        self.connections = []
        for conn in connection_set:
            self.connections.append((conn[0], conn[1], conn[2], conn[3], generateId()))

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
    def __init__(self, nodetype, columns):
        self.array = {}
        self.nodetype = nodetype
        self.index = 0
        self.column_names = columns

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
            node = data[:]
            node.insert(0, generateId())
            self.array[key] = node
        return node

    def print_node(self, node, cOut, cIn):
        id = node[0]
        values = [self.nodetype] + node[1:]
        obj = {
            "id": id,
            "label": "vertex",
            "properties": {name: [{"id": generateId(), "value": value}]
                for name, value in zip(["type"] + self.column_names, node)
            }
        }

        nodes_out = cOut.get(id)
        nodes_in = cIn.get(id)
        if nodes_out:
            obj['outE'] = {}
            for node1, node2, link_name, link_weight, link_id in nodes_out:
                if link_name not in obj['outE']:
                    obj['outE'][link_name] = []
                link = {
                    "id": link_id,
                    "inV": node2,
                }
                if link_weight:
                	link["weight"] = link_weight
                obj['outE'][link_name].append(link)
        if nodes_in:
            obj['inE'] = {}
            for node1, node2, link_name, link_weight, link_id in nodes_in:
                if link_name not in obj['inE']:
                    obj['inE'][link_name] = []
                link = {
                    "id": link_id,
                    "outV": node1,
                }
                if link_weight:
                	link["weight"] = link_weight
                obj['inE'][link_name].append(link)
        return json.dumps(obj)


Partidos = NodeGen("partido", ["sigla", "nome"])
Artigos = NodeGen("artigo", ["titulo"])
Termos = NodeGen("termo", ["nome"])

relevancia = pickle.load(open("relevancia.pkl"))
registries = pickle.load(open("registries.pkl"))

for partido, terms in relevancia.items():
	print partido
	partido_obj = Partidos.create([partido, partido]) # nome, sigla

	terms_tuple = terms.items()
	terms_tuple.sort(key=lambda t: -t[1])
	terms_tuple = terms_tuple[:800]
	terms_list = set()
	for term, weight in terms_tuple:
		termo_obj = Termos.create([term])
		terms_list.add(term)
		connectNode(partido_obj, termo_obj, "termoP", weight)

	this_registries = filter(lambda r: r[0] == partido, registries)
	this_registries = filter(lambda r: r[2] in terms_list, this_registries)
	artigos_list = list(set([r[1] for r in this_registries]))
	print len(artigos_list)

	for artigo in artigos_list:
		artigo_obj = Artigos.create([partido + "/" + artigo])
		connectNode(partido_obj, artigo_obj, "artigo")
		for artigo_term in [r[2] for r in this_registries if r[1] == artigo]:
			weight = terms[artigo_term]
			termo_obj = Termos.create([artigo_term])
			connectNode(artigo_obj, termo_obj, "termoA", weight)
	pass

#### top3 ####

top800 = {}
for partido, kk in relevancia.items():
    kt = kk.items()
    kt.sort(key=lambda a: -a[1])
    kt = kt[:1200]
    top800[partido] = kt

tt800 = defaultdict(set)
for p,v in top800.items():
    for vv in v:
        tt800[p].add(vv[0])

tt = {}
for p,v in tt800.items():
    for pp,vv in tt800.items():
        tt[(p,pp)] = len(v & vv)

top3 = {}
for partido in top800.keys():
    items = filter(lambda a: a[0][0] == partido, tt.items())
    items.sort(key=lambda a: -a[1])
    items = items[1:4]
    for a in items:
        partido2 = a[0][1]
        connectNode(Partidos.create([partido,partido]), Partidos.create([partido2,partido2]), "similar")

########

by1, by2 = connectNode.create_dicts()

with open("output_quads.nq", "w") as f:
	for partido in Partidos.array.values():
		f.write('<P:{}> <sigla> "{}" .\n'.format(partido[0], partido[1]))
		f.write('<P:{}> <tipo> "partido" .\n'.format(partido[0]))
		for partido2 in [r[1] for r in by1[partido[0]] if r[2] == "similar"]:
			f.write("<P:{}> <similar> <P:{}> .\n".format(partido[0], partido2))
	for artigo in Artigos.array.values():
		f.write('<A:{}> <titulo> "{}" .\n'.format(artigo[0], artigo[1]))
		f.write('<A:{}> <tipo> "artigo" .\n'.format(artigo[0]))
		partidos = [r[0] for r in by2[artigo[0]] if r[2] == "artigo"]
		for partido in partidos:
			f.write('<P:{}> <artigo> <A:{}> .\n'.format(partido, artigo[0]))
	for termo in Termos.array.values():
		f.write('<T:{}> <tipo> "termo" .\n'.format(termo[0]))
		f.write('<T:{}> <nome> "{}" .\n'.format(termo[0], termo[1].encode("utf-8")))
		partidos = [r for r in by2[termo[0]] if r[2] == "termoP"]
		artigos = [r for r in by2[termo[0]] if r[2] == "termoA"]
		for partido_ in partidos:
			weight_id = generateId()
			f.write('<P:{}> <peso_termo_partido> <W:{}> .\n'.format(partido_[0], weight_id))
			f.write('<W:{}> <peso> "{}" .\n'.format(weight_id, partido_[3]))
			f.write('<W:{}> <termo_partido> <T:{}> .\n'.format(weight_id, termo[0]))
		for artigo_ in artigos:
			weight_id = generateId()
			f.write('<A:{}> <peso_termo_artigo> <W:{}> .\n'.format(artigo_[0], weight_id))
			f.write('<W:{}> <peso> "{}" .\n'.format(weight_id, artigo_[3]))
			f.write('<W:{}> <termo_artigo> <T:{}> .\n'.format(weight_id, termo[0]))
	pass
