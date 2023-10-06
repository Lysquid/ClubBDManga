from pathlib import Path
from time import time
import json

from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views import generic
from django.views.decorators.csrf import csrf_exempt


class HomePageView(generic.TemplateView):
    template_name = "asso/home.html"

@csrf_exempt
def test(request: HttpRequest):
    print("test received")
    print(request.method)
    print(request.POST)
    return HttpResponse()

@csrf_exempt
def helloasso_notif(request: HttpRequest):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    # saving the content and headers for debug purposes (TO COMMENT)
    Path("/helloasso/notifs").mkdir(parents=True, exist_ok=True)
    with open(f"/helloasso/notifs/content_{int(time() * 1000)}.json", 'w') as f:
        json.dump(json.loads(request.body.decode()), f, indent=2)
    with open(f"/helloasso/notifs/headers_{int(time() * 1000)}.json", 'w') as f:
        json.dump(dict(request.headers), f, indent=2)

    data: dict = json.loads(request.body.decode())
    if set(data.keys()) != {"eventType", "data"}:
        # the payload does not correspond to what's expected
        # any other missing key will be a simple error
        return HttpResponseBadRequest()

    eventType = data["eventType"]
    data = data["data"]

    # These events do not need to be treated for now
    if eventType in {"Form", "Payment"}: return HttpResponse()

    user_email = data["payer"]["email"]
    user_name = f"""{data["payer"]["firstName"]} {data["payer"]["lastName"]}"""

    order = data["items"][0]
    order_id = data["id"]
    form_name = data["formSlug"]
    form_type = data["formType"]    # please only keep a single membership form active at once

    # handles membership payment (and refund)
    if form_type == "Membership":
        order_name = order["name"]      # the name of the membership option, need to find a way to normalize them
        fields = {}
        for field in order["customFields"]:
            fields[field["name"]] = field["answer"]
        
        tel = fields["Tel :"]
        status = fields["Statut :"]
        year = fields["Année d'étude"]   # useless

    else:
        pass
        # TODO : handles caution payment and refund

    # TODO : treat refunds as removing membership / caution

    return HttpResponse()
