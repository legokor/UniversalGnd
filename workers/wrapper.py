import re


class Wrapper:
    def __init__(self, pattern, consumer, sender):
        self.pattern = pattern
        self.consumer = consumer
        self.sender = sender
        self.buffer = ""

    def consume_character(self, char):
        self.buffer += char
        if len(self.buffer) == len(self.pattern):
            if re.match(self.pattern, self.buffer):
                self.digest_message(self.buffer)
                self.buffer = ""

    def digest_message(self, message):
        self.consumer(message)

    def send(self, message):
        self.sender(message)
