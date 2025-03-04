from rapporto.source.github.util import repository_name


def test_repository_name():
    assert repository_name("https://github.com/tech-writing/rapporto") == "rapporto"
    assert (
        repository_name("https://github.com/tech-writing/rapporto", with_org=True)
        == "tech-writing/rapporto"
    )
    assert repository_name("https://github.com/tech-writing/rapporto/issues/19") == "rapporto"
    assert (
        repository_name("https://github.com/tech-writing/rapporto/issues/19", with_org=True)
        == "tech-writing/rapporto"
    )
    assert (
        repository_name("https://api.github.com/repos/tech-writing/rapporto")
        == "rapporto"
    )
