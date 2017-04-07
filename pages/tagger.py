import nltk
import pickle
from string import punctuation
from random import shuffle

def simplify_to_universal_tag(t, reverse=False):
    tagmap = {
        'n': "NOUN",
        'num': "NUM",
        'v-fin': "VERB",
        'v-inf': "VERB",
        'v-ger': "VERB",
        'v-pcp': "VERB",
        'pron-det': "PRON",
        'pron-indp': "PRON",
        'pron-pers': "PRON",
        'art': "DET",
        'adv': "ADV",
        'conj-s': "CONJ",
        'conj-c': "CONJ",
        'conj-p': "CONJ",
        'adj': "ADJ",
        'ec': "PRT",
        'pp': "ADP",
        'prp': "ADP",
        'prop': "NOUN",
        'pro-ks-rel': "PRON",
        'proadj': "PRON",
        'prep': "ADP",
        'nprop': "NOUN",
        'vaux': "VERB",
        'propess': "PRON",
        'v': "VERB",
        'vp': "VERB",
        'in': "X",
        'prp-': "ADP",
        'adv-ks': "ADV",
        'dad': "NUM",
        'prosub': "PRON",
        'tel': "NUM",
        'ap': "NUM",
        'est': "NOUN",
        'cur': "X",
        'pcp': "VERB",
        'pro-ks': "PRON",
        'hor': "NUM",
        'pden': "ADV",
        'dat': "NUM",
        'kc': "ADP",
        'ks': "ADP",
        'adv-ks-rel': "ADV",
        'npro': "NOUN",
    }
    if t in ["N|AP","N|DAD","N|DAT","N|HOR","N|TEL"]:
        t = "NUM"
    if reverse:
        if "|" in t: t = t[0:t.index("|")]
    else:
        if "+" in t: t = t[t.index("+")+1:]
        if "|" in t: t = t[t.index("|")+1:]
        if "#" in t: t = t[0:t.index("#")]
    t = t.lower()
    return tagmap.get(t, "." if all(tt in punctuation for tt in t) else t)

dataset1 = list(nltk.corpus.floresta.tagged_sents())
dataset2 = [[w[0] for w in sent] for sent in nltk.corpus.mac_morpho.tagged_paras()]
traindata = [[(w, simplify_to_universal_tag(t)) for (w, t) in sent] for sent in dataset1]
traindata = traindata + [[(w, simplify_to_universal_tag(t, reverse=True)) for (w, t) in sent] for sent in dataset2]
shuffle(traindata)

regex_patterns = [
    (r"^[nN][ao]s?$", "ADP"),
    (r"^[dD][ao]s?$", "ADP"),
    (r"^[pP]el[ao]s?$", "ADP"),
    (r"^[nN]est[ae]s?$", "ADP"),
    (r"^[nN]um$", "ADP"),
    (r"^[nN]ess[ae]s?$", "ADP"),
    (r"^[nN]aquel[ae]s?$", "ADP"),
    (r"^\xe0$", "ADP"),
]


tagger = nltk.RegexpTagger(regex_patterns,
        backoff = nltk.NgramTagger(10, traindata,
        backoff = nltk.NgramTagger(9, traindata,
        backoff = nltk.NgramTagger(8, traindata,
        backoff = nltk.NgramTagger(7, traindata,
        backoff = nltk.NgramTagger(6, traindata,
        backoff = nltk.NgramTagger(5, traindata,
        backoff = nltk.NgramTagger(4, traindata,
        backoff = nltk.NgramTagger(3, traindata,
        backoff = nltk.NgramTagger(2, traindata,
        backoff=nltk.UnigramTagger(traindata,
        backoff=nltk.AffixTagger(traindata, affix_length=-4,
        backoff=nltk.DefaultTagger("NOUN")
        ))))))))))))

templates = nltk.brill.fntbl37()
tagger = nltk.BrillTaggerTrainer(tagger, templates)
tagger = tagger.train(traindata, max_rules=100)

with open("tagger_2.pkl", "wb") as f:
    pickle.dump(tagger, f)

