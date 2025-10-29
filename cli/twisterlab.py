"""
TwisterLab CLI - Command-line interface for managing TwisterLab agents.

Built with Typer for CLI and Rich for beautiful terminal output.
"""

import sys
import json
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import print as rprint

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base import HelpdeskAgent, ClassifierAgent, DesktopCommanderAgent

app = typer.Typer(
    name="twisterlab",
    help="TwisterLab CLI - Manage AI agents for IT Helpdesk automation",
    add_completion=False
)
console = Console()

# Agent registry
AGENTS = {
    "helpdesk-resolver": HelpdeskAgent,
    "classifier": ClassifierAgent,
    "desktop-commander": DesktopCommanderAgent,
}

SUPPORTED_FORMATS = ["microsoft", "langchain", "semantic-kernel", "openai"]


@app.command()
def version():
    """Show TwisterLab version."""
    console.print(Panel.fit(
        "[bold cyan]TwisterLab[/bold cyan] [green]v1.0.0[/green]\n"
        "AI-Powered IT Helpdesk Automation Platform",
        title="Version",
        border_style="cyan"
    ))


@app.command("list-agents")
def list_agents():
    """List all available TwisterLab agents."""
    table = Table(title="📋 Available TwisterLab Agents", show_header=True, header_style="bold magenta")

    table.add_column("Agent Name", style="cyan", no_wrap=True)
    table.add_column("Display Name", style="green")
    table.add_column("Role", style="yellow")
    table.add_column("Tools", justify="right", style="blue")

    for agent_name, agent_class in AGENTS.items():
        agent = agent_class()
        table.add_row(
            agent_name,
            agent.display_name,
            agent.role,
            str(len(agent.tools))
        )

    console.print(table)
    console.print(f"\n[dim]Total agents: {len(AGENTS)}[/dim]")


@app.command("export-agent")
def export_agent(
    agent_name: str = typer.Argument(
        ...,
        help="Agent name (e.g., helpdesk-resolver, classifier, desktop-commander)"
    ),
    format: str = typer.Option(
        "microsoft",
        "--format",
        "-f",
        help="Export format: microsoft | langchain | semantic-kernel | openai"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (default: print to stdout)"
    ),
    pretty: bool = typer.Option(
        True,
        "--pretty/--no-pretty",
        help="Pretty-print JSON output"
    )
):
    """
    Export agent schema in standard format for interoperability.

    Examples:

        Export to stdout:
        $ twisterlab export-agent helpdesk-resolver

        Export to file:
        $ twisterlab export-agent classifier --format microsoft --output classifier.json

        Export to LangChain format:
        $ twisterlab export-agent desktop-commander --format langchain
    """
    # Validate format
    format = format.lower()
    if format not in SUPPORTED_FORMATS:
        console.print(f"[red]Error:[/red] Unknown format '{format}'", style="bold")
        console.print(f"[yellow]Supported formats:[/yellow] {', '.join(SUPPORTED_FORMATS)}")
        raise typer.Exit(1)

    # Validate agent name
    if agent_name not in AGENTS:
        console.print(f"[red]Error:[/red] Unknown agent '{agent_name}'", style="bold")
        console.print(f"[yellow]Available agents:[/yellow] {', '.join(AGENTS.keys())}")
        raise typer.Exit(1)

    try:
        # Load agent
        with console.status(f"[bold green]Loading agent '{agent_name}'..."):
            agent_class = AGENTS[agent_name]
            agent = agent_class()

        # Export schema
        with console.status(f"[bold green]Exporting to {format} format..."):
            schema = agent.to_schema(format)

        # Format JSON
        indent = 2 if pretty else None
        json_output = json.dumps(schema, indent=indent, ensure_ascii=False)

        # Output
        if output:
            # Write to file
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json_output, encoding='utf-8')
            console.print(f"[green]✓[/green] Exported to [cyan]{output}[/cyan]")

            # Show summary
            console.print(f"\n[bold]Agent:[/bold] {agent.display_name}")
            console.print(f"[bold]Format:[/bold] {format}")
            console.print(f"[bold]Tools:[/bold] {len(agent.tools)}")

        else:
            # Print to stdout with syntax highlighting
            console.print(f"\n[bold cyan]Agent:[/bold cyan] {agent.display_name}")
            console.print(f"[bold cyan]Format:[/bold cyan] {format}\n")

            syntax = Syntax(json_output, "json", theme="monokai", line_numbers=False)
            console.print(syntax)

        # Show warnings for stub formats
        if format in ["langchain", "semantic-kernel", "openai"]:
            console.print(
                f"\n[yellow]⚠ Note:[/yellow] {format} support is a stub. "
                f"Full compatibility planned for v2.0"
            )

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="bold")
        raise typer.Exit(1)


