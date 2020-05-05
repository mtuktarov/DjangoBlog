import logging
from abc import ABCMeta, abstractmethod, abstractproperty

from django.db import models
from django.urls import reverse
from django.conf import settings
from uuslug import slugify
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from DjangoBlog.utils import get_current_site
from DjangoBlog.utils import cache_decorator, cache
from django.utils.timezone import now
from mdeditor.fields import MDTextField

logger = logging.getLogger(__name__)

LINK_SHOW_TYPE = (
    ('i', 'Home'),
    ('l', 'List'),
    ('p', 'Article page'),
    ('a', 'Full Site'),
    ('s', 'Friendly Link Page'),
)


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField('Время создания', default=now)
    last_mod_time = models.DateTimeField('Время изменения', default=now)

    def save(self, *args, **kwargs):
        is_update_views = isinstance(self, Article) and 'update_fields' in kwargs and kwargs['update_fields'] == [
            'views']
        if is_update_views:
            Article.objects.filter(pk=self.pk).update(views=self.views)
        else:
            if 'slug' in self.__dict__:
                slug = getattr(self, 'title') if 'title' in self.__dict__ else getattr(self, 'name')
                setattr(self, 'slug', slugify(slug))
            super().save(*args, **kwargs)

    def get_full_url(self):
        site = get_current_site().domain
        url = "https://{site}{path}".format(site=site, path=self.get_absolute_url())
        return url

    class Meta:
        abstract = True

    @abstractmethod
    def get_absolute_url(self):
        pass


class Article(BaseModel):
    """Article"""
    STATUS_CHOICES = (
        ('d', 'Черновик'),
        ('p', 'Публикация'),
    )
    COMMENT_STATUS = (
        ('o', 'Комментарии включены'),
        ('c', 'Комментарии выключены'),
    )
    TYPE = (
        ('a', 'Пост'),
        ('p', 'Страница'),
    )
    title = models.CharField('Название', max_length=200, unique=True)
    body = MDTextField('Содержимое')
    pub_time = models.DateTimeField('Время публикации', blank=False, null=False, default=now)
    status = models.CharField('Статус публикации', max_length=1, choices=STATUS_CHOICES, default='p')
    comment_status = models.CharField('Статус комментариев', max_length=1, choices=COMMENT_STATUS, default='o')
    type = models.CharField('Тип', max_length=1, choices=TYPE, default='a')
    views = models.PositiveIntegerField('Просмотры', default=0)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Автор', blank=False, null=False,
                               on_delete=models.CASCADE)
    article_order = models.IntegerField('Очередность', blank=False, null=False, default=0)
    category = models.ForeignKey('Category', verbose_name='Категория', on_delete=models.CASCADE, blank=True, null=True)
    tags = models.ManyToManyField('Tag', verbose_name='Тег', blank=True)

    def body_to_string(self):
        return self.body

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-article_order', '-pub_time']
        verbose_name = "Публикация"
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def get_absolute_url(self):
        return reverse('blog:detailbyid', kwargs={
            'article_id': self.id,
            'year': self.created_time.year,
            'month': self.created_time.month,
            'day': self.created_time.day
        })

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        tree = self.category.get_category_tree()
        names = list(map(lambda c: (c.name, c.get_absolute_url()), tree))

        return names

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])

    def comment_list(self):
        cache_key = 'article_comments_{id}'.format(id=self.id)
        value = cache.get(cache_key)
        if value:
            logger.info('get article comments:{id}'.format(id=self.id))
            return value
        else:
            comments = self.comment_set.filter(is_enable=True)
            cache.set(cache_key, comments, 60 * 100)
            logger.info('set article comments:{id}'.format(id=self.id))
            return comments

    def get_admin_url(self):
        info = (self._meta.app_label, self._meta.model_name)
        return reverse('admin:%s_%s_change' % info, args=(self.pk,))

    @cache_decorator(expiration=60 * 100)
    def next_article(self):
        # Следующая публикация
        return Article.objects.filter(id__gt=self.id, status='p').order_by('id').first()

    @cache_decorator(expiration=60 * 100)
    def prev_article(self):
        # Предыдущая публикация
        return Article.objects.filter(id__lt=self.id, status='p').first()


