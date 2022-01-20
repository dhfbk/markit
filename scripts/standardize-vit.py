import argparse
import re

parser = argparse.ArgumentParser(description="Extract texts from Moro's documents.")
parser.add_argument("input_file", help="Input CONLL file")
parser.add_argument("output_file", help="Output CONLL file")

args = parser.parse_args()

inputFile = args.input_file
outputFile = args.output_file

f = open(inputFile, "r")
fw = open(outputFile, "w")

for line in f:
	line = line.strip()

	line = re.sub(r"\tdel\tDET\tDI\t", r"\tdei\tDET\tRI\t", line)
	line = re.sub(r"(\tessere)\tAUX\tVA\t(.*\tcop\t)", r"\1\tAUX\tV\t\2", line)

	fw.write(line)
	fw.write("\n")

fw.close()
f.close()
