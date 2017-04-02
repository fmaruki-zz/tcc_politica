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
traindata2 = traindata + [[(w, simplify_to_universal_tag(t, reverse=True)) for (w, t) in sent] for sent in dataset2]
shuffle(traindata)
shuffle(traindata2)

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

tagger = nltk.BigramTagger(
            traindata, backoff=nltk.RegexpTagger(
                regex_patterns, backoff=nltk.UnigramTagger(
                    traindata2, backoff=nltk.AffixTagger(
                        traindata2, backoff=nltk.DefaultTagger('NOUN')
                    )
                )
            )
        )
templates = nltk.brill.fntbl37()
tagger = nltk.BrillTaggerTrainer(tagger, templates)
tagger = tagger.train(traindata, max_rules=100)

with open("tagger.pkl", "wb") as f:
    pickle.dump(tagger, f)



""" testando os modelos 

results = []
dataset_len = len(dataset) / 5
for i in range(5):
    test = dataset[i * dataset_len: (i+1) * dataset_len]
    traindata = [[(w, simplify_to_universal_tag(t)) for (w, t) in sent] for sent in dataset[: i * dataset_len] + dataset[(i+1) * dataset_len:]]
    # traindata2 = traindata + [[(w, simplify_to_universal_tag(t, reverse=True)) for (w, t) in sent] for sent in dataset2]
    shuffle(traindata)
    # shuffle(traindata2)
    tagger = nltk.BigramTagger(
                traindata, backoff=nltk.RegexpTagger(
                    regex_patterns, backoff=nltk.UnigramTagger(
                        traindata2, backoff=nltk.AffixTagger(
                            traindata2, backoff=nltk.DefaultTagger('NOUN')
                        )
                    )
                )
            )
    print "trained"
    total = 0
    correct = 0
    for test_sentence in test:
        prev = set(tagger.tag([w for w,t in test_sentence]))
        orig = set([(w, simplify_to_universal_tag(t)) for w,t in test_sentence])
        total += len(prev | orig)
        correct += len(prev & orig)
    results.append(correct * 1.0 / total)
    print results


results = []
train = dataset1
test = dataset2
traindata = [[(w, simplify_to_universal_tag(t)) for (w, t) in sent] for sent in train]
tagger = nltk.BigramTagger(
            traindata, backoff=nltk.UnigramTagger(
                traindata, backoff=nltk.AffixTagger(
                    traindata, backoff=nltk.DefaultTagger('NOUN')
                )
            )
        )
total = 0
correct = 0
for test_sentence in test:
    prev = set(tagger.tag([w for w,t in test_sentence]))
    orig = set([(w, simplify_to_universal_tag(t)) for w,t in test_sentence])
    total += len(prev | orig)
    correct += len(prev & orig)


results.append(correct * 1.0 / total)


[0.9390943246984378, 0.942435916432064, 0.9438245677326256, 0.9462862204226243, 0.947024054113854]



-- treinando apenas com o dataset1
- 4-gram
[0.8549612423064047, 0.8489808849931355, 0.8560790113024189, 0.8518394562726875, 0.8494448326733443]
- unigram
[0.8336324019482184, 0.8291682011890357, 0.8356178799757952, 0.828728008399703, 0.8301248967795211]
- BIGRAM
[0.8566052326330713, 0.8524603174603175, 0.8582385612271886, 0.8534724906584203, 0.8518969943725526]
- trigram
[0.8564654950265422, 0.8510137725025774, 0.8577923451046733, 0.8536830443408137, 0.8512760720300557]
- 5-gram
[0.853349799320778, 0.8479092468012136, 0.8539814839237201, 0.8505324347960286, 0.8480459353904249]
- bigram + affix
[0.886468027799822, 0.8862802465286937, 0.8942042087288433, 0.889765956139812, 0.8970955123664028]
- bigram + affix - unigram e affix treinados com o dataset2
[0.9002713046848505, 0.9065151001017985, 0.9120174393551495, 0.916549855153724, 0.9221455986519799]
[0.9177255911211195, 0.9189894532931554, 0.9154775265886377, 0.91157364802685, 0.9115104209014283]
- unigram + affix
[0.8730581564024792, 0.876506901942082, 0.8718798495489097, 0.8708808068948956, 0.8737796560301709]

-- BrillTagger dataset1
- max_rules 10 fntbl37
[0.9096734573999412, 0.9094219390077378, 0.9067088742285593, 0.9044331787293711, 0.9060094530722484]
- max_rules 20 fntbl37
[0.9105178857447944, 0.9106243975581022, 0.9083867876819888, 0.9063705782358814, 0.9077076914761364]

- max_rules 10 fntbl37 - dataset2 no afix e unigram
[0.9098276869158879, 0.9161210232943067, 0.9226653076825073, 0.9259827721221613, 0.9336202563458156]
- max_rules 20 fntbl37 - dataset2 no afix e unigram
[0.9119444782661634, 0.9188352826510722, 0.9245499515528584, 0.9278279408076248, 0.9357079979879276]



COMP 0.8545347192

-- treinando apenas com o dataset2
[0.8244514974258668, 0.8231992602441011, 0.8238641655645176, 0.8249829980875701, 0.8235258774483977]
- 5-gram
[0.818807931155214, 0.8231131645615761, 0.8197315721804441, 0.8185663462681653, 0.8202137373755913]
- 4-gram
[0.8224372590669499, 0.826523700998563, 0.8250096426861968, 0.8223538595766176, 0.823589322911866]
- trigram
[0.8218114071471936, 0.8255025563027982, 0.8252144864422236, 0.8204522583046517, 0.8250141895352754]
- bigram
[0.8271867479993285, 0.8296216425441325, 0.8269328014383639, 0.8256193834393019, 0.8272896953263564]
- unigram
[0.7986425968679591, 0.8005293209947205, 0.7999525137454085, 0.7989167199716525, 0.7995909076217697]

-- treinando com os 2 datasets
[0.8125999273957473, 0.8154706974896913, 0.8131708766251534, 0.8141792896013892, 0.8134858579704859]
- bigram
[0.8187679390803475, 0.8201240172825095, 0.8199141792952633, 0.8204233926397235, 0.8172831981496241]
- unigram
[0.7966660439338035, 0.797680865185648, 0.7970487219352489, 0.7967654522775173, 0.796123916277838]
- bigram + affix
[0.8326760807279368, 0.8341907946949267, 0.833355130964129, 0.8338319561845062, 0.831164382213157]
- unigram + affix
[0.8097319632895165, 0.811215659124524, 0.8098207418801396, 0.8094516156978255, 0.8094576672866101]

-- treino com dataset1, teste com dataset2
- 4-gram
0.6626492433193021
- trigram
0.6632627610405653
- bigram
0.6639576172702324
- unigram
0.6612423866263804
- bigram + affix
0.6818939969833052

-- treino com dataset2, teste com dataset1
- 4-gram
0.616106192300248
- trigram
0.6030596388447318
- bigram
0.6283029545184874
- unigram
0.6809573895951226
- bigram + affix
0.6385013180978975


0.8273300541494966
xxx = [sen for sen in dataset if len([(w,t) for w,t in sen if simplify_to_universal_tag(t) == "X"]) == 0]
"""
