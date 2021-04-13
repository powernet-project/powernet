#!/usr/bin/env python
import os
import sys
import environ
from app.settings.db import *

if __name__ == "__main__":
    env = environ.Env()
    print("yooo")
    print(os.environ.items())
    print("env123", env)
    # print("env", os.environ.get("DB_PASSWORD"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.base")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
