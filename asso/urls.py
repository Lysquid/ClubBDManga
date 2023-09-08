from django.urls import path

from asso import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("series/", views.SeriesListView.as_view(), name="series list"),
    path("series/<str:pk>/", views.SeriesDetailView.as_view(), name="series detail"),
]
