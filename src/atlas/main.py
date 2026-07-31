"""Command-line entry point for Project ATLAS."""

from atlas.config.settings import load_settings
from atlas.conversations.database import (
    ConversationDatabaseError,
    SQLiteConversationRepository,
)
from atlas.conversations.service import ConversationService
from atlas.core.app import AtlasApp
from atlas.memory.database import (
    MemoryDatabaseError,
    SQLiteMemoryRepository,
)
from atlas.memory.service import MemoryService
from atlas.models.base import ModelError
from atlas.models.factory import create_model_provider

ATLAS_NAME = "ATLAS"
ATLAS_VERSION = "0.5.0"
EXIT_COMMANDS = {"exit", "quit", "shutdown"}


def run_cli(app: AtlasApp) -> None:
    """Run the interactive ATLAS command-line interface."""
    print("=" * 50)
    print(f"{ATLAS_NAME} v{ATLAS_VERSION}")
    print("Personal AI Operating System")
    print(f"Model provider: {app.provider_name}")
    print(f"Persistent memory: {'Enabled' if app.memory_enabled else 'Disabled'}")
    print(f"Conversation sessions: {'Enabled' if app.conversations_enabled else 'Disabled'}")

    if app.active_conversation_id is not None:
        print(f"Active chat: {app.active_conversation_id}")

    print("=" * 50)
    print("Memory commands:")
    print("  remember <information>")
    print("  memories")
    print("  forget <memory ID>")
    print()
    print("Conversation commands:")
    print("  new chat [title]")
    print("  chats")
    print("  use chat <chat ID>")
    print("  rename chat <new title>")
    print("  history")
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
        except (
            ModelError,
            ConversationDatabaseError,
        ) as error:
            print(f"ATLAS ERROR: {error}\n")
            continue

        print(f"ATLAS: {response}\n")


def create_app() -> AtlasApp:
    """Configure and create the ATLAS application."""
    settings = load_settings()
    provider = create_model_provider(settings)

    memory_repository = SQLiteMemoryRepository(database_path=settings.memory_database_path)
    memory_service = MemoryService(memory_repository)
    memory_service.initialize()

    conversation_repository = SQLiteConversationRepository(
        database_path=settings.memory_database_path
    )
    conversation_service = ConversationService(conversation_repository)
    conversation_service.initialize()

    return AtlasApp(
        model_provider=provider,
        memory_service=memory_service,
        conversation_service=conversation_service,
    )


def main() -> None:
    """Configure and start Project ATLAS."""
    try:
        app = create_app()
    except (
        ModelError,
        MemoryDatabaseError,
        ConversationDatabaseError,
    ) as error:
        print(f"ATLAS STARTUP ERROR: {error}")
        return

    run_cli(app)


if __name__ == "__main__":
    main()
