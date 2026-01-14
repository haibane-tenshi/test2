from django.shortcuts import render
from django.http import (
    HttpResponse,
    HttpRequest,
    HttpResponseRedirect,
    HttpResponseForbidden,
)
from django.urls import reverse
from .secure import context
from .models import User, Session
from datetime import datetime, timedelta, timezone
import uuid


# Create your views here.


def require_session(fun):
    def wrapper(*args, **kwargs):
        request: HttpRequest = args[0]
        session_str = request.COOKIES.get("session")

        reject = HttpResponse("Not authorized. Consider logging in.", status=401)

        if session_str is None:
            return reject

        id = uuid.UUID(session_str)
        try:
            session = Session.objects.filter(uuid=id).get()
        except Session.DoesNotExist:
            return reject

        if session.expires_at < datetime.now(timezone.utc):
            return reject
        else:
            request.user = session.user
            request.session = session
            return fun(*args)

    return wrapper


def restricted(fun):
    def wrapper(*args):
        request: HttpRequest = args[0]
        if request.user.is_admin or request.path in [
            perm.url for perm in request.user.userpermission_set.all()
        ]:
            return fun(*args)
        else:
            return HttpResponse("Not authorized.", status=403)

    return wrapper


def index(request: HttpRequest) -> HttpResponse:
    return HttpResponseRedirect("/login")


@require_session
def status(request: HttpRequest) -> HttpResponse:
    return render(request, "status.html")


def login(request: HttpRequest) -> HttpResponse:
    match request.method:
        case "GET":
            return render(request, "login.html")
        case "POST":
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
            id = uuid.uuid7()
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=max_age)
            Session.objects.create(uuid=id, user=user, expires_at=expires_at)

            response = HttpResponseRedirect(reverse("status"))
            response.set_cookie(
                "session", str(id), max_age=max_age, secure=True, httponly=True
            )

            return response
        case _:
            pass


@require_session
def logout(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return HttpResponse(status=400)

    request.session.delete()

    response = HttpResponseRedirect(reverse("login"))
    response.set_cookie("session", "", max_age=0)
    return response


@require_session
@restricted
def test_a(request: HttpRequest) -> HttpResponse:
    return HttpResponse("This page contains letter A")


@require_session
@restricted
def test_b(request: HttpRequest) -> HttpResponse:
    return HttpResponse("This page contains letter B")


@require_session
@restricted
def test_c(request: HttpRequest) -> HttpResponse:
    return HttpResponse("This page contains letter C")
