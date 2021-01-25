#!/usr/bin/env python

from django.core.cache import cache
from django.contrib.sites.models import Site
from hashlib import md5
import markdown2
from django.conf import settings
import logging
import requests
import uuid
import os
logger = logging.getLogger(__name__)


def get_max_articleid_commentid():
    from blog.models import Article
    from comments.models import Comment
    return (Article.objects.latest().pk, Comment.objects.latest().pk)


def get_md5(str):
    m = md5(str.encode('utf-8'))
    return m.hexdigest()


def cache_decorator(expiration=3 * 60):
    def wrapper(func):
        def news(*args, **kwargs):
            try:
                view = args[0]
                key = view.get_cache_key()
            except:
                key = None
            if not key:
                unique_str = repr((func, args, kwargs))

                m = md5(unique_str.encode('utf-8'))
                key = m.hexdigest()
            value = cache.get(key)
            if value is not None:
                # logger.info('cache_decorator get cache:%s key:%s' % (func.__name__, key))
                if str(value) == '__default_cache_value__':
                    return None
                else:
                    return value
            else:
                # logger.debug('cache_decorator set cache:%s key:%s' % (func.__name__, key))
                value = func(*args, **kwargs)
                if value is None:
                    cache.set(key, '__default_cache_value__', expiration)
                else:
                    cache.set(key, value, expiration)
                return value

        return news

    return wrapper


def expire_view_cache(path, servername, serverport, key_prefix=None):
    '''
    Flush preliminary cache
    :param path:url path
    :param servername: host
    :param serverport: port
    :param key_prefix: prefix
    :return: status
    '''
    from django.http import HttpRequest
    from django.utils.cache import get_cache_key

    request = HttpRequest()
    request.META = {'SERVER_NAME': servername, 'SERVER_PORT': serverport}
    request.path = path

    key = get_cache_key(request, key_prefix=key_prefix, cache=cache)
    if key:
        logger.info('expire_view_cache:get key:{path}'.format(path=path))
        if cache.get(key):
            cache.delete(key)
        return True
    return False

@cache_decorator()
def get_current_site():
    site = Site.objects.get_current()
    return site


@cache_decorator()
def get_current_site_domain():
    if settings.DEBUG:
        return '127.0.0.1:8000'
    return Site.objects.get_current().domain

class CommonMarkdown():
    @staticmethod
    def get_markdown(content):
        return markdown2.markdown(content, extras=["tables", "cuddled-lists", "fenced-code-blocks"])

def render_template(template, **kwargs):
    ''' renders a Jinja template into HTML '''
    # check if template exists
    from DjangoBlog.settings import EMAIL_FILES
    full_path = os.path.join(EMAIL_FILES, template)
    if not os.path.isfile(full_path):
        logger.error('No template file present: %s' % template)
        return None

    from jinja2 import Template
    with open(full_path) as file_:
        template_content = Template(file_.read())
    return template_content.render(**kwargs)


def send_email(emailto, title, content, images=None):
    from DjangoBlog.blog_signals import send_email_signal
    send_email_signal.send(send_email.__class__, emailto=emailto, title=title, content=content, images=images)


def parse_dict_to_url(dict):
    from urllib.parse import quote
    url = '&'.join(['{}={}'.format(quote(k, safe='/'), quote(v, safe='/'))
                    for k, v in dict.items()])
    return url


def get_blog_setting():
    value = cache.get('get_blog_setting')
    if value:
        return value
    else:
        from blog.models import BlogSettings
        if not BlogSettings.objects.count():
            setting = BlogSettings()
            setting.sitename = 'mtuktarov empire'
            setting.site_description = 'if I had my own world...'
            setting.site_seo_description = 'mtuktarov'
            setting.site_keywords = 'love,hope,truth'
            setting.article_sub_length = 300
            setting.sidebar_article_count = 10
            setting.sidebar_comment_count = 5
            setting.show_google_adsense = False
            setting.enable_site_comment = True
            setting.analyticscode = ''
            setting.footer_title = 'if I had my own world...'
            setting.show_views_bar = False
            setting.show_category_bar = False
            setting.show_search_bar = False
            setting.show_menu_bar = False
            setting.save()
        value = BlogSettings.objects.first()
        # logger.debug('set cache get_blog_setting')
        cache.set('get_blog_setting', value)
        return value


def save_user_avatar(url):
    '''
    Save user avatar
    :param url: Avatar url
    :return: Local path
    '''
    setting = get_blog_setting()
    logger.info(url)
    try:
        imgname = url.split('/')[-1]
        if imgname:
            path = r'{basedir}/avatar/{img}'.format(basedir=setting.resource_path, img=imgname)
            if os.path.exists(path):
                os.remove(path)
    except:
        pass
    try:
        rsp = requests.get(url, timeout=2)
        logger.info(rsp)
        if rsp.status_code == 200:
            basepath = r'{basedir}/avatar/'.format(basedir=setting.resource_path)
            if not os.path.exists(basepath):
                os.makedirs(basepath)
            imgextensions = ['.jpg', '.png', 'jpeg', '.gif']
            isimage = len([i for i in imgextensions if url.endswith(i)]) > 0
            logger.info('isimage: {}'.format(isimage))
            ext = os.path.splitext(url)[1] if isimage else '.jpg'
            logger.info('ext: {}'.format(ext))
            savefilename = str(uuid.uuid4().hex) + ext
            logger.info('Save user avatar:' + basepath + savefilename)
            with open(basepath + savefilename, 'wb+') as file:
                logger.info("{}".format(rsp.content))
                file.write(rsp.content)
            return "{}".format(basepath + savefilename)
    except Exception as e:
        logger.error(e)
        logger.info("return url: {}".format(url))
        return url


def delete_sidebar_cache(username):
    from django.core.cache.utils import make_template_fragment_key
    from blog.models import LINK_SHOW_TYPE
    keys = (make_template_fragment_key('sidebar', [username + x[0]]) for x in LINK_SHOW_TYPE)
    for k in keys:
        # logger.debug('delete sidebar key:' + k)
        cache.delete(k)


def delete_view_cache(prefix, keys):
    from django.core.cache.utils import make_template_fragment_key
    key = make_template_fragment_key(prefix, keys)
    cache.delete(key)
