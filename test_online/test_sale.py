import datetime

from fiken_py.models import SaleDraftCreateRequest, SaleDraft, Contact, BankAccount, Sale, SaleRequest, PaymentSale
from fiken_py.shared_enums import SaleKind
from fiken_py.shared_types import OrderLine
from test_online import shared_tests


def test_sale_manual(unique_id: str, generic_contact: Contact, generic_bank_account: BankAccount):
    sale_line = OrderLine(
        description=f"En tilfeldig fjernkontroll (testprodukt {unique_id})",
        vatType="HIGH",
        account="3000",
        netPrice=1000,
        vat=250,
    )

    sale_request = SaleRequest(
        date=datetime.date.today(),
        lines=[sale_line],
        kind=SaleKind.EXTERNAL_INVOICE,
        customerId=generic_contact.contactId,
        currency="NOK",
    )

    sale: Sale = sale_request.save()

    assert sale is not None
    assert sale.saleId is not None

    assert len(sale.salePayments) == 0

    payment: PaymentSale = PaymentSale(
        saleId=sale.saleId,
        amount=1250,
        account=generic_bank_account.accountCode,
        date=datetime.date.today(),
    )
    payment.save()

    sale._refresh_object()

    assert len(sale.salePayments) == 1
    assert sale.salePayments[0].amount == 1250

def test_sale_draft(unique_id: str, generic_contact: Contact, generic_bank_account: BankAccount):
    sale: Sale = shared_tests.draftable_order_object_tests(
        SaleDraft,
        SaleDraftCreateRequest,
        "4000",
        unique_id,
        generic_contact,
        generic_bank_account
    )

    assert sale is not None

    assert sale.settled is False

    assert sale.set_settled() is True

    assert sale.settled

    sale.delete("Test delete sale.")

    assert sale.deleted
