# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a JSON-LD to SPARQL query tool that supports dual RDF engines (RDFLib and Oxigraph) for loading JSON-LD knowledge graphs and executing SPARQL queries. The project is built with Python using uv for dependency management.

## Core Architecture

### Three-Layer Architecture:
1. **CLI Layer** (`main.py`): Click-based CLI with rich formatting for user interaction
2. **Data Layer** (`src/loader.py`): `JSONLDLoader` class that abstracts RDFLib vs Oxigraph engines 
3. **Query Layer** (`src/queries.py`): Predefined SPARQL queries as a dictionary

### Dual Engine Support:
- **RDFLib**: Default engine, better for development (readable column names, detailed errors)
- **Oxigraph**: Alternative engine, faster for large datasets (results as `var_0`, `var_1`, etc.)

The `JSONLDLoader` class uses a boolean flag (`use_oxigraph`) to switch between engines, providing the same interface for both.

## Essential Commands

### Setup and Testing:
```bash
# Install dependencies
uv sync

# Run all tests (tests all queries against both engines)
uv run pytest

# Run specific tests
uv run pytest -k "rdflib"     # Test only RDFLib engine
uv run pytest -k "oxigraph"   # Test only Oxigraph engine
uv run pytest -k "consistency"  # Test engine result consistency
uv run pytest -v             # Verbose output with result counts
```

### CLI Usage:
```bash
# Load data and show statistics
uv run python main.py load data_example/file.jsonld [--engine oxigraph]

# List all predefined queries 
uv run python main.py list-queries

# Execute predefined query
uv run python main.py query data.jsonld --query-name count_documents [--engine oxigraph]

# Execute custom SPARQL
uv run python main.py query data.jsonld --query "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 5"

# Interactive SPARQL mode (multi-line query support)
uv run python main.py interactive data.jsonld [--engine oxigraph]
```

## Data Structure Understanding

The tool is designed for document understanding JSON-LD with this semantic model:
- **Documents** (`prov:Entity`) contain **chunks** (`ex:content_chunk`)
- **Chunks** have text content, positions, semantic concepts via `skos:member`
- **Concepts** have labels (`skos:prefLabel`), definitions (`skos:definition`), and confidence scores
- **Content analysis** includes competency questions, information needs, and relevance scores

## Key Implementation Details

### Engine Differences:
- **RDFLib**: Uses `Graph.parse()`, returns `row.asdict()`, supports namespace binding
- **Oxigraph**: Uses `Store.load()`, returns enumerated row items, stricter SPARQL syntax

### SPARQL Query Requirements:
- **Oxigraph requires ALL prefixes** to be explicitly declared (e.g., must include `PREFIX prov:` even if only used in OPTIONAL clauses)
- **RDFLib is more forgiving** with undefined prefixes

### Interactive Mode Implementation:
- Uses query buffering with balanced brace `{}` detection
- Multi-line input support with `...>` continuation prompt
- Auto-execution when SPARQL syntax appears complete

## Testing Strategy

The test suite (`tests/test_queries.py`) provides:
- **Parametrized tests** for all predefined queries × both engines (16 tests)
- **Consistency validation** comparing result counts between engines  
- **Data loading verification** ensuring both engines load same triple count
- **SPARQL syntax validation** checking query structure and balanced braces

Tests expect the data file at `data_example/enriched_chunks_training_set_complete_gpt-4.1-mini_fixed_vocab_mapped.jsonld`.

## Adding New Queries

Add to `EXAMPLE_QUERIES` dictionary in `src/queries.py`:

```python
EXAMPLE_QUERIES["my_query"] = """
    PREFIX schema: <http://schema.org/>
    PREFIX prov: <http://www.w3.org/ns/prov/>
    
    SELECT ?subject ?predicate ?object
    WHERE { ?subject ?predicate ?object }
    LIMIT 10
"""
```

**Important**: Include ALL prefixes used in the query for Oxigraph compatibility, even in OPTIONAL clauses.

## Performance Considerations

- **First run**: Slow due to data loading and indexing (~2 minutes for 13MB JSON-LD)
- **Oxigraph**: Faster queries on large datasets, but less readable output
- **RDFLib**: Better for development and debugging
- **Data size**: Current example handles ~177K triples efficiently