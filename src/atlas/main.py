"""Command-line entry point for Project ATLAS."""

import logging

from atlas.agent.exceptions import AgentError
from atlas.agent.parser import AgentDecisionParser
from atlas.agent.prompt import AgentPromptBuilder
from atlas.agent.service import AgentService
from atlas.config.settings import Settings, load_settings
from atlas.conversations.database import (
    ConversationDatabaseError,
    SQLiteConversationRepository,
)
from atlas.conversations.service import ConversationService
from atlas.core.app import AtlasApp
from atlas.filesystem.exceptions import FileSystemError
from atlas.filesystem.paths import ScopedPathResolver
from atlas.filesystem.service import FileSystemService
from atlas.memory.database import (
    MemoryDatabaseError,
    SQLiteMemoryRepository,
)
from atlas.memory.service import MemoryService
from atlas.models.base import ModelError
from atlas.models.factory import create_model_provider
from atlas.observability.logging import (
    LoggingConfigurationError,
    configure_logging,
)
from atlas.permissions.policy import PermissionPolicy
from atlas.permissions.service import PermissionService
from atlas.tools.base import ToolError
from atlas.tools.builtin import (
    CalculatorTool,
    ConfirmationDemoTool,
    CreateDirectoryTool,
    CurrentTimeTool,
    FileInfoTool,
    ListDirectoryTool,
    ReadTextFileTool,
    WriteTextFileTool,
)
from atlas.tools.executor import ToolExecutor
from atlas.tools.registry import ToolRegistry

ATLAS_NAME = "ATLAS"

ATLAS_VERSION = "1.0.0"

EXIT_COMMANDS = {
    "exit",
    "quit",
    "shutdown",
}

logger = logging.getLogger(__name__)


def run_cli(app: AtlasApp) -> None:
    """Run the interactive ATLAS command-line interface."""
    print("=" * 50)
    print(f"{ATLAS_NAME} v{ATLAS_VERSION}")
    print("Personal AI Operating System")
    print(f"Model provider: {app.provider_name}")
    print(f"Persistent memory: {'Enabled' if app.memory_enabled else 'Disabled'}")
    print(f"Conversation sessions: {'Enabled' if app.conversations_enabled else 'Disabled'}")
    print(f"Tool system: {'Enabled' if app.tools_enabled else 'Disabled'}")
    print(f"Permission system: {'Enabled' if app.permissions_enabled else 'Disabled'}")
    print(f"Agent system: {'Enabled' if app.agent_enabled else 'Disabled'}")

    if app.active_conversation_id is not None:
        print(f"Active chat: {app.active_conversation_id}")

    print("=" * 50)

    print("Natural-language agent examples:")
    print("  What is 347 multiplied by 982?")
    print("  What time is it?")
    print("  List the files in my workspace.")
    print("  Read Rocket Design/notes.txt")
    print()

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
    print()

    print("Explicit tool commands:")
    print("  tools")
    print('  tool calculator {"expression": "2 + 2"}')
    print("  tool current_time {}")
    print('  tool confirmation_demo {"message": "Approved action"}')
    print('  tool list_directory {"path": "."}')
    print('  tool file_info {"path": "example.txt"}')
    print('  tool read_text_file {"path": "example.txt"}')
    print('  tool create_directory {"path": "Rocket Design"}')
    print('  tool write_text_file {"path": "notes.txt", "content": "ATLAS test file."}')
    print()

    print("Confirmation commands:")
    print("  confirm yes")
    print("  confirm no")
    print()

    print("Session commands:")
    print("  exit")
    print()

    logger.info("ATLAS command-line interface started.")

    while True:
        try:
            user_message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            logger.info("ATLAS session interrupted by the user.")
            print("\nATLAS: Session interrupted. Shutting down.")
            break

        if user_message.lower() in EXIT_COMMANDS:
            logger.info("ATLAS shutdown command received.")
            print("ATLAS: Shutting down the current ATLAS session.")
            break

        try:
            response = app.process_message(user_message)
        except (
            AgentError,
            ModelError,
            ConversationDatabaseError,
            MemoryDatabaseError,
            FileSystemError,
            ToolError,
        ) as error:
            logger.exception("ATLAS request failed in the CLI.")
            print(f"ATLAS ERROR: {error}\n")
            continue

        print(f"ATLAS: {response}\n")

    logger.info("ATLAS command-line interface stopped.")


