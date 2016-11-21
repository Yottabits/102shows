def run(strip, conf, parameters):
    strip.clearStrip()


def parameters_valid(parameters: dict) -> bool:
    if "useless" in parameters:
        return True
    else:
        return False
