import csv
import json
import os
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from database import db
from models import (
    Feedback,
    Ingredient,
    Order,
    Product,
    ProductIngredient,
    ProductsOrder,
    User,
)


def create_db(product_file, ingredient_file):
    # Create all database tables
    with app.app_context():
        db.create_all()
        print("Create all tables successfully.")

        # Populate products from CSV file
        with open(product_file, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            next(reader)
            for row in reader:
                obj = Product(
                    name=row[0],
                    price=float(row[1]),
                    category=row[2],
                    description=row[3],
                    quantity=int(row[4]),
                )
                db.session.add(obj)
        db.session.commit()
        print("Successfully created all products.")

        # Populate ingredients from CSV file
        with open(ingredient_file, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            next(reader)
            for row in reader:
                obj = Ingredient(
                    name=row[0],
                    category=row[1],
                    description=row[2],
                    stock=int(row[3]),
                )
                db.session.add(obj)
        db.session.commit()
        print("Successfully created all ingredients.")


app = Flask(__name__)
app.instance_path = str(Path(".").resolve())
app.secret_key = "abcdefg"

# if __name__ == "__main__":
#     DB_NAME = "store"
# else:
#     DB_NAME = "test"
DB_NAME="freedb_reatea"

# app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql://freedb_reatea:$5Qha6Bc9RzUH!t@sql.freedb.tech/freedb_reatea"

login_manager = LoginManager(app)
app.instance_path = str(Path(".").resolve())
db.init_app(app)

# Create database and populate with initial data if it doesn't exist
# if not os.path.isfile(f"{DB_NAME}.db") and DB_NAME == "store":
# if not os.path.isfile(f"{DB_NAME}.db") and DB_NAME == "store":
# create_db("products.csv", "ingredients.csv")

# if DB_NAME == "test":
# create_db("test_products.csv", "ingredients.csv")

app.secret_key = "abcdefg"


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/menu")
def menu():
    # Retrieve all products from the database
    products = Product.query.all()
    categories = sorted(list(set([product.category for product in products])))
    product_dict = {}
    for category in categories:
        # Group products by category
        product_dict[category] = [
            product for product in products if product.category == category
        ]
    return render_template("menu.html", products=product_dict, categories=categories)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/instructions")
def contact():
    return render_template("instructions.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Retrieve the username and password from the form data
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if not user:
            return render_template("login.html", error="Username not found")

        elif user.password != password:
            return render_template("login.html", error="Incorrect password")

        else:
            login_user(user)
            session["username"] = user.username

            return redirect("dashboard")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Extract user data from the form
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        user_exists = User.query.filter_by(username=username).first()

        if user_exists:
            return render_template("signup.html", error="Username already taken")

        if password != confirm_password:
            return render_template("signup.html", error="Passwords do not match")

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("signup.html")

    

@app.route("/dashboard")
def dashboard():
    if current_user.is_authenticated:
        orders = Order.query.filter_by(name=current_user.username, completed=True).all()
        return render_template("dashboard.html", user=current_user, orders=orders)
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    logout_user()
    session.pop("username", None)
    return redirect(url_for("home"))




@app.route("/customize")
def customize():
    # Retrieve all ingredients from the database
    products = Ingredient.query.all()

    # Define the categories for the products
    categories = [
        "Tea Base",
        "Dairy",
        "Toppings",
        "Sweetener",
        "Sugar Level",
        "Ice Level",
    ]

    # Create a dictionary to store products categorized by their respective category
    product_dict = {}

    # Loop through each category
    for category in categories:
        # Filter the products based on the current category
        product_dict[category] = [
            product for product in products if product.category == category
        ]

    # Render the template 'customize1.html' and pass the product dictionary and categories as variables
    return render_template(
        "customize1.html", products=product_dict, categories=categories
    )


@app.route("/customize", methods=["POST"])
@login_required
def create_drink():
    data = request.json
    items = []

    # Loop through each category and validate the selected items
    for category in ("Tea Base", "Dairy", "Sweetener", "Sugar Level", "Ice Level"):
        if category not in data or len(data[category]) != 1:
            return (
                jsonify(
                    {"error": f"Category: '{category}' must have exactly one item"}
                ),
                400,
            )
        items.extend(data[category])

    # Validate the 'Toppings' category if present
    if "Toppings" in data:
        if len(data["Toppings"]) > 3:
            return jsonify({"error": "Category 'Toppings' must have 0-3 items"}), 400
        else:
            items.extend(data["Toppings"])

    # Generate a unique name for the custom drink
    base_name = "Custom"
    existing_custom_drinks_count = Product.query.filter(
        Product.name.like(f"{base_name}%")
    ).count()
    name = f"{base_name}{existing_custom_drinks_count + 1}"

    # Create a new custom product
    product = Product(
        name=name,
        price=7.0,
        category="Custom",
        description=", ".join(items),
        quantity=1,
    )

    # Add the selected ingredients to the custom product
    for ingredient_name in items:
        ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
        if ingredient is None:
            return jsonify({"error": f"Ingredient '{ingredient_name}' not found"}), 400

        product.ingredients.append(ingredient)

    db.session.add(product)
    db.session.commit()

    return jsonify({"url": url_for("menu")})



@app.route("/cart", defaults={"order_id": None})
@app.route("/cart/<int:order_id>")
def cart(order_id=None):
    def calculate_total(orders):
        return sum(order.total_price for order in orders)

    if order_id:
        order = db.session.get(Order, order_id)
    else:
        order = db.session.query(Order).order_by(Order.id.desc()).first()

        if order and order.completed:
            order = None

    order = [order] if order and not order.completed else []
    total = calculate_total(order)
    return render_template(
        "cart.html", orders=order, total=total, current_user=current_user
    )


@app.route("/delete_item", methods=["POST"])
def delete_item():
    # Get the product_id and order_id from the form data
    product_id = request.form.get("product_id")
    order_id = request.form.get("order_id")

    # Query the database for the ProductsOrder entry with the matching product_id and order_id
    product_order = (
        db.session.query(ProductsOrder)
        .filter(
            ProductsOrder.product_id == product_id, ProductsOrder.order_id == order_id
        )
        .first()
    )

    # If the ProductsOrder entry exists, delete it from the database
    if product_order:
        db.session.delete(product_order)
        db.session.commit()

    # Redirect to the cart page
    return redirect("/cart")


@app.route("/update_quantity", methods=["POST"])
def update_quantity():
    # Retrieve the order ID and quantities from the form data
    order_id = request.form.get("order_id")
    quantities = request.form.getlist("quantity[]")

    # Retrieve all product orders associated with the given order ID
    product_orders = db.session.query(ProductsOrder).filter_by(order_id=order_id).all()

    # Update the quantity for each product order
    for i, product_order in enumerate(product_orders):
        quantity = quantities[i]
        if quantity == "":
            quantity = 1
        else:
            quantity = int(quantity)
            if quantity < 1:
                quantity = 1
        product_order.quantity = quantity

    db.session.commit()

    # Redirect to the cart page
    return redirect("/cart")



@app.route('/cart', methods=['POST'])
def checkoutOrder():
    order_id = request.form.get('order_id')
    
    # Retrieve the order from the database
    order = Order.query.get(order_id)

    # Update the 'completed' column to True
    order.completed = True

    # Commit the changes to the database
    db.session.commit()

    # Redirect to the cart page or any other desired page
    return redirect('/checkout')



@app.route("/cancel", methods=["POST"])
def cancel_order():
    order_id = request.form.get("order_id")

    order = Order.query.get(order_id)
    db.session.delete(order)
    db.session.commit()

    return redirect("/cart")



@app.route("/checkout")
def checkout():
    return render_template("checkout.html")





@app.route("/order")
def order():
    menu = Product.query.all()
    return render_template("order.html", menu=menu)


@app.route("/order", methods=["POST"])
@login_required
def create_order():
    try:
        # Parse the JSON data from the request
        data = json.loads(request.get_json())
        if not data:
            return jsonify({"error": "No data provided"}), 400
    except:
        return jsonify({"error": "Invalid JSON"}), 400

    # Check if the required keys are present in the JSON data
    for key in ("name", "address", "products"):
        if key not in data:
            return jsonify({"error": f"The JSON is missing: {key}"}), 400

    # Check if the products list is empty
    if not data["products"]:
        return jsonify({"error": "No products provided"}), 400

    # Check if the name is provided
    if not data["name"]:
        return jsonify({"error": "No name provided"}), 400

    # Check if the address/note is provided
    if not data["address"]:
        return jsonify({"error": "No address/note provided"}), 400

    products = []
    for category in data["products"]:
        for product in data["products"][category]:
            # Retrieve the current product from the database
            current_product = (
                db.session.query(Product).filter_by(name=product["name"]).first()
            )
            # Check if the product exists
            if not current_product:
                return (
                    jsonify({"error": f"The product {product['name']} does not exist"}),
                    404,
                )
            products.append({"product": current_product, "count": product["count"]})

    # Create a new order with the provided name and address
    order = Order(
        name=data["name"],
        address=data["address"],
    )

    # Associate the products with the order and set the quantities
    for product in products:
        association = ProductsOrder(
            product=product["product"],
            order=order,
            quantity=product["count"],
        )
        db.session.add(association)
    db.session.add(order)
    db.session.commit()

    return jsonify({"location": url_for("cart")})


@app.route("/feedback")
def feedback():
    return render_template("feedback.html")


@app.route("/feedback", methods=["POST"])
def create_feedback():
    message = request.get_json()["message"]
    feedback = Feedback(message=message)

    db.session.add(feedback)
    db.session.commit()

    return redirect(url_for("feedback"))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
