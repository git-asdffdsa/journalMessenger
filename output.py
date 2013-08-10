from gi.repository import Notify
import re
import sys
import json


def putout(text, outputs, header):
    if 'stdout' in outputs:
        print(text)
    if 'libnotify' in outputs:
        noty = Notify.Notification.new(header, text, "")
        noty.show()


def customFormat(msg, rule, outputs, header):
    if not rule.surpress:
        putout(rule.applyRule(msg), outputs, header)


def message(msg, rules, outputs, header, verbose):
    for rule in rules:
        if rule.doesApply(msg):
            customFormat(msg, rule, outputs, header)
            if verbose:
                verboser = {}
                for field in msg:
                    if type(msg[field]) is int or type(msg[field]) is str:
                        verboser[field] = msg[field]
                print("'" + rule.name + "': " + json.dumps(verboser))
            break


Notify.init("journalnotify")
