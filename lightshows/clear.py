import apa102

class clear:
    def __init__(self, strip: apa102.APA102):
        self.strip = strip

    def run(self):
        strip.clear()
