#!/usr/bin/env python
import os
import sys

from django.core.management import execute_from_command_line
from django.conf import settings

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wrinklr_django.settings")
    execute_from_command_line(sys.argv)
