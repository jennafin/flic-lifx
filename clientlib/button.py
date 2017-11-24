import logging
class Button(object):
    """Representation of a flic button.
    """
    def __init__(self, button_id):
        self.button_id = button_id

    def __repr__(self):
        return "Flic button: %s" % self.button_id
