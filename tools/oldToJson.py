#!  /usr/bin/python

import sys
import os
import argparse
import json

helpOutput = '''
Usage:
 oldToJson [options] /path/to/oldRules/
Options:
 -h, --help             display this output
 -a, --append <ending>  append .<ending> to every file
 -p, --path <path>      store json files to <path>
 -f, --force            do not ask before overwriting existing files
 -u, --ugly             output non-fancy, but short json
'''


def tryLineOpens(line):
	if not line[-1:] == "{":
		raise Exception('Unexpected "' + line + '": expected to end with "{"')
def tryIsFilter(line):
	if not '=' in line:
		raise Exception('Unexpected "' + line + '": expected to contain a "="')
	if not line[line.find('=') + 1 : line.find('=') + 2] == '"' and line[-1:] == '"':
		raise Exception('Unexpected "' + line + '": part after "=" is expected to end and start with \'"\'')


#this function will read a file into list/dictionary structure
def readFile(f):
	#dictionary: 'RULENAME : RULECONTENT'
	listOfRules = {}
	for line in f:
		line = line.strip()
		tryLineOpens(line)
		name = line[:-1]
		#dictionary: 'VALUENAME : LIST OF ORDERS'
		values = {}
		#dictionary: 'FIELD : VALUE'
		filters = {}
		output = ''
		for line in f:
			line = line.strip()
			if line == '}':
			#this rule ends now
				rule = {'output' : output, 'filters' : filters, 'values' : values}
				listOfRules[name] = rule
				break
			tryLineOpens(line)
			if line == 'values{':
				#now all the values come
				for line in f:
					line = line.strip()
					if line == '}':
						break
					tryLineOpens(line)
					valueName = line[:-1]
					listOfCommands = []
					#now a list of commands comes
					for line in f:
						line = line.strip()
						if line	== '}':
							#this value ends now
							values[valueName] = listOfCommands
							break
						listOfCommands.append(line)
			elif line == 'filter{':
				#now all the filters come
				for line in f:
					line = line.strip()
					if line == '}':
						break
					tryIsFilter(line)
					filters[line[:line.find('=')]] = line[line.find('=') + 2 : -1]
			elif line == 'output{':
				for line in f:
					line = line.strip()
					if line == '}':
						break
					if output == '':
						output = line
					else:
						output = output + '\n' + line
			else:
				raise Exception('Unexpected "' + line + '": should be either "values{", "filter{", or "output{"')
	return listOfRules

#removes quotes from certain commands, e.g. 'regex ".*"' will be formatted to 'regex .*', as they are not necessary in json
def remQuot(listOfRules):
	for rule in listOfRules:
		print(str(rule))
		for value in listOfRules[rule]['values']:
			i=0
			for command in listOfRules[rule]['values'][value]:
				#the command itself
				firstPart = command[: command.find(' ')]
				#the argument for the command
				secondPart = command[command.find(' ') + 1 :]
				if secondPart[:1] == '"' and secondPart[-1:] == '"':
					if firstPart == "regex":
						secondPart = secondPart[1:-1]
				listOfRules[rule]['values'][value][i] = firstPart + " " + secondPart
				i += 1
	return listOfRules
#change one single file
def changeFile(inputFile, outputFile, makeFancy, force):
	if not force and os.path.exists(outputFile):
		print("The file " + outputFile + " does already exist. Overwrite? (Y/N)")
		if not sys.stdin.read(1) in 'yY':
			return False
	try:
		listOfRules = readFile(open(inputFile))
	except Exception as output:
		sys.stderr.write('Reading file ' + inputFile + ' not successfull:\n' + output.args[0] + ', file has not been changed\n')
		return False
	listOfRules = remQuot(listOfRules)
	if makeFancy:
		text = json.dumps(listOfRules, indent=4, separators=(',', ': '))
	else:
		text = json.dumps(listOfRules)
	f = open(outputFile, 'w')
	f.write(text)
	return True
#change all files in dir
def changeFiles(inputPath, outputPath, makeFancy, force, appendString):
	dirList = os.listdir(inputPath)
	for fileName in dirList:
		inputFile = inputPath + "/" + fileName
		outputFile = outputPath + "/" + fileName + appendString
		changeFile(inputFile, outputFile, makeFancy, force)
	return True
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('inputPath', help="the path to a directory containing rules or to a single rulesfile")
	parser.add_argument('-a', '--append', metavar = 'ENDING', help='append ending to every file')
	parser.add_argument('-p', '--path', help='store json files to path.')
	parser.add_argument('-f', '--force', help='do not ask before overwriting existing files', action='store_true')
	parser.add_argument('-u', '--ugly', help='output non-fancy but short json', action='store_true')
	args = parser.parse_args()
	#by default save to same dir
	outputPath = args.inputPath
	if args.path:
		outputPath = args.path
	outputPath = os.path.abspath(outputPath)
	inputPath = os.path.abspath(args.inputPath)
	append = ''
	if args.append:
		append = args.append
	#make some checks
	if not os.path.exists(inputPath):
		sys.stderr.write('Error: inputPath does not exist\n')
		return False
	if not os.path.isdir(outputPath):
		sys.stderr.write('Error: path is not an existing directory\n')
	if os.path.isdir(inputPath):
		return changeFiles(inputPath, outputPath, not args.ugly, args.force, append)
	elif os.path.isfile(inputPath):
		return changeFile(inputPath, outputPath + os.path.basename(inputPath) + append, not args.ugly, arg.force)
	else:
		sys.stderr.write('Error: inputPath is neighter directory not file\n')
		return False

main()
