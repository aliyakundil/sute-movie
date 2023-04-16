from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User


class IpModel(models.Model):
    ip = models.CharField(max_length=100)

    def __str__(self):
        return self.ip


class Movie(models.Model):
    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'

    image = models.ImageField(upload_to='images/news/%Y/%m/%d', blank=True, verbose_name='Фото')
    title = models.CharField(max_length=222, verbose_name='Название')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    year = models.PositiveSmallIntegerField("Дата выхода", default=2019)
    description = models.TextField(blank=True, verbose_name='Описание')
    category_id = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name='Категория')
    created_date = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    published_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата публикации')
    likes = models.ManyToManyField(User, related_name='post', blank=True)
    views = models.ManyToManyField(IpModel, related_name="post_views", blank=True)

    def total_views(self):
        return self.views.count()

    def __str__(self):
        return self.title

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def get_absolute_url(self):
        return reverse('new_detail', kwargs={'pk': self.pk})


class Category(models.Model):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']  # автосортировка

    title = models.CharField(max_length=222, db_index=True, verbose_name='Наименование категорий')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category', kwargs={'category_id': self.pk})
