import json
import os
import random
import string
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
print(BASE_DIR)


def generate_user_id():
    random_letters = "".join(random.choices(string.digits, k=10))
    return int(random_letters + "00000")


def get_firstname(username):
    firstname = "".join(c for c in username if c.isalpha())
    return firstname if firstname else "User"


with open(os.path.join(BASE_DIR, "usernames.json"), "r") as file:
    usernames = json.load(file)

users = []
for username in usernames:
    user = {
        "userID": generate_user_id(),
        "username": username,
        "firstname": get_firstname(username),
    }
    users.append(user)

with open(os.path.join(BASE_DIR, "users.json"), "w") as file:
    json.dump(users, file, indent=4)

print("Generated users.json with user data")
