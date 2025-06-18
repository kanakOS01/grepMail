import os

import mindsdb_sdk
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown

from grepmail.mindsdb.handlers.common import create_and_get_project
from grepmail.mindsdb.handlers.email import (
    create_and_get_email_engine,
    create_and_get_email_db,
    create_and_get_storage,
    create_and_get_email_kb,
    bulk_insert,
    query_email_kb
)

load_dotenv()

EMAIL_ID = os.getenv("EMAIL_ID")
EMAIL_PWD = os.getenv("EMAIL_PWD")


app = typer.Typer()
console = Console()


@app.command()
def run():
    """🚀 grepmail: Query your emails with AI-powered semantic search"""
    console.print(Panel.fit(
        "[bold cyan]📬 grepMail[/bold cyan]\n\n"
        "[green]Semantic search across your emails using MindsDB, vector embeddings, and local LLMs.[/green]",
        title="Welcome", border_style="cyan"
    ))

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
        email_engine = create_and_get_email_engine(server, EMAIL_ID, EMAIL_PWD)
        progress.update(task, completed=100)

        task = progress.add_task("📂 Creating email database...")
        email_db = create_and_get_email_db(server, EMAIL_ID)
        progress.update(task, completed=100)

        task = progress.add_task("💾 Setting up vector storage...")
        email_vs = create_and_get_storage(server, EMAIL_ID)
        progress.update(task, completed=100)

        task = progress.add_task("🧠 Creating email knowledge base...")
        email_kb = create_and_get_email_kb(project, EMAIL_ID)
        progress.update(task, completed=100)

        task = progress.add_task("📤 Bulk inserting emails (if empty)...")
        bulk_insert(project, email_kb, email_db, email_engine)
        progress.update(task, completed=100)

    console.print("\n[bold green]✅ Setup complete! You can now search your emails.[/bold green]")

    # Placeholder for query loop
    while True:
        query = Prompt.ask("\n🔍 Enter a semantic email query (or 'exit')")
        if query.strip().lower() == 'exit':
            console.print("👋 Goodbye!")
            break

        with console.status("🤖 Thinking...", spinner="dots"):
            results = query_email_kb(project, email_kb, email_engine, query, 20)

        if results:
            console.print("\n[bold blue]Search Results:[/bold blue]")
            console.print(results)

        else:
            console.print("[bold red]No results found.[/bold red]")


if __name__ == "__main__":
    app()
