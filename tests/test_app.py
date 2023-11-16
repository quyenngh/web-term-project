from app import Order, ProductsOrder, app, db
from models import Product, User


def test_config():
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///test.db"


def test_routing(test_client):
    urls = ["/", "/about", "/instructions", "/login", "/signup"]
    for url in urls:
        response = test_client.get(url)
        assert response.status_code == 200


def test_signup_successful(test_client):
    new_user = {
        "username": "test1",
        "password": "test1234",
        "confirm_password": "test1234",
    }
    response = test_client.post("/signup", data=new_user)
    assert response.status_code == 302
    assert User.query.filter_by(username=new_user["username"]).first() is not None


def test_signup_password_mismatch(test_client):
    new_user = {
        "username": "test2",
        "password": "test1234",
        "confirm_password": "test12345",
    }
    response = test_client.post("/signup", data=new_user)
    assert response.status_code == 200
    assert "Passwords do not match" in response.data.decode("utf-8")


def test_signup_username_taken(test_client):
    new_user = {
        "username": "test3",
        "password": "test1234",
        "confirm_password": "test1234",
    }
    response = test_client.post("/signup", data=new_user)
    assert response.status_code == 302
    assert User.query.filter_by(username=new_user["username"]).first() is not None
    response = test_client.post("/signup", data=new_user)
    assert response.status_code == 200
    assert "Username already taken" in response.data.decode("utf-8")


def test_login_successful(test_client):
    new_user = {
        "username": "test4",
        "password": "test1234",
        "confirm_password": "test1234",
    }
    response = test_client.post("/signup", data=new_user)

    login_user = {"username": "test4", "password": "test1234"}
    response = test_client.post("/login", data=login_user, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/dashboard"
    assert b"Hello test4!" in response.data


def test_login_incorrect_password(test_client):
    new_user = {
        "username": "test5",
        "password": "test1234",
        "confirm_password": "test1234",
    }
    response = test_client.post("/signup", data=new_user)

    login_user = {"username": "test5", "password": "wrongpassword"}
    response = test_client.post("/login", data=login_user)
    assert response.status_code == 200
    assert response.request.path == "/login"
    assert b"Incorrect password" in response.data


def test_logout(test_client):
    new_user = {
        "username": "test6",
        "password": "test1234",
        "confirm_password": "test1234",
    }
    response = test_client.post("/signup", data=new_user)

    login_user = {"username": "test6", "password": "test1234"}
    response = test_client.post("/login", data=login_user, follow_redirects=True)

    response = test_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/home"


def test_products(test_client):
    green_tea = Product.query.filter_by(name="Green Tea").first()
    assert green_tea is not None
    assert green_tea.price == 1.0
    assert green_tea.category == "Tea"
    assert green_tea.description == "Classic green tea"
    assert green_tea.quantity == 10

    apple_juice = Product.query.filter_by(name="Apple Juice").first()
    assert apple_juice is not None
    assert apple_juice.price == 2.5
    assert apple_juice.category == "Fruit"
    assert apple_juice.description == "Fresh apple juice"
    assert apple_juice.quantity == 2


def test_update_quantity(test_client):
    order = Order(name="Test Order", address="Test Address")
    product_orders = [
        ProductsOrder(product_id=1, quantity=3),
        ProductsOrder(product_id=2, quantity=4),
        ProductsOrder(product_id=3, quantity=7),
    ]
    order.products = product_orders

    db.session.add(order)
    db.session.commit()

    response = test_client.post(
        "/update_quantity",
        data={"order_id": "1", "quantity[]": ["2", "3", ""]},
    )

    assert response.status_code == 302
    assert response.location == "/cart"

    updated_order = db.session.get(Order, 1)

    assert updated_order.products[0].quantity == 2
    assert updated_order.products[1].quantity == 3
    assert updated_order.products[2].quantity == 1


def test_delete_item(test_client):
    order = Order(name="Test Order", address="Test Address")
    product_order = ProductsOrder(product_id=1, quantity=3)
    order.products.append(product_order)

    db.session.add(order)
    db.session.commit()

    initial_product_order = (
        db.session.query(ProductsOrder)
        .filter_by(product_id=1, order_id=order.id)
        .first()
    )
    assert initial_product_order is not None

    response = test_client.post(
        "/delete_item",
        data={"product_id": "1", "order_id": str(order.id)},
    )

    assert response.status_code == 302
    assert response.location == "/cart"

    deleted_product_order = (
        db.session.query(ProductsOrder)
        .filter_by(product_id=1, order_id=order.id)
        .first()
    )
    assert deleted_product_order is None
