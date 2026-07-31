"""Command-line entry point for Project ATLAS."""

from atlas.config.settings import load_settings
from atlas.core.app import AtlasApp
from atlas.models.base import ModelError
from atlas.models.factory import create_model_provider

ATLAS_NAME = "ATLAS"
ATLAS_VERSION = "0.3.0"
EXIT_COMMANDS = {"exit", "quit", "shutdown"}


def run_cli(app: AtlasApp) -> None:
    """Run the interactive ATLAS command-line interface."""
    print("=" * 50)
    print(f"{ATLAS_NAME} v{ATLAS_VERSION}")
    print("Personal AI Operating System")
    print(f"Model provider: {app.provider_name}")
    print("=" * 50)
    print("Type 'exit' to close the session.\n")

    while True:
        try:
            user_message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nATLAS: Session interrupted. Shutting down.")
            break

        if user_message.lower() in EXIT_COMMANDS:
            print("ATLAS: Shutting down the current ATLAS session.")
            break

        try:
            response = app.process_message(user_message)
        except ModelError as error:
            print(f"ATLAS ERROR: {error}\n")
            continue

        print(f"ATLAS: {response}\n")


def main() -> None:
    """Configure and start Project ATLAS."""
    try:
        settings = load_settings()
        provider = create_model_provider(settings)
        app = AtlasApp(model_provider=provider)
    except ModelError as error:
        print(f"ATLAS STARTUP ERROR: {error}")
        return

    run_cli(app)


if __name__ == "__main__":
    main()
