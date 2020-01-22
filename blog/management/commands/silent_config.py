"""
Create permission groups
Create permissions (read only) to models for a set of groups
"""
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import ContentType
from accounts.models import BlogUser
from django.contrib.sites.models import Site
from DjangoBlog.settings import DJANGO_SU_NAME, DJANGO_SU_EMAIL, DJANGO_SU_PASSWORD, SITE_DOMAIN_NAME, SITE_ID
import logging

GROUPS = ['new_users', 'devops', 'developers', 'qa', 'operators', 'product']
MODELS = ['logentry', 'permission', 'group', 'contenttype', 'session', 'site', 'blogsettings', 'links', 'sidebar', 'tag', 'category', 'article', 'bloguser', 'comment', 'commands', 'emailsendlog', 'sitecomment', 'comment', 'tasklist', 'attachment']


class Command(BaseCommand):
    help = 'Creates read only default permission groups for users'

    def handle(self, *args, **options):
        obj, created = Site.objects.get_or_create(
            pk=SITE_ID,
            defaults={
                "domain": SITE_DOMAIN_NAME,
                "name": SITE_DOMAIN_NAME
            }
        )
        obj.domain = SITE_DOMAIN_NAME
        obj.name = SITE_DOMAIN_NAME
        obj.save()
        logging.info("Site has been changed to %s" % SITE_DOMAIN_NAME)

        for group in GROUPS:
            new_group, created = Group.objects.get_or_create(name=group)
            for model in MODELS:
                if group == 'devops':
                    permissions = ['add', 'change', 'delete', 'view']
                else:
                    permissions = ['view', ]
                for permission in permissions:
                    content_type = ContentType.objects.get(model=model)
                    codename = "%s_%s" % (permission, model)
                    name = 'Can {} {}'.format(permission, model)
                    logging.info("Creating permission for group %s; app %s; model: %s" % (group, content_type.app_label, codename))
                    try:
                        model_add_perm = Permission.objects.get(codename=codename, content_type=content_type)
                    except Permission.DoesNotExist:
                        logging.warning("Permission not found with name '{}'.".format(name))
                        continue

                    new_group.permissions.add(model_add_perm)
                    new_group.save()
                    logging.info("Created default group and permissions.")

        try:
            superuser = BlogUser.objects.get(is_superuser=True)
        except ObjectDoesNotExist as err:
            logging.error("Could not query a superuser: {0}".format(err))
            superuser = BlogUser.objects.create_superuser(username=DJANGO_SU_NAME, email=DJANGO_SU_EMAIL, password=DJANGO_SU_PASSWORD)
            superuser.save()
            logging.info("Superuser created")

        try:
            my_group = Group.objects.get(name='devops')
            my_group.user_set.add(superuser)
            logging.info("Superuser has been added to devops group")
        except ObjectDoesNotExist as err:
            logging.error("Could not query a devops group: {0}".format(err))

