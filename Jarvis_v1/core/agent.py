class Agent:
    """
    JARVIS agent controller.
    """

    def __init__(self, brain):
        self.brain = brain

    def run(self, user_input):

        if not user_input:
            return None

        return self.brain.process(user_input)