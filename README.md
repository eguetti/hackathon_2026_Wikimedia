The goal of this example is to bridge the gap between non-technical users and Semantic Web technologies. By using an academic ontology, we demonstrate how users can ask questions in plain Portuguese and retrieve structured data from a Knowledge Graph without knowing SPARQL syntax.

**Key Features**

Schema Mapping: Maps NL entities to ontology classes (e.g., "Papers" → :Publication).

Relation Extraction: Identifies predicates like :authoredBy or :publishedIn.

Query Generation: Automatically constructs valid SELECT or ASK SPARQL queries.

**Ontology Structure**

The system is designed to work with a standard academic schema. 
Below is a simplified view of the classes and properties involved:


| **Class** | **Description**   |
| :--- | :--- |
| Person | Researchers, Professors, and Students. |
| Publication | Journal articles, Conference papers, and Books. |
| Organization | NeuroMAT |

**Example Translation**

Input (Natural Language):

"Quais são os artigos que  publicaram Antonio Galves e Aline Duarte?"

**Output (SPARQL):**

```sparql
SELECT DISTINCT ?Artigo ?ArtigoLabel WHERE {
  ?Artigo wdt:P50 ?item.
  VALUES ?item {
    wd:Q17489997
    wd:Q102930817
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
```
