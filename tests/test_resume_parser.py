import json
from pathlib import Path
import importlib.util
import pytest

# load ResumeParser directly from file (package dir has no __init__.py in this workspace)
spec = importlib.util.spec_from_file_location(
    "resume_parser_module",
    Path(__file__).resolve().parents[1] / "parsers" / "resume_parser.py",
)
_resume_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_resume_mod)
ResumeParser = _resume_mod.ResumeParser


def test_parse_file_type_error():
    parser = ResumeParser()
    with pytest.raises(TypeError):
        parser.parse_file(123)  # invalid type


def test_parse_file_with_path_object(tmp_path):
    p = tmp_path / "r.txt"
    p.write_text("Alice\nSkills: Python")

    r = ResumeParser().parse_file(p)  # accept pathlib.Path
    assert r['file_name'] == "r.txt"
    assert "Python" in r['text']


def test_parse_txt_success(tmp_path):
    p = tmp_path / "r2.txt"
    p.write_text("Hello world")

    r = ResumeParser().parse_file(str(p))
    assert r['file_name'] == "r2.txt"
    assert "Hello world" in r['text']


def test_parse_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        ResumeParser().parse_file("no-such-file.txt")


def test_unsupported_extension_raises(tmp_path):
    f = tmp_path / "a.xyz"
    f.write_text("x")
    with pytest.raises(ValueError):
        ResumeParser().parse_file(str(f))


def test_parse_jsonl_type_error():
    with pytest.raises(TypeError):
        ResumeParser().parse_jsonl(123)


def test_parse_jsonl_success(tmp_path):
    jl = tmp_path / "resumes.jsonl"
    jl.write_text(json.dumps({"ResumeID": "1", "Name": "Bob", "Text": "hi"}) + "\n")

    res = ResumeParser().parse_jsonl(str(jl))
    assert res[0]['name'] == "Bob"
    assert res[0]['resume_id'] == "1"
    assert "hi" in res[0]['text']


def test_parse_directory_type_error():
    with pytest.raises(TypeError):
        ResumeParser().parse_directory(123)


def test_parse_directory_success(tmp_path):
    d = tmp_path / "dir"
    d.mkdir()
    (d / "a.txt").write_text("content")
    (d / "b.xyz").write_text("ignored")

    res = ResumeParser().parse_directory(str(d))
    assert len(res) == 1
    assert res[0]['file_name'] == "a.txt"


def test_convert_doc_requires_soffice(tmp_path):
    parser = ResumeParser()
    doc = tmp_path / "a.doc"
    doc.write_text("dummy")
    with pytest.raises(RuntimeError):
        parser._convert_doc_to_docx(doc)


def test_parse_doc_conversion_and_cleanup(monkeypatch, tmp_path):
    parser = ResumeParser()
    src = tmp_path / "sample.doc"
    src.write_text("dummy")

    converted = tmp_path / "sample.docx"
    converted.write_text("fake")  # will be removed by parser after extraction

    # force the parser to use our prepared converted file and a stub extractor
    monkeypatch.setattr(ResumeParser, "_convert_doc_to_docx", lambda self, p: converted)
    monkeypatch.setattr(ResumeParser, "_extract_docx", lambda self, p: "EXTRACTED")

    result = parser.parse_file(str(src))
    assert result['text'] == "EXTRACTED"
    # parser should remove the temporary converted file
    assert not converted.exists()
