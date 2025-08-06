from pathlib import Path
from typing import Optional, Dict, Any
import json
from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery
from pyoxigraph import Store
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JSONLDLoader:
    def __init__(self, use_oxigraph: bool = False):
        self.use_oxigraph = use_oxigraph
        
        if use_oxigraph:
            self.store = Store()
            self.graph = None
        else:
            self.graph = Graph()
            self.store = None
        
        self.namespaces = {
            'schema': Namespace('http://schema.org/'),
            'ex': Namespace('http://example.org/kg/'),
            'prov': Namespace('http://www.w3.org/ns/prov/'),
            'skos': Namespace('http://www.w3.org/2004/02/skos/core#'),
        }
        
        if self.graph:
            for prefix, ns in self.namespaces.items():
                self.graph.bind(prefix, ns)
    
    def load_jsonld(self, file_path: str) -> None:
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Loading JSON-LD from {file_path}")
        
        if self.use_oxigraph:
            with open(file_path, 'rb') as f:
                self.store.load(f.read(), mime_type="application/ld+json")
            logger.info(f"Loaded into Oxigraph store. Triple count: {len(self.store)}")
        else:
            self.graph.parse(file_path, format="json-ld")
            logger.info(f"Loaded into RDFLib graph. Triple count: {len(self.graph)}")
    
    def query(self, sparql_query: str, limit: Optional[int] = None) -> list:
        if limit:
            if "LIMIT" not in sparql_query.upper():
                sparql_query += f" LIMIT {limit}"
        
        logger.info(f"Executing SPARQL query...")
        
        if self.use_oxigraph:
            results = []
            for row in self.store.query(sparql_query):
                results.append({str(var): str(val) for var, val in row.items()})
            return results
        else:
            qres = self.graph.query(sparql_query)
            results = []
            for row in qres:
                results.append({str(var): str(val) for var, val in row.asdict().items()})
            return results
    
    def get_stats(self) -> Dict[str, Any]:
        stats = {}
        
        if self.use_oxigraph:
            stats['total_triples'] = len(self.store)
            
            type_query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                SELECT ?type (COUNT(?s) as ?count)
                WHERE { ?s rdf:type ?type }
                GROUP BY ?type
                ORDER BY DESC(?count)
            """
            stats['types'] = self.query(type_query)
            
        else:
            stats['total_triples'] = len(self.graph)
            stats['subjects'] = len(set(self.graph.subjects()))
            stats['predicates'] = len(set(self.graph.predicates()))
            stats['objects'] = len(set(self.graph.objects()))
            
            type_query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                SELECT ?type (COUNT(?s) as ?count)
                WHERE { ?s rdf:type ?type }
                GROUP BY ?type
                ORDER BY DESC(?count)
            """
            stats['types'] = self.query(type_query)
        
        return stats