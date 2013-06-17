from gi.repository import Notify
import re
import sys

notifyHeader = [None]

def setOutput(text):
	global outputs
	outputs = [False, False]
	textList = text.rsplit(',')
	for word in textList:
		if word == 'libnotify':
			outputs[0] = True
		elif word == 'stdout':
			outputs[1] = True
		else:
			print("invalid output '" + word + "'")
			print("to get a list of possible outputs, type " + sys.argv[0] + " --help")
			sys.exit(2)
def putout(text):
	if outputs[1]:
		print(text)
	if outputs[0]:
		noty = Notify.Notification.new(notifyHeader[0],text,"")
		noty.show()
def costumFormat(msg, i, allValues, allValueNames, allOutput, allSurpress):
	#this is a dictionary
	if allSurpress[i]:
		return False
	values = {}
	u = 0
	for value in allValues[i]:
		for command in value:
			if command[:5] == "read ":
				try:
					values[allValueNames[i][u]] = msg[command[5:]]
				except KeyError:
					values[allValueNames[i][u]] = "Field '" + command[5:] + "' not available"
			elif command[:6] == "regex ":
				try:
					values[allValueNames[i][u]] = re.search(command[7:-1], values[allValueNames[i][u]]).group(0)
				except AttributeError:
					values[allValueNames[i][u]] = ''
			elif command[:4] == "rdns":
				try:
					values[allValueNames[i][u]] = socket.gethostbyaddr(values[allValueNames[i][u]])[0]
				except socket.herror:
					values[allValueNames[i][u]] = "unknown host"
				except OSError:
					values[allValueNames[i][u]] = "multiple hosts"
			elif command[:3] == "dns":
				values[allValueNames[i][u]] = socket.gethostbyname(values[allValueNames[i][u]])
			elif command[:4] == "cutl":
				values[allValueNames[i][u]] = values[allValueNames[i][u]][int(command[5:]):]
			elif command[:4] == "cutr":
				values[allValueNames[i][u]] = values[allValueNames[i][u]][:int(command[5:])]
			else:
				print("unknown command in value '" + allValueNames[i][u] + "': " + command)
				values[allValueNames[i][u]] = ">>ERROR<<"
		u += 1
	putout(allOutput[i].format(**values))
	
def message(msg, argList, allFilters, allValues, allValueNames, allOutput, allSurpress, allNames):
	i = 0
	for f in allFilters:
		applies = True
		u = 0
		for a in argList:
			try:
				if len(f) > u and f[u] != 0 and not re.match(f[u], str(msg[a])):
					applies = False
					break
			#this field does not even exist, will be treated as if its empty
			except KeyError:
				if not re.match(f[u], ""):
					applies = False
					break
			u += 1
		if applies:
			#the entry number i seems to have the right filters for this
			costumFormat(msg, i, allValues, allValueNames, allOutput, allSurpress)
			return True
		i += 1
	return False

Notify.init("journalnotify")
