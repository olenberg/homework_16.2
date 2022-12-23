import json


def load_users():
    with open('data/users.json', 'r', encoding='utf-8') as file:
        users = json.loads(file.read())
        return users


def load_orders():
    with open('data/orders.json', 'r', encoding='utf-8') as file:
        orders = json.loads(file.read())
        return orders


def load_offers():
    with open('data/offers.json', 'r', encoding='utf-8') as file:
        offers = json.loads(file.read())
        return offers
