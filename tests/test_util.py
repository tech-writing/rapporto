from rapporto.util import sanitize_title, week_to_day_range


def test_sanitize_title():
    assert sanitize_title("[Foo] Hotzenplotz") == "⎡Foo⎦ Hotzenplotz"


def test_week_to_day_range():
    assert len(week_to_day_range("2025W09", skip_the_future=False)) == 7
