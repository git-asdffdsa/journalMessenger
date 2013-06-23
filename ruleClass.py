import re
import sys

#a list containing all valid commands which can be part of a value
COMMANDLIST = [
	'read',
	'regex',
	'cutl',
	'cutr',
	'dns',
	'rdns'
]

class rule:
	"""
	a class containing a rule which consists of
	-on what this rule applies
	-how to deal with output that this rule applies to
	how a rule is built:
	name='name'
	values|
	      |'value1':|
	      |         |'command 1'
	      |         |'command 2'
	      |         |...
	      |
	      |'value2':|
	      |         |'command 1'
	      |         |...
	      |...

	filters|
	       |'field1':'value'
	       |'field2':'value2'
	       |....

	output='output'
	surpress=True/False
	"""
	name = ''
	values = {}
	filters = {}
	output = ''
	surpress= False
	def readDict(self, name, ruleDict):
		if 'values' in ruleDict:
			self.values = ruleDict['values']
		if 'filters' in ruleDict:
			self.filters = ruleDict['filters']
		if 'output' in ruleDict:
			self.output = ruleDict['output']
		self.name = name
	#check if all values consist of valid commands
	def isValid(self):
		for value in self.values:
			for command in self.values[value]:
				if not command in COMMANDLIST and not command[: command.find(' ')] in COMMANDLIST:
					return False
		return True
	#checks wether its filter are okay for this outputDict
	def doesApply(self, outputDict):
		#for every entry in filter
		for field in self.filters:
			if field in outputDict:
				testField = str(outputDict[field])
			else:
				#if the output to be tested does not have this entry, set it to blank
				testField = ''
			if not re.match(self.filters[field],testField):
				return False
		return True
	#applies the rule and returns the formatted output
	def applyRule(self, outputDict):
		if self.surpress:
			return
		#first, evaluate the values
		#a dict containing the strings the values got in the end
		valueStrings = {}
		for valueName in self.values:
			valueStrings[valueName] = ''
			for command in self.values[valueName]:
				#read from a field
				if command[:command.find(' ')] == 'read':
					try:
						valueStrings[valueName] = outputDict[command[command.find(' ') + 1 :]]
					#this field was not find - make this value empty
					except KeyError:
						valueStrings[valueName] = ''
				#apply regex operation
				elif command[:command.find(' ')] == 'regex':
					try:
						#always take the first hit
						valueStrings[valueName] = re.search(command[command.find(' ') + 1 :], valueStrings[valueName]).group(0)
					#this regex does not exist in here - make this value empty
					except AttributeError:
						valueStrings[valueName] = ''
				#cut the part from the left until character number _n_
				#so only take the part on the right of _n_
				elif command[:command.find(' ')] == 'cutl':
					valueStrings[valueName] = valueStrings[valueName][int(command[command.find(' ') + 1]):]
				#cut the part from the right from character number _n_
				#so only take the part on the left of _n_
				elif command[:command.find(' ')] == 'cutr':
					valueStrings[valueName] = valueStrings[valueName][:int(command[command.find(' ') + 1])]
				#dns request: get host by name... takes name, outputs its ip
				elif command == 'dns':
					valueStrings[valueName] = socket.gethostbyname(valueStrings[valueName])
				#rdns request: get host by ip addr... takes ip, outputs the name
				elif command == 'rdns':
					valueStrings[valueName] = socket.gethostbyaddr(valueStrings[valueName])
				else:
					sys.stderr.write('Error: rule "' + self.name + '": command "' + command + '" does not exist.\n')
					valueStrings[valueName] = ''
		return self.output.format(**valueStrings)
