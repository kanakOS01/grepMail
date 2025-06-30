import os

import mindsdb_sdk
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table

from grepmail.mindsdb.handlers.common import (
    create_and_get_project,
    create_gemini_engine,
    create_and_get_gist_model,
    query_gist_model
)
from grepmail.mindsdb.handlers.email import (
    create_and_get_email_engine,
    create_and_get_email_db,
    create_and_get_storage,
    create_and_get_email_kb,
    bulk_insert,
    query_email_db,
    query_email_kb,
    create_kb_index,
    create_jobs,
)
from grepmail.logger import logger


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

        task = progress.add_task("Creating knowledge base index...")
        create_kb_index(project, email_kb)
        progress.update(task, completed=100)

        task = progress.add_task("Creating jobs for email processing...")
        create_jobs(project, email_kb, email_db, email_engine)
        progress.update(task, completed=100)

        task = progress.add_task("Setting up Gemini model...")
        create_gemini_engine(server)
        gist_model = create_and_get_gist_model(project)
        progress.update(task, completed=100)

    console.print("\n[bold green]✅ Setup complete! You can now search your emails.[/bold green]")
    console.print(
        "[bold yellow]Tip:[/bold yellow] Use [bold blue]/help[/bold blue] to see available commands.\n"
    )

    while True:
        query = Prompt.ask("\n🔍 Enter a command or semantic query ([blue]/help[/blue] for options)")
        cmd = query.strip().lower()

        if cmd in ["/exit", "/bye"]:
            console.print("👋 Goodbye!")
            break

        elif cmd.startswith("/ls"):
            try:
                count = int(cmd.split(" ")[1]) if len(cmd.split(" ")) > 1 else 5
            except ValueError:
                count = 5

            with console.status("📬 Fetching latest emails...", spinner="dots"):
                query_str = f"SELECT id, subject, from_field, datetime FROM {email_db.name}.emails ORDER BY datetime DESC LIMIT {count};"
                res = query_email_db(email_db, query_str)

            if res:
                table = Table(title=f"🕐 Last {count} Emails", show_lines=True)
                table.add_column("ID", style="cyan")
                table.add_column("Subject", style="cyan")
                table.add_column("From", style="yellow")
                table.add_column("Date", style="white")

                for row in res:
                    id = row.get("id")
                    subject = row.get("subject", "No Subject")
                    from_ = row.get("from_field", "Unknown").split(" ")[-1].strip("<>")
                    date = row.get("datetime")
                    if date:
                        date = date.split(" ")[0]
                    else:
                        date = "Unknown Date"
                    table.add_row(str(id), subject, from_, date)

                console.print(table)
            else:
                console.print("[bold red]No recent emails found.[/bold red]")

        elif cmd.startswith("/clear"):
            console.clear()
            console.print(
                Panel.fit(
                    "[bold yellow]/help[/bold yellow] - Show this help\n"
                    "[bold yellow]/bye[/bold yellow] or [bold yellow]/exit[/bold yellow] - Exit the program\n"
                    "[bold yellow]/clear[/bold yellow] - Clear the console\n"
                    "[bold yellow]/ls [n][/bold yellow] - List last n emails (default 5)\n"
                    "[bold yellow]/grep <pattern>[/bold yellow] - Regex search on email subjects\n"
                    "[bold yellow]/fzf <query>[/bold yellow] - Semantic search using vector embeddings\n"
                    "[bold yellow]/on <yyyy-mm-dd> <query>[/bold yellow] - Semantic search for emails on a specific date\n"
                    "[bold yellow]/fetch <id>[/bold yellow] - Fetch entire email by id\n"
                    "[bold yellow]/gist <id>[/bold yellow] - Generate a gist for the email with the given id\n"
                    "\nOr just type your natural language query to search emails!",
                    title="📘 Commands",
                    border_style="blue"
                )
            )
            

        elif cmd.startswith("/grep"):
            import re
            pattern = query.replace("/grep", "").strip()
            if not pattern:
                console.print("[red]Usage: /grep <regex_pattern>[/red]")
                continue

            with console.status("🧵 Grepping subjects...", spinner="dots"):
                res = query_email_db(email_db, f"SELECT id, subject, from_field, datetime FROM {email_db.name}.emails;")

            matches = [row for row in res if re.search(pattern, row.get("subject", ""), re.IGNORECASE)]

            if matches:
                table = Table(title=f"🔎 Subjects matching /{pattern}/", show_lines=True)
                table.add_column("ID", style="cyan")
                table.add_column("Subject", style="cyan")
                table.add_column("From", style="yellow")
                table.add_column("Date", style="white")

                for row in matches:
                    id = row.get("id")
                    subject = row.get("subject", "No Subject")
                    from_ = row.get("from_field", "Unknown").split(" ")[-1].strip("<>")
                    date = row.get("datetime")
                    if date:
                        date = date.split(" ")[0]
                    else:
                        date = "Unknown Date"
                    table.add_row(str(id), subject, from_, date)

                console.print(table)
            else:
                console.print("[red]No matches found.[/red]")

        elif cmd.startswith("/fzf"):
            query_term = query.replace("/fzf", "").strip()
            if not query_term:
                console.print("[red]Usage: /fzf <semantic query>[/red]")
                continue

            with console.status("🤖 Performing semantic search...", spinner="dots"):
                results = query_email_kb(project, email_kb, email_db, query_term, 10)

            if results:
                table = Table(title=f"🧠 Semantic Results for: {query_term}", show_lines=True)
                table.add_column("ID", style="cyan")
                table.add_column("Subject", style="bold cyan")
                table.add_column("From", style="yellow")
                table.add_column("Date", style="white")
                table.add_column("Snippet", style="dim", overflow="fold")

                for email in results:
                    id = email.get("id")
                    subject = email.get("subject", "No Subject")[:100] + "..."
                    from_ = email.get("from_field", "Unknown").split(" ")[-1].strip("<>")
                    date = email.get("datetime")
                    if date:
                        date = date.split(" ")[0]
                    else:
                        date = "Unknown Date"
                    snippet = email.get("body", "").strip().replace("\n", " ")[:100] + "..."
                    table.add_row(str(id), subject, from_, date, snippet)

                console.print(table)
            else:
                console.print("[red]No semantic results found.[/red]")

        elif cmd.startswith("/on "):
            parts = cmd.split(" ", 2)
            if len(parts) < 3:
                console.print("[red]Usage: /on <yyyy-mm-dd> <query>[/red]")
                continue

            date_filter, user_query = parts[1], parts[2]

            if not re.match(r"\d{4}-\d{2}-\d{2}", date_filter):
                console.print("[red]Date must be in YYYY-MM-DD format.[/red]")
                continue

            with console.status(f"🔍 Searching for emails on [bold]{date_filter}[/bold]...", spinner="dots"):
                results = query_email_kb(project, email_kb, email_db, user_query, 10, date_filter)

            if results:
                table = Table(title=f"🧠 Results for '{user_query}' on {date_filter}", show_lines=True)
                table.add_column("ID", style="cyan")
                table.add_column("Subject", style="cyan")
                table.add_column("From", style="yellow")
                table.add_column("Date", style="white")
                table.add_column("Snippet", style="dim")

                for email in results:
                    id = email.get("id")
                    subject = email.get("subject", "No Subject")[:100] + "..."
                    from_ = email.get("from_field", "Unknown").split(" ")[-1].strip("<>")
                    date = email.get("datetime")
                    if date:
                        date = date.split(" ")[0]
                    else:
                        date = "Unknown Date"
                    snippet = email.get("body", "").strip().replace("\n", " ")[:100] + "..."
                    table.add_row(str(id), subject, from_, date, snippet)

                console.print(table)
            else:
                console.print("[red]No results for that date/query.[/red]")

        elif cmd.startswith("/fetch "):
            parts = cmd.split(" ", 1)
            if len(parts) < 2 or not parts[1].isdigit():
                console.print("[red]Usage: /fetch <id>[/red]")
                continue

            email_id = parts[1]

            with console.status(f"📥 Fetching email with ID {email_id}...", spinner="dots"):
                try:
                    query = f"SELECT * FROM {email_db.name}.emails WHERE id = {email_id};"
                    email = query_email_db(email_db, query)[0]
                    if email:
                        console.print(Panel.fit(
                            f"[bold cyan]Subject:[/bold cyan] {email.get('subject', 'No Subject')}\n"
                            f"[bold yellow]From:[/bold yellow] {email.get('from_field', 'Unknown')}\n"
                            f"[bold white]Date:[/bold white] {email.get('datetime', 'Unknown Date')}\n\n"
                            f"[dim]{email.get('body', 'No content available').strip()}[/dim]",
                            title=f"📧 Email ID: {email_id}",
                            border_style="blue"
                        ))
                    else:
                        console.print("[red]No email found with that ID.[/red]")
                except Exception as e:
                    console.print(f"[red]Error fetching email: {str(e)}[/red]")

        elif cmd.startswith("/gist "):
            parts = cmd.split(" ", 1)
            if len(parts) < 2 or not parts[1].isdigit():
                console.print("[red]Usage: /gist <id>[/red]")
                continue

            email_id = parts[1]

            with console.status(f"📝 Generating gist for email ID {email_id}...", spinner="dots"):
                try:
                    query = f"SELECT * FROM {email_db.name}.emails WHERE id = {email_id};"
                    email = query_email_db(email_db, query)[0]
                    if email:
                        gist_content = f"Subject: {email.get('subject', 'No Subject')}\n"
                        gist_content += f"From: {email.get('from_field', 'Unknown')}\n"
                        gist_content += email.get('body', 'No content available').strip()

                        res = query_gist_model(project, gist_content)

                        console.print(Panel.fit(
                            res,
                            title=f"Gist for Email ID: {email_id}",
                            border_style="blue"
                        ))
                    else:
                        console.print("[red]No email found with that ID.[/red]")
                except Exception as e:
                    console.print(f"[red]Error generating gist: {str(e)}[/red]")

        elif cmd in ["/help", "help"]:
            console.print(
                Panel.fit(
                    "[bold yellow]/help[/bold yellow] - Show this help\n"
                    "[bold yellow]/bye[/bold yellow] or [bold yellow]/exit[/bold yellow] - Exit the program\n"
                    "[bold yellow]/clear[/bold yellow] - Clear the console\n"
                    "[bold yellow]/ls [n][/bold yellow] - List last n emails (default 5)\n"
                    "[bold yellow]/grep <pattern>[/bold yellow] - Regex search on email subjects\n"
                    "[bold yellow]/fzf <query>[/bold yellow] - Semantic search using vector embeddings\n"
                    "[bold yellow]/on <yyyy-mm-dd> <query>[/bold yellow] - Semantic search for emails on a specific date\n"
                    "[bold yellow]/fetch <id>[/bold yellow] - Fetch entire email by id\n"
                    "[bold yellow]/gist <id>[/bold yellow] - Generate a gist for the email with the given id\n"
                    "\nOr just type your natural language query to search emails!",
                    title="📘 Commands",
                    border_style="blue"
                )
            )

        else:
            with console.status("🤖 Thinking...", spinner="dots"):
                results = query_email_kb(project, email_kb, email_db, query, 10)

            if results:
                console.print(f"\n[bold blue]📨 Found {len(results)} matching emails:[/bold blue]\n")

                table = Table(title="📧 Email Results", show_lines=True, title_style="bold green")
                table.add_column("ID", style="cyan")
                table.add_column("Subject", style="bold cyan")
                table.add_column("From", style="yellow")
                table.add_column("Date", style="white")
                table.add_column("Snippet", style="dim", overflow="fold")

                for email in results:
                    id = email.get("id")
                    subject = email.get("subject", "No Subject")[:100] + "..."
                    from_ = email.get("from_field", "Unknown").split(" ")[-1].strip("<>")
                    date = email.get("datetime")
                    if date:
                        date = date.split(" ")[0]
                    else:
                        date = "Unknown Date"
                    content_snippet = email.get("body", "").strip().replace("\n", " ")[:100] + "..."

                    table.add_row(str(id), subject, from_, str(date), content_snippet)

                console.print(table)
            else:
                console.print("[bold red]No results found.[/bold red]")


if __name__ == "__main__":
    app()
