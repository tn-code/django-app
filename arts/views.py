from django.shortcuts import render, get_object_or_404, redirect
from .models import Exhibition, Work, Genre, Artist, Museum, Design
from django.forms.models import model_to_dict


def index(request):
    exhibitions = Exhibition.objects.all().order_by('-open_at')[:6]
    works = Work.objects.all().order_by('?')[:12]
    museums = Museum.objects.all().order_by('-id')[:4]
    work = Work.objects.all().order_by('?')[:1]
    designs = Design.objects.all().order_by('?')[:12]
    context = {
        'title': 'arts',
        'exhibitions': exhibitions,
        'works': works,
        'museums': museums,
        'work': work,
        'designs': designs
    }
    return render(request, 'arts/index.html', context)


def exhibitions(request):
    exhibitions = Exhibition.objects.all().order_by('-open_at')
    return render(request, 'arts/exhibitions.html',
                  {
                      'title': "Exhibitions",
                      'exhibitions': exhibitions
                  })


def exhibition(request, pk):
    exhibition = Exhibition.objects.get(id=pk)
    museum = exhibition.museum
    return render(request, 'arts/exhibition.html',
                  {
                      'title': exhibition.name,
                      'exhibition': exhibition,
                      'museum': museum
                  }

                  )


def works(request):
    pass


def work(request, id):
    work = Work.objects.get(id=id)
    return render(request, 'arts/work.html',
                  {
                      'title': work.title_jp,
                      'work': work
                  }

                  )


def design(request, pk):
    design = Design.objects.get(id=pk)
    return render(request, 'arts/design.html',
                  {
                      'title': design.name,
                      'exhibition': design,
                  }

                  )


def designs(request):
    designs = Design.objects.all().order_by('-id')
    return render(request, 'arts/designs.html',
                  {
                      'title': "Designs",
                      'designs': designs
                  })


def artists(request):
    pass


def artist(request, id):
    artist = Artist.objects.get(id=id)
    return render(request, 'arts/artist.html',
                  {
                      'title': artist.name_jp,
                      'artist': artist
                  }

                  )


def genres(request):
    pass


def genre(request, id):
    genre = Genre.objects.get(id=id)
    artists = genre.artists_related.all()

    l = []
    for artist in artists:
        l.append(artist.id)

    works = Work.objects.filter(artist_id__in=l)
    return render(request, 'arts/genre.html',
                  {
                      'title': genre.name,
                      'genre': genre,
                      'artists': artists,
                      'works': works
                  }

                  )


def museums(request):
    museums = Museum.objects.all().order_by('-id')
    return render(request, 'arts/museums.html', {
        'museums': museums
    })


def museum(request, pk):
    museum = get_object_or_404(Museum, id=pk)
    exhibitions = Exhibition.objects.filter(museum=museum)
    works = Work.objects.filter(museum=museum)
    context = {
        'museum': museum,
        'exhibitions': exhibitions,
        'works': works
    }
    return render(request, 'arts/museum.html', context)
