# The Haven Los Angeles

The Haven is a hotel booking and operations demo for a fictional boutique hotel in downtown Los Angeles. Guests can explore the property and make reservations, while front-desk staff and managers have their own dashboards.

## Run the website in Jupyter Notebook

1. Download or clone the entire repository to your computer. Use Python 3.10 or newer.
2. Open [Launch website.ipynb](Launch%20website.ipynb) in your local Jupyter Notebook or JupyterLab.
3. In the launch cell, set `project` to the folder containing `app.py` and `launch_hotel.py`. If the notebook is already running from that folder, use:

   ```python
   project = Path.cwd()
   ```

4. Install the dependencies once by running this in a separate notebook cell from the project folder:

   ```python
   %pip install -r requirements.txt
   ```

5. Run the launch cell and click **Open The Haven** when it appears. Keep the notebook kernel running while you use the site.

The app creates a SQLite demo database on first launch if one is missing.

## Demo accounts

On the hotel homepage, select **Sign in** and choose the matching role.

| Role | Username | Password | What to try |
| --- | --- | --- | --- |
| Customer | `customer` | `customer123` | Book a room or facility and review your itemized folio. |
| Staff | `staff` | `staff123` | View the guest roster and room inventory, then update a work order. |
| Manager | `manager` | `manager123` | Explore revenue trends, facility usage, and staff feedback. |

## Website features

- **Hotel website** — Browse four room types and nine facilities, including restaurants, a cedar bathhouse, a fitness studio, and meeting and event spaces. Check room availability by dates and guest count.
- **Customer portal** — Create an account, book a room or reserve a facility, select a late check-out option, and review charges and simulated payments.
- **Staff dashboard** — View the guest roster, room inventory, and occupancy. Update guest requests as pending, in progress, or completed.
- **Manager dashboard** — Review weekly, monthly, and yearly revenue trends, charges by category, top-spending guests, facility usage, and staff feedback. Managers can also access the staff dashboard.

## Try the booking workflow

1. On the homepage, select your dates and guest count, then click **Check availability**.
2. Choose a room and sign in as **Customer**. Confirm the booking in **My stay** and check your folio for the room charge.
3. Sign out and sign in as **Staff** to find the reservation in the guest roster.

## Tech stack

- **Backend** — Python and Flask
- **Frontend** — Jinja templates, CSS, and JavaScript
- **Database** — SQLite
- **Reporting** — Chart.js, loaded from a CDNeservations, folios, and payments
- **Reporting** — Chart.js for manager charts, loaded from a CDN
