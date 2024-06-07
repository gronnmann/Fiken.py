from typing import Type

from fiken_py.fiken_object import FikenObjectAttachable, FikenObjectCountable
from fiken_py.models import Contact, Product, BankAccount
from fiken_py.models.draft import DraftInvoiceIsh, DraftInvoiceIshCreateRequest
from fiken_py.shared_enums import VatTypeProductSale
from fiken_py.shared_types import DraftLineInvoiceIsh, Attachment


def draftable_invoiceish_object_tests(DraftObject: Type[DraftInvoiceIsh],
                                      CraftCreateRequestObject: Type[DraftInvoiceIshCreateRequest],
                                      unique_id: str,
                                      generic_product: Product,
                                      generic_customer: Contact,
                                      generic_bank_account: BankAccount):
    """Tests for Draft objects, such as OfferDraft, InvoiceDraft, CreditNoteDraft.
    Returns the object created from the draft.
    """
    draft_line = DraftLineInvoiceIsh(
        productId=generic_product.productId,
        quantity=1,
        vatType=VatTypeProductSale.HIGH,
    )

    draft = CraftCreateRequestObject(
        customerId=generic_customer.contactId,
        lines=[draft_line],
        daysUntilDueDate=7,
        bankAccountNumber=generic_bank_account.bankAccountNumber,
        ourReference=unique_id,
    )

    draft_copied = draft.model_copy()

    # OfferDraft - POST, PUT, DELETE, GET
    draft: DraftObject = draft.save()
    assert draft.draftId is not None
    draft_id = draft.draftId
    draft.yourReference = f"Edited reference"
    draft.save()

    draft_from_get = DraftObject.get(draftId=draft_id)
    assert draft_from_get is not None
    assert draft_from_get.yourReference == "Edited reference"

    attachable_object_tests(draft_from_get)

    draft.delete()
    assert DraftObject.get(draftId=draft_id) is None

    # Create Class from draft, test GET

    draft = draft_copied.save()
    object = draft.submit_object()
    assert object is not None

    return object


def attachable_object_tests(attachable_object: FikenObjectAttachable):
    """Tests for objects that can have attachments. Please provide an object, not the class"""
    with open("test_online/dummy_attachment.pdf", "rb") as file:
        pdf_data = file.read()

    attachable_object.add_attachment("test_online/dummy_attachment.pdf", "dummy_attachment.pdf",
                                                              "This is the second attachment test")
    attachable_object.add_attachment_bytes("bytes_attachment.pdf", pdf_data, "This is the first attachment test")

    attachments: list[Attachment] = attachable_object.get_attachments()
    print(attachments)
    for attachment in attachments:
        assert attachment.comment in ["This is the first attachment test", "This is the second attachment test"]


def countable_object_tests(CounterObject: Type[FikenObjectCountable]):
    """Test for objects that have a counter. Please provide the class, not an object."""
    counter = CounterObject.get_counter()

    assert counter is not None
    assert counter >= 0
    assert isinstance(counter, int)