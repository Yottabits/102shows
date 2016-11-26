"""
Color Cycle Template
(c) 2015 Martin Erzberger, modified 2016 by Simon Leiner

This class is the basis of all color cycles, such as rainbow or theater chase.
A specific color cycle must subclass this template, and implement at least the
'update' method.
"""

from drivers.fake_apa102 import APA102
import time


class ColorCycleTemplate:
    def __init__(self, strip: APA102, pauseValue=0, numStepsPerCycle=100, numCycles=-1, order='rgb'):  # Init method
        self.strip = strip  # store the strip handle
        self.pauseValue = pauseValue  # How long to pause between two runs
        self.numStepsPerCycle = numStepsPerCycle  # The number of steps in one cycle.
        self.numCycles = numCycles  # How many times will the program run
        self.order = order  # Strip colour ordering

    """
    void init()
    This method is called to initialize a color program.
    """

    def init(self, strip):
        # The default does nothing. A particular subclass could setup variables, or
        # even light the strip in an initial color.
        print('Init not implemented')

    """
    void shutdown()
    This method is called at the end, when the light program should terminate
    """

    def shutdown(self, strip):
        # The default does nothing
        print('Shutdown not implemented')

    """
    void update()
    This method paints one subcycle. It must be implemented
    currentStep: This goes from zero to numStepsPerCycle-1, and then back to zero. It is up to the subclass to define
                 what is done in one cycle. One cycle could be one pass through the rainbow. Or it could
                 be one pixel wandering through the entire strip (so for this case, the numStepsPerCycle should be
                 equal to numLEDs).
    currentCycle: Starts with zero, and goes up by one whenever a full cycle has completed.
    """

    def update(self, strip, numStepsPerCycle, currentStep, currentCycle):
        raise NotImplementedError("Please implement the update() method")

    def cleanup(self, strip):
        self.shutdown(strip)
        strip.clearStrip()
        print('Strip cleared')
        strip.cleanup()
        print('SPI closed')

    """
    Start the actual work
    """

    def start(self):
        try:
            self.init(self.strip)  # Call the subclasses init method
            self.strip.show()
            currentCycle = 0
            while True:  # Loop forever (no 'for' here due to the possibility of infinite loops)
                for currentStep in range(self.numStepsPerCycle):
                    needRepaint = self.update(self.strip, self.numStepsPerCycle, currentStep,
                                              currentCycle)  # Call the subclasses update method
                    if needRepaint:
                        self.strip.show()  # Display, only if required
                    time.sleep(self.pauseValue)  # Pause until the next step
                currentCycle += 1
                if self.numCycles != -1 and currentCycle >= self.numCycles:
                    break
            # Finished, cleanup everything
            self.cleanup(self.strip)

        except KeyboardInterrupt:  # Ctrl-C can halt the light program
            print('Interrupted...')
            self.cleanup(self.strip)
