import datetime

import pytest

from fiken_py.errors import RequestContentNotFoundException
from fiken_py.models import Product, Contact, Offer, OfferDraft, OfferDraftCreateRequest
from fiken_py.shared_enums import VatTypeProductSale
from fiken_py.shared_types import DraftLine


def test_create_offer_full(unique_id: str, generic_product: Product,
                           generic_customer: Contact, generic_bank_account):
    draft_line = DraftLine(
        productId=generic_product.productId,
        quantity=1,
        vatType=VatTypeProductSale.HIGH,
    )

    offer_draft: OfferDraftCreateRequest = OfferDraftCreateRequest(
        customerId=generic_customer.contactId,
        lines=[draft_line],
        daysUntilDueDate=7,
        bankAccountNumber=generic_bank_account.bankAccountNumber,
    )

    offer_draft_bak = offer_draft.model_copy()

    # OfferDraft - POST, PUT, DELETE, GET

    offer_draft: OfferDraft = offer_draft.save()
    assert offer_draft.draftId is not None
    offer_draft_id = offer_draft.draftId
    offer_draft.yourReference = f"Edited reference"
    offer_draft.save()

    get_offer_draft = OfferDraft.get(draftId=offer_draft_id)
    assert get_offer_draft is not None
    assert get_offer_draft.yourReference == "Edited reference"

    offer_draft.delete()
    assert OfferDraft.get(draftId=offer_draft_id) is None

    # Create Offer from draft, test GET

    offer_draft = offer_draft_bak.save()
    offer: Offer = offer_draft.submit_object()
    assert offer is not None
    assert offer.offerId is not None

    offer_id = offer.offerId

    get_offer = Offer.get(offerId=offer_id)
    assert get_offer is not None


def test_counter():
    counter: int = Offer.get_counter()
    assert counter is not None
    assert counter >= 0
    assert isinstance(counter, int)
