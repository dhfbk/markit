import math
import os
import argparse
import re

parser = argparse.ArgumentParser(description="Extract texts from Moro's documents.")
parser.add_argument("input_file", help="Input CONLL file")
parser.add_argument("output_folder", help="Output folder")
parser.add_argument("conversion_file", help="Conversion TXT file")
parser.add_argument("--test_min", help="Minimum number of sentences in test for each category", type=int, default=2, metavar="NUM")
parser.add_argument("--dev_min", help="Minimum number of sentences in dev for each category", type=int, default=2, metavar="NUM")
parser.add_argument("--test_percent", help="Percentage of sentences for test set", type=float, default=0.1, metavar="NUM")
parser.add_argument("--dev_percent", help="Percentage of sentences for dev set", type=float, default=0.1, metavar="NUM")
parser.add_argument("--default_type", help="Default type label", default="ALTRO", metavar="LABEL")
parser.add_argument("--default_prefix", help="Default UD prefix", default="it_markit-ud-", metavar="PREFIX")
parser.add_argument("-v", "--verbose", help="Display more information", action="store_true")

args = parser.parse_args()

outputFolder = args.output_folder
inputFile = args.input_file
conversionFile = args.conversion_file

verbose = args.verbose

defaultTypeLabel = args.default_type
defaultPrefix = args.default_prefix

testPercent = args.test_percent
devPercent = args.dev_percent
testMin = args.test_min
devMin = args.dev_min

###

if not os.path.exists(outputFolder):
    os.mkdir(outputFolder)

trainFile = os.path.join(outputFolder, defaultPrefix + "train.conll")
testFile = os.path.join(outputFolder, defaultPrefix + "test.conll")
devFile = os.path.join(outputFolder, defaultPrefix + "dev.conll")

posConvert1 = {}
posConvert2 = {}

convert = {}
with open(conversionFile, 'r') as f:
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        convert[parts[0]] = parts[1]

sentencesByType = {}
sbagliate = 0

buffer = []
sentences = []

with open(inputFile) as f:
    for line in f:
        line = line.strip()
        if line == "":
            if len(buffer) > 0:
                sentences.append(buffer)
                buffer = []
                sentenceType = ""
        else:
            buffer.append(line)

sent_id = 0
for sentence in sentences:
    skip = False
    sentenceType = ""
    text = ""
    sentenceInfo = {}
    words = []
    file_id = ""
    count = 0
    count2 = 0

    for line in sentence:
        if line.startswith("#"):
            line = line[1:].strip()
            if line.startswith("sbagliat"):
                skip = True
            if line.startswith("file_id"):
                line = line[7:]
                line = line.replace("=", "")
                line = line.strip()
                file_id = line
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
                if len(sentenceType) == 0:
                    sentenceType = defaultTypeLabel
                if sentenceType in convert:
                    sentenceType = convert[sentenceType]
        else:
            line = line.strip()
            words.append(line)
            count2 += 1
            if re.match(r"^[0-9]+\s", line):
                count += 1

    if skip:
        sbagliate += 1
        continue

    sent_id += 1

    sentenceInfo["text"] = text
    sentenceInfo["words"] = "\n".join(words)
    sentenceInfo["type"] = sentenceType
    sentenceInfo["sent_id"] = sent_id
    sentenceInfo["file_id"] = file_id
    sentenceInfo["count"] = count

    if sentenceType not in sentencesByType:
        sentencesByType[sentenceType] = []

    sentencesByType[sentenceType].append(sentenceInfo)

train = {}
dev = {}
test = {}
count = {}
count['test'] = count['train'] = count['dev'] = 0

for k in sentencesByType:
    train[k] = []
    test[k] = []
    dev[k] = []
    testSize = math.ceil(len(sentencesByType[k]) * testPercent)
    devSize = math.ceil(len(sentencesByType[k]) * devPercent)
    testSize = max(testSize, testMin)
    devSize = max(devSize, devMin)

    i = 0
    for s in sentencesByType[k]:

        txt = ""
        txt += "# text = " + s["text"] + "\n"
        txt += "# sent_id = " + str(s["sent_id"]) + "\n"
        txt += "# file_id = " + s["file_id"] + "\n"
        txt += "# type = " + s["type"] + "\n"
        txt += s["words"] + "\n\n"

        # Global fixes
        txt = re.sub(r"(\tessere)\tVERB\t(.*\tcop\t)", r"\1\tAUX\t\2", txt)
        txt = re.sub(r"(\tstare)\tVERB\t(.*\tcop\t)", r"\tessere\tAUX\t\2", txt)
        txt = re.sub(r"(\tche)\tPRON\t[A-Z]+\t(.*\tmark\t)", r"\1\tSCONJ\tCS\t\2", txt)
        txt = re.sub(r"(\tavere)\tVERB\tV\t(.*\taux\t)", r"\1\tAUX\tVA\t\2", txt)
        txt = re.sub(r"(\tdei\tDET)\t[DR]I\t(.*)\t(case|det)\t", r"\1\tRI\t\2\tdet\t", txt)

        txt = re.sub(r"\tnsubjpass\t", r"\tnsubj:pass\t", txt)
        txt = re.sub(r"\tauxpass\t", r"\taux:pass\t", txt)
        txt = re.sub(r"\tdobj\t", r"\tobj\t", txt)
        txt = re.sub(r"’", r"'", txt)

        for line in txt.split("\n"):
            parts = line.split("\t")
            if len(parts) < 5:
                continue
            if parts[4] == "_":
                continue
            if parts[4] not in posConvert1:
                posConvert1[parts[4]] = set()
            posConvert1[parts[4]].add(parts[3])
            if parts[3] not in posConvert2:
                posConvert2[parts[3]] = set()
            posConvert2[parts[3]].add(parts[4])

        if i < testSize:
            test[k].append(txt)
            count['test'] += s['count']
        elif i < (testSize + devSize):
            dev[k].append(txt)
            count['dev'] += s['count']
        else:
            train[k].append(txt)
            count['train'] += s['count']

        i += 1

    print(k, len(sentencesByType[k]), len(train[k]), len(test[k]), len(dev[k]))

with open(trainFile, "w") as fw:
    for k in train:
        for s in train[k]:
            fw.write(s)

with open(testFile, "w") as fw:
    for k in test:
        for s in test[k]:
            fw.write(s)

if len(dev) > 0:
    with open(devFile, "w") as fw:
        for k in dev:
            for s in dev[k]:
                fw.write(s)

print()
print("Giuste:", sent_id)
print("Sbagliate:", sbagliate)

if verbose:
    print()
    print("Tokens:", count)
    print()
    for k in posConvert1:
        print("%s => %s" % (k, str(posConvert1[k])))
    print()
    for k in posConvert2:
        print("%s => %s" % (k, str(posConvert2[k])))
