from app import db
from app.models import User, Ticket


def register(client, name="Test User", email="test@example.com", password="password123"):
    return client.post(
        "/register",
        data={
            "name": name,
            "email": email,
            "password": password
        },
        follow_redirects=True
    )


def login(client, email="test@example.com", password="password123"):
    return client.post(
        "/login",
        data={
            "email": email,
            "password": password
        },
        follow_redirects=True
    )


def test_register_user(client, app):
    response = register(client)

    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        assert user is not None
        assert user.name == "Test User"


def test_duplicate_registration(client):
    register(client)

    response = register(client)

    assert b"Email is already registered" in response.data


def test_valid_login(client):
    register(client)

    response = login(client)

    assert response.status_code == 200
    assert b"Support Ticket Dashboard" in response.data


def test_invalid_login(client):
    register(client)

    response = login(client, password="wrongpassword")

    assert b"Invalid email or password" in response.data


def test_dashboard_requires_login(client):
    response = client.get("/", follow_redirects=True)

    assert response.status_code == 200
    assert b"Login" in response.data


def test_create_ticket(client, app):
    register(client)
    login(client)

    response = client.post(
        "/tickets/add",
        data={
            "title": "Test Ticket",
            "description": "Testing ticket creation",
            "priority": "High"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Ticket created successfully" in response.data

    with app.app_context():
        ticket = Ticket.query.filter_by(title="Test Ticket").first()
        assert ticket is not None
        assert ticket.priority == "High"
        assert ticket.status == "Open"


def test_edit_ticket(client, app):
    register(client)
    login(client)

    client.post(
        "/tickets/add",
        data={
            "title": "Original Ticket",
            "description": "Original description",
            "priority": "Low"
        }
    )

    with app.app_context():
        ticket = Ticket.query.filter_by(title="Original Ticket").first()
        ticket_id = ticket.id

    response = client.post(
        f"/tickets/{ticket_id}/edit",
        data={
            "title": "Updated Ticket",
            "description": "Updated description",
            "priority": "High",
            "status": "In Progress"
        },
        follow_redirects=True
    )

    assert b"Ticket updated successfully" in response.data

    with app.app_context():
        updated_ticket = db.session.get(Ticket, ticket_id)

        assert updated_ticket.title == "Updated Ticket"
        assert updated_ticket.priority == "High"
        assert updated_ticket.status == "In Progress"


def test_delete_ticket(client, app):
    register(client)
    login(client)

    client.post(
        "/tickets/add",
        data={
            "title": "Delete Me",
            "description": "Ticket to delete",
            "priority": "Medium"
        }
    )

    with app.app_context():
        ticket = Ticket.query.filter_by(title="Delete Me").first()
        ticket_id = ticket.id

    response = client.post(
        f"/tickets/{ticket_id}/delete",
        follow_redirects=True
    )

    assert b"Ticket deleted successfully" in response.data

    with app.app_context():
        ticket = db.session.get(Ticket, ticket_id)
        assert ticket is None