from flask_login import UserMixin

from database import db


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, nullable=False)

    ingredients = db.relationship(
        "Ingredient",
        secondary="product_ingredient",
        lazy="subquery",
        backref=db.backref("products", lazy=True),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "description": self.description,
            "ingredients": [ingredient.to_dict() for ingredient in self.ingredients],
        }


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    products = db.relationship("ProductsOrder", back_populates="order", cascade="all, delete-orphan")


    @property
    def total_price(self):
        if not self.products:
            return 0
        return round(
            sum(product.product.price * product.quantity for product in self.products),
            2,
        )

    def to_dict(self):
        return {
            "name": self.name,
            "address": self.address,
            "products": [
                {
                    "name": product.product_name,
                    "quantity": product.quantity,
                }
                for product in self.products
            ],
            "price": self.total_price,
        }

    def process(self):
        if self.completed:
            return

        for product_order in self.products:
            product = product_order.product
            if product.quantity < product_order.quantity:
                product_order.quantity = product.quantity
            product.quantity -= product_order.quantity

        self.completed = True
        db.session.commit()


class ProductsOrder(db.Model):
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    product = db.relationship("Product")
    order = db.relationship("Order", back_populates="products")




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String, nullable=False)


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)
    stock = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "stock": self.stock,
        }


class ProductIngredient(db.Model):
    __tablename__ = "product_ingredient"
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), primary_key=True)
    ingredient_id = db.Column(
        db.Integer, db.ForeignKey("ingredient.id"), primary_key=True
    )
