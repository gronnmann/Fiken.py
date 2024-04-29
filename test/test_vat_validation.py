import pytest

from fiken_py.fiken_types import VatTypeProductSale
from fiken_py.vat_validation import VATValidator


def test_account_match():
    assert VATValidator._account_match("3100", "31xx")
    assert VATValidator._account_match("3100", "3xxx")
    assert VATValidator._account_match("3200", "32xx")
    assert VATValidator._account_match("3100", "32xx") is False
    assert VATValidator._account_match("3100", "31x9") is False
    assert VATValidator._account_match("3129", "31x9")


def test_sale_high():
    vat_high = VatTypeProductSale.HIGH

    assert VATValidator.validate_vat_type_sale(vat_high, percentage=25)
    assert VATValidator.validate_vat_type_sale(vat_high, percentage=22) is False

    with pytest.raises(ValueError):
        VATValidator.validate_vat_type_sale(vat_high, percentage=25, account_code="3000")

    assert VATValidator.validate_vat_type_sale(vat_high, account_code="3000")
    assert VATValidator.validate_vat_type_sale(vat_high, account_code="3030") is False


def test_sale_high_forbidden():
    vat_outside = VatTypeProductSale.OUTSIDE

    assert VATValidator.validate_vat_type_sale(vat_outside, percentage=0)

    assert VATValidator.validate_vat_type_sale(vat_outside, account_code="3200")
    assert VATValidator.validate_vat_type_sale(vat_outside, account_code="3210") is False
