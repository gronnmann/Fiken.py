import datetime

from fiken_py.models import PurchaseRequest, Purchase, Contact, BankAccount, PurchaseDraft, PurchaseDraftCreateRequest
from fiken_py.shared_enums import PurchaseKind
from fiken_py.shared_types import OrderLine
from fiken_py.models.payment import Payment, PaymentPurchase
from test_online import shared_tests


def test_purchase_cash(unique_id: str, generic_bank_account):
    purchase_line = OrderLine(
        description=f"En veldig stor hagesaks (testprodukt {unique_id})",
        vatType="HIGH",
        account="4300",
        netPrice=1000,
        vat="250",
    )

    purchase_request = PurchaseRequest(
        date=datetime.date.today(),
        kind=PurchaseKind.CASH_PURCHASE,
        currency="NOK",
        lines=[purchase_line],
        paid=True,
        paymentAccount=generic_bank_account.accountCode,
        paymentDate=datetime.date.today(),
    )

    purchase: Purchase = purchase_request.save()

    assert purchase is not None
    assert purchase.purchaseId is not None
    assert purchase.deleted is False

    assert len(purchase.payments) == 1


def test_purchase_supplier(unique_id: str, generic_bank_account, generic_contact: Contact):
    purchase_line = OrderLine(
        description=f"En veldig billig AK (testprodukt {unique_id})",
        vatType="HIGH",
        account="4300",
        netPrice=100000,
        vat="25000",
    )

    purchase_request = PurchaseRequest(
        date=datetime.date.today(),
        kind=PurchaseKind.SUPPLIER,
        currency="NOK",
        lines=[purchase_line],
        paid=True,
        supplierId=generic_contact.contactId,
    )

    purchase: Purchase = purchase_request.save()

    assert len(purchase.payments) == 0

    payment = PaymentPurchase(
        date=datetime.date.today(),
        amount=125000,
        account=generic_bank_account.accountCode,
        purchaseId=purchase.purchaseId,
    )
    payment: Payment = payment.save()

    purchase._refresh_object()

    assert len(purchase.payments) == 1

    assert purchase.payments[0].paymentId == payment.paymentId
    assert purchase.payments[0].amount == payment.amount

    assert purchase.paid is True

    set_deleted = purchase.delete("Test delete purchase")

    assert purchase.deleted is True


def test_purchase_draft(unique_id: str, generic_contact: Contact, generic_bank_account: BankAccount):
    shared_tests.draftable_order_object_tests(
        PurchaseDraft,
        PurchaseDraftCreateRequest,
        "3000",
        unique_id,
        generic_contact,
        generic_bank_account
    )