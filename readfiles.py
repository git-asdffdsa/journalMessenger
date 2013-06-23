import json
import re
import sys

#local module
import ruleClass

#read rules out of a json formatted file
def readrules (f, rules):
	ruleJson = json.loads(f.read())
	for rule in ruleJson:
		currentRule = ruleClass.rule()
		#rule is the name, ruleJson[rule] is the dict
		currentRule.readDict(rule,ruleJson[rule])
		if currentRule.isValid():
			rules.append(currentRule)
		else:
			sys.stderr.write('Error: rule ' + rule + ' contains invalid commands. Rule will be skipped.\n')

#set surpression status for every rule whichs name matches 'ruleMatch' to 'surpress'
def setSurpression(entryName, surpress, rules):
	for rule in rules:
		if re.match(entryName, rule.name):
			rule.surpress = surpress
#read a profile
def readprofile(f, rules):
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
				setSurpression(inLine.strip(), surpression, rules )
		elif line[:9] == 'surpress ':
			setSurpression(line[9:], True, rules)
		elif line[:11] == 'nosurpress ':
			setSurpression(line[11:], False, rules)
