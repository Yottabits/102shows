"""
Color Cycle Template
(c) 2015 Martin Erzberger, modified 2016 by Simon Leiner

This class is the basis of all color cycles, such as rainbow or theater chase.
A specific color cycle must subclass this template, and implement at least the
'update' method.
"""

from drivers.apa102 import APA102 as LEDStrip
from DefaultConfig import Configuration
from lightshows.metashow import Lightshow, InvalidParameters
import logging as log
import time
from abc import abstractmethod


class ColorCycleTemplate(Lightshow):
    # Parameters
    @property
    def pause_sec(self):
        return self.__pause_sec

    @pause_sec.setter
    def pause_sec(self, pause_sec):
        if type(pause_sec) in (int, float):
            self.__pause_sec = pause_sec
        else:
            raise InvalidParameters("Parameter \"pause_sec\" must be numeric!")

    @property
    def num_steps_per_cycle(self):
        return self.__num_steps_per_cycle

    @num_steps_per_cycle.setter
    def num_steps_per_cycle(self, num_steps_per_cycle):
        try:
            num_steps_per_cycle = int(num_steps_per_cycle)
        except ValueError as e:
            raise InvalidParameters("Parameter \"num_steps_per_cycle\" must be numeric! (given: {given})".
                                    format(given=num_steps_per_cycle))
        else:
            self.__num_steps_per_cycle = num_steps_per_cycle

    @property
    def num_cycles(self):
        return self.__num_cycles

    @num_cycles.setter
    def num_cycles(self, num_cycles):
        try:
            num_steps_per_cycle = int(num_steps_per_cycle)
        except ValueError as e:
            raise InvalidParameters("Parameter \"num_steps_per_cycle\" must be numeric! (given: {given})".
                                    format(given=num_steps_per_cycle))
        else:
            self.__num_steps_per_cycle = num_steps_per_cycle

    def __init__(self, strip: LEDStrip, conf: Configuration, parameters: dict):
        super().__init__(strip, conf, parameters, check_runnable=False)
        self.__parameter_map = {"pause_sec": self.pause_sec,
                                "num_steps_per_cycle": self.num_steps_per_cycle,
                                "num_cycles": self.num_cycles}
        for parameter in self.__parameter_map:
            self.__parameter_map[parameter] = None

        self.order = 'rgb'  # this should not be changed!

        try:
            self.pause_sec = parameters["pause_sec"]
            self.num_steps_per_cycle = parameters["num_steps_per_cycle"]
            self.num_cycles = parameters["num_cycles"]
        except KeyError as missing_key:
            raise InvalidParameters("Key \"{name}\" is missing!".format(name=missing_key))

    def check_runnable(self) -> bool:
        return True


    """
    void init()
    This method is called to initialize a color program.
    """

    @abstractmethod
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

    @abstractmethod
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

    def run(self):
        try:
            self.init(self.strip)  # Call the subclasses init method
            self.strip.show()
            currentCycle = 0
            while True:  # Loop forever (no 'for' here due to the possibility of infinite loops)
                for currentStep in range(self.num_steps_per_cycle):
                    needRepaint = self.update(self.strip, self.num_steps_per_cycle, currentStep,
                                              currentCycle)  # Call the subclasses update method
                    if needRepaint:
                        self.strip.show()  # Display, only if required
                    time.sleep(self.pause_sec)  # Pause until the next step
                currentCycle += 1
                if self.num_cycles != -1 and currentCycle >= self.num_cycles:
                    break
            # Finished, cleanup everything
            self.cleanup(self.strip)

        except KeyboardInterrupt:  # Ctrl-C can halt the light program
            print('Interrupted...')
            self.cleanup(self.strip)
