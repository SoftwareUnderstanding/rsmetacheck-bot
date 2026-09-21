"""Token verification command - check if tokens have correct permissions."""

from pathlib import Path

import click
from dotenv import load_dotenv

from . import github_api, gitlab_api


@click.command()
@click.option(
    "--github",
    is_flag=True,
    default=False,
    help="Check GitHub token only.",
)
@click.option(
    "--gitlab",
    is_flag=True,
    default=False,
    help="Check GitLab token only.",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    default=False,
    help="Output results as JSON.",
)
def verify_tokens_command(github: bool, gitlab: bool, output_json: bool):
    """Verify that tokens are set and have correct permissions."""
    # Load .env file if it exists
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        click.echo(f"ℹ️  Loaded environment from {env_path}\n", err=False)

    results = []

    # Check GitHub if not specifically asking for GitLab only
    if not gitlab or github:
        try:
            gh_api = github_api.GitHubAPI()
            results.append(gh_api.verify_auth())
        except ValueError as e:
            results.append(
                {
                    "platform": "GitHub",
                    "token_set": False,
                    "authenticated": False,
                    "has_issues_permission": False,
                    "has_contents_permission": False,
                    "user": None,
                    "scopes": [],
                    "errors": [str(e)],
                }
            )

    # Check GitLab if not specifically asking for GitHub only
    if not github or gitlab:
        try:
            gl_api = gitlab_api.GitLabAPI()
            results.append(gl_api.verify_auth())
        except ValueError as e:
            results.append(
                {
                    "platform": "GitLab",
                    "host": "gitlab.com",
                    "token_set": False,
                    "authenticated": False,
                    "has_issues_permission": False,
                    "has_contents_permission": False,
                    "user": None,
                    "scopes": [],
                    "errors": [str(e)],
                }
            )

    if output_json:
        import json

        click.echo(json.dumps(results, indent=2))
        return

    # Pretty print results
    click.echo("\n" + "=" * 60)
    click.echo("Token Verification Results")
    click.echo("=" * 60 + "\n")

    all_valid = True

    for result in results:
        platform = result["platform"]
        click.echo(f"📊 {platform}")
        click.echo(f"  Token set: {'✅ Yes' if result['token_set'] else '❌ No'}")

        if result["token_set"]:
            click.echo(
                f"  Authenticated: {'✅ Yes' if result['authenticated'] else '❌ No'}"
            )

            if result["authenticated"]:
                click.echo(f"  User: {result['user']}")
                if result.get("scopes"):
                    click.echo(f"  Scopes: {', '.join(result['scopes'])}")
                click.echo(
                    f"  Issues permission: {'✅ Yes' if result['has_issues_permission'] else '⚠️  No'}"
                )
                click.echo(
                    f"  Contents permission: {'✅ Yes' if result['has_contents_permission'] else '⚠️  No'}"
                )

                if result.get("errors"):
                    click.echo("  ⚠️  Warnings:")
                    for error in result["errors"]:
                        click.echo(f"    - {error}")
            else:
                click.echo("  ❌ Authentication failed:")
                for error in result.get("errors", []):
                    click.echo(f"    - {error}")
                all_valid = False
        else:
            click.echo("  ⚠️  Token not configured:")
            for error in result.get("errors", []):
                click.echo(f"    - {error}")

        click.echo()

    click.echo("=" * 60)

    if all_valid:
        click.echo("✅ All tokens are configured and valid!")
        click.echo("=" * 60 + "\n")
    else:
        click.echo("❌ Some tokens need attention.")
        click.echo("=" * 60 + "\n")
        exit(1)
