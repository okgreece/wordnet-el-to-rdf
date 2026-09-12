# Greek WordNet RDF conversion

This project converts the Greek WordNet XML dataset to modern,
standards-compliant RDF in Turtle format using Python and [RDFLib](https://rdflib.readthedocs.io/).

The source snapshot contains 18,461 synsets and 24,477 Greek lexical entries.
The converter provides stable ID-based IRIs, safe Unicode URI encoding,
streaming XML input, explicit language tags, and RDF parsing tests.

## Requirements and installation

Python 3.10 or newer is required.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## Convert

The source file is stored unchanged at `data/source/wngre2.xml`.

```sh
wordnet-el data/source/wngre2.xml wordnet-el.ttl
```

## Verify

```sh
python -m pip install pytest
pytest
python -c "from rdflib import Graph; g=Graph().parse('wordnet-el.ttl'); print(len(g))"
```

## Data model

- Synsets use `https://w3id.org/wordnet-el/resource/synset/{WordNet-ID}`.
- Words and senses are distinct RDF resources.
- Definitions and Greek labels carry the `el` language tag.
- Inter-lingual relations use the WordNet 2.0 RDF vocabulary.
- Unknown relation types are retained as `wnel-onto:related`.
- The graph contains a machine-readable CC BY 4.0 license statement.

## Provenance and changes

This project modernizes the Greek WordNet conversion package dated
2013. The original XML is retained unchanged as inherited from thw Balkanet project. The file was developed by a team of linguists in the DataBase Sysemts Laboratory (DBLab), University of Patras with the attendance of University of Athens. The converter was originally written in C++, to be replaced by a
Python implementation; identifiers, escaping, error handling, metadata, and serialization were
modernized. The result is not byte-for-byte compatible with the historical N3.

## License and attribution

The project, source data, and generated RDF are available under the
[Creative Commons Attribution 4.0 International license](https://creativecommons.org/licenses/by/4.0/).

When redistributing or adapting the material, credit **Greek WordNet
contributors**, identify this project as the source, link to the license, and
indicate whether changes were made. Replace or supplement that placeholder with
the precise creator and project URL before public release if known.

See `LICENSE` for the legal text and `CITATION.cff` for citation metadata.
