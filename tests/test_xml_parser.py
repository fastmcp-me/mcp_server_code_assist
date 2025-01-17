from mcp_server_code_assist.xml_parser import XMLProcessor


def test_parse_create():
    xml = """<?xml version="1.0"?>
    <instruction>
        <function>create</function>
        <path>/tmp/test.txt</path>
        <content>test content</content>
    </instruction>"""

    result = XMLProcessor().parse(xml)
    assert result["function"] == "create"
    assert result["path"] == "/tmp/test.txt"
    assert result["content"] == "test content"


def test_parse_modify():
    xml = """<?xml version="1.0"?>
    <instruction>
        <function>modify</function>
        <path>/tmp/test.txt</path>
        <replacements>
            <old>new</old>
            <test>example</test>
        </replacements>
    </instruction>"""

    result = XMLProcessor().parse(xml)
    assert result["function"] == "modify"
    assert result["replacements"] == {"old": "new", "test": "example"}


def test_generate():
    data = {"function": "create", "path": "/tmp/test.txt", "content": "test content"}

    xml = XMLProcessor().generate(data)
    assert all(x in xml for x in ["create", "/tmp/test.txt", "test content"])
