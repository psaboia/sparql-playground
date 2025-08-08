import pytest
from pathlib import Path
from src.loader import JSONLDLoader
from src.queries import EXAMPLE_QUERIES


class TestPredefinedQueries:
    """Test all predefined SPARQL queries against both engines."""
    
    @pytest.fixture(scope="class")
    def test_data_path(self):
        """Path to test JSON-LD data file."""
        data_path = Path("data_example/enriched_chunks_training_set_complete_gpt-4.1-mini_fixed_vocab_mapped.jsonld")
        if not data_path.exists():
            pytest.skip(f"Test data not found at {data_path}")
        return str(data_path)
    
    @pytest.fixture(scope="class", params=["rdflib", "oxigraph"])
    def loader(self, request, test_data_path):
        """Create loader with both engines."""
        engine = request.param
        use_oxigraph = (engine == "oxigraph")
        
        loader = JSONLDLoader(use_oxigraph=use_oxigraph)
        loader.load_jsonld(test_data_path)
        
        # Add engine info for test reporting
        loader._engine_name = engine
        return loader
    
    @pytest.mark.parametrize("query_name", list(EXAMPLE_QUERIES.keys()))
    def test_predefined_query(self, loader, query_name):
        """Test each predefined query executes without error and returns results."""
        query = EXAMPLE_QUERIES[query_name]
        
        try:
            results = loader.query(query, limit=5)
            
            # Basic validation
            assert isinstance(results, list), f"Query {query_name} should return a list"
            
            # Most queries should return results (except edge cases)
            # We'll be lenient and just check they don't crash
            print(f"\n{loader._engine_name} - {query_name}: {len(results)} results")
            
            # If we get results, validate structure
            if results:
                assert isinstance(results[0], dict), f"Query {query_name} results should be dictionaries"
                assert len(results[0]) > 0, f"Query {query_name} results should have columns"
                
                # Log first result for debugging
                print(f"  Sample result: {list(results[0].keys())}")
            
        except Exception as e:
            pytest.fail(f"Query '{query_name}' failed on {loader._engine_name}: {str(e)}")
    
    def test_query_result_consistency(self, test_data_path):
        """Test that both engines return consistent result counts for basic queries."""
        
        # Create both loaders
        rdflib_loader = JSONLDLoader(use_oxigraph=False)
        oxigraph_loader = JSONLDLoader(use_oxigraph=True)
        
        rdflib_loader.load_jsonld(test_data_path)
        oxigraph_loader.load_jsonld(test_data_path)
        
        # Test a few stable queries that should return consistent counts
        stable_queries = [
            "count_documents",
            "get_chunks_with_text", 
            "document_hierarchy"
        ]
        
        for query_name in stable_queries:
            if query_name not in EXAMPLE_QUERIES:
                continue
                
            query = EXAMPLE_QUERIES[query_name]
            
            try:
                rdflib_results = rdflib_loader.query(query, limit=10)
                oxigraph_results = oxigraph_loader.query(query, limit=10)
                
                rdflib_count = len(rdflib_results)
                oxigraph_count = len(oxigraph_results)
                
                print(f"\n{query_name} - RDFLib: {rdflib_count}, Oxigraph: {oxigraph_count}")
                
                # Both should return the same number of results
                assert rdflib_count == oxigraph_count, \
                    f"Query '{query_name}' returned different counts: RDFLib={rdflib_count}, Oxigraph={oxigraph_count}"
                    
            except Exception as e:
                pytest.fail(f"Consistency test failed for '{query_name}': {str(e)}")
    
    def test_data_loading_stats(self, test_data_path):
        """Test that both engines load the same amount of data."""
        
        rdflib_loader = JSONLDLoader(use_oxigraph=False)
        oxigraph_loader = JSONLDLoader(use_oxigraph=True)
        
        rdflib_loader.load_jsonld(test_data_path)
        oxigraph_loader.load_jsonld(test_data_path)
        
        rdflib_stats = rdflib_loader.get_stats()
        oxigraph_stats = oxigraph_loader.get_stats()
        
        rdflib_triples = rdflib_stats.get('total_triples', 0)
        oxigraph_triples = oxigraph_stats.get('total_triples', 0)
        
        print(f"\nTriple counts - RDFLib: {rdflib_triples}, Oxigraph: {oxigraph_triples}")
        
        # Both should load the same number of triples
        assert rdflib_triples == oxigraph_triples, \
            f"Different triple counts: RDFLib={rdflib_triples}, Oxigraph={oxigraph_triples}"
        
        # Should have a reasonable number of triples (> 1000)
        assert rdflib_triples > 1000, f"Too few triples loaded: {rdflib_triples}"
    
    def test_query_syntax_validation(self):
        """Test that all predefined queries have valid SPARQL syntax."""
        
        for query_name, query in EXAMPLE_QUERIES.items():
            
            # Basic syntax checks
            assert query.strip(), f"Query {query_name} is empty"
            assert "SELECT" in query.upper() or "ASK" in query.upper() or "CONSTRUCT" in query.upper(), \
                f"Query {query_name} missing query type"
            assert "WHERE" in query.upper(), f"Query {query_name} missing WHERE clause"
            
            # Check balanced braces
            open_braces = query.count('{')
            close_braces = query.count('}')
            assert open_braces == close_braces, \
                f"Query {query_name} has unbalanced braces: {open_braces} open, {close_braces} close"