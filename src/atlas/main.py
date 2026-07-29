"""Primary entry point for Project ATLAS."""

from datetime import datetime

ATLAS_NAME = "ATLAS"
ATLAS_VERSION = "0.1.0"


def create_response(user_message: str) -> str:
    """Create a temporary rule-based response.

    This function will later be replaced by ATLAS's model interface.
    """
    normalized_message = user_message.strip().lower()

    if not normalized_message:
        return "I did not receive a message."

    if normalized_message in {"hello", "hi", "hey"}:
        return "Hello, Victoria. ATLAS is online."

    if "time" in normalized_message:
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The current local time is {current_time}."

    if normalized_message in {"exit", "quit", "shutdown"}:
        return "Shutting down the current ATLAS session."

    return f"I received your message: {user_message}"


def main() -> None:
    """Start the ATLAS command-line interface."""
    print("=" * 50)
    print(f"{ATLAS_NAME} v{ATLAS_VERSION}")
    print("Personal AI Operating System")
    print("=" * 50)
    print("Type 'exit' to close the session.\n")

    while True:
        try:
            user_message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nATLAS: Session interrupted. Shutting down.")
            break

        response = create_response(user_message)
        print(f"ATLAS: {response}\n")

        if user_message.lower() in {"exit", "quit", "shutdown"}:
            break


if __name__ == "__main__":
    main()
