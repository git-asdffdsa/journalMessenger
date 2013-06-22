#! /usr/bin/python

from systemd import journal
from gi.repository import Notify
import socket
import re
import os
import sys
import getopt
import readfiles
import output
import json

helpOutput = """
Usage:
 messenger [options]
Options:
 -h, --help                     display this help text and exit
 -l, --list-only                display the rules and exit
 -p, --profile <profile>        use the profile <profile>
                                   by default, it is 'default'
     --profilesPath <path>      load the profile from <path>
                                   by default, it is 'profiles'
 -r, --rulesPath <path>         load the rules from all files within <path>
                                   by default, it is 'rules'
 -o, --output <destinations>    output to <destinations>
                                   by default, it is 'stdout,libnotify'
 -t, --title <title>            use <title> as title for libnotify, only important if libnotify
                                is activated as output
                                   by default, it is 'messenger:'
 -i, --input <input>            use <input> as input
                                   by default, it is 'liveFeed'
Destinations:
 [stdout,libnotify]
Input:
 liveFeed                       use the systemd journal live feed
                                as in the command 'journalctl -f -n 0'
 stdin                          use the standard input as input
                                the input must be formatted as json string
"""

def main(argv):
	try:
		opts,args = getopt.getopt(argv, "hlp:r:o:t:i:", ["help","list-only","profile=","rulesPath=","profilesPath=","output=","title=","input="])
	except getopt.GetoptError:
		print("invalid arguments")
		print("to get a list of possible arguments, type " + sys.argv[0] + " --help")
		sys.exit(2)
	emptyList = []
	argList = []
	#the rules overall
	allFilters = []
	allValues = []
	allValueNames = []
	allOutput = []
	allSurpress = []
	allNames = []
	rulesPath = "rules"
	profilesPath = "profiles"
	profile = "default"
	inputSource = "liveFeed"
	outputStr = "stdout,libnotify"
	notifyHeader = "messenger:"
	list_only = False
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print(helpOutput)
			sys.exit()
		elif opt in ("-l","--list-only"):
			list_only = True
		elif opt in ("-p","--profile"):
			profile = arg
		elif opt in ("-r","--rulesPath"):
			rulesPath = arg
		elif opt == '--profilesPath':
			profilesPath = arg
		elif opt in ("-o","--output"):
			outputStr = arg
		elif opt in ("-t","--title"):
			notifyHeader = arg
		elif opt in ("-i","--input"):
			inputSource = arg
	if not inputSource in ("liveFeed","stdin"):
		print("invalid input '" + inputSource + "'")
		print("to get a list of possible inputs, type " + sys.argv[0] + " --help")
		sys.exit(2)	
	output.setOutput(outputStr)
	output.notifyHeader[0] = notifyHeader
	#check rulesPath
	rulesPath = os.path.expanduser(rulesPath)
	if not os.path.isdir(rulesPath):
		sys.stderr.write(rulesPath + ' is not a valid path\n')
		sys.exit(2)
	#check profilesPath
	profilesPath = os.path.expanduser(profilesPath)
	if not os.path.isdir(profilesPath):
		sys.stderr.write(profilesPath + ' is not a valid path\n')
		sys.exit(2)
	dirList = os.listdir(rulesPath)
	dirList.sort()
	for fname in dirList:
		readfiles.readrules(open(rulesPath + "/" + fname), emptyList, argList, allFilters, allValues, allValueNames, allOutput, allSurpress, allNames)
	#if list_only, only list the names of the rules
	if list_only:
		for name in allNames:
			print(name)
		sys.exit()
	#now import the profile
	readfiles.readprofile(open(profilesPath + "/" + profile), allNames, allSurpress)
	#output all journal new thing
	if inputSource == 'liveFeed':
		reader = journal.Reader()
		reader.seek_tail()
		newMessage = 0
		while True:
			oldMessage = reader.get_previous()
			reader.wait()
			reader.seek_tail()
			while newMessage != oldMessage:
				newMessage = reader.get_previous()
				output.message(newMessage, argList, allFilters, allValues, allValueNames, allOutput, allSurpress, allNames)
			reader.seek_tail()
	elif inputSource == 'stdin':
		for line in sys.stdin:
			output.message(json.loads(line), argList, allFilters, allValues, allValueNames, allOutput, allSurpress, allNames)
		print("not supported yet")
if __name__ == "__main__":
	main(sys.argv[1:])
