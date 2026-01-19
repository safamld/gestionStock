#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_stock.settings')
django.setup()

from django.contrib.auth.models import User

print("Users:")
for user in User.objects.all():
    print("  - {} (staff: {})".format(user.username, user.is_staff))
    if user.groups.exists():
        groups = ', '.join([g.name for g in user.groups.all()])
        print("    Groups: {}".format(groups))