@app.command("show-agent")
def show_agent(
    agent_name: str = typer.Argument(
        ...,
        help="Agent name to display details"
    )
):
    """Show detailed information about an agent."""
    if agent_name not in AGENTS:
        console.print(f"[red]Error:[/red] Unknown agent '{agent_name}'", style="bold")
        console.print(f"[yellow]Available agents:[/yellow] {', '.join(AGENTS.keys())}")
        raise typer.Exit(1)

    try:
        agent_class = AGENTS[agent_name]
        agent = agent_class()

        # Agent info panel
        info_text = f"""[bold cyan]Name:[/bold cyan] {agent.display_name}
[bold cyan]ID:[/bold cyan] {agent.name}
[bold cyan]Role:[/bold cyan] {agent.role}
[bold cyan]Model:[/bold cyan] {agent.model}
[bold cyan]Temperature:[/bold cyan] {agent.temperature}

[bold yellow]Description:[/bold yellow]
{agent.description}

[bold yellow]Instructions:[/bold yellow]
{agent.instructions[:200]}..."""

        console.print(Panel(
            info_text,
            title=f"🤖 {agent.display_name}",
            border_style="cyan",
            expand=False
        ))

        # Tools table
        if agent.tools:
            table = Table(title="🔧 Available Tools", show_header=True, header_style="bold magenta")
            table.add_column("Tool Name", style="cyan", no_wrap=True)
            table.add_column("Description", style="white")

            for tool in agent.tools:
                func = tool.get("function", {})
                table.add_row(
                    func.get("name", "unknown"),
                    func.get("description", "No description")[:60] + "..."
                )

            console.print("\n")
            console.print(table)

        # Metadata
        if agent.metadata:
            console.print("\n[bold yellow]Metadata:[/bold yellow]")
            for key, value in agent.metadata.items():
                console.print(f"  [cyan]{key}:[/cyan] {value}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="bold")
        raise typer.Exit(1)


@app.command("validate-schema")
def validate_schema(
    schema_file: Path = typer.Argument(
        ...,
        help="Path to schema JSON file to validate"
    ),
    format: str = typer.Option(
        "microsoft",
        "--format",
        "-f",
        help="Schema format to validate against"
    )
):
    """Validate an exported agent schema file."""
    if not schema_file.exists():
        console.print(f"[red]Error:[/red] File not found: {schema_file}", style="bold")
        raise typer.Exit(1)

    try:
        # Load schema
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = json.load(f)

        # Basic validation
        required_fields = {
            "microsoft": ["id", "object", "name", "model", "instructions", "tools"],
            "openai": ["id", "object", "name", "model", "instructions", "tools"],
            "langchain": ["name", "description", "llm", "tools"],
            "semantic-kernel": ["name", "description", "functions", "settings"]
        }

        format = format.lower()
        if format not in required_fields:
            console.print(f"[red]Error:[/red] Unknown format '{format}'", style="bold")
            raise typer.Exit(1)

        missing = []
        for field in required_fields[format]:
            if field not in schema:
                missing.append(field)

        if missing:
            console.print(f"[red]✗ Validation failed[/red]")
            console.print(f"[yellow]Missing fields:[/yellow] {', '.join(missing)}")
            raise typer.Exit(1)

        console.print(f"[green]✓ Schema is valid[/green] ({format} format)")
        console.print(f"\n[bold]Agent:[/bold] {schema.get('name', 'N/A')}")
        console.print(f"[bold]Tools:[/bold] {len(schema.get('tools', []))}")

    except json.JSONDecodeError as e:
        console.print(f"[red]Error:[/red] Invalid JSON: {str(e)}", style="bold")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="bold")
        raise typer.Exit(1)


@app.command()
def formats():
    """List supported export formats and their status."""
    table = Table(title="📋 Supported Export Formats", show_header=True, header_style="bold magenta")

    table.add_column("Format", style="cyan", no_wrap=True)
    table.add_column("Status", style="white")
    table.add_column("Documentation", style="blue")

    formats_data = [
        ("microsoft", "✅ Production", "https://learn.microsoft.com/azure/ai-services/agents/"),
        ("langchain", "⚠️ Stub (v2.0)", "https://python.langchain.com/docs/modules/agents/"),
        ("semantic-kernel", "⚠️ Stub (v2.0)", "https://learn.microsoft.com/semantic-kernel/"),
        ("openai", "⚠️ Stub (v2.0)", "https://platform.openai.com/docs/assistants/"),
    ]

    for fmt, status, docs in formats_data:
        table.add_row(fmt, status, docs)

    console.print(table)
    console.print("\n[dim]✅ = Production ready | ⚠️ = Planned for future release[/dim]")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
