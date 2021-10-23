class InvalidStateError(Exception):
    pass


class InvalidDeckError(InvalidStateError):
    def __init__(self, card_type):
        self.card_type = card_type
