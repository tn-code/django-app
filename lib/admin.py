from django.contrib import admin
from .models import Book, Quote, Category, Theme, Memo, Terminology, Tag

admin.site.register(Book)
admin.site.register(Quote)
admin.site.register(Category)
admin.site.register(Theme)
admin.site.register(Memo)
admin.site.register(Terminology)
admin.site.register(Tag)
