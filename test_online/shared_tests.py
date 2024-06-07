import datetime
from typing import Type

from fiken_py.fiken_object import FikenObjectAttachable, FikenObjectCountable
from fiken_py.models import Contact, Product, BankAccount
from fiken_py.models.draft import DraftInvoiceIsh, DraftInvoiceIshCreateRequest, DraftOrder, DraftOrderCreateRequest
from fiken_py.shared_enums import VatTypeProductSale, VatTypeProduct
from fiken_py.shared_types import DraftLineInvoiceIsh, Attachment, OrderLine, DraftLineOrder


def draftable_invoiceish_object_tests(DraftObject: Type[DraftInvoiceIsh],
                                      DraftCreateRequestObject: Type[DraftInvoiceIshCreateRequest],
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

    draft = DraftCreateRequestObject(
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
    created_object = draft.submit_object()
    assert created_object is not None

    return created_object


def draftable_order_object_tests(
        DraftObject: Type[DraftOrder],
        DraftCreateRequestObject: Type[DraftOrderCreateRequest],
        product_account: str,
        unique_id: str,
        generic_customer: Contact,
        generic_bank_account: BankAccount
):
    order_line = DraftLineOrder(
        text=f"En billig yacht (testprodukt {unique_id})",
        vatType="HIGH",
        net=10000,
        gross=12500,
        incomeAccount=product_account,
    )

    draft = DraftCreateRequestObject(
        customerId=generic_customer.contactId,
        lines=[order_line],
        bankAccountCode=generic_bank_account.accountCode,
        cash=False,
        paid=False,
        invoiceIssueDate=datetime.date.today(),
        contactId=generic_customer.contactId,
    )

    draft_copied = draft.model_copy()

    draft: DraftObject = draft.save()
    assert draft.draftId is not None
    draft_id = draft.draftId

    draft.kid = "123456789"

    draft.save()

    draft_from_get = DraftObject.get(draftId=draft_id)
    assert draft_from_get is not None
    assert draft_from_get.kid == "123456789"

    attachable_object_tests(draft_from_get, False)

    draft.delete()
    assert DraftObject.get(draftId=draft_id) is None

    # Test creating object from draft

    draft_copied: DraftOrder = draft_copied.save()
    created_object = draft_copied.submit_object()

    assert created_object is not None

    return created_object


def attachable_object_tests(attachable_object: FikenObjectAttachable, test_comments: bool = True):
    """Tests for objects that can have attachments. Please provide an object, not the class
    :param attachable_object: The object to test
    :param test_comments: Whether to test the comments on the attachments (they are not supported on all object types)
    """
    with open("test_online/dummy_attachment.pdf", "rb") as file:
        pdf_data = file.read()

    assert attachable_object.add_attachment("test_online/dummy_attachment.pdf", "dummy_attachment.pdf",
                                     "This is the second attachment test" if test_comments else None)
    assert attachable_object.add_attachment_bytes("bytes_attachment.pdf", pdf_data,
                                           "This is the first attachment test" if test_comments else None)

    attachments: list[Attachment] = attachable_object.get_attachments()
    assert len(attachments) == 2

    if test_comments:
        for attachment in attachments:
            assert attachment.comment in ["This is the first attachment test", "This is the second attachment test"]


def countable_object_tests(CounterObject: Type[FikenObjectCountable]):
    """Test for objects that have a counter. Please provide the class, not an object."""
    counter = CounterObject.get_counter()

    assert counter is not None
    assert counter >= 0
    assert isinstance(counter, int)
