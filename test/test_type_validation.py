import pytest
from pydantic import ValidationError

from fiken_py.fiken_types import InvoiceLineRequest


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