from pathlib import Path
from time import time

from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.views import generic


class HomePageView(generic.TemplateView):
    template_name = "asso/home.html"


def helloasso_notif(request: HttpRequest):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    data = request.POST
    Path("helloasso/notifs/").mkdir(parents=True, exist_ok=True)
    with open(f"helloasso/notifs/{int(time() * 1000)}.json", 'w') as f:
        f.write(data)

    return HttpResponse()
