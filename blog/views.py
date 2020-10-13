from django.shortcuts import render
from django.conf import settings
import urllib.request
import urllib.error
from .models import Post, Category


def check_online():
    try:
        urllib.request.urlopen('http://216.58.192.142', timeout=1)
        return True
    except urllib.error.URLError as err:
        return False


def index(request):
    posts = Post.objects.order_by('-created_at')
    return render(request, 'blog/index.html', {'posts': posts})


def contentful(request):
    if check_online() == True:
        posts = client.entries()
        return render(request, 'blog/index.html', {'posts': posts})
    else:
        return render(request, 'blog/index.html', {'error': "インターネット接続がないためコンテンツを表示できません。"})


def slug(request, slug):
    post = Post.objects.get(slug=slug)
    return render(request, 'blog/slug.html', {'post': post})
