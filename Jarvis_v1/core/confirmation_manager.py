class ConfirmationManager:

    def __init__(self):
        self.pending_action = None

    # =========================================================
    # SET PENDING ACTION
    # =========================================================

    def set_pending(
        self,
        action,
        arguments=None,
        message=None,
        original_request=None,
    ):
        self.pending_action = {
            "action": action,
            "arguments": arguments or {},
            "message": message or "",
            "original_request": original_request or "",
        }

    # =========================================================
    # CHECK PENDING ACTION
    # =========================================================

    def has_pending(self):
        return self.pending_action is not None

    # =========================================================
    # GET PENDING ACTION
    # =========================================================

    def get_pending(self):
        return self.pending_action

    # =========================================================
    # CONFIRM
    # =========================================================

    def confirm(self):
        pending = self.pending_action
        self.pending_action = None
        return pending

    # =========================================================
    # CANCEL
    # =========================================================

    def cancel(self):
        self.pending_action = None

    # =========================================================
    # YES DETECTION
    # =========================================================

    def is_confirmation(self, user_input):

        if not user_input:
            return False

        text = str(user_input).strip().lower()

        return text in {
            "yes",
            "y",
            "yeah",
            "yep",
            "sure",
            "okay",
            "ok",
            "confirm",
            "do it",
            "go ahead",
            "proceed",
        }

    # =========================================================
    # NO DETECTION
    # =========================================================

    def is_cancellation(self, user_input):

        if not user_input:
            return False

        text = str(user_input).strip().lower()

        return text in {
            "no",
            "n",
            "nope",
            "cancel",
            "stop",
            "don't",
            "do not",
            "never mind",
            "nevermind",
        }