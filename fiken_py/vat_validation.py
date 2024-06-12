import logging
import re

from fiken_py.shared_enums import VatTypeProductSale

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from fiken_py.shared_types import AccountingAccountIncome

logger = logging.getLogger("fiken_py")


class VATValidator:
    vat_types_product_sale: dict[VatTypeProductSale, tuple[float, list[str]]] = {
        VatTypeProductSale.HIGH: (25, [
            "3000",
            "3010",
            "3020",
            "3061",
            "3070",
            "3081",
            "3090",
        ]),

        VatTypeProductSale.MEDIUM: (15, [
            "3030",
            "3040",
            "3063",
        ]),

        VatTypeProductSale.LOW: (12, [
            "3050",
            "3081",
            "3090"
        ]),

        VatTypeProductSale.NONE: (0, [
            "xxx9"
        ]),
        VatTypeProductSale.OUTSIDE: (0, [
            "32xx",
            "-3210",
            "-3209",
            "-3219",
            "-3229"
        ]),
        VatTypeProductSale.EXEMPT: (0, [
            "31xx",
        ]),
        VatTypeProductSale.EXEMPT_IMPORT_EXPORT: (0, [
            "31xx"
            "-31x9"
        ]),
        VatTypeProductSale.RAW_FISH: (11.11, [
            "3030",
        ]),
    }

    @classmethod
    def _account_match(cls, account_code: str, match_code: str) -> bool:
        """Checks whenever account_code (for example 31) matches the given match_code (for example 31xx)."""

        match_code = match_code.replace("-", "")
        match_as_regex = match_code.replace("x", r"\d")

        return True if re.match(match_as_regex, account_code) else False

    @classmethod
    def validate_vat_type_sale(cls, vat_type: VatTypeProductSale, account_code: Optional['AccountingAccountIncome'] = None,
                               percentage: Optional[float] = None):
        """Validates either an vat type against an account code or a percentage.
            Account data is from: https://kontohjelp.fiken.no/as/medMoms/

            The data is stored in a dictionary with the format: 'xxxx' where 'x' is an arbitrary digit.
            Minus in front of the account code means that all matches should not be included.

            Args:
                vat_type (VatTypeProductSale): The vat type to validate.
                account_code (AccountingAccountIncome): The account code to validate against.
                percentage (float): The percentage to validate against.

            Raises:
                ValueError: If both account_code and percentage is provided.

            returns True if the account code or percentage is valid for the vat type, False otherwise.

        """
        # TODO - "Foretak som ikke er mva-registrerte bruker inntektskontoene i 32xx-serien."
        # TODO - enk

        if account_code is not None and percentage is not None:
            raise ValueError("Only one of account_code or percentage can be provided")

        if cls.vat_types_product_sale.get(vat_type, None) is None:
            logger.warning(f"Vat type {vat_type} is not implemented. Approved by default.")
            return True

        if percentage is not None:
            return cls.vat_types_product_sale[vat_type][0] == percentage

        # acc code not none
        # For correct match - one of strings must match, and none of the forbidden strings must match

        correct_match = False
        forbidden_match = False
        for match_code in cls.vat_types_product_sale[vat_type][1]:
            if match_code.startswith("-"):
                forbidden_match = forbidden_match or cls._account_match(account_code, match_code)
            else:
                correct_match = correct_match or cls._account_match(account_code, match_code)

        return correct_match and not forbidden_match
