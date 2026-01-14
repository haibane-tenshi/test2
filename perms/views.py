from django.shortcuts import render
from django.http import (
    HttpResponse,
    HttpRequest,
    HttpResponseRedirect,
    HttpResponseForbidden,
)
from django.urls import reverse
from .secure import context
from .models import User, Session, UserPermission
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

        if not session.is_active():
            session.delete()
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


def restricted_to_admin(fun):
    def wrapper(*args):
        request: HttpRequest = args[0]
        if request.user.is_admin:
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

            reject = HttpResponseForbidden("Invalid username and/or password")

            try:
                user = User.objects.get(name=name)
            except User.DoesNotExist:
                return reject

            if not user.is_active:
                return reject

            if not context.verify(password, user.passhash):
                return reject

            # Check existing sessions, some of them may have expired.
            for session in user.session_set.all():
                if not session.is_active():
                    session.delete()

            # in seconds
            max_age = 60 * 60

            # If there is one active, join it instead of creating a new one.
            session = user.session_set.first()
            if session is None:
                id = uuid.uuid7()
                expires_at = datetime.now(timezone.utc) + timedelta(seconds=max_age)
                Session.objects.create(uuid=id, user=user, expires_at=expires_at)
            else:
                id = session.uuid

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
def remove(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return HttpResponse(status=400)

    for session in request.user.session_set.all():
        session.delete()
    request.user.is_active = False
    request.user.save()

    response = HttpResponseRedirect(reverse("login"))
    response.set_cookie("session", "", max_age=0)
    return response


@require_session
@restricted_to_admin
def update_perms(request: HttpRequest) -> HttpResponse:
    match request.method:
        case "GET":
            return render(request, "update_perms.html")
        case "POST":
            username = request.POST["username"]
            url = request.POST["url"]
            opkind = request.POST["opkind"]

            try:
                user = User.objects.get(name=username)
            except User.DoesNotExist:
                return HttpResponse("User does not exist", status=400)

            perms = user.userpermission_set.filter(url=url).all()
            match opkind:
                case "add":
                    if len(perms) == 0:
                        UserPermission.objects.create(group=user, url=url)
                case "rem":
                    for perm in perms:
                        perm.delete()
                case _:
                    pass

            return HttpResponse()


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
