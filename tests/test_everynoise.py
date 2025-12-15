from classically_punk.ingest.everynoise import _parse_style, parse_everynoise_html


def test_parse_style_extracts_numbers():
    style = "color: #ad8907; top: 4997px; left: 783px; font-size: 160%"
    parsed = _parse_style(style)
    assert parsed["color"] == "#ad8907"
    assert parsed["top_px"] == 4997.0
    assert parsed["left_px"] == 783.0
    assert parsed["font_size_pct"] == 160.0


def test_parse_everynoise_html_extracts_records():
    sample = '''
    <div id=item1 preview_url="https://example.com/a" class="genre scanme" scan=true
    style="color: #ad8907; top: 100px; left: 200px; font-size: 120%" role="button" tabindex="0">pop</div>
    '''
    records = parse_everynoise_html(sample)
    assert len(records) == 1
    rec = records[0]
    assert rec["name"] == "pop"
    assert rec["preview_url"] == "https://example.com/a"
    assert rec["top_px"] == 100.0
