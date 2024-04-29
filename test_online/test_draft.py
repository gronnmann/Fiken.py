import datetime

from fiken_py.fiken_types import VatTypeProduct, VatTypeProductSale
from fiken_py.models import BankAccount, Contact, Product, InvoiceDraftCreateRequest, InvoiceDraft, Invoice, DraftLine


def test_all_invoice_draft(unique_id: str, generic_product: Product, generic_customer: Contact, generic_bank_account: BankAccount):

    draft_line = DraftLine(
        productId=generic_product.productId,
        quantity=1,
        vatType=VatTypeProductSale.HIGH,
    )

    draft_line_non_product = DraftLine(
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




