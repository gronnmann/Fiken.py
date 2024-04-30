import datetime
import logging
import os
import time
from random import random

import dotenv
from urllib3.connection import HTTPConnection

from fiken_py.fiken_object import FikenObject
from fiken_py.models import UserInfo, Company, BankAccount, BankAccountCreateRequest, Contact, ContactPerson, \
    ProductSalesReportRequest, Product, Transaction, JournalEntry, Account, JournalEntryRequest, InboxDocumentRequest, \
    ProjectCreateRequest, SaleRequest, InvoiceRequest, Project, BankAccountType
from fiken_py.shared_types import JournalEntryLine, VatTypeProduct, OrderLine, \
    InvoiceLineRequest
from fiken_py.shared_enums import SaleKind, SendMethod, SendEmailOption
from fiken_py.models.invoice import InvoiceSendRequest, Invoice

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

    product = Product(name=random_str, vatType=VatTypeProduct.HIGH,
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


def upload_and_read_dummy_pdf():
    with open("dummy.pdf", "rb") as f:
        file_bytes = f.read()

    # inbox_document = InboxDocumentRequest(name="Testdokument", filename="dummy_doc.pdf", file=file_bytes,
    #                                       description="Dette er en test")

    inbox_document = InboxDocumentRequest.from_filepath(name="Testdokument", filepath="dummy.pdf",
                                                        description="Dette er en test")

    doc = inbox_document.save(companySlug='fiken-demo-drage-og-elefant-as')
    print(doc)


def create_project():
    customers = Contact.getAll(companySlug='fiken-demo-drage-og-elefant-as', name="FikenPy Bruker")
    print(len(customers))
    if len(customers) == 0:
        contact = Contact(name="FikenPy Bruker")
        contact.customer = True
        contact.save(companySlug='fiken-demo-drage-og-elefant-as')
    else:
        contact = customers[0]

    proj = ProjectCreateRequest(name="Et prosjekt",
                                number=1,
                                description="Dette er et prosjekt", startDate=datetime.date.today())

    proj = proj.save(companySlug='fiken-demo-drage-og-elefant-as')
    print(proj)

    proj.delete(companySlug='fiken-demo-drage-og-elefant-as')


def create_sale():
    customers = Contact.getAll(companySlug='fiken-demo-drage-og-elefant-as', name="FikenPy Bruker")
    print(len(customers))
    if len(customers) == 0:
        contact = Contact(name="FikenPy Bruker")
        contact.customer = True
        contact.save(companySlug='fiken-demo-drage-og-elefant-as')
    else:
        contact = customers[0]

    acc = BankAccount.getAll(companySlug='fiken-demo-drage-og-elefant-as')[0]

    print("Using customer ", contact)

    order_line = OrderLine(
        vatType=VatTypeProduct.HIGH,
        netPrice=1000,
        description="Testprodukt",
        account=3000,
    )

    req = SaleRequest(
        date=datetime.date.today(),
        dueDate="2024-04-24",
        kind=SaleKind.CASH_SALE,
        lines=[order_line],
        currency="NOK",
        customerId=contact.contactId,
        totalPaid=1000,
        saleNumber="TRALALA",
        paymentAccount=acc.bankAccountNumber,
        paymentDate=datetime.date.today(),
        paymentFee=0,
    )

    sale = req.save(companySlug='fiken-demo-drage-og-elefant-as')

    print(sale)


def create_contact_and_add_attachment():
    contacts = Contact.getAll(companySlug='fiken-demo-drage-og-elefant-as', name="Testbruker")
    contact = contacts[0]

    # print(contact)
    # with open("dummy.pdf", "rb") as f:
    #     file_bytes = f.read()
    #
    # contact.add_attachment_bytes("attachment_name.pdf", file_bytes, "Dette er en test av add_attachment_bytes"
    #                              , companySlug='fiken-demo-drage-og-elefant-as')
    # contact.add_attachment("dummy.pdf", "add_attachment_test.pdf", companySlug='fiken-demo-drage-og-elefant-as')

    atts = contact.get_attachments(companySlug='fiken-demo-drage-og-elefant-as')
    for a in atts:
        print(a)


def find_journal_entry_and_add_attachment():
    entries = JournalEntry.getAll(companySlug='fiken-demo-drage-og-elefant-as', description="Testjournalpost")
    entry = entries[0]

    with open("dummy.pdf", "rb") as f:
        file_bytes = f.read()

    entry.add_attachment_bytes("attachment_name.pdf", file_bytes, "Dette er en test av add_attachment_bytes"
                               , companySlug='fiken-demo-drage-og-elefant-as')

    atts = entry.get_attachments(companySlug='fiken-demo-drage-og-elefant-as')
    for a in atts:
        print(a)


def create_and_invoice_user():
    customer = Contact.getAll(companySlug='fiken-demo-drage-og-elefant-as', name="FikenPy Bruker")
    if len(customer) == 0:
        customer = Contact(name="FikenPy Bruker")
    else:
        customer = customer[0]
    customer.customer = True
    customer.email = "barti.mruk@gmail.com"
    customer.save(companySlug='fiken-demo-drage-og-elefant-as')

    bankAccount = BankAccount.getAll(companySlug='fiken-demo-drage-og-elefant-as')[0]
    print(bankAccount)

    product = Product.getAll(companySlug='fiken-demo-drage-og-elefant-as', name="Et produkt")
    if len(product) == 0:
        product = Product(name="Et produkt", vatType=VatTypeProduct.NONE, incomeAccount="3000",
                          unitPrice=1000)
        product.save(companySlug='fiken-demo-drage-og-elefant-as')
    else:
        product = product[0]

    print(product)

    invoice_line = InvoiceLineRequest(
        vatType=VatTypeProduct.NONE,
        quantity=5,
        productId=product.productId,
    )

    invoices = Invoice.getAll(companySlug='fiken-demo-drage-og-elefant-as', customerId=customer.contactId)

    if len(invoices) > 0:
        invoice = invoices[0]
    else:
        invoice = InvoiceRequest(
            issueDate=datetime.date.today(),
            dueDate="2024-04-24",
            lines=[invoice_line],
            bankAccountCode=bankAccount.accountCode,
            customerId=customer.contactId,
            cash=False
        )

        invoice = invoice.save(companySlug='fiken-demo-drage-og-elefant-as')
    print(invoice)
    invoice.dueDate = "2024-04-29"
    invoice.save(companySlug='fiken-demo-drage-og-elefant-as')

    send_req = InvoiceSendRequest(
        invoiceId=invoice.invoiceId,
        method=[SendMethod.EMAIL],
        includeDocumentAttachments=False,
        recipientName=customer.name,
        message="Dette er en test av send_invoice",
        emailSendOption=SendEmailOption.AUTO
    )

    Invoice.send_to_customer(send_req, companySlug='fiken-demo-drage-og-elefant-as', invoice=invoice)


def get_and_edit_project():


    # project = ProjectRequest(name="Et prosjekt",
    #                          number="1",
    #                          description="Dette er et prosjekt", startDate=datetime.date.today())
    # project = project.save(companySlug='fiken-demo-drage-og-elefant-as')
    # print(project)

    project = Project.get(companySlug='fiken-demo-drage-og-elefant-as', projectId=5904217115)

    project.name = "Endret prosjektnavn"
    project.save(companySlug='fiken-demo-drage-og-elefant-as')
    print(project)


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

    HTTPConnection.debuglevel = 1

    invoice_line = InvoiceLineRequest(
        vatType=VatTypeProduct.NONE,
        quantity=5,

    )

    # get_transactions()
    # test_creating_journal_entry()
    # test_create_get_edit_get_and_delete_product()
    # upload_and_read_dummy_pdf()
    # create_project()
    # create_sale()
    # create_contact_and_add_attachment()
    # find_journal_entry_and_add_attachment()
    # create_and_invoice_user()
    # counter = Invoice.get_counter()
    # get_and_edit_project()