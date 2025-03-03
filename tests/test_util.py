from rapporto.util import sanitize_title


def test_sanitize_title():
    assert sanitize_title("[Foo] Hotzenplotz") == "⎡Foo⎦ Hotzenplotz"
