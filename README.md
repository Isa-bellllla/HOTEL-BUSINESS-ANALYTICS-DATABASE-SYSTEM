# The Haven Los Angeles

The Haven is a hotel booking and operations demo for a fictional boutique hotel in downtown Los Angeles. Guests can explore the property and make reservations, while front-desk staff and managers sign in to their own dashboards.

![The Haven terrace overlooking downtown Los Angeles](static/images/terrace.webp)

## Run locally

Download or clone the repository and open a terminal in the project folder. Use Python 3.10 or newer.

```bash
python3 -m pip install -r requirements.txt
python3 app.py
```

Open [The Haven in your browser](http://127.0.0.1:5000). On first launch, the app creates a SQLite database with sample bookings, billing history, and the demo accounts below.

## Demo accounts

Select **Sign in** in the top navigation and choose the matching role.

| Role | Username | Password | What to try |
| --- | --- | --- | --- |
| Customer | `customer` | `customer123` | Book a room or facility and review your itemized folio. |
| Staff | `staff` | `staff123` | View the guest roster and room inventory, then update a work order. |
| Manager | `manager` | `manager123` | Explore revenue trends, facility usage, and staff feedback. |

## Website features

- **Hotel website** — Explore four room types and nine facilities, including dining, a cedar bathhouse, a fitness studio, and meeting and event spaces. Search for available rooms by dates and guest count.
- **Customer portal** — Create an account, book a room or reserve a facility, select a late check-out option, and review charges and payments. The demo uses simulated payments.
- **Staff dashboard** — View the guest roster, room inventory, and occupancy. Update guest requests as pending, in progress, or completed.
- **Manager dashboard** — Review weekly, monthly, and yearly revenue trends, revenue by charge category, top-spending guests, facility usage, and staff feedback. Managers can also access the staff dashboard.

## Try the booking workflow

1. On the homepage, choose your dates and guest count, then select **Check availability**.
2. Select a room and sign in as **Customer**. Confirm the booking in **My stay** and check the room charge in your folio.
3. Sign out and sign in as **Staff** to find the reservation in the guest roster.

## Tech stack

- **Backend** — Python and Flask with session-based role checks
- **Frontend** — Jinja templates, CSS, and JavaScript
- **Database** — SQLite for guest accounts, inventory, reservations, folios, and payments
- **Reporting** — Chart.js for manager charts, loaded from a CDN
