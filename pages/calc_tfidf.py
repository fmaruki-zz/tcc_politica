import pickle
import re
import math
from collections import defaultdict
from nltk.stem.snowball import PortugueseStemmer
stemmer = PortugueseStemmer()
registries = pickle.load(open("registries.pkl")) # (partido, document, term)

stem_counter = defaultdict(lambda: defaultdict(int))

relevancia = defaultdict(dict)
dict_partido_by_term = defaultdict(lambda: defaultdict(set))
partidos = set()
qtd_doc_by_partido = defaultdict(int)
for partido, doc, term in registries:
    partidos.add(partido)
    stem = stemmer.stem(term)
    stem_counter[stem][term] += 1
    dict_partido_by_term[stem][partido].add(doc)
    qtd_doc_by_partido[partido] += 1

stem_to_term = {}
for stem, counter_dict in stem_counter.items():
    counter_list = counter_dict.items()
    counter_list.sort(key=lambda a: -a[1])
    term = counter_list[0][0]
    stem_to_term[stem] = term

qtd_partidos = len(partidos)
for stem, dict_doc_by_partido in dict_partido_by_term.items():
    term = stem_to_term[stem]
    num_words = len(re.sub(r"\S+", "", term)) + 1
    fator = math.log(2*num_words) / 1.2 ** (num_words - 1)
    qtd_partidos_by_term = len(dict_doc_by_partido.keys())
    if qtd_partidos_by_term <= 1:
        # eliminando termos que so existem em um partido, geralmente e sujeira do html
        continue
    idf = math.log(qtd_partidos / qtd_partidos_by_term)
    for partido, docs in dict_doc_by_partido.items():
        tf = (1 + math.log(len(docs))) / qtd_doc_by_partido[partido]
        tfidf = fator * tf * idf
        relevancia[partido][term] = tfidf

pickle.dump(relevancia, open("relevancia.pkl", "wb"))
