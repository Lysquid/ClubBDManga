from django.urls import path

from inventory import views

urlpatterns = [
    path("series/", views.SeriesListView.as_view(), name="series list"),
    path("series/<str:pk>/", views.SeriesDetailView.as_view(), name="series detail"),
]
