import datetime

import pytest

from fiken_py.errors import RequestContentNotFoundException
from fiken_py.shared_types import InvoiceLineRequest
from fiken_py.models import Product, Contact, InvoiceRequest, Invoice
from fiken_py.models.credit_note import (
    CreditNote,
    CreditNoteDraftRequest,
    CreditNoteDraft,
)
from test_online import shared_tests, sample_object_factory


def test_create_credit_note_full(
    unique_id: str,
    generic_product: Product,
    generic_contact: Contact,
    generic_bank_account,
):
    invoice_request = sample_object_factory.invoice_request(
        unique_id, generic_product, generic_contact, generic_bank_account
    )
    invoice_request.ourReference = "#test_credit_note_full"

    invoice: Invoice = invoice_request.save()

    assert invoice is not None

    credit_note: CreditNote = CreditNote.create_from_invoice_full(
        invoiceId=invoice.invoiceId
    )
    assert credit_note is not None
    assert credit_note.creditNoteId is not None
    assert credit_note.associatedInvoiceId == invoice.invoiceId

    with pytest.raises(RequestContentNotFoundException):
        CreditNote.create_from_invoice_full(invoiceId=99999)


def test_create_through_draft(
    unique_id, generic_contact, generic_product, generic_bank_account
):
    shared_tests.draftable_invoiceish_object_tests(
        CreditNoteDraft,
        CreditNoteDraftRequest,
        unique_id,
        generic_product,
        generic_contact,
        generic_bank_account,
    )


def test_counter():
    shared_tests.countable_object_tests(Invoice)
