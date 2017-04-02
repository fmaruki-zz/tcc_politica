import yaml
from collections import defaultdict
import os
import re
import nltk
import pickle

tagger = pickle.load(open("tagger.pkl"))
portuguese_sent_tokenizer = nltk.data.load("tokenizers/punkt/portuguese.pickle")

def extract_entity_names(t):
    entity_names = []
    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))
    return entity_names

def chunk_sent(words):
    res = []
    len_words = len(words)
    for index_start in xrange(len_words):
        word = words[index_start]
        if word[1] != "NOUN":
            continue
        res.append(word[0])
        this_chunk = word[0]
        last_was_adp = False
        for index_next in xrange(index_start+1, len_words):
            word = words[index_next]
            this_chunk += " " + word[0]
            pos_tag = word[1]
            if pos_tag == "ADJ":
                res.append(this_chunk)
                break
            elif pos_tag == "NOUN":
                res.append(this_chunk)
                last_was_adp = False
                continue
            elif pos_tag == "ADP":
                if last_was_adp:
                    break
                last_was_adp = True
                continue
            else:
                break
    return res

def extract_entities(text, tagger):
    text = re.sub(r"\.\s*\.", ".",text)
    entities = []
    all_tags = []
    pattern = re.compile(r'[^\w_-]+', re.UNICODE)
    chunker = nltk.RegexpParser(" NE: {<NOUN><ADP|NOUN>*<NOUN><ADJ>?}\n{<NOUN>+<ADJ>?} ")
    # chunker2 = nltk.RegexpParser(" NE: {<NOUN>+<ADP>*<NOUN>*<ADP>*<NOUN>+<ADJ>?}\n{<NOUN>+<ADJ>?} ")
    sentences = portuguese_sent_tokenizer.tokenize(text)
    for sentence in sentences:
        tokens = nltk.word_tokenize(sentence)
        tokens = [re.sub(pattern, "", word) for word in tokens]
        tokens = ["," if a == "" else a for a in tokens]
        tags = tagger.tag(tokens)
        # chunks = chunker.parse(tags)
        # entities.extend(extract_entity_names(chunks))
        entities.extend(chunk_sent(tags))
        all_tags.extend(tags)
    entities = filter(lambda e: e.strip(), entities)
    return (entities, all_tags)

registries = []
configs = yaml.load(open("config.yaml").read())
for config in configs:
    partido = config['partido']
    sigla = config['sigla']
    files = os.listdir("text/" + config['sigla'])
    for filename in files:
        with open("text/" + config['sigla'] + "/" + filename) as f:
            text = f.read().decode("utf-8")
        entities, tags = extract_entities(text, tagger)
        for entity in entities:
            registries.append((sigla, filename, entity))
    pass

pickle.dump(registries, open("registries.pkl", "wb"))