def create_app(settings: Settings) -> AtlasApp:
    """Create ATLAS using validated application settings."""
    logger.info(
        "Creating ATLAS application. provider=%s model=%s",
        settings.provider,
        settings.model,
    )

    provider = create_model_provider(settings)

    memory_repository = SQLiteMemoryRepository(database_path=settings.memory_database_path)
    memory_service = MemoryService(memory_repository)
    memory_service.initialize()

    logger.info(
        "Persistent memory initialized. database=%s",
        settings.memory_database_path,
    )

    conversation_repository = SQLiteConversationRepository(
        database_path=settings.memory_database_path
    )
    conversation_service = ConversationService(conversation_repository)
    conversation_service.initialize()

    logger.info("Conversation sessions initialized.")

    path_resolver = ScopedPathResolver(allowed_directories=settings.allowed_directories)

    filesystem_service = FileSystemService(
        path_resolver=path_resolver,
        max_read_bytes=settings.filesystem_max_read_bytes,
        max_write_characters=(settings.filesystem_max_write_characters),
    )

    logger.info(
        "Scoped file-system service initialized. "
        "allowed_directory_count=%d "
        "max_read_bytes=%d "
        "max_write_characters=%d",
        len(filesystem_service.allowed_directories),
        settings.filesystem_max_read_bytes,
        settings.filesystem_max_write_characters,
    )

    tool_registry = ToolRegistry()

    tool_registry.register(CalculatorTool())
    tool_registry.register(CurrentTimeTool())
    tool_registry.register(ConfirmationDemoTool())
    tool_registry.register(ListDirectoryTool(filesystem_service))
    tool_registry.register(FileInfoTool(filesystem_service))
    tool_registry.register(ReadTextFileTool(filesystem_service))
    tool_registry.register(CreateDirectoryTool(filesystem_service))
    tool_registry.register(WriteTextFileTool(filesystem_service))

    tool_executor = ToolExecutor(tool_registry)

    logger.info(
        "Tool system initialized. tool_count=%d",
        len(tool_registry.list_definitions()),
    )

    permission_service = PermissionService(PermissionPolicy())

    logger.info("Permission system initialized.")

    agent_service = AgentService(
        model_provider=provider,
        prompt_builder=AgentPromptBuilder(tool_registry),
        decision_parser=AgentDecisionParser(),
        tool_executor=tool_executor,
        permission_service=permission_service,
    )

    logger.info("Agent system initialized.")

    app = AtlasApp(
        model_provider=provider,
        memory_service=memory_service,
        conversation_service=conversation_service,
        tool_executor=tool_executor,
        permission_service=permission_service,
        agent_service=agent_service,
    )

    logger.info("ATLAS application created successfully.")

    return app


def main() -> None:
    """Configure and start Project ATLAS."""
    try:
        settings = load_settings()

        log_file = configure_logging(
            log_directory=settings.log_directory,
            log_level=settings.log_level,
            max_bytes=settings.log_max_bytes,
            backup_count=settings.log_backup_count,
        )

        logger.info(
            "Starting %s v%s. log_file=%s",
            ATLAS_NAME,
            ATLAS_VERSION,
            log_file,
        )

        app = create_app(settings)
        run_cli(app)

    except (
        AgentError,
        ModelError,
        MemoryDatabaseError,
        ConversationDatabaseError,
        FileSystemError,
        LoggingConfigurationError,
        ToolError,
    ) as error:
        logger.exception("ATLAS startup failed.")
        print(f"ATLAS STARTUP ERROR: {error}")

    finally:
        logging.shutdown()


if __name__ == "__main__":
    main()
