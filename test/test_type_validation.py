import pytest
from pydantic import ValidationError, BaseModel

from fiken_py.models.draft import PurchaseDraftCreateRequest, SaleDraftCreateRequest
from fiken_py.shared_enums import VatTypeProductSale, VatTypeProductPurchase
from fiken_py.shared_types import InvoiceLineRequest, AccountingAccount, AccountingAccountAssets, \
    AccountingAccountCosts, AccountingAccountIncome, AccountingAccountEquityAndLiabilities, DraftLineOrder, OrderLine
from fiken_py.models import BankAccount, BankAccountCreateRequest, DraftLineInvoiceIsh, BankAccountType


def test_validate_invoice_line():
    invoice_line = InvoiceLineRequest(
        productId=1,
        quantity=1,
    )

    assert invoice_line.productId is not None

    with pytest.raises(ValidationError):
        invoice_line = InvoiceLineRequest(
            quantity=1,
            description="En banankasse fra Bendit (testprodukt fritekst)",
        )

    invoice_line = InvoiceLineRequest(
        quantity=1,
        description="En banankasse fra Bendit (testprodukt fritekst)",
        unitPrice=10000,
        vatType="EXEMPT",
        incomeAccount="3100",
    )
    assert invoice_line is not None


def test_validate_draft_line():
    draft_line = DraftLineInvoiceIsh(
        productId=1,
        quantity=1,
    )

    assert draft_line.productId is not None

    with pytest.raises(ValidationError):
        draft_line = DraftLineInvoiceIsh(
            quantity=1,
            description="En banankasse fra Bendit (testprodukt fritekst)",
        )

    draft_line = DraftLineInvoiceIsh(
        quantity=1,
        description="En banankasse fra Bendit (testprodukt fritekst)",
        unitPrice=10000,
        vatType="HIGH",
        incomeAccount="3000",
    )
    assert draft_line is not None

    with pytest.raises(ValidationError):
        draft_line = DraftLineInvoiceIsh(
            quantity=1,
            description="En banankasse fra Bendit (testprodukt fritekst)",
            unitPrice=10000,
            vatType="NONE",
            incomeAccount="3000",  # wrong VAT Type
        )


def test_bankaccount_request_foreignservice():
    bank_account = BankAccountCreateRequest(
        name="Test Bank Account",
        bankAccountNumber="12345678901",
        type=BankAccountType.FOREIGN,
        foreignService="Test Service",
    )

    assert bank_account is not None

    bank_account = BankAccountCreateRequest(
        name="Test Bank Account",
        bankAccountNumber="12345678901",
        type=BankAccountType.NORMAL,
    )

    assert bank_account is not None

    # type normal, but foreignService
    with pytest.raises(ValidationError):
        bank_account = BankAccountCreateRequest(
            name="Test Bank Account",
            bankAccountNumber="12345678901",
            type=BankAccountType.NORMAL,
            foreignService="Test Service",
        )

    # type foreign, but no foreignService
    with pytest.raises(ValidationError):
        bank_account = BankAccountCreateRequest(
            name="Test Bank Account",
            bankAccountNumber="12345678901",
            type=BankAccountType.FOREIGN,
        )


@pytest.mark.parametrize("test_input,valid", [
    ("3020", True),
    ("1500:10001", True),
    ("1", False),
    ("1234", True),
    ("12345:", False),
    ("150010001", False),
    ("9000", False),
])
def test_accounting_account(test_input, valid):
    class AccountCodeTest(BaseModel):
        accountCode: AccountingAccount

    if not valid:
        with pytest.raises(ValidationError):
            acc = AccountCodeTest(
                accountCode=test_input
            )
    else:
        acc = AccountCodeTest(
            accountCode=test_input
        )
        assert acc is not None
        assert acc.accountCode == test_input


@pytest.mark.parametrize("test_input,valid_assets,valid_equity_and_liabilities,valid_income,valid_costs",
                         [
                             ("1500", True, False, False, False),
                             ("1500:10001", True, False, False, False),
                             ("2000", False, True, False, False),
                             ("3000", False, False, True, False),
                             ("3200", False, False, True, False),
                             ("4000", False, False, False, True),
                             ("1", False, False, False, False),
                             ("1234", True, False, False, False),
                             ("12345:", False, False, False, False),
                             ("150010001", False, False, False, False),
                             ("8123", False, False, True, True),
                         ])
def test_account_account_classes(
        test_input, valid_assets, valid_equity_and_liabilities, valid_income, valid_costs):
    class AssetsAccount(BaseModel):
        accountCode: AccountingAccountAssets

    if not valid_assets:
        with pytest.raises(ValidationError):
            acc = AssetsAccount(
                accountCode=test_input
            )
    else:
        acc = AssetsAccount(
            accountCode=test_input
        )
        assert acc is not None
        assert acc.accountCode == test_input

    class EquityAndLiabilitiesAccount(BaseModel):
        accountCode: AccountingAccountEquityAndLiabilities

    if not valid_equity_and_liabilities:
        with pytest.raises(ValidationError):
            acc = EquityAndLiabilitiesAccount(
                accountCode=test_input
            )

    else:
        acc = EquityAndLiabilitiesAccount(
            accountCode=test_input
        )
        assert acc is not None
        assert acc.accountCode == test_input

    class IncomeAccount(BaseModel):
        accountCode: AccountingAccountIncome

    if not valid_income:
        with pytest.raises(ValidationError):
            acc = IncomeAccount(
                accountCode=test_input
            )

    else:
        acc = IncomeAccount(
            accountCode=test_input
        )
        assert acc is not None
        assert acc.accountCode == test_input

    class CostsAccount(BaseModel):
        accountCode: AccountingAccountCosts

    if not valid_costs:
        with pytest.raises(ValidationError):
            acc = CostsAccount(
                accountCode=test_input
            )



def test_sale_purcahse_draft_vat_types():
    draft_line_purchase = DraftLineOrder(
        vatType=VatTypeProductPurchase.HIGH_PURCHASE_OF_EMISSIONSTRADING_OR_GOLD_NONDEDUCTIBLE,
    )

    draft_line_sale = DraftLineOrder(
        vatType=VatTypeProductSale.EXEMPT)

    draft_line_both = DraftLineOrder(
        vatType="HIGH"
    )

    correct = PurchaseDraftCreateRequest(
        cash=True, lines=[draft_line_purchase]
    )
    assert correct is not None

    with pytest.raises(ValidationError):
        wrong = PurchaseDraftCreateRequest(
            cash=True, lines=[draft_line_sale]
        )

    correct = PurchaseDraftCreateRequest(
        cash=True, lines=[draft_line_both]
    )
    assert correct is not None

    correct = SaleDraftCreateRequest(
        cash=True, lines=[draft_line_sale]
    )
    assert correct is not None

    with pytest.raises(ValidationError):
        wrong = SaleDraftCreateRequest(
            cash=True, lines=[draft_line_purchase]
        )

    correct = SaleDraftCreateRequest(
        cash=True, lines=[draft_line_both]
    )

    assert correct is not None


def test_order_line_netPrice_or_netPriceInCurrency():
    with pytest.raises(ValidationError):
        order_line = OrderLine(
            description="Test",
            vatType="HIGH",
            account="3000",
        )

    order_line = OrderLine(
        netPrice=100,
        vatType="HIGH",
    )
    assert order_line is not None

    order_line = OrderLine(
        netPriceInCurrency=100,
        vatType="HIGH",
    )
    assert order_line is not None