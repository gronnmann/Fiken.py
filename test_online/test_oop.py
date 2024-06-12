import datetime

from fiken_py.fiken_object import FikenObject
from fiken_py.models import (
    FikenPy,
    Contact,
    Product,
    BankAccount,
    InvoiceDraftRequest,
    CreditNoteDraftRequest,
    OfferDraftRequest,
    OrderConfirmationDraftRequest,
    SaleDraftRequest,
    PaymentSale,
    PurchaseDraftRequest,
    PaymentPurchase,
)
from test_online import sample_object_factory


# This test is waaaaay too long, but it's a good example of how to use the OOP interface
def test_company_methods(
    unique_id, generic_bank_account, generic_product, generic_contact
):
    # Clear auth token and company slug
    AUTH_TOKEN = FikenObject._AUTH_TOKEN
    COMPANY_SLUG = FikenObject._COMPANY_SLUG

    FikenObject.clear_auth_token()
    FikenObject.clear_company_slug()

    # Step 1) Clear global settings

    assert FikenObject._AUTH_TOKEN is None
    assert FikenObject._COMPANY_SLUG is None

    # Step 2) Do the OOP tests

    company_method_tests(
        unique_id,
        AUTH_TOKEN,
        COMPANY_SLUG,
        generic_bank_account,
        generic_product,
        generic_contact,
    )

    # Step 3) Restore global settings
    FikenObject.set_auth_token(AUTH_TOKEN)
    FikenObject.set_company_slug(COMPANY_SLUG)

    assert FikenObject._AUTH_TOKEN == AUTH_TOKEN
    assert FikenObject._COMPANY_SLUG == COMPANY_SLUG


