from django.shortcuts import render
from django.http import (
    HttpResponse,
    HttpRequest,
    HttpResponseRedirect,
    HttpResponseForbidden,
)
from django.urls import reverse

# Create your views here.


def index(request: HttpRequest) -> HttpResponse:
    return HttpResponseRedirect("/login")


def login(request: HttpRequest) -> HttpResponse:
    match request.method:
        case "GET":
            return render(request, "login.html")
        case "POST":
            from .secure import context
            from .models import User, Session
            from datetime import datetime, timedelta
            import uuid

            name = request.POST["login"]
            password = request.POST["password"]

            try:
                user = User.objects.get(name=name)
            except User.DoesNotExist:
                return HttpResponseForbidden("Invalid username and/or password")

            if not context.verify(password, user.passhash):
                return HttpResponseForbidden("Invalid username and/or password")

            # Currently we always create a new session
            # It might be correct to join an existing session instead (if there is one)

            # in seconds
            max_age = 60 * 60
            uuid = uuid.uuid7()
            expires_at = datetime.now() + timedelta(seconds=max_age)
            Session.objects.create(uuid=uuid, user=user, expires_at=expires_at)

            response = HttpResponseRedirect(reverse("status"))
            response.set_cookie(
                "session", str(uuid), max_age=max_age, secure=True, httponly=True
            )

            return response
        case _:
            pass
