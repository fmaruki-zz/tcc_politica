import pickle
import math
from collections import defaultdict
registries = pickle.load(open("registries.pkl")) # (partido, document, term)

relevancia = defaultdict(dict)
dict_partido_by_term = defaultdict(lambda: defaultdict(set))
partidos = set()
qtd_doc_by_partido = defaultdict(int)
for partido, doc, term in registries:
    partidos.add(partido)
    dict_partido_by_term[term][partido].add(doc)
    qtd_doc_by_partido[partido] += 1

qtd_partidos = len(partidos)
for term, dict_doc_by_partido in dict_partido_by_term.items():
    qtd_partidos_by_term = len(dict_doc_by_partido.keys())
    if qtd_partidos_by_term <= 1:
        # eliminando termos que so existem em um partido, geralmente e sujeira do html
        continue
    idf = math.log(qtd_partidos / qtd_partidos_by_term)
    for partido, docs in dict_doc_by_partido.items():
        tf = (1 + math.log(len(docs))) / qtd_doc_by_partido[partido]
        tfidf = tf * idf
        relevancia[partido][term] = tfidf

pickle.dump(relevancia, open("relevancia.pkl", "wb"))