class Category(BaseModel):
    """Article Category"""
    name = models.CharField('Имя', max_length=30, unique=True)
    parent_category = models.ForeignKey('self', verbose_name="Надкатегория", blank=True, null=True, on_delete=models.CASCADE)
    slug = models.SlugField(default='no-slug', max_length=60, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Категория"
        verbose_name_plural = verbose_name

    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'category_name': self.slug})

    def __str__(self):
        return self.name

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        """
        Recursively get the parent of the catalog
        :return:
        """
        categorys = []

        def parse(category):
            categorys.append(category)
            if category.parent_category:
                parse(category.parent_category)

        parse(self)
        return categorys

    @cache_decorator(60 * 60 * 10)
    def get_sub_categorys(self):
        """
        Get all subsets of the current catalog
        :return:
        """
        categorys = []
        all_categorys = Category.objects.all()

        def parse(category):
            if category not in categorys:
                categorys.append(category)
            childs = all_categorys.filter(parent_category=category)
            for child in childs:
                if category not in categorys:
                    categorys.append(child)
                parse(child)

        parse(self)
        return categorys


class Tag(BaseModel):
    """Article tags"""
    name = models.CharField('Тег', max_length=30, unique=True)
    slug = models.SlugField(default='no-slug', max_length=60, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'tag_name': self.slug})

    @cache_decorator(60 * 60 * 10)
    def get_article_count(self):
        return Article.objects.filter(tags__name=self.name).distinct().count()

    class Meta:
        ordering = ['name']
        verbose_name = "Тег"
        verbose_name_plural = verbose_name


class Links(models.Model):
    """Links"""

    name = models.CharField('Ссылка', max_length=30, unique=True)
    link = models.URLField('Адрес')
    sequence = models.IntegerField('Очередность', unique=True)
    is_enable = models.BooleanField('Включена', default=True, blank=False, null=False)
    show_type = models.CharField('Показывать тип', max_length=1, choices=LINK_SHOW_TYPE, default='i')
    created_time = models.DateTimeField('Дата создания', default=now)
    last_mod_time = models.DateTimeField('Дата редактирования', default=now)

    class Meta:
        ordering = ['sequence']
        verbose_name = 'Ссылки'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SideBar(models.Model):
    """Sidebar, can display some html content"""
    name = models.CharField('Название', max_length=100)
    content = models.TextField("Содержимое")
    sequence = models.IntegerField('Позиция', unique=True)
    is_enable = models.BooleanField('Включен', default=True)
    created_time = models.DateTimeField('Дата создания', default=now)
    last_mod_time = models.DateTimeField('Дата редактирования', default=now)

    class Meta:
        ordering = ['sequence']
        verbose_name = 'Боковая панель'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class BlogSettings(models.Model):
    '''Site settings'''
    sitename = models.CharField("Имя сайта", max_length=200, null=False, blank=False, default='')
    site_description = models.TextField("Описание сайта", max_length=1000, null=False, blank=False, default='')
    site_seo_description = models.TextField("Владелец сайта", max_length=1000, null=False, blank=False, default='')
    site_keywords = models.TextField("Ключевые слова сайта", max_length=1000, null=False, blank=False, default='')
    article_sub_length = models.IntegerField("Отображаемая длина поста", default=300)
    sidebar_article_count = models.IntegerField("Количество постов на боковой панели", default=10)
    sidebar_comment_count = models.IntegerField("Количество комментариев на боковой панели", default=5)
    show_google_adsense = models.BooleanField('Показывать рекламу Гугла', default=False)
    google_adsense_codes = models.TextField('Рекламный контент', max_length=2000, null=True, blank=True, default='')
    open_site_comment = models.BooleanField('Включить комментарии', default=True)
    analyticscode = models.TextField("Код статистики сайта", max_length=1000, null=True, blank=True, default='')
    resource_path = models.CharField("Каталог со статикой", max_length=300, null=False, default='media')
    show_views_bar = models.BooleanField('Показывать панель ПРОСМОТРЫ', default=False)
    show_category_bar = models.BooleanField('Показывать панель КАТЕГОРИИ', default=False)
    show_search_bar = models.BooleanField('Показывать панель ПОИСКА', default=False)
    show_menu_bar = models.BooleanField('Показывать панель МЕНЮ', default=False)

    class Meta:
        verbose_name = 'Конфигурация сайта'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sitename

    def clean(self):
        if BlogSettings.objects.exclude(id=self.id).count():
            raise ValidationError(_('Возможна только одна конфигурация'))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from DjangoBlog.utils import cache
        cache.clear()
