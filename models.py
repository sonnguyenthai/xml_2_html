from jsonobject import *


class Seller(JsonObject):
    name = StringProperty(default="")
    price = StringProperty(default="")


class Product(JsonObject):

    distributor_code = StringProperty(default="")
    brand = StringProperty(default="")
    label = StringProperty(default="")
    ean = StringProperty(default="")
    ipc = StringProperty(default="")
    price = StringProperty(default="")
    position = StringProperty(default="") # ranking for each product compared to the price of other distributors.
    suppliers = ListProperty(Seller, default=[])
    sellers = ListProperty(Seller, default=[])
    best_seller_price = StringProperty(default="") # lowest price of seller
    best_seller = StringProperty(default="") # seller with best price
    bc_matching = BooleanProperty(default=False)
    bc_less_exp = BooleanProperty(default=False)
    bc_more_exp = BooleanProperty(default=False)


class Brand(JsonObject):
    name = StringProperty(default="")
    distributor_code = StringProperty(default="")
    position1 = FloatProperty(default=0)
    position2 = FloatProperty(default=0)
    position3 = FloatProperty(default=0)
    products = ListProperty(Product, default=[])
