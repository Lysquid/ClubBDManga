from django.urls import path

from asso import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("stats/", views.StatsPageView.as_view(), name="stats"),
]
