from django.urls import path

from inventory import views

urlpatterns = [
    path("livre/", views.SeriesListView.as_view(), name="series list"),
    path("livre/<str:pk>/", views.SeriesDetailView.as_view(), name="series detail"),
]
