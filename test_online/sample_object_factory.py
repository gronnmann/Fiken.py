import datetime
from typing import Type

from fiken_py.models import (
    BankAccount,
    BankAccountType,
    Contact,
    ContactPerson,
    Product,
    JournalEntry,
    Project,
    Transaction,
    Invoice,
    Sale,
    Purchase,
)
from fiken_py.models.draft import DraftInvoiceIsh, DraftOrder
from fiken_py.shared_enums import (
    VatTypeProduct,
    VatTypeProductSale,
    SaleKind,
    PurchaseKind,
)
from fiken_py.shared_types import (
    JournalEntryLine,
    DraftLineInvoiceIsh,
    OrderLine,
    DraftLineOrder,
    InvoiceLine,
)


def bank_account(unique_id: str) -> BankAccount:
    return BankAccount(
        name=f"Onkel Skrues safe ({unique_id})",
        bankAccountNumber="11112233334",
        type=BankAccountType.NORMAL,
    )


def contact(unique_id) -> Contact:
    return Contact(name=f"Ole Brumm (testperson {unique_id})")


def contact_person(unique_id) -> ContactPerson:
    return ContactPerson(
        name=f"Ola Olafson (testperson {unique_id})",
        email="test@test.com",
        phoneNumber="123456789",
    )


def product(unique_id) -> Product:
    return Product(
        name=f"En knekt stol (testprodukt {unique_id})",
        vatType=VatTypeProduct.HIGH,
        incomeAccount="3000",
        unitPrice=1000,
    )


def transaction(
    unique_id, bank_account_1: BankAccount, bank_account_2: BankAccount
) -> Transaction:
    """Returns sample Journal Entry with 10 kr flowing from bank_account_1 to bank_account_2."""

    entry_line = JournalEntryLine(
        amount=1000,
        debitAccount=bank_account_1.accountCode,
        creditAccount=bank_account_2.accountCode,
        debitVatCode=0,
        creditVatCode=0,
    )

    entry = JournalEntry(
        description=f"Litt pengeflyt (test fripostering {unique_id})",
        lines=[entry_line],
        date=datetime.date.today(),
    )

    transaction = Transaction(
        entries=[entry],
    )

    return transaction


def invoice(
    unique_id, product: Product, contact: Contact, bank_account: BankAccount
) -> Invoice:
    invoice_line: InvoiceLine = InvoiceLine(
        productId=product.productId,
        quantity=1,
    )

    return Invoice(
        issueDate=datetime.date.today(),
        dueDate=datetime.date.today() + datetime.timedelta(days=14),
        customer=contact,
        lines=[invoice_line],
        bankAccountCode=bank_account.accountCode,
        cash=False,
        ourReference=f"Test invoice ({unique_id}#product)",
        invoiceText="This is a test invoice sent by FikenPy",
    )


def draft_invoiceish(
    unique_id: str,
    DraftInvoiceIshType: Type[DraftInvoiceIsh],
    product: Product,
    contact: Contact,
    bank_account: BankAccount,
) -> DraftInvoiceIsh:
    draft_line = DraftLineInvoiceIsh(
        productId=product.productId,
        quantity=1,
        vatType=VatTypeProductSale.HIGH,
    )

    return DraftInvoiceIshType(
        customers=[contact],
        lines=[draft_line],
        daysUntilDueDate=7,
        bankAccountNumber=bank_account.bankAccountNumber,
        ourReference=unique_id,
    )


def draft_order(
    unique_id: str,
    DraftOrderType: Type[DraftOrder],
    accounting_account: str,
    customer: Contact,
    bank_account: BankAccount,
) -> DraftOrder:
    order_line = DraftLineOrder(
        text=f"En billig yacht (testprodukt {unique_id})",
        vatType="HIGH",
        net=10000,
        gross=12500,
        incomeAccount=accounting_account,
    )

    return DraftOrderType(
        customerId=customer.contactId,
        lines=[order_line],
        bankAccountCode=bank_account.accountCode,
        cash=False,
        paid=False,
        invoiceIssueDate=datetime.date.today(),
        contact=customer,
    )


def sale(unique_id: str, contact: Contact) -> Sale:
    sale_line = OrderLine(
        description=f"En tilfeldig fjernkontroll (testprodukt {unique_id})",
        vatType=VatTypeProductSale.HIGH,
        account="3000",
        netPrice=1000,
        vat=250,
    )

    return Sale(
        date=datetime.date.today(),
        lines=[sale_line],
        kind=SaleKind.EXTERNAL_INVOICE,
        customer=contact,
        currency="NOK",
    )


def purchase(unique_id: str, contact: Contact) -> Purchase:
    purchase_line = OrderLine(
        description=f"En veldig billig AK (testprodukt {unique_id})",
        vatType="HIGH",
        account="4300",
        netPrice=100000,
        vat="25000",
    )

    return Purchase(
        date=datetime.date.today(),
        kind=PurchaseKind.SUPPLIER,
        currency="NOK",
        lines=[purchase_line],
        paid=True,
        supplier=contact,
    )


def project(unique_id) -> Project:
    return Project(
        name=f"Prosjekt {unique_id}",
        number=unique_id + "_sample",
        startDate=datetime.date.today(),
    )
