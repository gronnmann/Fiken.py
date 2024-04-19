import logging
import os
import time
from random import random

import dotenv
from urllib3.connection import HTTPConnection

from fiken_py.fiken_object import FikenObject
from fiken_py.models import UserInfo, Company, BankAccount, BankAccountCreateRequest, Contact, ContactPerson, \
    ProductSalesReportRequest, Product, Transaction, JournalEntry, Account, JournalEntryRequest
from fiken_py.fiken_types import BankAccountType, JournalEntryLine, ProductVatType

dotenv.load_dotenv(".env")

FikenObject.set_auth_token(os.getenv("FIKEN_API_TOKEN"))


def get_user_info():
    user = UserInfo.get()
    print(user)


def get_companies():
    companies = Company.getAll(sortBy='name desc')

    for company in companies:
        print(company)


def get_company():
    company = Company.get(companySlug='fiken-demo-drage-og-elefant-as')
    print(company)


def get_bank_accounts():
    # bank_accounts = BankAccount.getAll(companySlug='fiken-demo-drage-og-elefant-as')

    demo_konto = BankAccount.get(companySlug='fiken-demo-drage-og-elefant-as', bankAccountId=2882125076)
    print(demo_konto)


def create_bank_account():
    new_account = BankAccountCreateRequest(name="Testkonto", bankAccountNumber="11152233334 "
                                           , type=BankAccountType.NORMAL)
    print("Type of object in start: ", type(new_account))
    new_acc = new_account.save(companySlug='fiken-demo-drage-og-elefant-as')
    print("Type of object in end: ", type(new_acc))

    print(new_acc)
    print("New account created")


def get_contacts():
    contacts = Contact.getAll(companySlug='fiken-demo-drage-og-elefant-as')
    for c in contacts:
        print(c.name)
        # print(c)
    contact_single = Contact.get(companySlug='fiken-demo-drage-og-elefant-as', contactId=contacts[0].contactId)
    print(contact_single)


def create_and_edit_contact():
    new_contact = Contact(name="En testbruker")
    new_contact.save(companySlug='fiken-demo-drage-og-elefant-as')
    print(new_contact)
    time.sleep(5)
    print(f"Before edit: {new_contact}")

    new_contact.email = "test@test.no"
    new_contact.save(companySlug='fiken-demo-drage-og-elefant-as')
    print(f"After edit: {new_contact}")


def del_test_contacts():
    contacts = Contact.getAll(companySlug='fiken-demo-drage-og-elefant-as', name="Testbruker 1")
    for c in contacts:
        print(c)
        c.delete(companySlug='fiken-demo-drage-og-elefant-as')


def create_and_edit_contact_person():
    contact_for_person = Contact(name="Bedrift med kontaktperson")
    contact_for_person.save(companySlug='fiken-demo-drage-og-elefant-as')

    contact_person = ContactPerson(name="Testperson", email="old_epost@epost.no")
    contact_person.save(companySlug='fiken-demo-drage-og-elefant-as', contactId=contact_for_person.contactId)
    print(contact_person)

    contact_person.email = "en_epost@epost.no"
    contact_person.save(companySlug='fiken-demo-drage-og-elefant-as', contactId=contact_for_person.contactId)

    print(contact_person)

    # contact_person.delete(companySlug='fiken-demo-drage-og-elefant-as', contactId=contact_for_person.contactId)
    # contact_for_person.delete(companySlug='fiken-demo-drage-og-elefant-as')


def get_sales_report():
    sales_report_request = ProductSalesReportRequest(**{
        "from": "2024-01-01",
        "to": "2024-12-31",
    })
    sales_report = sales_report_request.save(companySlug='fiken-demo-drage-og-elefant-as')
    print(sales_report)


def get_products():
    products = Product.getAll(companySlug='fiken-demo-drage-og-elefant-as')
    for p in products:
        print(p)
    product_single = Product.get(companySlug='fiken-demo-drage-og-elefant-as', productId=products[0].productId)

    # duplicatge
    product_single_dup = product_single
    product_single_dup.productId = None
    product_single_dup.save(companySlug='fiken-demo-drage-og-elefant-as')
    product_single_dup.name = "Demoprodukt kopi"
    product_single_dup.save(companySlug='fiken-demo-drage-og-elefant-as')


def get_transactions():
    transactions = Transaction.getAll(companySlug='fiken-demo-drage-og-elefant-as')
    for t in transactions:
        print(t)


def test_creating_journal_entry():
    bank_accounts = Account.getAll(companySlug='fiken-demo-drage-og-elefant-as')

    ba_1 = bank_accounts[0]
    ba_2 = bank_accounts[1]

    entry_line = JournalEntryLine(
        amount=1000,
        debitAccount=ba_1.code,
        creditAccount=ba_2.code,
        debitVatCode=0,
        creditVatCode=0,
    )

    entry = JournalEntry(
        description="Testjournalpost",
        lines=[entry_line],
        date="2024-04-18"
    )

    request = JournalEntryRequest(
        journalEntries=[entry]
    )

    journal_entry = request.save(companySlug='fiken-demo-drage-og-elefant-as')
    print(journal_entry)
    print(type(journal_entry))


def test_create_get_edit_get_and_delete_product():
    random_str = "Some random string: " + str(random())[:5]

    product = Product(name=random_str, vatType=ProductVatType.HIGH,
                      incomeAccount="3000")
    product.save(companySlug='fiken-demo-drage-og-elefant-as')
    print(product)

    product_get = Product.get(companySlug='fiken-demo-drage-og-elefant-as', productId=product.productId)

    if product_get != product:
        print("Product get is not equal to product")
        print(product_get)
        print(product)

    product_get.name = f"EDITED {random_str}"
    product_get.save(companySlug='fiken-demo-drage-og-elefant-as')
    print(product_get)

    prod_id = product_get.productId

    product_get.delete(companySlug='fiken-demo-drage-og-elefant-as')
    product_get = Product.get(companySlug='fiken-demo-drage-og-elefant-as', productId=prod_id)
    print(product_get)


if __name__ == "__main__":
    # get_bank_accounts()
    # create_and_edit_contact()
    # create_bank_account()
    # create_and_edit_contact_person()
    # get_sales_report()
    # get_products()

    logging.basicConfig(level=logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    # HTTPConnection.debuglevel = 1

    # get_transactions()
    # test_creating_journal_entry()
    test_create_get_edit_get_and_delete_product()
