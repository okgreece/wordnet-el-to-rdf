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
- The graph contains a machine-readable CC BY-SA 4.0 license statement.

## Provenance and changes

This project modernizes a Greek WordNet conversion package dated 2013. The
original XML is retained unchanged. The Greek WordNet was funded by the then
General Secretariat for Research and Technology (GSRT), with the Database
Laboratory of the University of Patras as the main contractor. The resource
was later made available to the CLARIN network as part of the collection of
Greek lexicographical and linguistic resources.

The converter was originally written in C++ and has been replaced by a Python
implementation. Identifiers, escaping, error handling, metadata, and
serialization were modernized. The result is not byte-for-byte compatible with
the historical N3.

## License and attribution

The project, source data, and generated RDF are available under the
[Creative Commons Attribution-ShareAlike 4.0 International
license](https://creativecommons.org/licenses/by-sa/4.0/).

Any use or redistribution should acknowledge:

- the Greek WordNet project and its contributors;
- the then General Secretariat for Research and Technology (GSRT), which
  funded the resource;
- the Database Laboratory of the University of Patras, the main contractor;
- the [CLARIN Greece network](https://www.clarin.gr/el), through which the
  resource was made available; and
- the relevant project publications listed below.

Related publications:

- <https://cgi.di.uoa.gr/~harryk/papers/RJIST.pdf>
- <https://www.researchgate.net/publication/221098292_Greek_WordNet_and_Its_Extension_with_Terms_of_the_Computer_Science_Domain>
- <https://link.springer.com/chapter/10.1007/3-540-45154-4_5>

When adapting the material, indicate that changes were made and distribute the
adaptation under the same or a compatible license, as required by CC BY-SA 4.0.

See `LICENSE` for the legal text and `CITATION.cff` for citation metadata.
