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
    description='description'
    """
    name = ''
    values = {}
    filters = {}
    output = ''
    surpress = False
    description = ''

    def readDict(self, name, ruleDict):
        if 'values' in ruleDict:
            self.values = ruleDict['values']
        if 'filters' in ruleDict:
            self.filters = ruleDict['filters']
        if 'output' in ruleDict:
            self.output = ruleDict['output']
        if 'description' in ruleDict:
            self.description = ruleDict['description']
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
            if not re.match(self.filters[field], testField):
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
            command_pieces = command.split(' ', 1)
            try:
                command_function = gettattr(self, "command_" + command_pieces[0])
            except AttributeError:
                sys.stderr.write('Error: rule "' + self.name + '": command "' + command + '" does not exist.\n')
                valueStrings[valueName] = ''
            else:
                #the command is valid
                valueStrings[valueName] = command_function(outputDict, valueStrings[valueName], *command_pieces[1:])
            return self.output.format(**valueStrings)
    #the functions for the commands
    def command_read(self, outputDict, currentValue, argument):
        try:
            newValue = outputDict[argument]
        except KeyError:
            #this field does not exist
            newValue = ''
        return newValue
    def command_regex(self, outputDict, currentValue, argument):
        try:
            #always take the first hit
            newValue = re.search(argument, currentValue).group(0)
        except AttributeError:
            #this regex does not exist
            newValue = ''
        return newValue
    def command_cutl(self, outputDict, currentValue, argument):
        #cut away everything up to the character number provided
        newValue = currentValue[int(argument):]
        return newValue
    def command_cutr(self, outputDict, currentValue, argument):
        #cut away everything from the character number provided
        newValue = currentValue[:int(argument)]
        return newValue
    def command_dns(self, outputDict, currentValue):
        #resolves an dns name
        newValue = socket.gethostbyname(currentValue)
        return newValue
    def command_rdns(self, outputDict, currentValue):
        newValue = socket.gethostbyaddr(currentValue)
        return newValue
