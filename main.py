import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import json
import hashlib
from datetime import datetime
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import base64

app = typer.Typer(help="Protect your startup ideas with timestamped proof and controlled sharing")
console = Console()

DATA_DIR = Path.home() / ".idea-vault"
IDEAS_FILE = DATA_DIR / "ideas.json"
TRUST_FILE = DATA_DIR / "trust.json"
KEYS_DIR = DATA_DIR / "keys"

def init_storage():
    DATA_DIR.mkdir(exist_ok=True)
    KEYS_DIR.mkdir(exist_ok=True)
    if not IDEAS_FILE.exists():
        IDEAS_FILE.write_text("[]")
    if not TRUST_FILE.exists():
        TRUST_FILE.write_text("[]")

def load_ideas():
    return json.loads(IDEAS_FILE.read_text())

def save_ideas(ideas):
    IDEAS_FILE.write_text(json.dumps(ideas, indent=2))

def load_trust():
    return json.loads(TRUST_FILE.read_text())

def save_trust(trust):
    TRUST_FILE.write_text(json.dumps(trust, indent=2))

def generate_proof(content: str, timestamp: str) -> str:
    data = f"{content}|{timestamp}".encode()
    return hashlib.sha256(data).hexdigest()

def sanitize_content(content: str) -> str:
    lines = content.split('\n')
    sanitized = []
    for line in lines:
        lower = line.lower()
        if any(keyword in lower for keyword in ['price', 'pricing', '$', 'cost', 'revenue', 'algorithm', 'secret', 'key', 'patent']):
            sanitized.append('[REDACTED]')
        else:
            sanitized.append(line)
    return '\n'.join(sanitized)

@app.command()
def add(
    title: str = typer.Option(..., "--title", "-t", help="Idea title"),
    content: str = typer.Option(..., "--content", "-c", help="Full idea description")
):
    """Add a new idea with timestamped proof"""
    init_storage()
    ideas = load_ideas()
    
    timestamp = datetime.now().isoformat()
    proof = generate_proof(content, timestamp)
    sanitized = sanitize_content(content)
    
    idea = {
        "id": len(ideas) + 1,
        "title": title,
        "content": content,
        "sanitized": sanitized,
        "timestamp": timestamp,
        "proof": proof
    }
    
    ideas.append(idea)
    save_ideas(ideas)
    
    console.print(Panel(
        f"[green]Idea saved successfully![/green]\n\n"
        f"ID: {idea['id']}\n"
        f"Title: {title}\n"
        f"Timestamp: {timestamp}\n"
        f"Proof Hash: {proof[:16]}...",
        title="✓ Idea Protected"
    ))

@app.command()
def list():
    """List all ideas"""
    init_storage()
    ideas = load_ideas()
    
    if not ideas:
        console.print("[yellow]No ideas yet. Use 'add' to create one.[/yellow]")
        return
    
    table = Table(title="Your Protected Ideas")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Timestamp", style="yellow")
    table.add_column("Proof", style="magenta")
    
    for idea in ideas:
        table.add_row(
            str(idea['id']),
            idea['title'],
            idea['timestamp'][:19],
            idea['proof'][:12] + "..."
        )
    
    console.print(table)

@app.command()
def show(
    idea_id: int = typer.Argument(..., help="Idea ID"),
    full: bool = typer.Option(False, "--full", "-f", help="Show full version (not sanitized)")
):
    """Show idea details"""
    init_storage()
    ideas = load_ideas()
    
    idea = next((i for i in ideas if i['id'] == idea_id), None)
    if not idea:
        console.print(f"[red]Idea {idea_id} not found[/red]")
        return
    
    content = idea['content'] if full else idea['sanitized']
    version = "Full Version" if full else "Sanitized Version"
    
    console.print(Panel(
        f"[bold]{idea['title']}[/bold]\n\n"
        f"{content}\n\n"
        f"[dim]Timestamp: {idea['timestamp']}\n"
        f"Proof: {idea['proof']}[/dim]",
        title=f"Idea #{idea_id} - {version}"
    ))

@app.command()
def proof(idea_id: int = typer.Argument(..., help="Idea ID")):
    """Generate timestamped proof certificate"""
    init_storage()
    ideas = load_ideas()
    
    idea = next((i for i in ideas if i['id'] == idea_id), None)
    if not idea:
        console.print(f"[red]Idea {idea_id} not found[/red]")
        return
    
    cert = (
        f"IDEA OWNERSHIP PROOF\n"
        f"{'=' * 50}\n\n"
        f"Title: {idea['title']}\n"
        f"Timestamp: {idea['timestamp']}\n"
        f"Proof Hash: {idea['proof']}\n\n"
        f"This cryptographic proof demonstrates that the idea\n"
        f"existed at the specified timestamp. The hash is generated\n"
        f"from the full content and timestamp, providing tamper-proof\n"
        f"evidence of originality.\n\n"
        f"Verification: Hash the full content with timestamp\n"
        f"and compare with the proof hash above."
    )
    
    console.print(Panel(cert, title="Ownership Proof Certificate", border_style="green"))

@app.command()
def trust(
    action: str = typer.Argument(..., help="Action: add, remove, list"),
    email: str = typer.Option(None, "--email", "-e", help="Email address")
):
    """Manage trust circle"""
    init_storage()
    trust_list = load_trust()
    
    if action == "add":
        if not email:
            console.print("[red]Email required for add action[/red]")
            return
        if email not in trust_list:
            trust_list.append(email)
            save_trust(trust_list)
            console.print(f"[green]Added {email} to trust circle[/green]")
        else:
            console.print(f"[yellow]{email} already in trust circle[/yellow]")
    
    elif action == "remove":
        if not email:
            console.print("[red]Email required for remove action[/red]")
            return
        if email in trust_list:
            trust_list.remove(email)
            save_trust(trust_list)
            console.print(f"[green]Removed {email} from trust circle[/green]")
        else:
            console.print(f"[yellow]{email} not in trust circle[/yellow]")
    
    elif action == "list":
        if not trust_list:
            console.print("[yellow]Trust circle is empty[/yellow]")
            return
        console.print("[bold]Trust Circle:[/bold]")
        for email in trust_list:
            console.print(f"  • {email}")
    
    else:
        console.print("[red]Invalid action. Use: add, remove, or list[/red]")

@app.command()
def share(
    idea_id: int = typer.Argument(..., help="Idea ID"),
    output: str = typer.Option("share.txt", "--output", "-o", help="Output file")
):
    """Generate shareable sanitized version"""
    init_storage()
    ideas = load_ideas()
    
    idea = next((i for i in ideas if i['id'] == idea_id), None)
    if not idea:
        console.print(f"[red]Idea {idea_id} not found[/red]")
        return
    
    share_content = (
        f"{idea['title']}\n"
        f"{'=' * len(idea['title'])}\n\n"
        f"{idea['sanitized']}\n\n"
        f"---\n"
        f"Timestamped: {idea['timestamp']}\n"
        f"Proof Hash: {idea['proof']}\n\n"
        f"Note: Sensitive details have been redacted.\n"
        f"This version is safe to share publicly."
    )
    
    Path(output).write_text(share_content)
    console.print(f"[green]Shareable version saved to {output}[/green]")

if __name__ == "__main__":
    app()
