#!/usr/bin/env python

from django.core.management.base import BaseCommand
# from oauth.models import OAuthUser
from DjangoBlog.utils import save_user_avatar


class Command(BaseCommand):
    help = 'sync user avatar'

    def handle(self, *args, **options):
        pass
