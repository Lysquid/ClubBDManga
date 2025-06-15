from django.urls import path

from inventory import views

urlpatterns = [
    path("livres/", views.LibraryView.as_view(), name="library"),
    path("livre/<str:code>/", views.SeriesDetailView.as_view(), name="series detail"),
    path('api/series/', views.series_list, name="series list"),
]
