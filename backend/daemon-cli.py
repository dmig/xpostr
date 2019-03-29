#! /usr/bin/env python3

import os
import sys
from pprint import pprint
from aiorpc import server
from lib.rpc_client import rpc_call
from lib.daemon import handlers

handlers.init()

commands = list(sorted(fn for fn in server.__dict__['_methods']))
if len(sys.argv) < 2:
    print('Usage: {} <command>[ <argument>[ <argument> ...]]'.format(os.path.basename(sys.argv[0])))
    print(' Available commands:')
    pprint(commands, indent=4)
    exit(1)

command = sys.argv[1]
if command not in commands:
    print(' Unknown command {}'.format(command))
    exit(2)

pprint(rpc_call(command, *sys.argv[2:]))
