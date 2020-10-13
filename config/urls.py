from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('en/', include(('en.urls', 'en'), namespace='en')),
    path('es/', include(('es.urls', 'es'), namespace='es')),
    path('cuisine/', include(('cuisine.urls', 'cuisine'), namespace='cuisine')),
    path('arts/', include(('arts.urls', 'arts'), namespace='arts')),
    path('atelier/', include(('atelier.urls', 'atelier'), namespace='atelier')),
    path('lib/', include(('lib.urls', 'lib'), namespace='lib')),
    path('blog/', include(('blog.urls', 'blog'), namespace='blog')),
    path('utility/', include(('utility.urls', 'utility'), namespace='utility')),
    path('news/', include(('news.urls', 'news'), namespace='news')),
    path('music/', include(('music.urls', 'music'), namespace='music')),
    path('pharmacy/', include(('pharmacy.urls', 'pharmacy'), namespace='pharmacy')),
    path('admin/', admin.site.urls),
    path('about/', views.about, name='about'),
    path('search/', views.search, name='search'),
    path('calender/', views.calender),
    path('calendar/detail/<int:year>/<int:month>/<int:day>/', views.calender_detail),
    path('summernote/', include('django_summernote.urls')),
    path('nested_admin/', include('nested_admin.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
