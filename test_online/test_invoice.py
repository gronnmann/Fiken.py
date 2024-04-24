import datetime

from fiken_py.fiken_types import InvoiceLineRequest, VatTypeProduct
from fiken_py.models import Product, Contact, InvoiceRequest, Invoice


def test_create_invoice_product(unique_id: str, generic_product: Product,
                        generic_customer: Contact, generic_bank_account):
    invoice_line: InvoiceLineRequest = InvoiceLineRequest(
        productId=generic_product.productId,
        quantity=1,
    )

    invoice: InvoiceRequest = InvoiceRequest(
        issueDate=datetime.date.today(),
        dueDate=datetime.date.today() + datetime.timedelta(days=14),
        customerId=generic_customer.contactId,
        lines=[invoice_line],
        bankAccountCode=generic_bank_account.accountCode,
        cash=False,
        ourReference=f"Test invoice ({unique_id}#product)",
        invoiceText="This is a test invoice sent by FikenPy",
    )

    invoice: Invoice = invoice.save()

    assert invoice is not None
    assert invoice.invoiceId is not None
    assert invoice.issueDate == datetime.date.today()

    get_invoice = Invoice.get(invoiceId=invoice.invoiceId)
    assert get_invoice is not None
    assert get_invoice.invoiceId == invoice.invoiceId


def test_create_invoice_product_freetext(unique_id: str,
                        generic_customer: Contact, generic_bank_account):
    invoice_line: InvoiceLineRequest = InvoiceLineRequest(
        quantity=1,
        description="En banankasse fra Bendit (testprodukt fritekst)",
        unitPrice=10000,
        vatType=VatTypeProduct.NONE,
        incomeAccount="3000",
    )

    invoice: InvoiceRequest = InvoiceRequest(
        issueDate=datetime.date.today(),
        dueDate=datetime.date.today() + datetime.timedelta(days=14),
        customerId=generic_customer.contactId,
        lines=[invoice_line],
        bankAccountCode=generic_bank_account.accountCode,
        cash=False,
        ourReference=f"Test invoice ({unique_id}#freeText)",
        invoiceText="This is a test invoice sent by FikenPy",
    )

    invoice: Invoice = invoice.save()

    assert invoice is not None
    assert invoice.invoiceId is not None
    assert invoice.issueDate == datetime.date.today()

    get_invoice = Invoice.get(invoiceId=invoice.invoiceId)
    assert get_invoice is not None
    assert get_invoice.invoiceId == invoice.invoiceId