from pathlib import Path
from time import time
from json import dump

from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.views import generic


class HomePageView(generic.TemplateView):
    template_name = "asso/home.html"


def test(request: HttpRequest):
    print("test received")
    print(request.method)
    print(request.POST)
    return HttpResponse()

def helloasso_notif(request: HttpRequest):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    Path("helloasso/notifs/").mkdir(parents=True, exist_ok=True)
    with open(f"helloasso/notifs/content_{int(time() * 1000)}.json", 'w') as f:
        dump(request.POST.dict(), f, indent=2)
    with open(f"helloasso/notifs/headers_{int(time() * 1000)}.json", 'w') as f:
        dump(dict(request.headers), f, indent=2)

    return HttpResponse()
