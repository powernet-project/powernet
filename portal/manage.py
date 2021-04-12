#!/usr/bin/env python
import os
import sys
import environ

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.base")

    from django.core.management import execute_from_command_line

    env = environ.Env()
    print("env", os.environ)
    execute_from_command_line(sys.argv)
