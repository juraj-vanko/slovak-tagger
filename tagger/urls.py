
from django.urls import path

from . import views

urlpatterns = [
  path('tagger/', views.TaggerView.as_view()),
]