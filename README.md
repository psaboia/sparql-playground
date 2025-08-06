# JSON-LD SPARQL Query Tool

A Python tool for loading JSON-LD files and running SPARQL queries using RDFLib or Oxigraph.

## Installation

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

## Usage

### Load and inspect data
```bash
# Using RDFLib (default)
uv run python main.py load data_example/enriched_chunks_training_set_complete_gpt-4.1-mini_fixed_vocab_mapped.jsonld

# Using Oxigraph (faster for large datasets)
uv run python main.py load data_example/enriched_chunks_training_set_complete_gpt-4.1-mini_fixed_vocab_mapped.jsonld --engine oxigraph
```

### Run predefined queries
```bash
# List available queries
uv run python main.py list-queries

# Run a specific query
uv run python main.py query data_example/enriched_chunks_training_set_complete_gpt-4.1-mini_fixed_vocab_mapped.jsonld --query-name count_documents

# Run with Oxigraph
uv run python main.py query data_example/enriched_chunks_training_set_complete_gpt-4.1-mini_fixed_vocab_mapped.jsonld --query-name get_chunks_with_text --engine oxigraph
```

### Custom SPARQL queries
```bash
uv run python main.py query data_example/enriched_chunks_training_set_complete_gpt-4.1-mini_fixed_vocab_mapped.jsonld --query "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 5"
```

### Interactive mode
```bash
uv run python main.py interactive data_example/enriched_chunks_training_set_complete_gpt-4.1-mini_fixed_vocab_mapped.jsonld
```

## Example Queries

- `count_documents`: Count total documents
- `get_chunks_with_text`: Get text chunks with their content
- `find_chunks_by_keyword`: Search chunks by text content
- `document_hierarchy`: Show document-chunk-subchunk structure
- `chunks_with_high_relevance_questions`: Find competency questions with high relevance
- `information_needs_analysis`: Extract information needs from chunks
- `chunk_positions`: Get text positions and offsets
- `semantic_concepts`: Find semantic concepts linked to chunks

## Performance Tips

- Use **Oxigraph** (`--engine oxigraph`) for faster queries on large datasets
- RDFLib is better for development and debugging with more detailed error messages
- First run may be slow as it loads and indexes the data

## Extending

Add new queries in `src/queries.py`:

```python
EXAMPLE_QUERIES["my_query"] = """
    PREFIX schema: <http://schema.org/>
    SELECT ?s ?p ?o
    WHERE { ?s ?p ?o }
    LIMIT 10
"""
```