import re

def readrules(f, emptyList, argList, allFilters, allValues, allValueNames, allOutput, allSurpress, allNames):
	for name in f:
		values = []
		valueNames = []
		output = ""
		surpress = False
		filters = emptyList[:]
		for comesNext in f:
			comesNext = comesNext.strip()
			if comesNext == "}":
				break
			if comesNext == "output{":
				output = f.readline().strip()
				f.readline()
			elif comesNext == "filter{":
				for line in f:
					if line.strip() == "}":
						break
					arg = line.strip()[:line.find("=") - 2]
					value = line.strip()[line.find("=") - 1:]
					if value[0] == '"' and value[-1:] == '"':
						value = value[1:-1]
					try:
						filters[argList.index(arg)] = value
					except ValueError:
						argList.append(arg)
						filters.append(value)
						emptyList.append(0)
			elif comesNext == "values{":
				for value in f:
					if value.strip() == "}":
						break
					if value.strip()[-1:] != "{":
						raise ValueError
					valueNames.append(value.strip()[:-1])
					commandList = []
					for command in f:
						if command.strip() == "}":
							break
						commandList.append(command.strip())
					values.append(commandList)
			elif comesNext == "surpress":
				surpress = True
			else:
				print(comesNext)
				raise ValueError
		allFilters.append(filters)
		allValues.append(values)
		allValueNames.append(valueNames)
		allOutput.append(output)
		allSurpress.append(surpress)
		allNames.append(name[:-2])
def setSurpression(entryName, surpress, allNames, allSurpress):
	i = 0
	for name in allNames:
		if re.match(entryName, name):
			allSurpress[i] = surpress
		i += 1
def readprofile(f, allNames, allSurpress):
	for line in f:
		line = line.strip()
		if line[-1:] == '{':
			if line[:-1] == "surpress":
				surpression = True
			elif line[:-1] == "nosurpress":	
				surpression = False
			else:
				raise ValueException
			for inLine in f:
				if inLine.strip() == '}':
					break
				setSurpression(inLine.strip(), surpression, allNames, allSurpress)
		elif line[:9] == 'surpress ':
			setSurpression(line[9:], True, allNames, allSurpress)
		elif line[:11] == 'nosurpress ':
			setSurpression(line[11:], False, allNames, allSurpress)
