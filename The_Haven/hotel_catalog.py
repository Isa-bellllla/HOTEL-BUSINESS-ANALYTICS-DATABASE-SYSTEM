"""The Haven's room and venue catalog, shared by new and existing databases."""

# Each entry pairs its original name with the current seed record. Keeping the
# original names lets us update this catalog without replacing referenced rows.
ROOM_TYPES = (
    ("Corner Studio with Balcony",
     ("Corner King Studio", 289, 2, 1,
      "A king bed, an oak writing desk and a private balcony for slow mornings.",
      "/static/images/corner-king.webp")),
    ("Two-Queen Guestroom",
     ("Deluxe Two Queens", 229, 4, 0,
      "Two queen beds, natural linen and a walk-in rain shower.",
      "/static/images/deluxe-queens.webp")),
    ("Executive One-Bedroom Suite",
     ("One-Bedroom Suite", 399, 3, 1,
      "A separate sitting room, a deep soaking tub and an espresso station.",
      "/static/images/one-bedroom.webp")),
    ("Light-Filled Family Suite",
     ("The Family Suite", 539, 5, 1,
      "A generous corner suite with a dining nook, daybeds and a pantry.",
      "/static/images/family.webp")),
)

FACILITIES = (
    ("Nami Noodle & Rice Bar",
     ("Nami Noodle Bar", "Asian Food", 42, 40,
      "House-made noodles, dashi broths and charcoal skewers at a warm oak counter.",
      "/static/images/nami.webp")),
    ("Casa Olivo Tapas & Wine",
     ("Oliva Tapas & Wine", "Spain Food", 52, 50,
      "Spanish small plates, sherry and California wines in an intimate dining room.",
      "/static/images/oliva.webp")),
    ("The Daily Roast & Bakery",
     ("Lobby Coffee & Bakery", "Western Brunch", 32, 60,
      "Local coffee, fresh pastries and a California breakfast in the morning light.",
      "/static/images/coffee.webp")),
    ("Oak & Timber Bistro",
     ("Paloma Kitchen", "Neighborhood Bistro", 62, 55,
      "A seasonal California dining room serving market vegetables and wood-fired mains.",
      "/static/images/paloma.webp")),
    ("The Club Room (Cards & Board Games)",
     ("The Club Room", "Board Game / Social Lounge", 35, 24,
      "A relaxed lounge for chess, cards and board games with friends.",
      "/static/images/club.webp")),
    ("The Bathhouse & Sauna",
     ("Cedar Spa & Bathhouse", "Bathhouse & Spa", 60, 25,
      "A cedar dry sauna, a warm soaking bath and a quiet space for tea.",
      "/static/images/cedar.webp")),
    ("Studio Fitness & Squash Court",
     ("Fitness Studio & Squash", "Fitness & Squash", 32, 30,
      "Reserve time in the light-filled fitness studio and indoor squash court.",
      "/static/images/fitness.webp")),
    ("The North Forum (Event Hall)",
     ("The Grand Room", "Event Hall", 425, 300,
      "A flexible, oak-lined event hall for receptions, dinners and gatherings.",
      "/static/images/grand.webp")),
    ("The Library Conference Room",
     ("The Library Boardroom", "Meeting Room", 145, 18,
      "A private meeting room with a presentation display and seating for 18.",
      "/static/images/library.webp")),
)

FACILITY_SECTIONS = (
    ("dining", "Dining", "From morning coffee to dinner.",
     {"Asian Food": "Japanese noodle bar", "Spain Food": "Tapas & wine",
      "Western Brunch": "Coffee & breakfast", "Neighborhood Bistro": "California dining"}),
    ("wellness", "Wellness", "Make time to unwind.",
     {"Bathhouse & Spa": "Sauna & soaking bath", "Fitness & Squash": "Fitness & squash"}),
    ("meetings", "Meetings & Social", "Spaces to bring people together.",
     {"Event Hall": "Event hall", "Meeting Room": "Boardroom",
      "Board Game / Social Lounge": "Games & lounge"}),
)

EXTENDED_CHECKOUT_RATE = 65
DINING_DISCOUNT = 0.5


def update_catalog(conn):
    for original, room in ROOM_TYPES:
        name, rate, _, _, description, image = room
        conn.execute(
            "UPDATE room_type SET type_name=?, base_rate=?, description=?, image_url=? WHERE type_name=?",
            (name, rate, description, image, original),
        )
    for original, facility in FACILITIES:
        name, _, rate, _, description, image = facility
        conn.execute(
            "UPDATE facility SET facility_name=?, hourly_rate=?, description=?, image_url=? WHERE facility_name=?",
            (name, rate, description, image, original),
        )
