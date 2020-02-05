from flask import url_for

from app.config import EMAIL_DOMAIN, MAX_NB_EMAIL_FREE_PLAN, PAGE_LIMIT
from app.extensions import db
from app.models import User, ApiKey, GenEmail
from app.utils import random_word


def test_error_without_pagination(flask_client):
    user = User.create(
        email="a@b.c", password="password", name="Test User", activated=True
    )
    db.session.commit()

    # create api_key
    api_key = ApiKey.create(user.id, "for test")
    db.session.commit()

    r = flask_client.get(
        url_for("api.get_aliases"), headers={"Authentication": api_key.code},
    )

    assert r.status_code == 400
    assert r.json["error"]


def test_success_with_pagination(flask_client):
    user = User.create(
        email="a@b.c", password="password", name="Test User", activated=True
    )
    db.session.commit()

    # create api_key
    api_key = ApiKey.create(user.id, "for test")
    db.session.commit()

    # create more aliases than PAGE_LIMIT
    for _ in range(PAGE_LIMIT + 1):
        GenEmail.create_new_random(user.id)
    db.session.commit()

    # get aliases on the 1st page, should return PAGE_LIMIT aliases
    r = flask_client.get(
        url_for("api.get_aliases", page_id=0), headers={"Authentication": api_key.code},
    )
    assert r.status_code == 200
    assert len(r.json["aliases"]) == PAGE_LIMIT

    # get aliases on the 2nd page, should return 2 aliases
    # as the total number of aliases is PAGE_LIMIT +2
    # 1 alias is created when user is created
    r = flask_client.get(
        url_for("api.get_aliases", page_id=1), headers={"Authentication": api_key.code},
    )
    assert r.status_code == 200
    assert len(r.json["aliases"]) == 2