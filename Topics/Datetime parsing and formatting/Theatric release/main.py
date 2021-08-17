from datetime import datetime


def get_release_date(release_str):
    return datetime.strptime(release_str.split(": ")[-1], "%d %B %Y")
