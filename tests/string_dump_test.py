from sql_mapper.string_dump import raw, UnformattableString, FormattableString


def test_string_dump():
    assert (raw("abc") + "def" + "ghi").strings == [
        UnformattableString("abc"), FormattableString("def"),
        FormattableString("ghi")
    ]
