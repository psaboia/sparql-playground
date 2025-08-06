EXAMPLE_QUERIES = {
    "count_documents": """
        PREFIX schema: <http://schema.org/>
        PREFIX prov: <http://www.w3.org/ns/prov/>
        
        SELECT (COUNT(DISTINCT ?doc) as ?count)
        WHERE {
            ?doc a prov:Entity .
        }
    """,
    
    "get_chunks_with_text": """
        PREFIX schema: <http://schema.org/>
        PREFIX ex: <http://example.org/kg/>
        
        SELECT ?chunk ?text ?heading
        WHERE {
            ?chunk a ex:content_chunk .
            ?chunk schema:text ?text .
            OPTIONAL { ?chunk ex:heading ?heading }
        }
        LIMIT 10
    """,
    
    "find_chunks_by_keyword": """
        PREFIX schema: <http://schema.org/>
        PREFIX ex: <http://example.org/kg/>
        
        SELECT ?chunk ?text ?description
        WHERE {
            ?chunk schema:text ?text .
            OPTIONAL { ?chunk schema:description ?description }
            FILTER(CONTAINS(LCASE(?text), "newport"))
        }
    """,
    
    "document_hierarchy": """
        PREFIX schema: <http://schema.org/>
        PREFIX prov: <http://www.w3.org/ns/prov/>
        
        SELECT ?doc ?docName ?chunk ?chunkPosition ?subchunk
        WHERE {
            ?doc a prov:Entity .
            ?doc schema:name ?docName .
            ?doc schema:hasPart ?chunk .
            ?chunk schema:position ?chunkPosition .
            OPTIONAL { ?chunk schema:hasPart ?subchunk }
        }
        ORDER BY ?doc ?chunkPosition
        LIMIT 20
    """,
    
    "chunks_with_high_relevance_questions": """
        PREFIX schema: <http://schema.org/>
        PREFIX ex: <http://example.org/kg/>
        
        SELECT ?chunk ?text ?question ?relevance ?explanation
        WHERE {
            ?chunk schema:text ?text .
            ?chunk ex:contentAnalysis ?analysis .
            ?analysis ex:competencyQuestions ?cq .
            ?cq schema:question ?question .
            ?cq ex:relevance ?relevance .
            ?cq schema:explanation ?explanation .
            FILTER(?relevance >= 0.8)
        }
        ORDER BY DESC(?relevance)
        LIMIT 10
    """,
    
    "information_needs_analysis": """
        PREFIX ex: <http://example.org/kg/>
        PREFIX schema: <http://schema.org/>
        
        SELECT ?chunk ?text ?need
        WHERE {
            ?chunk schema:text ?text .
            ?chunk ex:contentAnalysis ?analysis .
            ?analysis ex:informationNeeds ?need .
        }
        LIMIT 20
    """,
    
    "chunk_positions": """
        PREFIX schema: <http://schema.org/>
        
        SELECT ?chunk ?text ?startOffset ?endOffset ?pageNumber
        WHERE {
            ?chunk schema:text ?text .
            ?chunk schema:textPosition ?pos .
            ?pos schema:startOffset ?startOffset .
            ?pos schema:endOffset ?endOffset .
            OPTIONAL { ?pos schema:pageNumber ?pageNumber }
        }
        LIMIT 10
    """,
    
    "semantic_concepts": """
        PREFIX ex: <http://example.org/kg/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        
        SELECT ?chunk ?concept ?label
        WHERE {
            ?chunk ex:semantic_concepts ?concept .
            OPTIONAL { ?concept skos:prefLabel ?label }
        }
        LIMIT 20
    """,
}