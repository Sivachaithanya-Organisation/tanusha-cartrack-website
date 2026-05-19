from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecret-sportscar-key-2024'

CARS = [
    {
        "id": 1,
        "name": "Ferrari 296 GTB",
        "brand": "Ferrari",
        "price": 322000,
        "year": 2024,
        "horsepower": 819,
        "top_speed": 330,
        "0_to_100": 2.9,
        "engine": "3.0L V6 Hybrid",
        "color": "Rosso Corsa",
        "category": "supercar",
        "in_stock": True,
        "image_color": "#CC0000",
        "badge": "BESTSELLER",
    },
    {
        "id": 2,
        "name": "Lamborghini Huracán EVO",
        "brand": "Lamborghini",
        "price": 287000,
        "year": 2024,
        "horsepower": 630,
        "top_speed": 325,
        "0_to_100": 2.9,
        "engine": "5.2L V10",
        "color": "Giallo Orion",
        "category": "supercar",
        "in_stock": True,
        "image_color": "#F5A623",
        "badge": "HOT",
    },
    {
        "id": 3,
        "name": "Porsche 911 Turbo S",
        "brand": "Porsche",
        "price": 216000,
        "year": 2024,
        "horsepower": 650,
        "top_speed": 330,
        "0_to_100": 2.7,
        "engine": "3.8L Flat-6 Turbo",
        "color": "GT Silver",
        "category": "sports",
        "in_stock": True,
        "image_color": "#B0B8C1",
        "badge": "NEW",
    },
    {
        "id": 4,
        "name": "McLaren 720S",
        "brand": "McLaren",
        "price": 299000,
        "year": 2024,
        "horsepower": 720,
        "top_speed": 341,
        "0_to_100": 2.8,
        "engine": "4.0L V8 Twin-Turbo",
        "color": "Papaya Spark",
        "category": "supercar",
        "in_stock": False,
        "image_color": "#FF5F00",
        "badge": "LIMITED",
    },
    {
        "id": 5,
        "name": "Bugatti Chiron",
        "brand": "Bugatti",
        "price": 3200000,
        "year": 2024,
        "horsepower": 1479,
        "top_speed": 420,
        "0_to_100": 2.4,
        "engine": "8.0L W16 Quad-Turbo",
        "color": "Atlantic Blue",
        "category": "hypercar",
        "in_stock": True,
        "image_color": "#003087",
        "badge": "ULTRA RARE",
    },
    {
        "id": 6,
        "name": "Mercedes-AMG GT 63 S",
        "brand": "Mercedes",
        "price": 162000,
        "year": 2024,
        "horsepower": 630,
        "top_speed": 315,
        "0_to_100": 3.2,
        "engine": "4.0L V8 Biturbo",
        "color": "Obsidian Black",
        "category": "sports",
        "in_stock": True,
        "image_color": "#1A1A2E",
        "badge": "VALUE PICK",
    },
]

ORDERS = []

@app.route('/')
def index():
    return render_template('index.html', cars=CARS)

@app.route('/car/<int:car_id>')
def car_detail(car_id):
    car = next((c for c in CARS if c['id'] == car_id), None)
    if not car:
        return redirect(url_for('index'))
    return render_template('detail.html', car=car)

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    cart_cars = []
    total = 0
    for item in cart_items:
        car = next((c for c in CARS if c['id'] == item['car_id']), None)
        if car:
            cart_cars.append({'car': car, 'qty': item['qty']})
            total += car['price'] * item['qty']
    return render_template('cart.html', cart_cars=cart_cars, total=total)

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    car_id = data.get('car_id')
    cart = session.get('cart', [])
    for item in cart:
        if item['car_id'] == car_id:
            item['qty'] += 1
            session['cart'] = cart
            return jsonify({'success': True, 'count': sum(i['qty'] for i in cart)})
    cart.append({'car_id': car_id, 'qty': 1})
    session['cart'] = cart
    return jsonify({'success': True, 'count': sum(i['qty'] for i in cart)})

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    data = request.get_json()
    car_id = data.get('car_id')
    cart = session.get('cart', [])
    cart = [i for i in cart if i['car_id'] != car_id]
    session['cart'] = cart
    return jsonify({'success': True, 'count': sum(i['qty'] for i in cart)})

@app.route('/api/cart/count')
def cart_count():
    cart = session.get('cart', [])
    return jsonify({'count': sum(i['qty'] for i in cart)})

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        data = request.form
        cart_items = session.get('cart', [])
        order_id = str(uuid.uuid4())[:8].upper()
        total = sum(
            next((c['price'] for c in CARS if c['id'] == i['car_id']), 0) * i['qty']
            for i in cart_items
        )
        order = {
            'id': order_id,
            'name': data.get('name'),
            'email': data.get('email'),
            'items': cart_items,
            'total': total,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        }
        ORDERS.append(order)
        session['cart'] = []
        session['last_order'] = order
        return redirect(url_for('confirmation'))
    cart_items = session.get('cart', [])
    total = sum(
        next((c['price'] for c in CARS if c['id'] == i['car_id']), 0) * i['qty']
        for i in cart_items
    )
    return render_template('checkout.html', total=total)

@app.route('/confirmation')
def confirmation():
    order = session.get('last_order')
    return render_template('confirmation.html', order=order)

@app.route('/api/filter')
def filter_cars():
    category = request.args.get('category', 'all')
    sort = request.args.get('sort', 'default')
    filtered = CARS if category == 'all' else [c for c in CARS if c['category'] == category]
    if sort == 'price_asc':
        filtered = sorted(filtered, key=lambda x: x['price'])
    elif sort == 'price_desc':
        filtered = sorted(filtered, key=lambda x: x['price'], reverse=True)
    elif sort == 'hp':
        filtered = sorted(filtered, key=lambda x: x['horsepower'], reverse=True)
    return jsonify(filtered)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
