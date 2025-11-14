import click
import os

from genocrate import cli

def list_command_names_md(f):
    f.write("# CLI Commands\n\n")
    for name in cli.commands:
        f.write(f"- `{name}`\n")
    f.write("\n---\n\n")

def list_help_subcommand(cmd, f):
    ctx = click.core.Context(cmd, info_name=cmd.name)
    commands = getattr(cmd, 'commands', {})
    for sub in commands.values():
        f.write(f"## `{sub.name}`\n\n")
        f.write("```\n")
        f.write(sub.get_help(ctx))
        f.write("\n```\n\n")

if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(__file__), "..", "docs", "cli.md")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        list_command_names_md(f)
        list_help_subcommand(cli, f)

