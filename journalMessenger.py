#! /usr/bin/python

from systemd import journal
import socket
import os
import sys
import json
import argparse

#local modules
import ruleClass
import readfiles
import output


DEFAULT_VALUES = {
	'list-only' : False,
	'profile' : 'default',
	'profilesPath' : 'profiles',
	'rulesPath' : 'rules',
	'output' : ['libnotify', 'stdout'],
	'verbose' : False,
	'title' : 'journalMessenger:',
	'input' : 'liveFeed'
}
OUTPUTS = [ "libnotify", "stdout"]
	

def main():
	rules = []
	#parse arguments
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-l', '--list-only', help='display the rules and exit', action='store_true')
	parser.add_argument('-p', '--profile', help='use this profile')
	parser.add_argument('--profilesPath', metavar='PATH', help='load the profile from this path')
	parser.add_argument('-r', '--rulesPath', metavar='PATH', help='load the rules from all files within this path')
	parser.add_argument('-o', '--output', metavar='DESTINATION',  help='output to all destinations provided, seperated by space', nargs="+", choices=OUTPUTS)
	parser.add_argument('-v', '--verbose', help='output applied rules with original json strings to console', action='store_true')
	parser.add_argument('-t', '--title', help='use this as title for the output to libnotify')
	parser.add_argument('-i', '--input', help='use this as input.', choices=['liveFeed', 'stdin'])
	parser.set_defaults(**DEFAULT_VALUES)
	args = parser.parse_args() 
	#check rulesPath
	#profilesPath will be checked later; is not needed if --list-only is True
	args.rulesPath = os.path.expanduser(args.rulesPath)
	if not os.path.isdir(args.rulesPath):
		sys.stderr.write(args.rulesPath + ' is not a valid path\n')
		sys.exit(2)
	dirList = os.listdir(args.rulesPath)
	dirList.sort()
	for fname in dirList:
		readfiles.readrules(open(os.path.join(args.rulesPath, fname)), rules)
	#if list_only, list only and exit then
	if args.list_only:
		for rule in rules:
			print(rule.name)
		return 1
	#now check profilesPath
	args.profilesPath = os.path.expanduser(args.profilesPath)
	if not os.path.isfile(os.path.join(args.profilesPath, args.profile)):
		sys.stderr.write('Error: file "' + os.path.join(args.profilesPath, args.profile) + '" does not exist\n')
		sys.exit(2)
	#now import the profile
	readfiles.readprofile(open(os.path.join(args.profilesPath, args.profile)), rules)
	#output all journal new thing
	if args.input == 'liveFeed':
		reader = journal.Reader()
		while True:
			reader.seek_tail()
			#oldMessage is the latest output
			oldMessage = reader.get_previous()
			reader.wait()
			reader.seek_tail()
			#newMessage is the (new) latest output
			newMessage = reader.get_previous()
			#go back in journal, until newMessage is oldMessage
			while newMessage != oldMessage:
				output.message(newMessage,rules, args.output, args.title, args.verbose)
				newMessage = reader.get_previous()
	#output from stdin
	elif args.input == 'stdin':
		for line in sys.stdin:
			output.message(json.loads(line), rules, args.output, args.title)
if __name__ == "__main__":
	main()
