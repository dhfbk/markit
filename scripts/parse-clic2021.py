import math

testPercent = 0.1
testMin = 2

sentencesByType = {}
sbagliate = 0
giuste = 0

convert = {}
convert["C'È PRESENTATIVO"] = "C_E_PRESENTATIVO"
convert["C'É PRESENTATIVO"] = "C_E_PRESENTATIVO"

convert["DISLOCAZIONI (Destra)"] = "DISLOCAZIONI_DX"
convert["DISLOCAZIONI (Sinistra)"] = "DISLOCAZIONI_SX"

convert["DISLOCAZIONI (Tema_sospeso)"] = "TEMA_SOSPESO"
convert["DISLOCAZIONI (Tema sospeso_Anacoluto)"] = "TEMA_SOSPESO"

convert["SOGGETTO POSTVERBALE"] = "SOGGETTO_POSTVERBALE"

convert["RELATIVA_IMPLICITA"] = "ALTRO" # "RELATIVA_IMPLICITA"
convert["RELATIVA_ESPLICITA"] = "ALTRO" # "RELATIVA_ESPLICITA"
convert["RELATIVA IMPLICITA"] = "ALTRO" # "RELATIVA_IMPLICITA"
convert["RELATIVA ESPLICITA"] = "ALTRO" # "RELATIVA_ESPLICITA"
convert["RELATIVA _ESPLICITA"] = "ALTRO" # "RELATIVA_ESPLICITA"
convert["RELATIVE_ESPLICITA"] = "ALTRO" # "RELATIVA_ESPLICITA"
convert["RELATOVA_ESPLICITA"] = "ALTRO" # "RELATIVA_ESPLICITA"
convert["FRELATIVA_ESPLICITA"] = "ALTRO" # "RELATIVA_ESPLICITA"
convert["RELATIVA SEMPLICE"] = "ALTRO" # "RELATIVA_ESPLICITA"
convert["RELATIVA_SEMPLICE"] = "ALTRO" # "RELATIVA_ESPLICITA"
convert["FRASI_SCISSE (rel)"] = "ALTRO" # "RELATIVA_ESPLICITA"

convert["DISLOCAZIONI"] = "ALTRO"
convert["DISLOCAZIONI x"] = "ALTRO"
convert["DISLOCAZIONI (passivo)"] = "ALTRO"
convert["PASSIVO"] = "ALTRO"
convert["PASSIVO"] = "ALTRO"
convert[""] = "ALTRO"

buffer = []
sentences = []

with open("original.conllu") as f:
    for line in f:
        line = line.strip()
        if line == "":
            if len(buffer) > 0:
                sentences.append(buffer)
                buffer = []
                sentenceType = ""
        else:
            buffer.append(line)

over1000 = False
for sentence in sentences:
    skip = False
    sentenceType = ""
    text = ""

    for line in sentence:
        if line.startswith("#"):
            line = line[1:].strip()
            if line == "1000":
                over1000 = True
            if line.startswith("sbagliat"):
                skip = True
            if line.startswith("text"):
                line = line[4:]
                line = line.replace("=", "")
                line = line.strip()
                text = line
            if line.startswith("type"):
                line = line[4:]
                line = line.replace("=", "")
                line = line.replace("24_", "")
                line = line.replace("25_", "")
                line = line.strip()
                sentenceType = line
                if sentenceType in convert:
                    sentenceType = convert[sentenceType]

    if skip:
        sbagliate += 1
        continue

    if sentenceType not in sentencesByType:
        sentencesByType[sentenceType] = []

    if not over1000 or sentenceType == "TEMA_SOSPESO" or sentenceType == "DISLOCAZIONI_DX":
        giuste += 1
        sentencesByType[sentenceType].append(sentence)

train = {}
dev = {}
test = {}
for k in sentencesByType:
    train[k] = []
    test[k] = []
    dev[k] = []
    testSize = math.ceil(len(sentencesByType[k]) * testPercent)
    testSize = max(testSize, testMin)

    i = 0
    for s in sentencesByType[k]:
        if i < testSize:
            test[k].append(s)
        elif i < (testSize * 2):
            dev[k].append(s)
        else:
            train[k].append(s)

        i += 1

    print(k, len(sentencesByType[k]), len(train[k]), len(test[k]), len(dev[k]))

with open("train.conll", "w") as fw:
    for k in train:
        for s in train[k]:
            fw.write("\n".join(s))
            fw.write("\n\n")

with open("test.conll", "w") as fw:
    for k in test:
        for s in test[k]:
            fw.write("\n".join(s))
            fw.write("\n\n")

with open("dev.conll", "w") as fw:
    for k in dev:
        for s in dev[k]:
            fw.write("\n".join(s))
            fw.write("\n\n")

print("Giuste: ", giuste)
print("Sbagliate: ", sbagliate)
