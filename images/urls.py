from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from images import views

app_name = 'images'
urlpatterns = [
    path('create/', views.image_create, name='create'),
    path('detail/<id>/<slug>/', views.image_detail, name='detail'),
    path('like/', views.image_like, name='like'),
    path('', views.image_list, name='list'),
    path('ranking/', views.image_ranking, name='ranking'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