def company_method_tests(
    unique_id: str,
    auth_token: str,
    company_slug: str,
    generic_bank_account: BankAccount,
    generic_product: Product,
    generic_contact: Contact,
):
    fiken_py = FikenPy(auth_token)

    assert fiken_py.get_user_info() is not None
    assert fiken_py.get_companies() is not None

    company = fiken_py.get_company(company_slug)
    assert company is not None

    # Projects
    project = sample_object_factory.project(unique_id)
    project = company.create_project(project)
    assert project.projectId is not None

    assert len(company.get_projects(follow_pages=False)) > 0
    proj_id = project.projectId
    assert company.get_project(proj_id) is not None

    # Accounts
    assert company.get_balance_accounts(follow_pages=False) is not None
    assert company.get_balance_account("3000") is not None

    assert company.get_balance_account_balance("3000") is not None
    assert company.get_balance_account_balances() is not None

    # Bank accounts

    bank_acc_req = sample_object_factory.bank_account_request(unique_id)
    bank_acc = company.create_bank_account(bank_acc_req)
    assert bank_acc.bankAccountId is not None

    assert len(company.get_bank_accounts(follow_pages=False)) > 0
    assert company.get_bank_account(bank_acc.bankAccountId) is not None

    # Contact
    contact_req = sample_object_factory.contact(unique_id)
    contact = company.create_contact(contact_req)
    assert contact.contactId is not None

    assert len(company.get_contacts(follow_pages=False)) > 0
    assert company.get_contact(contact.contactId) is not None

    # Product
    product_req = sample_object_factory.product(unique_id)
    product = company.create_product(product_req)
    assert product.productId is not None

    assert len(company.get_products(follow_pages=False)) > 0
    assert company.get_product(product.productId) is not None
    prod_id = product.productId
    product.delete()
    assert company.get_product(prod_id) is None

    # Journal entry and transactions
    journal_entry_req = sample_object_factory.journal_entry_request(
        unique_id, generic_bank_account, bank_acc
    )
    transaction = company.create_journal_entry(journal_entry_req)
    assert transaction.transactionId is not None
    assert transaction.entries[0].journalEntryId is not None

    assert len(company.get_journal_entries(follow_pages=False)) > 0
    assert company.get_journal_entry(transaction.entries[0].journalEntryId) is not None

    assert len(company.get_transactions(follow_pages=False)) > 0
    assert company.get_transaction(transaction.transactionId) is not None

    # Invoice
    invoice_req = sample_object_factory.invoice_request(
        unique_id, generic_product, generic_contact, bank_acc
    )
    invoice = company.create_invoice(invoice_req)
    assert invoice.invoiceId is not None

    assert len(company.get_invoices(follow_pages=False)) > 0
    assert company.get_invoice(invoice.invoiceId) is not None

    # Credit note
    credit_note = company.create_credit_note_from_invoice_full(
        invoice.invoiceId, "Test credit note"
    )
    assert credit_note.creditNoteId is not None

    assert company.get_credit_notes(follow_pages=False) is not None

    # Offer
    assert company.get_offers(follow_pages=False) is not None

    # Order confirmation
    assert company.get_order_confirmations(follow_pages=False) is not None

    # Draft -> Invoice, Credit Note, Offer, Order
    draft_invoice_req = sample_object_factory.draft_invoiceish_request(
        unique_id, InvoiceDraftRequest, generic_product, generic_contact, bank_acc
    )
    draft_invoice_req = company.create_invoice_draft(draft_invoice_req)
    assert draft_invoice_req.draftId is not None
    assert draft_invoice_req.submit_object().invoiceId is not None

    draft_credit_note_req = sample_object_factory.draft_invoiceish_request(
        unique_id, CreditNoteDraftRequest, generic_product, generic_contact, bank_acc
    )
    draft_credit_note_req = company.create_credit_note_draft(draft_credit_note_req)
    assert draft_credit_note_req.draftId is not None
    assert draft_credit_note_req.submit_object().creditNoteId is not None

    draft_offer_req = sample_object_factory.draft_invoiceish_request(
        unique_id, OfferDraftRequest, generic_product, generic_contact, bank_acc
    )
    draft_offer_req = company.create_offer_draft(draft_offer_req)
    assert draft_offer_req.draftId is not None
    assert draft_offer_req.submit_object().offerId is not None

    draft_order_confirmation_req = sample_object_factory.draft_invoiceish_request(
        unique_id,
        OrderConfirmationDraftRequest,
        generic_product,
        generic_contact,
        bank_acc,
    )
    draft_order_confirmation_req = company.create_order_confirmation_draft(
        draft_order_confirmation_req
    )
    assert draft_order_confirmation_req.draftId is not None
    assert draft_order_confirmation_req.submit_object().confirmationId is not None

    # Sale
    sale_req = sample_object_factory.sale_request(unique_id, generic_contact)
    sale = company.create_sale(sale_req)
    assert sale.saleId is not None

    assert len(company.get_sales(follow_pages=False)) > 0
    assert company.get_sale(sale.saleId) is not None

    # Sale draft
    sale_draft_req = sample_object_factory.draft_order_request(
        unique_id, SaleDraftRequest, "3000", generic_contact, bank_acc
    )
    sale_draft_req = company.create_sale_draft(sale_draft_req)
    assert sale_draft_req.draftId is not None
    assert sale_draft_req.submit_object().saleId is not None

    # Payment
    payment: PaymentSale = PaymentSale(
        amount=1250,
        account=generic_bank_account.accountCode,
        date=datetime.date.today(),
    )
    sale.add_payment(payment)

    sale.delete("some bs reason")
    assert sale.deleted

    # Purchase
    purchase_req = sample_object_factory.purchase_request(unique_id, generic_contact)
    purchase = company.create_purchase(purchase_req)
    assert purchase.purchaseId is not None

    assert len(company.get_purchases(follow_pages=False)) > 0
    assert company.get_purchase(purchase.purchaseId) is not None

    # Purchase draft
    purchase_draft_req = sample_object_factory.draft_order_request(
        unique_id, PurchaseDraftRequest, "3000", generic_contact, bank_acc
    )
    purchase_draft_req = company.create_purchase_draft(purchase_draft_req)
    assert purchase_draft_req.draftId is not None
    assert purchase_draft_req.submit_object().purchaseId is not None

    # Payment
    payment: PaymentPurchase = PaymentPurchase(
        amount=1250,
        account=generic_bank_account.accountCode,
        date=datetime.date.today(),
    )
    purchase.add_payment(payment)

    purchase.delete("some bs reason")
    assert purchase.deleted
