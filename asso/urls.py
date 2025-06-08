from django.urls import path

from asso import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("stats/", views.StatsPageView.as_view(), name="stats"),
    path("actus/", views.NewsListView.as_view(), name="news list"),
    path("actus/<slug:slug>/", views.NewsDetailView.as_view(), name="news detail"),
]
