"""Stream Greek WordNet XML into standards-compliant RDF/Turtle."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote
from xml.etree.ElementTree import iterparse

from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import DCTERMS, XSD

WN = Namespace("http://www.w3.org/2006/03/wn/wn20/schema/")
WNEL = Namespace("https://w3id.org/wordnet-el/resource/")
ONTO = Namespace("https://w3id.org/wordnet-el/ontology/")

POS_TYPES = {
    "n": WN.NounSynset,
    "v": WN.VerbSynset,
    "a": WN.AdjectiveSynset,
    "b": WN.AdverbSynset,
    "r": WN.AdverbSynset,
    "s": WN.AdjectiveSynset,
}

RELATIONS = {
    "category_domain": WN.classifiedByTopic,
    "causes": WN.causes,
    "derived": WN.derivationallyRelated,
    "holo_member": WN.memberHolonymOf,
    "holo_part": WN.partHolonymOf,
    "holo_substance": WN.substanceHolonymOf,
    "hypernym": WN.hypernymOf,
    "near_antonym": WN.antonymOf,
    "antonym": WN.antonymOf,
    "region_domain": WN.classifiedByRegion,
    "similar_to": WN.similarTo,
    "usage_domain": WN.classifiedByUsage,
    "verb_group": WN.sameVerbGroupAs,
    "also_see": WN.seeAlso,
    "be_in_state": ONTO.beInState,
    "holo_portion": ONTO.portionHolonymOf,
    "subevent": ONTO.subeventOf,
}


@dataclass
class Statistics:
    synsets: int = 0
    senses: int = 0
    relations: int = 0
    unknown_relations: int = 0


def component(value: str) -> str:
    """Encode arbitrary Unicode text safely for use in an IRI path component."""
    return quote(value.strip(), safe="-._~")


def text_of(element, child: str) -> str:
    node = element.find(child)
    return "" if node is None or node.text is None else node.text.strip()


def convert(source: Path, destination: Path) -> Statistics:
    graph = Graph()
    graph.bind("wn", WN)
    graph.bind("wnel", WNEL)
    graph.bind("wnel-onto", ONTO)
    graph.bind("dcterms", DCTERMS)

    dataset = URIRef(WNEL["dataset"])
    graph.add((dataset, RDF.type, ONTO.WordNetDataset))
    graph.add((dataset, DCTERMS.title, Literal("Greek WordNet", lang="en")))
    graph.add((dataset, DCTERMS.language, Literal("el")))
    graph.add((dataset, DCTERMS.license, URIRef("https://creativecommons.org/licenses/by-sa/4.0/")))

    stats = Statistics()
    for _, synset in iterparse(source, events=("end",)):
        if synset.tag != "SYNSET":
            continue

        synset_id = text_of(synset, "ID")
        pos = text_of(synset, "POS")
        if not synset_id:
            synset.clear()
            continue

        subject = URIRef(WNEL[f"synset/{component(synset_id)}"])
        graph.add((subject, WN.synsetId, Literal(synset_id)))
        graph.add((subject, RDF.type, POS_TYPES.get(pos, WN.Synset)))

        definition = text_of(synset, "DEF")
        if definition:
            graph.add((subject, WN.gloss, Literal(definition, lang="el")))
        bcs = text_of(synset, "BCS")
        if bcs:
            graph.add((subject, ONTO.bcs, Literal(bcs, datatype=XSD.integer if bcs.isdigit() else None)))
        usage = text_of(synset, "USAGE")
        if usage:
            graph.add((subject, ONTO.usage, Literal(usage, lang="el")))
        stamp = text_of(synset, "STAMP")
        if stamp:
            graph.add((subject, ONTO.stamp, Literal(stamp)))

        synonym = synset.find("SYNONYM")
        if synonym is not None:
            for index, literal_node in enumerate(synonym.findall("LITERAL"), start=1):
                lemma = (literal_node.text or "").strip()
                if not lemma:
                    continue
                sense_number = text_of(literal_node, "SENSE") or "0"
                lnote = text_of(literal_node, "LNOTE")
                word = URIRef(WNEL[f"word/{component(lemma)}"])
                sense = URIRef(WNEL[f"sense/{component(synset_id)}/{index}"])
                graph.add((subject, WN.containsWordSense, sense))
                graph.add((subject, RDFS.label, Literal(lemma, lang="el")))
                graph.add((sense, RDF.type, WN.WordSense))
                graph.add((sense, WN.word, word))
                graph.add((sense, WN.sense, Literal(sense_number)))
                graph.add((sense, RDFS.label, Literal(lemma, lang="el")))
                graph.add((word, RDF.type, WN.Word))
                graph.add((word, WN.lexicalForm, Literal(lemma, lang="el")))
                graph.add((word, RDFS.label, Literal(lemma, lang="el")))
                if lnote:
                    graph.add((sense, ONTO.transliteration, Literal(lnote)))
                stats.senses += 1

        for relation in synset.findall("ILR"):
            target_id = (relation.text or "").strip()
            relation_type = text_of(relation, "TYPE")
            predicate = RELATIONS.get(relation_type)
            if target_id and predicate is not None:
                graph.add((subject, predicate, URIRef(WNEL[f"synset/{component(target_id)}"])))
                stats.relations += 1
            elif target_id:
                graph.add((subject, ONTO.related, URIRef(WNEL[f"synset/{component(target_id)}"])))
                stats.unknown_relations += 1

        stats.synsets += 1
        synset.clear()

    destination.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=destination, format="turtle", encoding="utf-8")
    return stats


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("source", type=Path, help="Greek WordNet XML input")
    result.add_argument("destination", type=Path, help="Turtle output file")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if not args.source.is_file():
        print(f"error: input file not found: {args.source}", file=sys.stderr)
        return 2
    stats = convert(args.source, args.destination)
    print(f"Wrote {args.destination}: {stats.synsets} synsets, {stats.senses} senses, "
          f"{stats.relations} relations ({stats.unknown_relations} unknown relation types).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
