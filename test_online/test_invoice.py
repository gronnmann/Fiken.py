import datetime

from fiken_py.shared_types import InvoiceLineRequest
from fiken_py.shared_enums import VatTypeProduct, VatTypeProductSale
from fiken_py.models import Product, Contact, InvoiceRequest, Invoice, InvoiceDraftRequest, InvoiceDraft
import test_online.shared_tests as shared_tests
from test_online import sample_object_factory


def test_create_get_patch_invoice_product(unique_id: str, generic_product: Product,
                                          generic_contact: Contact, generic_bank_account):
    invoice = sample_object_factory.invoice_request(unique_id, generic_product, generic_contact, generic_bank_account)

    invoice: Invoice = invoice.save()

    assert invoice is not None
    assert invoice.invoiceId is not None
    assert invoice.issueDate == datetime.date.today()

    get_invoice: Invoice = Invoice.get(invoiceId=invoice.invoiceId)
    assert get_invoice is not None
    assert get_invoice.invoiceId == invoice.invoiceId

    new_due = get_invoice.dueDate + datetime.timedelta(days=7)
    get_invoice.dueDate = new_due
    get_invoice.save()
    assert get_invoice.dueDate == new_due

    sent_manually = get_invoice.sentManually
    get_invoice.sentManually = not sent_manually
    get_invoice.save()
    assert get_invoice.sentManually != sent_manually


def test_create_invoice_product_freetext_and_invoice_counter(unique_id: str,
                                                             generic_contact: Contact, generic_bank_account):
    invoice_line: InvoiceLineRequest = InvoiceLineRequest(
        quantity=1,
        description="En banankasse fra Bendit (testprodukt fritekst)",
        unitPrice=10000,
        vatType=VatTypeProductSale.EXEMPT,
        incomeAccount="3100",
    )

    invoice: InvoiceRequest = InvoiceRequest(
        issueDate=datetime.date.today(),
        dueDate=datetime.date.today() + datetime.timedelta(days=14),
        customerId=generic_contact.contactId,
        lines=[invoice_line],
        bankAccountCode=generic_bank_account.accountCode,
        cash=False,
        ourReference=f"Test invoice ({unique_id}#freeText)",
        invoiceText="This is a test invoice sent by FikenPy",
    )

    counter: int = Invoice.get_counter()

    invoice: Invoice = invoice.save()

    assert Invoice.get_counter() == counter + 1

    assert invoice is not None
    assert invoice.invoiceId is not None
    assert invoice.issueDate == datetime.date.today()

    get_invoice = Invoice.get(invoiceId=invoice.invoiceId)
    assert get_invoice is not None
    assert get_invoice.invoiceId == invoice.invoiceId

    shared_tests.attachable_object_tests(get_invoice, False)


def test_create_through_draft(unique_id, generic_contact, generic_product, generic_bank_account):
    shared_tests.draftable_invoiceish_object_tests(
        InvoiceDraft,
        InvoiceDraftRequest,
        unique_id,
        generic_product,
        generic_contact,
        generic_bank_account
    )


def test_counter():
    shared_tests.countable_object_tests(Invoice)
