from classically_punk.tags.normalize import TagAlias, build_language_variant_edges, build_slang_edges, detect_language, normalize_tag


def test_normalize_tag_simplifies_text():
    assert normalize_tag("Électro-Pop!!") == "electro-pop"
    assert normalize_tag("Hip  Hop 2.0") == "hip hop 2 0"


def test_detect_language_returns_code():
    assert detect_language("bonjour le monde") == "fr"


def test_build_slang_edges_creates_edge():
    aliases = [TagAlias(alias="trap", canonical="southern hip hop", confidence=0.8, source="test")]
    edges = build_slang_edges(aliases)
    assert len(edges) == 1
    e = edges[0]
    assert e.type == "SLANG_ALIAS"
    assert e.weight == 0.8
    assert e.src.endswith("trap")


def test_build_language_variant_edges():
    variants = [{"canonical": "hip hop", "translated": "hip-hop", "language": "en"}]
    edges = build_language_variant_edges(variants, source="test", version="v2")
    assert len(edges) == 1
    assert edges[0].type == "LANG_VARIANT"
    assert edges[0].version == "v2"
