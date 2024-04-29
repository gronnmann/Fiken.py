import datetime

import pytest

from fiken_py.errors import RequestContentNotFoundException
from fiken_py.fiken_types import InvoiceLineRequest
from fiken_py.models import Product, Contact, InvoiceRequest, Invoice
from fiken_py.models.credit_note import CreditNote


def test_create_credit_note_full(unique_id: str, generic_product: Product,
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
        ourReference=f"Test invoice to be fully refunded ({unique_id}#product)",
        invoiceText="This is a test invoice sent by FikenPy",
    )

    invoice: Invoice = invoice.save()

    assert invoice is not None

    credit_note: CreditNote = CreditNote.create_from_invoice_full(invoiceId=invoice.invoiceId)
    assert credit_note is not None
    assert credit_note.creditNoteId is not None
    assert credit_note.associatedInvoiceId == invoice.invoiceId

    with pytest.raises(RequestContentNotFoundException):
        CreditNote.create_from_invoice_full(invoiceId=99999)
