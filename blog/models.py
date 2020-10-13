import os
from django.db import models


def get_image_path(self, filename):
    return os.path.join('images', self.__class__.__name__, self.title, filename)


class Category(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Post(models.Model):
    title = models.CharField(max_length=128)
    slug = models.SlugField()
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    body = models.TextField(null=False)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, blank=True, null=True)
    tags = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
