import io
import numpy as np
import datetime

import re
try:
    import matplotlib
    matplotlib.use('Agg')
finally:
    from matplotlib import pyplot as plt

from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.forms.models import model_to_dict
from django.views.generic.edit import CreateView
from django.contrib import messages

from .models import Book, Quote, Theme, Memo, Category
from .forms import QuoteForm, ThemeCommentForm, ThemeForm, BookForm


def pluralize(num, unit):
    if num > 1:
        return str(num) + ' ' + unit + 's'
    else:
        return str(num) + ' ' + unit


def index(request):
    books = Book.objects.all().order_by('-updated_at', '-id')[:6]
    quote = Quote.objects.all().order_by('?').first()
    themes = Theme.objects.all().order_by('-id')[:8]
    memos = Memo.objects.all().order_by('-id')[:3]
    categories = Category.objects.all()
    return render(request, 'lib/index.html',
                  {
                      'title': 'Library',
                      'books': books,
                      'quote': quote,
                      'themes': themes,
                      'memos': memos,
                      'categories': categories
                  }
                  )


def books(request):
    if request.GET.get('q') and request.GET.get('q') != None:
        query = request.GET.get('q')
        books = Book.objects.filter(name__contains=query)
        title = 'Search results - 「' + str(query) + '」'
    else:
        books = Book.objects.all().order_by('-purchased_at')
        title = 'All books'

    context = {
        'books': books,
        'title': title
    }
    return render(request, 'lib/books.html', context)


def category(request, pk):
    category = Category.objects.get(id=pk)
    books = Book.objects.filter(category=pk)

    context = {
        'books': books,
        'category': category
    }
    return render(request, 'lib/books.html', context)


def book(request, pk):
    book = get_object_or_404(Book, id=pk)
    quotes = Quote.objects.filter(book_id=pk)
    themes = Theme.objects.all()
    form = QuoteForm(request.POST or None, initial={'book': book})
    now = datetime.datetime.now()
    context = {
        'book': book,
        'form': form,
        'themes': themes,
    }
    # request.POST
    if request.method == 'POST':
        # Add a new quote to its book field
        if 'add_quote' in request.POST and form.is_valid():
            # Need to save first to generate id which is used to set relationship
            instance = form.save(commit=False)
            instance.book = book
            form.save()

            # Update related book instance's field to sync the change
            book.updated_at = datetime.datetime.now()
            book.save(update_fields=["updated_at"])

            messages.success(
                request, 'New quote has been added successfully [ID:' + str(instance.id) + ']')

            return redirect('lib:book', pk=pk)

        # Add quotes to a specific theme
        elif request.POST.get('quotes_theme'):
            pk = request.POST.get('pk')
            theme = Theme.objects.get(id=pk)
            # Get quote pks passed through checkboxes as list
            l = request.POST.getlist('qs[]')
            qs = Quote.objects.filter(id__in=l)
            # Note that Theme model has the quote field, not Book model
            for q in qs:
                theme.quotes.add(q)
            theme.save()
            messages.success(
                request, str(qs.count()) + ' quotes has been added to the theme「' + theme.name + '」')
            return redirect('lib:book', pk=book.id)
        else:
            messages.error(request, "Error")
            return render(request, 'lib/book.html', context)

    # request.GET(Search)
    else:
        # with search query
        if request.GET.get('q'):
            query = request.GET.get('q')
            context['keyword'] = query
            context['has_filter'] = True
            try:
                space_count = 0
                for q in query:
                    if q.isspace() == True:
                        space_count += 1
                    else:
                        pass
            except:
                space_count = None

            if query != None and space_count < 1:

                quotes = Quote.objects.filter(
                    book_id=book.id, body__contains=query)
                if quotes.count() != 0:
                    pass
                else:
                    messages.warning(
                        request, 'No results matched with the following keyword: ' + query)
            else:
                messages.warning(request, 'The keyword you entered is unjustifiable(containing ' +
                                 pluralize(space_count, 'space') + ') ' + '. Showing all quotes instead.')
                quotes = Quote.objects.all()

        # without search query
        else:
            pass

        context['quotes'] = quotes
        return render(request, 'lib/book.html', context)


def book_add(request):
    form = BookForm(request.POST or None, files=request.FILES or None)
    context = {'form': form}
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            messages.success(
                request, 'The book 「' + instance.name + '」 has been added successfully')
            return redirect('lib:books')
        else:
            messages.error(request, "Error")
            return render(request, 'lib/book_add.html', context)
    else:
        return render(request, 'lib/book_add.html', context)


def quote(request, id):
    quote = get_object_or_404(Quote, id=id)
    themes = Theme.objects.all()
    book = quote.book
    context = {
        'quote': quote,
        'themes': themes,
        'book': book
    }
    if request.method == 'POST':
        if 'update' in request.POST:
            form = QuoteForm(request.POST, files=request.FILES,
                             initial=model_to_dict(quote))
            if form.is_valid():
                form.save(update_fields=["comment", 'image', 'quotes'])
                return redirect('lib:quote', id=id)
            else:
                messages.error(request, "Error")
                return render(request, 'lib/quote.html', context)
        elif 'theme' in request.POST:
            pass
        else:
            return
    else:
        context['form'] = QuoteForm(initial=model_to_dict(quote))
        return render(request, 'lib/quote.html', context)


