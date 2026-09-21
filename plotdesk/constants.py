import os

ADMIN_USERNAMES = {"admin@plotdesk.app"}
SITE_COUNTER_KEY = "garden_plot_sequence"

DEFAULT_CROP_FOCUSES = [
    {"name": "Vegetables"},
    {"name": "Herbs"},
    {"name": "Fruit trees"},
    {"name": "Flowers / pollinator beds"},
    {"name": "Community orchard"},
    {"name": "Mixed / general"},
]

DEFAULT_FACILITIES = [
    {"name": "Raised beds"},
    {"name": "Water tap"},
    {"name": "Tool shed"},
    {"name": "Compost bay"},
    {"name": "Greenhouse"},
]

DEFAULT_STATUSES = [
    {"status": "Pending Review"},
    {"status": "Approved"},
    {"status": "Active"},
    {"status": "On Hold"},
    {"status": "Closed"},
]


def load_env_file():
    if os.path.exists("env.py"):
        import env  # noqa: F401
