from django.urls import path

from asso import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("test", views.test),
    path("helloasso/notifs", views.helloasso_notif)
]
