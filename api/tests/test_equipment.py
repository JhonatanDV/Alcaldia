import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User, Group
from api.models import Equipment

@pytest.mark.django_db
def test_equipment_crud():
    # Crear usuario con grupo Admin
    user = User.objects.create_user(username="tester", password="12345")
    admin_group = Group.objects.get_or_create(name="Admin")[0]
    user.groups.add(admin_group)
    user.save()

    client = APIClient()
    # Obtener token
    res = client.post("/api/token/", {"username": "tester", "password": "12345"}, format="json")
    access = res.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    # Crear
    res = client.post("/api/equipments/", {"code":"EQ001","name":"Laptop","location":"Oficina"}, format="json")
    assert res.status_code == 201

    # Listar
    res = client.get("/api/equipments/")
    assert res.status_code == 200
    assert len(res.data) == 1
