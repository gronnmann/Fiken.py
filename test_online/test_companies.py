import os

from fiken_py.models import Company


def test_find_company_slug():
    company_slug = os.getenv("FIKEN_COMPANY_SLUG")

    company: Company = Company.get(company_slug=company_slug)
    assert company is not None

def test_get_all():
    companies: list[Company] = Company.getAll()
    assert companies is not None
    assert len(companies) > 0

    company_slug = os.getenv("FIKEN_COMPANY_SLUG")

    assert any(company.slug == company_slug for company in companies)