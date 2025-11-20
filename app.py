"""
Flask web application for Moving Forward to New Beginnings (MFTNB).

This lightweight web app provides a friendly experience for potential moving
clients.  Visitors can explore packing and moving tips, build an inventory
of their belongings using an interactive form, and submit a booking request
that feeds back to the server (displayed on a confirmation page for now).

The goal of this example is to demonstrate how MFTNB could enhance
customer engagement on mftnb.com with a modern, responsive and helpful tool.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
import datetime

def compute_estimate(bedrooms: int, stairs_origin: int, stairs_destination: int,
                     heavy_items: int, distance_km: float, peak_season: bool = False):
    """
    Compute an estimated number of movers, total hours and cost for a move.

    The calculation is based on guidelines from professional moving resources.  

    - Crew size comes from typical recommendations: two movers for small homes, 
      three for medium homes and four for larger homes【159051122869171†L167-L173】.  
    - Job duration uses the load/unload estimates compiled by HireAHelper and Qshark:
      a studio/one‑bedroom move takes around 4 hours, a two‑bedroom move around 6
      hours, a three bedroom about 8 hours and larger homes 10 hours【940396082598849†L210-L222】【426727494212747†L119-L163】.
      Extra time is added for heavy items and flights of stairs【940396082598849†L210-L222】.
    - Travel time is calculated from the round‑trip distance divided by an
      average driving speed (approx. 50 km/h).  A fuel surcharge is added based
      on federal mileage rates (72 cents/km) or a flat local fee【701723300189565†L243-L249】【751482581235258†L71-L78】.
    - Hourly rates are derived from Western Canadian moving cost data: two movers
      with a truck cost roughly $130‑$150/hour【701723300189565†L150-L159】.  The
      calculation uses $140/hour for two movers, $160/hour for three movers and
      $180/hour for four movers.  During peak moving season (June–August),
      hourly rates are increased by 20%【701723300189565†L220-L228】.

    Returns a tuple of (movers, hours, cost).
    """
    # Determine crew size
    if bedrooms <= 1:
        movers = 2
    elif bedrooms == 2:
        movers = 3
    else:
        movers = 4

    # Base hours based on home size
    if bedrooms <= 1:
        hours = 4.0
    elif bedrooms == 2:
        hours = 6.0
    elif bedrooms == 3:
        hours = 8.0
    else:
        hours = 10.0

    # Add extra time for heavy items (0.5 hours each)
    hours += 0.5 * heavy_items

    # Add travel time: round‑trip distance / average speed (km/h)
    hours += distance_km / 50.0

    # Add time for stairs: 0.5 hours per flight of stairs at each location
    hours += 0.5 * (stairs_origin + stairs_destination)

    # Determine hourly rate
    if movers == 2:
        hourly_rate = 140.0
    elif movers == 3:
        hourly_rate = 160.0
    else:
        hourly_rate = 180.0

    # Peak season adjustment (20% increase)
    if peak_season:
        hourly_rate *= 1.2

    cost = hours * hourly_rate

    # Fuel surcharge: flat $40 for short distances (<100 km), otherwise mileage
    if distance_km <= 100:
        cost += 40.0
    else:
        cost += distance_km * 0.72

    return movers, round(hours, 1), round(cost, 2)


def create_app():
    """Factory to create and configure the Flask application."""
    app = Flask(__name__)
    # Secret key required for session management; this should be changed for production.
    app.secret_key = "replace-with-a-secure-random-key"

    @app.route("/")
    def index():
        """Homepage introducing MFTNB and linking to other tools."""
        return render_template("index.html")

    @app.route("/inventory", methods=["GET", "POST"])
    def inventory():
        """Form for users to build a list of items they plan to move."""
        if request.method == "POST":
            # The form sends a JSON payload from the client-side script.  We'll
            # extract it from the hidden field 'inventory_data'.
            inventory_data = request.form.get('inventory_data', '')
            session['inventory_data'] = inventory_data
            return redirect(url_for('booking'))
        return render_template("inventory.html")

    @app.route("/tips")
    def tips():
        """Display packing and moving tips compiled from authoritative sources."""
        # Define a list of dictionaries representing each tip.  When updating
        # these tips, be sure to cite sources in the final answer for user
        # transparency.  The citations are not displayed in the website itself.
        tips_list = [
            {
                "title": "Choose the Right Box",
                "body": (
                    "Use a variety of box sizes to suit different items. Pack heavy items like books "
                    "in small boxes and lighter items such as linens in larger boxes. Specialized kits "
                    "for dishes, glassware and wardrobe items keep fragile belongings safe."
                ),
            },
            {
                "title": "Group Items and Pack by Room",
                "body": (
                    "When packing, group similar items together and organize boxes by room (e.g. "
                    "kitchen, master bedroom). Prepare a separate essentials box for items you'll need "
                    "right away at your new home like toiletries, phone chargers and bedding."
                ),
            },
            {
                "title": "Label Every Box",
                "body": (
                    "Label boxes clearly with both a description of the contents and the room they're "
                    "destined for. Numbering each box and keeping a master inventory list helps track "
                    "your belongings. Mark boxes containing breakables as ‘FRAGILE’."
                ),
            },
            {
                "title": "Seal Boxes Securely",
                "body": (
                    "Tape the top and bottom seams of each box rather than just folding the flaps. "
                    "Choose a strong packing tape capable of holding the weight of your heaviest items."
                ),
            },
            {
                "title": "Don't Overload Boxes",
                "body": (
                    "Keep box weights under roughly 50 lbs to prevent injuries and avoid crushed contents. "
                    "Use proper lifting aids like gloves or a forearm forklift for heavier objects."
                ),
            },
            {
                "title": "Disassemble Furniture Carefully",
                "body": (
                    "Take apart furniture when possible and store the hardware (nuts, bolts, screws) in "
                    "labelled bags. Use moving blankets to protect pieces from scratches during transit."
                ),
            },
            {
                "title": "Load Your Truck Strategically",
                "body": (
                    "Place heavier boxes and furniture at the bottom and toward the front of the truck to "
                    "maintain stability. Stack lighter boxes on top. Load items you will need first last "
                    "so they’re easily accessible at your destination."
                ),
            },
            {
                "title": "Take a Video of Your Home Contents",
                "body": (
                    "Before packing begins, record a quick video walkthrough of your home. This will help "
                    "you verify that everything arrives safely and can document damage for insurance claims "
                    "if needed."
                ),
            },
            {
                "title": "Sort and Declutter",
                "body": (
                    "Reduce moving costs by touching every item you own and deciding whether it should move "
                    "with you. Donate, sell or dispose of things you no longer need."
                ),
            },
            {
                "title": "Gather Supplies Early",
                "body": (
                    "If you’re doing your own packing, gather boxes, bubble wrap, paper and markers well "
                    "ahead of moving day. Don’t forget to schedule pickup or delivery of specialty boxes "
                    "and packing kits if required."
                ),
            },
        ]
        return render_template("tips.html", tips=tips_list)

    @app.route("/booking", methods=["GET", "POST"])
    def booking():
        """
        Collect booking information, estimate move requirements, and redirect
        the user to a confirmation page.  Users provide basic contact info
        alongside details about their home size, stairs, heavy items and travel
        distance.  The estimate is computed server‑side and stored in the session.
        """
        if request.method == "POST":
            # Basic contact details
            session['name'] = request.form.get('name', '')
            session['email'] = request.form.get('email', '')
            session['phone'] = request.form.get('phone', '')
            session['move_date'] = request.form.get('move_date', '')
            session['origin'] = request.form.get('origin', '')
            session['destination'] = request.form.get('destination', '')
            session['notes'] = request.form.get('notes', '')

            # Moving parameters
            try:
                bedrooms = int(request.form.get('bedrooms', '1'))
                stairs_origin = int(request.form.get('stairs_origin', '0'))
                stairs_destination = int(request.form.get('stairs_destination', '0'))
                heavy_items = int(request.form.get('heavy_items', '0'))
                distance_km = float(request.form.get('distance_km', '0'))
            except ValueError:
                flash('Please provide valid numbers for bedrooms, stairs, heavy items and distance.')
                return redirect(url_for('booking'))

            # Determine if the date falls within peak season (June–August)
            peak = False
            try:
                if session['move_date']:
                    date_obj = datetime.datetime.strptime(session['move_date'], '%Y-%m-%d').date()
                    if date_obj.month in (6, 7, 8):
                        peak = True
            except Exception:
                # If parsing fails, assume non‑peak
                peak = False

            # Compute estimate and store in session
            movers, hours, cost = compute_estimate(bedrooms, stairs_origin,
                                                  stairs_destination, heavy_items,
                                                  distance_km, peak)
            session['estimate'] = {
                'movers': movers,
                'hours': hours,
                'cost': cost,
                'bedrooms': bedrooms,
                'stairs_origin': stairs_origin,
                'stairs_destination': stairs_destination,
                'heavy_items': heavy_items,
                'distance_km': distance_km,
                'peak_season': peak,
            }

            return redirect(url_for('confirmation'))

        return render_template("booking.html")

    @app.route("/confirmation")
    def confirmation():
        """Show a summary of the user's booking and inventory data."""
        # Retrieve data from the session.  In a production app you would
        # persist this in a database and trigger a backend workflow.
        inventory_json = session.get('inventory_data', '')
        # Parse inventory JSON if available
        import json
        try:
            inventory_data = json.loads(inventory_json) if inventory_json else []
        except Exception:
            inventory_data = []
        booking_data = {
            'name': session.get('name', ''),
            'email': session.get('email', ''),
            'phone': session.get('phone', ''),
            'move_date': session.get('move_date', ''),
            'origin': session.get('origin', ''),
            'destination': session.get('destination', ''),
            'notes': session.get('notes', ''),
        }
        estimate = session.get('estimate', None)
        return render_template("confirmation.html", inventory_data=inventory_data,
                               booking=booking_data, estimate=estimate)

    return app


if __name__ == "__main__":
    app = create_app()
    # Run the app on port 5000 by default.  Set debug=True for development.
    app.run(host="0.0.0.0", port=5000, debug=True)