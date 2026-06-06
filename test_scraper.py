"""
test_scraper.py — Basic sanity tests for the job scraper pipeline

Run with: python -m pytest test_scraper.py -v
"""

from companies import (
    GREENHOUSE_COMPANIES,
    LEVER_COMPANIES,
    WORKDAY_COMPANIES,
    ASHBY_COMPANIES,
    SMARTRECRUITERS_COMPANIES,
    SEARCH_KEYWORDS,
    ALL_COMPANIES,
)


# ─────────────────────────────────────────────
# companies.py structure tests
# ─────────────────────────────────────────────

def test_greenhouse_companies_have_required_keys():
    for company in GREENHOUSE_COMPANIES:
        assert "name" in company, f"Missing 'name' in: {company}"
        assert "board_token" in company, f"Missing 'board_token' in: {company}"
        assert "category" in company, f"Missing 'category' in: {company}"


def test_lever_companies_have_required_keys():
    for company in LEVER_COMPANIES:
        assert "name" in company, f"Missing 'name' in: {company}"
        assert "company_id" in company, f"Missing 'company_id' in: {company}"
        assert "category" in company, f"Missing 'category' in: {company}"


def test_workday_companies_have_required_keys():
    for company in WORKDAY_COMPANIES:
        assert "name" in company, f"Missing 'name' in: {company}"
        assert "url" in company, f"Missing 'url' in: {company}"
        assert "category" in company, f"Missing 'category' in: {company}"


def test_ashby_companies_have_required_keys():
    for company in ASHBY_COMPANIES:
        assert "name" in company, f"Missing 'name' in: {company}"
        assert "company_id" in company, f"Missing 'company_id' in: {company}"
        assert "category" in company, f"Missing 'category' in: {company}"


def test_smartrecruiters_companies_have_required_keys():
    for company in SMARTRECRUITERS_COMPANIES:
        assert "name" in company, f"Missing 'name' in: {company}"
        assert "company_id" in company, f"Missing 'company_id' in: {company}"
        assert "category" in company, f"Missing 'category' in: {company}"


def test_all_categories_are_valid():
    valid = {"food", "analytics"}
    for company in ALL_COMPANIES:
        assert company["category"] in valid, (
            f"{company['name']} has invalid category: {company['category']}"
        )


def test_no_duplicate_company_names():
    names = [c["name"] for c in ALL_COMPANIES]
    duplicates = [n for n in names if names.count(n) > 1]
    assert not duplicates, f"Duplicate company names found: {set(duplicates)}"


def test_all_companies_count_matches_sum():
    expected = (
        len(GREENHOUSE_COMPANIES)
        + len(LEVER_COMPANIES)
        + len(WORKDAY_COMPANIES)
        + len(ASHBY_COMPANIES)
        + len(SMARTRECRUITERS_COMPANIES)
    )
    assert len(ALL_COMPANIES) == expected, (
        f"ALL_COMPANIES has {len(ALL_COMPANIES)} entries, expected {expected}"
    )


# ─────────────────────────────────────────────
# Keyword filter tests
# ─────────────────────────────────────────────

def title_matches_keywords(title: str, keywords: list[str]) -> bool:
    """Mirror the filter logic used in scraper.py."""
    title_lower = title.lower()
    return any(kw.lower() in title_lower for kw in keywords)


def test_matching_titles_are_surfaced():
    should_match = [
        "Data Analyst",
        "Business Intelligence Analyst",
        "Analytics Intern",
        "Junior Data Analyst",
        "Reporting Analyst",
        "BI Analyst",
        "Data Engineering Intern",
        "Supply Chain Analyst",
    ]
    for title in should_match:
        assert title_matches_keywords(title, SEARCH_KEYWORDS), (
            f"Expected title to match but did not: '{title}'"
        )


def test_non_matching_titles_are_skipped():
    should_not_match = [
        "Software Engineer",
        "Senior Marketing Manager",
        "Executive Chef",
        "Line Cook",
        "DevOps Engineer",
        "Product Designer",
    ]
    for title in should_not_match:
        assert not title_matches_keywords(title, SEARCH_KEYWORDS), (
            f"Expected title NOT to match but it did: '{title}'"
        )


def test_search_keywords_list_is_nonempty():
    assert len(SEARCH_KEYWORDS) > 0, "SEARCH_KEYWORDS is empty"


def test_core_keywords_present():
    keywords_lower = [kw.lower() for kw in SEARCH_KEYWORDS]
    for expected in ["data analyst", "business intelligence", "analytics intern"]:
        assert expected in keywords_lower, f"Expected keyword missing: '{expected}'"
