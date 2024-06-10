import logging
import os
import uuid
import random

import dotenv
import pytest

from fiken_py.fiken_object import FikenObject
from fiken_py.shared_enums import VatTypeProduct
from fiken_py.models import Product, Contact, BankAccount, BankAccountRequest, BankAccountType


@pytest.fixture(autouse=True, scope="session")
def set_auth_token():
    dotenv.load_dotenv("test_online/.env")

    FikenObject.set_auth_token(os.getenv("FIKEN_API_TOKEN"))
    FikenObject.set_company_slug(os.getenv("FIKEN_COMPANY_SLUG"))


@pytest.fixture(autouse=True, scope="session")
def set_logger_level():
    logger = logging.getLogger("fiken_py")
    logger.setLevel(logging.DEBUG)


@pytest.fixture(scope="session")
def unique_id() -> str:
    abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(random.choices(abc, k=4))


@pytest.fixture(scope="session")
def generic_product(set_auth_token) -> Product:
    name = "Banankasse fra BAMA (generisk testprodukt)"
    found_products = Product.getAll(name=name, active=True)
    if len(found_products) > 0:
        return found_products[0]
    else:
        product = Product(name=name, vatType=VatTypeProduct.HIGH, incomeAccount="3000", unitPrice=1000)
        product.save()
        return product


@pytest.fixture(scope="session")
def generic_contact(set_auth_token) -> Contact:
    name = "Pippi Hippie (generisk testkunde)"
    found_contacts = Contact.getAll(name=name)
    if len(found_contacts) > 0:
        return found_contacts[0]
    else:
        contact = Contact(name=name, email="test@test.com",
                          customer=True, supplier=True)
        contact.save()
        return contact


@pytest.fixture(scope="session")
def generic_bank_account(set_auth_token) -> BankAccount:
    found_bank_accounts = BankAccount.getAll()
    name = "Spareborse Gris (generisk testkonto)"

    if len(found_bank_accounts) > 0:
        for bank_account in found_bank_accounts:
            if bank_account.name == name:
                return bank_account

    bank_account = BankAccountRequest(name=name, bankAccountNumber="11112233334", type=BankAccountType.NORMAL)
    bank_account: BankAccount = bank_account.save()
    return bank_account