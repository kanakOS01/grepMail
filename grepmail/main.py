import mindsdb_sdk
import time
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from grepmail.mindsdb.handlers.common import create_and_get_project
from grepmail.mindsdb.handlers.email import (
    create_and_get_email_db,
    create_and_get_storage,
    create_and_get_email_kb,
    bulk_insert_email_kb,
)

app = typer.Typer()
console = Console()

EMAIL_ID = "user@gmail.com"     # Replace with dynamic input or config
EMAIL_PWD = "yourpassword"      # Don't hardcode this in production


@app.command()
def run():
    """🚀 grepmail: Query your emails with AI-powered semantic search"""
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True
    ) as progress:
        task = progress.add_task("🔌 Connecting to MindsDB...", start=False)
        server = mindsdb_sdk.connect("http://127.0.0.1:47334")
        progress.update(task, completed=100)

        task = progress.add_task("📁 Getting MindsDB project...")
        project = create_and_get_project(server, "grepmail")
        progress.update(task, completed=100)

        task = progress.add_task("📧 Setting up email database...")
        email_db = create_and_get_email_db(server, EMAIL_ID, EMAIL_PWD)
        progress.update(task, completed=100)

        task = progress.add_task("💾 Setting up vector storage...")
        email_vs = create_and_get_storage(server, EMAIL_ID)
        progress.update(task, completed=100)

        task = progress.add_task("🧠 Creating email knowledge base...")
        email_kb = create_and_get_email_kb(project, EMAIL_ID)
        progress.update(task, completed=100)

        task = progress.add_task("📤 Bulk inserting emails (if empty)...")
        bulk_insert_email_kb(project, email_kb, email_db)
        progress.update(task, completed=100)

    console.print("\n[bold green]✅ Setup complete! You can now search your emails.[/bold green]")

    # Placeholder for query loop
    while True:
        query = typer.prompt("🔍 Enter a semantic email query (or 'exit')")
        if query.lower() in ["exit", "quit"]:
            break
        # Call a MindsDB query function here — we'll plug it in later
        console.print(f"[cyan]→ You asked:[/cyan] {query}")
        console.print("[yellow]🔎 Searching...[/yellow]")
        # Placeholder result
        console.print("[green]Top result:[/green] (placeholder)\n")


if __name__ == "__main__":
    app()
