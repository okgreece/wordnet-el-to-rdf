from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS

from wordnet_el.converter import WN, WNEL, convert


def test_conversion(tmp_path: Path) -> None:
    source = tmp_path / "sample.xml"
    source.write_text(
        """<WordNet><SYNSET><ID>ENG20-00000001-n</ID><POS>n</POS>
        <SYNONYM><LITERAL>λέξη<SENSE>1</SENSE><LNOTE>lexi</LNOTE></LITERAL></SYNONYM>
        <ILR>ENG20-00000002-n<TYPE>hypernym</TYPE></ILR>
        <DEF>ένας ορισμός</DEF><BCS>2</BCS></SYNSET></WordNet>""",
        encoding="utf-8",
    )
    output = tmp_path / "output.ttl"
    stats = convert(source, output)
    graph = Graph().parse(output, format="turtle")
    subject = URIRef(WNEL["synset/ENG20-00000001-n"])

    assert stats.synsets == 1
    assert stats.senses == 1
    assert stats.relations == 1
    assert (subject, WN.gloss, Literal("ένας ορισμός", lang="el")) in graph
    assert (URIRef(WNEL["dataset"]), DCTERMS.license,
            URIRef("https://creativecommons.org/licenses/by/4.0/")) in graph

