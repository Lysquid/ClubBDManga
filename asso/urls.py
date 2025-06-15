from django.urls import path
from django.views.generic import TemplateView

from asso import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("actus/", views.NewsListView.as_view(), name="news list"),
    path("actus/<slug:slug>/", views.NewsDetailView.as_view(), name="news detail"),
    path("infos/", views.InfoPageView.as_view(), name="info"),
    path("stats/", views.StatsPageView.as_view(), name="stats"),
    path("robots.txt", TemplateView.as_view(template_name="asso/robots.txt", content_type="text/plain")),
]
