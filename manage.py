#!/usr/bin/env python
import os
import sys

from argparse import ArgumentParser

from django.core.management import execute_from_command_line
from django.conf import settings

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wrinklr_django.settings")

    #Add -d argument for easily setting DEBUG = True
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', default=False, action='store_true')
    args, unknown = parser.parse_known_args()

    if args.debug:
        os.environ.setdefault("DEBUG", 'True')

    sys.argv[1:] = unknown
    
    execute_from_command_line(sys.argv)
