import pytest
from pydantic import ValidationError, BaseModel

from fiken_py.fiken_types import InvoiceLineRequest, BankAccountType, AccountCode
from fiken_py.models import BankAccount, BankAccountCreateRequest


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
        vatType="NONE",
        incomeAccount="3000",
    )
    assert invoice_line is not None


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
    ("150010001", False)
])
def test_account_code(test_input, valid):
    class AccountCodeTest(BaseModel):
        accountCode: AccountCode

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