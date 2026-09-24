from rsmetacheck_bot import reporting


def test_extract_bot_version_from_legacy_keys():
    assert reporting.extract_bot_version({"bot_version": "1.2.3"}) == "1.2.3"
    assert (
        reporting.extract_bot_version({"rsmetacheck_bot_version": "2.0.0"}) == "2.0.0"
    )
    assert (
        reporting.extract_bot_version({"rsmetacheck_bot_version": "3.0.0"}) == "3.0.0"
    )
    assert reporting.extract_bot_version({}) is None


def test_reportrecord_from_dict_uses_extracted_version():
    d = {
        "repo_url": "https://example.com",
        "rsmetacheck_version": "x",
        "bot_version": "9.9.9",
    }
    rr = reporting.ReportRecord.from_dict(d)
    assert rr.rsmetacheck_bot_version == "9.9.9"
