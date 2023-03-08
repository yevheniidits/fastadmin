from fastadmin import register_admin_model_class, unregister_admin_model_class
from tests.api.fastapi.helpers import sign_in, sign_out
from tests.models.orms.tortoise.admins import EventModelAdmin


async def test_list(tortoise_superuser, tortoise_event, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)
    register_admin_model_class(EventModelAdmin, [tortoise_event.__class__])
    r = await fastapi_client.get(
        f"/api/list/{tortoise_event.__class__.__name__}",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] == 1
    item = data["results"][0]
    assert item["id"] == tortoise_event.id
    assert item["name"] == tortoise_event.name
    assert item["tournament_id"] == tortoise_event.tournament_id
    assert item["created_at"] == tortoise_event.created_at.isoformat()
    assert item["updated_at"] == tortoise_event.updated_at.isoformat()
    assert "participants" not in item  # no m2m2 fields on list

    unregister_admin_model_class([tortoise_event.__class__])
    await sign_out(fastapi_client, tortoise_superuser)


async def test_list_filters(tortoise_superuser, tortoise_event, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)
    register_admin_model_class(EventModelAdmin, [tortoise_event.__class__])
    r = await fastapi_client.get(
        f"/api/list/{tortoise_event.__class__.__name__}?name__icontains={tortoise_event.name[:2]}",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] == 1
    item = data["results"][0]
    assert item["id"] == tortoise_event.id

    r = await fastapi_client.get(
        f"/api/list/{tortoise_event.__class__.__name__}?name__icontains=invalid",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] == 0

    r = await fastapi_client.get(
        f"/api/list/{tortoise_event.__class__.__name__}?invalid__icontains={tortoise_event.name[:2]}",
    )
    assert r.status_code == 422, r.text

    unregister_admin_model_class([tortoise_event.__class__])
    await sign_out(fastapi_client, tortoise_superuser)


async def test_list_search(tortoise_superuser, tortoise_event, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)
    register_admin_model_class(EventModelAdmin, [tortoise_event.__class__])

    EventModelAdmin.search_fields = ["name"]
    r = await fastapi_client.get(
        f"/api/list/{tortoise_event.__class__.__name__}?search={tortoise_event.name[:2]}",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] == 1
    item = data["results"][0]
    assert item["id"] == tortoise_event.id

    r = await fastapi_client.get(
        f"/api/list/{tortoise_event.__class__.__name__}?search=invalid",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] == 0

    EventModelAdmin.search_fields = ["invalid"]
    r = await fastapi_client.get(
        f"/api/list/{tortoise_event.__class__.__name__}?search={tortoise_event.name[:2]}",
    )
    assert r.status_code == 422, r.text

    EventModelAdmin.search_fields = ()
    unregister_admin_model_class([tortoise_event.__class__])
    await sign_out(fastapi_client, tortoise_superuser)


async def test_list_sort_by(tortoise_superuser, tortoise_event, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)
    register_admin_model_class(EventModelAdmin, [tortoise_event.__class__])

    r = await fastapi_client.get(
        f"/api/list/{tortoise_event.__class__.__name__}?sort_by=-name",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] == 1

    r = await fastapi_client.get(
        f"/api/list/{tortoise_event.__class__.__name__}?sort_by=invalid",
    )
    assert r.status_code == 422, r.text

    EventModelAdmin.ordering = ["name"]
    r = await fastapi_client.get(
        f"/api/list/{tortoise_event.__class__.__name__}",
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data
    assert data["total"] == 1

    EventModelAdmin.ordering = ["invalid"]
    r = await fastapi_client.get(
        f"/api/list/{tortoise_event.__class__.__name__}",
    )
    assert r.status_code == 422, r.text

    EventModelAdmin.ordering = ()
    unregister_admin_model_class([tortoise_event.__class__])
    await sign_out(fastapi_client, tortoise_superuser)


async def test_list_select_related(tortoise_superuser, tortoise_event, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)
    register_admin_model_class(EventModelAdmin, [tortoise_event.__class__])

    EventModelAdmin.list_select_related = ["tournament_id"]
    r = await fastapi_client.get(
        f"/api/list/{tortoise_event.__class__.__name__}",
    )
    assert r.status_code == 200, r.text

    EventModelAdmin.list_select_related = ["invalid"]
    r = await fastapi_client.get(
        f"/api/list/{tortoise_event.__class__.__name__}",
    )
    assert r.status_code == 422, r.text

    EventModelAdmin.list_select_related = ()
    unregister_admin_model_class([tortoise_event.__class__])
    await sign_out(fastapi_client, tortoise_superuser)


async def test_list_display_fields(tortoise_superuser, tortoise_event, fastapi_client):
    await sign_in(fastapi_client, tortoise_superuser)
    register_admin_model_class(EventModelAdmin, [tortoise_event.__class__])

    EventModelAdmin.list_display = ["started", "name_with_price"]
    r = await fastapi_client.get(
        f"/api/list/{tortoise_event.__class__.__name__}",
    )
    assert r.status_code == 200, r.text

    EventModelAdmin.list_display = ["invalid"]
    r = await fastapi_client.get(
        f"/api/list/{tortoise_event.__class__.__name__}",
    )
    assert r.status_code == 200, r.text

    EventModelAdmin.list_display = ()
    unregister_admin_model_class([tortoise_event.__class__])
    await sign_out(fastapi_client, tortoise_superuser)


async def test_list_401(tortoise_superuser, tortoise_event, fastapi_client):
    tortoise_event = tortoise_event
    r = await fastapi_client.get(
        f"/api/list/{tortoise_event.__class__.__name__}",
    )
    assert r.status_code == 401, r.text


async def test_list_404(tortoise_superuser, tortoise_event, fastapi_client):
    unregister_admin_model_class([tortoise_event.__class__])
    await sign_in(fastapi_client, tortoise_superuser)
    r = await fastapi_client.get(
        f"/api/list/{tortoise_event.__class__.__name__}",
    )
    assert r.status_code == 404, r.text
    await sign_out(fastapi_client, tortoise_superuser)
