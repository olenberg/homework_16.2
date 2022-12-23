import os
import json
from datetime import datetime
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from utils import load_users, load_orders, load_offers

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(25))
    phone = db.Column(db.String(25))


class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.String(100), db.ForeignKey('user.id'))
    executor_id = db.Column(db.String(100), db.ForeignKey('user.id'))

    customer = relationship('User', foreign_keys=[customer_id])
    executor = relationship('User', foreign_keys=[executor_id])


class Offer(db.Model):
    __tablename__ = 'offer'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    orders = relationship('Order')
    user = relationship('User')

with app.app_context():
    db.drop_all()
    db.create_all()

    users = []
    for user in load_users():
        users.append(User(
            id=user.get('id'),
            first_name=user.get('first_name'),
            last_name=user.get('last_name'),
            age=user.get('age'),
            email=user.get('email'),
            role=user.get('role'),
            phone=user.get('phone')
        ))

    orders = []
    for order in load_orders():
        orders.append(Order(
            id=order.get('id'),
            name=order.get('name'),
            description=order.get('description'),
            start_date=datetime.strptime(order.get('start_date'), "%m/%d/%Y").date(),
            end_date=datetime.strptime(order.get('end_date'), "%m/%d/%Y").date(),
            address=order.get('address'),
            price=order.get('price'),
            customer_id=order.get('customer_id'),
            executor_id=order.get('executor_id')
        ))

    offers = []
    for offer in load_offers():
        offers.append(Offer(
            id=offer.get('id'),
            order_id=offer.get('order_id'),
            executor_id=offer.get('executor_id')
        ))

    with db.session.begin():
        db.session.add_all(users)
        db.session.add_all(orders)
        db.session.add_all(offers)


@app.get('/users')
def get_users():
    users = User.query.all()
    response = []

    for user in users:
        response.append({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "age": user.age,
            "email": user.email,
            "role": user.role,
            "phone": user.phone
        })

    return json.dumps(response)


@app.get('/users/<int:id>')
def get_user(id):
    user = User.query.get(id)

    response = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "age": user.age,
        "email": user.email,
        "role": user.role,
        "pone": user.phone
    }

    return json.dumps(response)


@app.post('/users')
def create_user():
    content_type = request.headers.get('Content-Type')

    if (content_type == 'application/json'):
        json_request = request.json

    user = User(
        first_name=json_request.get('first_name'),
        last_name=json_request.get('last_name'),
        age=json_request.get('age'),
        email=json_request.get('email'),
        role=json_request.get('role'),
        phone=json_request.get('phone')
    )

    db.session.add(user)
    db.session.commit()

    return f'user with id {user.id} created'


@app.put('/users/<int:id>/update')
def update_user(id):
    content_type = request.headers.get('Content-Type')

    if (content_type == 'application/json'):
        json_request = request.json

    user = User.query.get(id)
    user.first_name = json_request.get('first_name')
    user.last_name = json_request.get('last_name')
    user.age = json_request.get('age')
    user.email = json_request.get('email')
    user.role = json_request.get('role')
    user.phone = json_request.get('phone')

    db.session.add(user)
    db.session.commit()

    return f'user with id {user.id} updated'


@app.delete('/users/<int:id>/delete')
def delete_user(id):
    user = User.query.get(id)

    db.session.delete(user)
    db.session.commit()

    return f'user with id {user.id} deleted'


@app.get('/orders')
def get_orders():
    orders = Order.query.all()
    response = []

    for order in orders:
        response.append({
            "id": order.id,
            "name": order.name,
            "description": order.description,
            "start_date": order.start_date.__str__(),
            "end_date": order.end_date.__str__(),
            "address": order.address,
            "price": order.price,
            "customer_id": order.customer_id,
            "executor_id": order.executor_id
        })

    return json.dumps(response, ensure_ascii=False)


@app.get('/orders/<int:id>')
def get_order(id):
    order = Order.query.get(id)

    response = {
        "id": order.id,
        "name": order.name,
        "description": order.description,
        "start_date": order.start_date.__str__(),
        "end_date": order.end_date.__str__(),
        "address": order.address,
        "price": order.price,
        "customer_id": order.customer_id,
        "executor_id": order.executor_id
    }

    return json.dumps(response, ensure_ascii=False)


@app.post('/orders')
def create_order():
    content_type = request.headers.get('Content-Type')

    if (content_type == 'application/json'):
        json_request = request.json

    order = Order(
        name=json_request.get('name'),
        description=json_request.get('description'),
        age=json_request.get('age'),
        start_date=json_request.get('start_date'),
        end_date=json_request.get('end_date'),
        address=json_request.get('address'),
        price=json_request.get('price'),
        customer_id=json_request.get('customer_id'),
        executor_id=json_request.get('executor_id'),
    )

    db.session.add(order)
    db.session.commit()

    return f'user with id {order.id} created'


@app.put('/orders/<int:id>/update')
def update_order(id):
    content_type = request.headers.get('Content-Type')

    if (content_type == 'application/json'):
        json_request = request.json

    order = Order.query.get(id)
    order.name = json_request.get('name'),
    order.description = json_request.get('description'),
    order.age = json_request.get('age'),
    order.start_date = json_request.get('start_date'),
    order.end_date = json_request.get('end_date'),
    order.address = json_request.get('address'),
    order.price = json_request.get('price'),
    order.customer_id = json_request.get('customer_id'),
    order.executor_id = json_request.get('executor_id'),

    db.session.add(order)
    db.session.commit()

    return f'user with id {order.id} updated'


@app.delete('/orders/<int:id>/delete')
def delete_order(id):
    order = Order.query.get(id)

    db.session.delete(order)
    db.session.commit()

    return f'user with id {order.id} deleted'


@app.get('/offers')
def get_offers():
    offers = Offer.query.all()
    response = []

    for offer in offers:
        response.append({
            "id": offer.id,
            "order_id": offer.order_id,
            "executor_id": offer.executor_id,
        })

    return json.dumps(response)


@app.get('/offers/<int:id>')
def get_offer(id):
    offer = Offer.query.get(id)

    response = {
        "id": offer.id,
        "order_id": offer.order_id,
        "executor_id": offer.executor_id,
    }

    return json.dumps(response)


@app.post('/offers')
def create_offer():
    content_type = request.headers.get('Content-Type')

    if (content_type == 'application/json'):
        json_request = request.json

    offer = Offer(
        order_id=json_request.get('order_id'),
        executor_id=json_request.get('executor_id')
    )

    db.session.add(offer)
    db.session.commit()

    return f'user with id {offer.id} created'


@app.put('/offers/<int:id>/update')
def update_offer(id):
    content_type = request.headers.get('Content-Type')

    if (content_type == 'application/json'):
        json_request = request.json

    offer = Offer.query.get(id)
    offer.order_id = json_request.get('order_id')
    offer.executor_id = json_request.get('executor_id')

    db.session.add(offer)
    db.session.commit()

    return f'user with id {offer.id} updated'


@app.delete('/offers/<int:id>/delete')
def delete_offer(id):
    offer = Offer.query.get(id)

    db.session.delete(offer)
    db.session.commit()

    return f'user with id {offer.id} deleted'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
