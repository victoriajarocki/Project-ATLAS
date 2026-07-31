"""Command-line entry point for Project ATLAS."""

from atlas.config.settings import load_settings
from atlas.core.app import AtlasApp
from atlas.memory.database import (
    MemoryDatabaseError,
    SQLiteMemoryRepository,
)
from atlas.memory.service import MemoryService
from atlas.models.base import ModelError
from atlas.models.factory import create_model_provider

ATLAS_NAME = "ATLAS"
ATLAS_VERSION = "0.4.0"
EXIT_COMMANDS = {"exit", "quit", "shutdown"}


def run_cli(app: AtlasApp) -> None:
    """Run the interactive ATLAS command-line interface."""
    print("=" * 50)
    print(f"{ATLAS_NAME} v{ATLAS_VERSION}")
    print("Personal AI Operating System")
    print(f"Model provider: {app.provider_name}")
    print(f"Persistent memory: {'Enabled' if app.memory_enabled else 'Disabled'}")
    print("=" * 50)
    print("Commands:")
    print("  remember <information>")
    print("  memories")
    print("  forget <memory ID>")
    print("  exit")
    print()

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


def create_app() -> AtlasApp:
    """Configure and create the ATLAS application."""
    settings = load_settings()

    provider = create_model_provider(settings)

    repository = SQLiteMemoryRepository(database_path=settings.memory_database_path)

    memory_service = MemoryService(repository)
    memory_service.initialize()

    return AtlasApp(
        model_provider=provider,
        memory_service=memory_service,
    )


def main() -> None:
    """Configure and start Project ATLAS."""
    try:
        app = create_app()
    except (ModelError, MemoryDatabaseError) as error:
        print(f"ATLAS STARTUP ERROR: {error}")
        return

    run_cli(app)


if __name__ == "__main__":
    main()
