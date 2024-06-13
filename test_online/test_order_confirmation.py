from fiken_py.models import (
    OrderConfirmation,
    OrderConfirmationDraft,
    Contact,
    Product,
)
from test_online import shared_tests


def test_create_order_confirmation_full(
    unique_id: str,
    generic_product: Product,
    generic_contact: Contact,
    generic_bank_account,
):

    draft_from_test: OrderConfirmation = shared_tests.draftable_invoiceish_object_tests(
        DraftObject=OrderConfirmationDraft,
        unique_id=unique_id,
        generic_product=generic_product,
        generic_customer=generic_contact,
        generic_bank_account=generic_bank_account,
    )

    confirmation_id = draft_from_test.confirmationId

    get_confirmation: OrderConfirmation = OrderConfirmation.get(
        confirmationId=confirmation_id
    )
    assert get_confirmation is not None

    invoice_draft: "InvoiceDraft" = get_confirmation.to_invoice_draft()
    assert invoice_draft is not None
    assert invoice_draft.draftId is not None


def test_counter():
    shared_tests.countable_object_tests(OrderConfirmation)
