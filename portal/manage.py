#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.base")

    from django.core.management import execute_from_command_line
    print("env", os.environ.get('DATABASE_PASSWORD'))
    execute_from_command_line(sys.argv)
