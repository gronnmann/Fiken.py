from fiken_py.models import Product, Contact, Offer, OfferDraft, OfferDraftRequest

import test_online.shared_tests as shared_tests


def test_create_offer_full(
    unique_id: str,
    generic_product: Product,
    generic_contact: Contact,
    generic_bank_account,
):
    draft_from_test: Offer = shared_tests.draftable_invoiceish_object_tests(
        DraftObject=OfferDraft,
        DraftCreateRequestObject=OfferDraftRequest,
        unique_id=unique_id,
        generic_product=generic_product,
        generic_customer=generic_contact,
        generic_bank_account=generic_bank_account,
    )

    offer_id = draft_from_test.offerId

    get_offer = Offer.get(offerId=offer_id)
    assert get_offer is not None


def test_counter():
    shared_tests.countable_object_tests(Offer)
