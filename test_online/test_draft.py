import datetime

from fiken_py.shared_enums import VatTypeProduct, VatTypeProductSale
from fiken_py.models import BankAccount, Contact, Product, InvoiceDraftCreateRequest, InvoiceDraft, Invoice, DraftLineInvoiceIsh
from fiken_py.models.credit_note import CreditNote
from fiken_py.models.draft import CreditNoteDraftCreateRequest, CreditNoteDraft


def test_all_invoice_draft(unique_id: str, generic_product: Product, generic_customer: Contact,
                           generic_bank_account: BankAccount):
    draft_line = DraftLineInvoiceIsh(
        productId=generic_product.productId,
        quantity=1,
        vatType=VatTypeProductSale.HIGH,
    )

    draft_line_non_product = DraftLineInvoiceIsh(
        description="En banankasse fra Bendit (testprodukt fritekst)",
        unitPrice=10000,
        vatType=VatTypeProductSale.HIGH,
        incomeAccount="3000",
        quantity=2,
    )

    draft: InvoiceDraftCreateRequest = InvoiceDraftCreateRequest(
        issueDate=datetime.date.today(),
        daysUntilDueDate=7,
        customerId=generic_customer.contactId,
        lines=[draft_line, draft_line_non_product],
        ourReference=f"Test draft ({unique_id}#product)",
        invoiceText="This is a test draft sent by FikenPy",
        bankAccountNumber=generic_bank_account.bankAccountNumber,
    )

    request_copy = draft.model_copy()

    # Step 1 - create and validate draft object
    draft: InvoiceDraft = draft.save()
    assert draft.draftId is not None
    assert draft.daysUntilDueDate == 7
    assert draft.customers[0].contactId == generic_customer.contactId
    assert draft.lines[0].productId == generic_product.productId
    for k, v in draft_line_non_product.model_dump().items():
        if v is None:
            continue
        assert draft.lines[1].model_dump()[k] == v

    # Step 2 - make sure draft object exists
    get_draft: InvoiceDraft = InvoiceDraft.get(draftId=draft.draftId)
    assert get_draft is not None
    assert get_draft == draft

    # Step 3 - test draft PUT
    draft.lines.pop()
    draft.save()
    assert len(draft.lines) == 1
    assert draft.lines[0].productId == generic_product.productId

    # Step 4 - test draft submit (create invoice)
    invoice: Invoice = draft.submit_object()
    assert invoice is not None
    assert invoice.invoiceId is not None

    get_draft = InvoiceDraft.get(draftId=draft.draftId)
    assert get_draft is None

    # Step 5 - recreate draft, test delete
    new_draft: InvoiceDraft = request_copy.save()
    assert InvoiceDraft.get(draftId=new_draft.draftId) is not None
    id = new_draft.draftId
    new_draft.delete()
    assert InvoiceDraft.get(draftId=id) is None


def test_all_credit_note(unique_id: str, generic_product: Product, generic_customer: Contact,
                         generic_bank_account: BankAccount):
    draft_line = DraftLineInvoiceIsh(
        productId=generic_product.productId,
        quantity=1,
        vatType=VatTypeProductSale.HIGH,
    )

    draft: CreditNoteDraftCreateRequest = CreditNoteDraftCreateRequest(
        issueDate=datetime.date.today(),
        daysUntilDueDate=7,
        customerId=generic_customer.contactId,
        lines=[draft_line],
        ourReference=f"Test credit note ({unique_id}#product)",
        invoiceText="This is a test credit note sent by FikenPy",
        bankAccountNumber=generic_bank_account.bankAccountNumber,
    )

    request_copy = draft.model_copy()

    # Step 1 - test GET and POST
    credit_note_draft: CreditNoteDraft = draft.save()
    assert credit_note_draft.draftId is not None
    draft_id = credit_note_draft.draftId

    # Step 2 - test PUT

    credit_note_draft.ourReference = "endret referanse"
    credit_note_draft.save()

    credit_note_draft = CreditNoteDraft.get(draftId=draft_id)
    assert credit_note_draft.ourReference == "endret referanse"

    # Step 3 - test delete
    credit_note_draft.delete()
    assert CreditNoteDraft.get(draftId=draft_id) is None

    # Step 4 - recreate draft, test delete
    new_draft: CreditNoteDraft = request_copy.save()
    assert CreditNoteDraft.get(draftId=new_draft.draftId) is not None

    credit_note: CreditNote = new_draft.submit_object()
    assert credit_note is not None
    assert credit_note.creditNoteId is not None

