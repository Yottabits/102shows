def dim(undimmed: tuple, factor: float) -> tuple:
    """ multiply all components of :param undimmed with :param factor
    :return: resulting vector, as int
    """
    dimmed = ()
    for i in undimmed:
        i = int(factor * i)  # brightness needs to be an integer
        dimmed = dimmed + (i,)  # merge tuples
    return dimmed

def fadeout(fadetime_sec: float):
    pass # @todo
