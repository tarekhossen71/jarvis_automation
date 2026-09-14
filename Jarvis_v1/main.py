from config import ASSISTANT_NAME, INPUT_MODE

from core.brain import Brain
from core.agent import Agent
from input.input_manager import InputManager
from output.output_manager import OutputManager

def main():

    print("=" * 50)
    print(f"        {ASSISTANT_NAME} v3")
    print("=" * 50)

    print(f"Input Mode : {INPUT_MODE}")
    print()

    # ======================================
    # INITIALIZE
    # ======================================

    brain = Brain()

    
    agent = Agent(brain)

    input_manager = InputManager(
        initial_mode=INPUT_MODE
    )

    output_manager = OutputManager()

    # ======================================
    # MAIN LOOP
    # ======================================

    while True:

        try:

            # ==================================
            # GET USER INPUT
            # ==================================

            user_input = input_manager.get_input()

            if not user_input:
                continue

            # ==================================
            # EXIT
            # ==================================

            if user_input == "__EXIT__":

                output_manager.send(
                    "Goodbye Tarek.",
                    input_manager.mode
                )

                break

            # ==================================
            # MODE SWITCH
            #
            # InputManager already changed
            # the actual mode.
            #
            # main.py only continues the loop.
            # ==================================

            if user_input == "__VOICE_MODE__":

                output_manager.send(
                    "Voice mode activated.",
                    input_manager.mode
                )

                continue

            if user_input == "__TEXT_MODE__":

                output_manager.send(
                    "Text mode activated.",
                    input_manager.mode
                )

                continue

            # ==================================
            # VOICE STANDBY
            # ==================================

            if user_input == "__STANDBY__":

                output_manager.send(
                    "Okay. Going to standby.",
                    input_manager.mode
                )

                continue

            # ==================================
            # NORMAL EXIT COMMANDS
            # ==================================

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

            # ==================================
            # SEND TO BRAIN
            # ==================================

            # response = brain.process(
            #     user_input
            # )

            response = agent.run(user_input)

            # ==================================
            # SEND RESPONSE
            # ==================================

            if response:

                output_manager.send(
                    response,
                    input_manager.mode
                )

        # ======================================
        # CTRL + C
        # ======================================

        except KeyboardInterrupt:

            print()

            output_manager.send(
                "JARVIS shutting down.",
                input_manager.mode
            )

            break

        # ======================================
        # ERROR
        # ======================================

        except Exception as e:

            print(
                f"❌ Error: {e}"
            )

    # ======================================
    # CLEANUP
    # ======================================

    try:
        input_manager.stop()
    except Exception:
        pass


if __name__ == "__main__":
    main()