def quotes(request):
    quotes = Quote.objects.all()
    themes = Theme.objects.all()
    categories = Category.objects.all()
    if request.method == 'POST':
        pk = request.POST.get('pk')
        theme = Theme.objects.get(id=pk)
        list = request.POST.getlist('qs[]')
        qs = Quote.objects.filter(
            id__in=list)
        for q in qs:
            theme.quotes.add(q)
        theme.save()
        return render(request, 'lib/quotes.html',
                      {
                          'title': "All Quotes",
                          'quotes': quotes,

                          'themes': themes,
                          'qs_count': qs.count,
                          'target_theme': theme
                      }

                      )
    else:

        if request.GET.get('q'):
            query = request.GET.get('q')
            if query != None:
                quotes = Quote.objects.filter(body__contains=query)
                return render(request, 'lib/quotes.html',
                              {
                                  'title': "All Quotes",
                                  'quotes': quotes,
                                  'hits': quotes.count,
                                  'query': query,
                                  'categories': categories,

                                  'themes': themes
                              })

            elif query == None:
                quotes = Quote.objects.all()
                return render(request, 'lib/quotes.html',
                              {
                                  'title': "All Quotes",
                                  'quotes': quotes,
                                  'hits': quotes.count,
                                  'query': query,
                                  'categories': categories,

                                  'themes': themes
                              })
        elif request.GET.get('c'):
            cquery = request.GET.get('c')
            s_category = Category.objects.get(id=cquery).name
            books = Book.objects.filter(category_id=cquery)
            quotes = Quote.objects.filter(book__in=books)

            return render(request, 'lib/quotes.html',
                          {
                              'title': "All Quotes",
                              'books': books,
                              'cquery': cquery,
                              'categories': categories,
                              's_category': s_category,

                              'quotes': quotes,
                              'themes': themes
                          })

        else:
            quotes = Quote.objects.all()
            return render(request, 'lib/quotes.html',
                          {
                              'title': "All Quotes",
                              'categories': categories,

                              'quotes': quotes,
                              'themes': themes
                          })


def themes(request):
    themes = Theme.objects.all()
    form = ThemeForm(request.POST, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            return HttpResponseRedirect('/lib/themes/' + str(instance.id))

    else:
        return render(request, 'lib/themes.html',
                      {
                          'title': themes,
                          'themes': themes,
                          'form': form
                      }

                      )


def theme(request, id):
    theme = Theme.objects.get(id=id)
    if request.method == 'POST':
        form = ThemeCommentForm(request.POST, initial={
            'id': theme.id,
            'name': theme.name,
            'category': theme.category,
            'quotes': theme.quotes,
            'image': theme.image,
            'description': theme.description
        })
        if form.is_valid():
            file = form.save(commit=False)
            file.id = theme.id
            file.name = theme.name
            file.category = theme.category
            file.image = theme.image
            file.description = theme.description
            file.save()

            return HttpResponseRedirect('/lib/themes/' + str(theme.id))

    else:
        form = ThemeCommentForm(initial={
            'id': theme.id,
            'name': theme.name,
            'category': theme.category,
            'quotes': theme.quotes,
            'image': theme.image,
            'description': theme.description
        })

        return render(request, 'lib/theme.html',
                      {
                          'title': theme.name,
                          'theme': theme,
                          'form': form,
                          'quotes': theme.quotes,
                      }

                      )


class ThemeCreate(CreateView):
    model = Theme
    fields = '__all__'
    template_name = 'lib/theme_add.html'


def memos(request):
    memos = Memo.objects.all().order_by('-id')
    return render(request, 'lib/memos.html',
                  {
                      'title': "Memos",
                      'memos': memos
                  }

                  )


def getFig():
    today = datetime.date.today()
    year = today.year
    nums = []
    for i in range(1, 13):
        nums.append(str(i).zfill(2))
    list_purchased = [Book.objects.filter(purchased_at__year=year).filter(purchased_at__month=i).count()
                      for i in nums]
    list_read = [Book.objects.filter(purchased_at__year=year).filter(read_at__month=i).count()
                 for i in nums]
    months = np.array(['Jan', 'Feb', 'Mar', 'Apr', 'May',
                       'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    purchased = np.array(list_purchased)
    read = np.array(list_read)
    max_purchase = max(list_purchased)
    fig, ax = plt.subplots(figsize=(
        15, 5), dpi=80, facecolor='w', edgecolor='k')
    ax.axhspan(0, max_purchase, facecolor='red', alpha=0.1)
    ax.set(xlabel='months (s)', ylabel='books',
           title='Monthly Reading Stats.({})'.format(str(year)))
    ax.grid()
    ax.bar(months, purchased, color="green", width=0.5)
    ax.plot(months, read,  'r-',  markersize=5, markeredgewidth=3,
            markeredgecolor='red', alpha=0.8)
    ax.plot(months, read,  'o', markersize=5, markeredgewidth=3,
            markeredgecolor='red', alpha=0.8)

    return fig


def get_svg(request):
    fig = getFig()
    buf = io.BytesIO()
    plt.savefig(buf, format='svg')
    plt.close(fig)
    response = HttpResponse(buf.getvalue(), content_type='image/svg+xml')
    return response
