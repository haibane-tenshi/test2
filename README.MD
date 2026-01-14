# Installing

Required installation of Python and [poetry](https://python-poetry.org/docs/).
From inside repo run the following commands:

Install dependencies

```
poetry install
```

Init database:

```
poetry run py manage.py migrate
```

Init test data:

```
poetry run py manage.py testdata
```

Run dev server:

```
poetry run py manage.py runserver
```


# Access control structure

The system is simplistic:
* every user has a list of urls they are permitted to access
* users marked as admin bypass this mechanism and can access any url freely
* urls *paths* are checked verbatim (this excludes params and such)
* currently there is no support for url groups/prefixes (that is `/test` does not permit access to `/test/a` for example)
* currently there is no support for user groups, permissions are set per user

Both limitations can be ameliorated if required.
Implementation is not provided for the sake of simplicity as managing additional parameters explodes endpoints and frontend interfaces.
This entire process should be managed in a different way, but I consider that to be out of scope for the test.
There is generally little to no input validation in place except for few correctness checks (such as username and session id uniqueness); fully tightening it up to validate and restrict all possible user interactions is again out of scope for the test.

On the server side individual endpoints can be marked with decorators:
* `require_session` - requires user to be logged in to access, doesn't impose access restrictions, that is all users can access this resource
* `restricted` - applied after `require_session` to limit access only to authorized users and admins
* `restricted_to_admin` - applied after `require_session` to limit access only to users marked as admins (disregarding the other permission mechanism)

# Test data

Test data includes three users:

* `alice`, `bob` and `charlie` are regular users
* `admin` has administrator rights

All accounts use their username as password.

Server provides the following endpoints:

* Account management: `/account/login`, `/account/status`
* Permission management (admin only): `/admin/update_perms`
* Test endpoints with restricted access: `/test/a`, `/test/b` and `test/c`. 
  Test accounts are preconfigured with access to some of those.
