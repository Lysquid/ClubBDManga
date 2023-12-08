from django.urls import path

from inventory import views

urlpatterns = [
    path("livres/", views.LibraryView.as_view(), name="library"),
    path("livre/<str:pk>/", views.SeriesDetailView.as_view(), name="series detail"),
    path("search/", views.series_search, name="series list"),
]
