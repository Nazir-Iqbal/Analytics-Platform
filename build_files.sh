#!/bin/bash
# In Vercel builds, do NOT run `pip install` manually — the platform
# installs packages from requirements.txt. Running pip here may try to
# modify a system-managed Python (PEP 668) and fail with
# "externally-managed-environment". Only collect static files.
python manage.py collectstatic --noinput
