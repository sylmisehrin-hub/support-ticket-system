from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from app.models import Ticket

main = Blueprint("main", __name__)


@main.route("/")
@login_required
def home():
    tickets = Ticket.query.filter_by(
        user_id=current_user.id
    ).all()

    total_tickets = len(tickets)

    open_tickets = sum(
        1 for ticket in tickets
        if ticket.status == "Open"
    )

    progress_tickets = sum(
        1 for ticket in tickets
        if ticket.status == "In Progress"
    )

    closed_tickets = sum(
        1 for ticket in tickets
        if ticket.status == "Closed"
    )

    high_priority = sum(
        1 for ticket in tickets
        if ticket.priority == "High"
    )

    return render_template(
        "dashboard.html",
        user=current_user,
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        progress_tickets=progress_tickets,
        closed_tickets=closed_tickets,
        high_priority=high_priority
    )

@main.route("/tickets")
@login_required
def tickets():
    user_tickets = Ticket.query.filter_by(
        user_id=current_user.id
    ).order_by(Ticket.created_at.desc()).all()

    return render_template(
        "tickets.html",
        tickets=user_tickets
    )


@main.route("/tickets/add", methods=["GET", "POST"])
@login_required
def add_ticket():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        priority = request.form.get("priority")

        if not title or not description:
            flash("Title and description are required.")
            return redirect(url_for("main.add_ticket"))

        ticket = Ticket(
            title=title,
            description=description,
            priority=priority,
            status="Open",
            user_id=current_user.id
        )

        db.session.add(ticket)
        db.session.commit()

        flash("Ticket created successfully.")
        return redirect(url_for("main.tickets"))

    return render_template("add_ticket.html")

@main.route("/tickets/<int:ticket_id>/edit", methods=["GET", "POST"])
@login_required
def edit_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if ticket.user_id != current_user.id:
        abort(403)

    if request.method == "POST":
        ticket.title = request.form.get("title")
        ticket.description = request.form.get("description")
        ticket.priority = request.form.get("priority")
        ticket.status = request.form.get("status")

        db.session.commit()

        flash("Ticket updated successfully.")
        return redirect(url_for("main.tickets"))

    return render_template("edit_ticket.html", ticket=ticket)


@main.route("/tickets/<int:ticket_id>/delete", methods=["POST"])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if ticket.user_id != current_user.id:
        abort(403)

    db.session.delete(ticket)
    db.session.commit()

    flash("Ticket deleted successfully.")
    return redirect(url_for("main.tickets"))