from fiken_py.models import Product
from test_online import sample_object_factory


def test_product_lifecycle(unique_id):
    prod = sample_object_factory.product(unique_id)

    prod.save()
    assert prod.productId is not None

    assert prod.stock is None

    prod.stock = 10

    prod.save()

    prod2 = Product.get(productId=prod.productId)

    assert prod2.stock == 10
    assert prod2.productId == prod.productId

    prod2.delete()

    assert Product.get(productId=prod.productId) is None