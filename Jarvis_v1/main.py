from config import ASSISTANT_NAME, INPUT_MODE

from core.brain import Brain
from input.input_manager import InputManager
from output.output_manager import OutputManager


def main():

    print("=" * 50)
    print(f"        {ASSISTANT_NAME} v3")
    print("=" * 50)

    print(f"Input Mode : {INPUT_MODE}")
    print()

    brain = Brain()
    input_manager = InputManager()
    output_manager = OutputManager()

    while True:

        try:

            user_input = input_manager.get_input()

            if not user_input:
                continue

            # ======================================
            # EXIT
            # ======================================

            if user_input.lower() in [
                "exit",
                "quit",
                "bye",
                "goodbye",
            ]:

                output_manager.send(
                    "Goodbye Tarek.",
                    input_manager.mode
                )

                break


            # ======================================
            # PROCESS
            # ======================================

            response = brain.process(
                user_input
            )

            output_manager.send(
                response,
                input_manager.mode
            )


        except KeyboardInterrupt:

            print("\n")

            output_manager.send(
                "JARVIS shutting down.",
                input_manager.mode
            )

            break


        except Exception as e:

            print(
                f"❌ Error: {e}"
            )


if __name__ == "__main__":
    main()