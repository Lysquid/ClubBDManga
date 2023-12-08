from django.urls import path

from inventory import views

urlpatterns = [
    path("livres/", views.SeriesListView.as_view(), name="series list"),
    path("livres/<str:pk>/", views.SeriesDetailView.as_view(), name="series detail"),
]
