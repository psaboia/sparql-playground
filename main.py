#!/usr/bin/env python3

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel
import json

from src.loader import JSONLDLoader
from src.queries import EXAMPLE_QUERIES

console = Console()


@click.group()
def cli():
    """JSON-LD to SPARQL Query Tool"""
    pass


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--engine', type=click.Choice(['rdflib', 'oxigraph']), default='rdflib', help='RDF engine to use')
def load(file_path, engine):
    """Load a JSON-LD file and show statistics"""
    
    console.print(f"\n[bold cyan]Loading JSON-LD file with {engine}...[/bold cyan]")
    
    loader = JSONLDLoader(use_oxigraph=(engine == 'oxigraph'))
    
    try:
        loader.load_jsonld(file_path)
        stats = loader.get_stats()
        
        console.print(Panel(f"[green]✓ Successfully loaded {file_path}[/green]"))
        
        table = Table(title="Dataset Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Total Triples", str(stats.get('total_triples', 'N/A')))
        
        if 'subjects' in stats:
            table.add_row("Unique Subjects", str(stats['subjects']))
            table.add_row("Unique Predicates", str(stats['predicates']))
            table.add_row("Unique Objects", str(stats['objects']))
        
        console.print(table)
        
        if stats.get('types'):
            type_table = Table(title="Entity Types")
            type_table.add_column("Type", style="cyan")
            type_table.add_column("Count", style="magenta")
            
            for type_info in stats['types'][:10]:
                type_table.add_row(
                    type_info.get('type', 'N/A').split('/')[-1].split('#')[-1],
                    type_info.get('count', 'N/A')
                )
            
            console.print(type_table)
            
    except Exception as e:
        console.print(f"[red]Error loading file: {e}[/red]")


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--query-name', type=click.Choice(list(EXAMPLE_QUERIES.keys())), help='Predefined query to run')
@click.option('--query', type=str, help='Custom SPARQL query')
@click.option('--engine', type=click.Choice(['rdflib', 'oxigraph']), default='rdflib', help='RDF engine to use')
@click.option('--limit', type=int, default=10, help='Limit results')
@click.option('--output', type=click.Choice(['table', 'json']), default='table', help='Output format')
def query(file_path, query_name, query, engine, limit, output):
    """Run SPARQL queries on JSON-LD data"""
    
    if not query_name and not query:
        console.print("[red]Please provide either --query-name or --query[/red]")
        console.print("\nAvailable queries:")
        for name in EXAMPLE_QUERIES:
            console.print(f"  - {name}")
        return
    
    loader = JSONLDLoader(use_oxigraph=(engine == 'oxigraph'))
    
    console.print(f"[cyan]Loading data with {engine}...[/cyan]")
    loader.load_jsonld(file_path)
    
    sparql_query = EXAMPLE_QUERIES.get(query_name) if query_name else query
    
    console.print("\n[bold]Query:[/bold]")
    console.print(Syntax(sparql_query, "sparql", theme="monokai"))
    
    try:
        results = loader.query(sparql_query, limit=limit)
        
        if output == 'json':
            console.print(json.dumps(results, indent=2))
        else:
            if results:
                table = Table(title=f"Query Results ({len(results)} rows)")
                
                for key in results[0].keys():
                    table.add_column(key, style="cyan")
                
                for row in results[:limit]:
                    values = []
                    for val in row.values():
                        val_str = str(val)
                        if len(val_str) > 50:
                            val_str = val_str[:47] + "..."
                        values.append(val_str)
                    table.add_row(*values)
                
                console.print(table)
            else:
                console.print("[yellow]No results found[/yellow]")
                
    except Exception as e:
        console.print(f"[red]Query error: {e}[/red]")


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--engine', type=click.Choice(['rdflib', 'oxigraph']), default='rdflib', help='RDF engine to use')
def interactive(file_path, engine):
    """Interactive SPARQL query mode"""
    
    loader = JSONLDLoader(use_oxigraph=(engine == 'oxigraph'))
    
    console.print(f"[cyan]Loading data with {engine}...[/cyan]")
    loader.load_jsonld(file_path)
    console.print("[green]Ready for queries! Type 'help' for examples, 'exit' to quit[/green]\n")
    
    while True:
        try:
            query_input = console.input("[bold]SPARQL>[/bold] ")
            
            if query_input.lower() == 'exit':
                break
            
            if query_input.lower() == 'help':
                console.print("\n[bold]Available example queries:[/bold]")
                for name, q in EXAMPLE_QUERIES.items():
                    console.print(f"\n[cyan]{name}:[/cyan]")
                    console.print(Syntax(q[:200] + "..." if len(q) > 200 else q, "sparql"))
                continue
            
            if query_input.strip():
                results = loader.query(query_input)
                
                if results:
                    table = Table()
                    for key in results[0].keys():
                        table.add_column(key)
                    
                    for row in results[:10]:
                        values = [str(v)[:50] + "..." if len(str(v)) > 50 else str(v) 
                                 for v in row.values()]
                        table.add_row(*values)
                    
                    console.print(table)
                    if len(results) > 10:
                        console.print(f"[dim]Showing first 10 of {len(results)} results[/dim]")
                else:
                    console.print("[yellow]No results[/yellow]")
                    
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    console.print("\n[cyan]Goodbye![/cyan]")


@cli.command()
def list_queries():
    """List all available example queries"""
    
    console.print("\n[bold cyan]Available Example Queries:[/bold cyan]\n")
    
    for name, query in EXAMPLE_QUERIES.items():
        console.print(Panel(
            Syntax(query, "sparql", theme="monokai"),
            title=f"[bold]{name}[/bold]",
            border_style="cyan"
        ))


if __name__ == '__main__':
    cli()