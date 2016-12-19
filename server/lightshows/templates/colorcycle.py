"""
Color Cycle Template
(c) 2015 Martin Erzberger, 2016 Simon Leiner
licensed under the GNU Public License, version 2
"""

from lightshows.templates.base import *


class ColorCycle(Lightshow):
    """
    This class is the basis of all color cycles, such as rainbow or theater chase.
    A specific color cycle must subclass this template, and implement at least the
    following methods:
     - before_start()
     - update()
    """

    def init_parameters(self):
        """ default parameters"""
        self.register('pause_sec', 0, verify.not_negative_numeric)
        self.register('num_steps_per_cycle', None, verify.positive_integer)
        self.register('num_cycles', float("inf"), verify.positive_integer)

    def check_runnable(self):
        """ checks if all necessary parameters are set """
        if self.p['pause_sec'] is None:
            raise InvalidParameters("Missing parameter \"pause_sec\"!")
        if self.p['num_steps_per_cycle'] is None:
            raise InvalidParameters("Missing parameter \"num_steps_per_cycle\"!")
        if self.p['num_cycles'] is None:
            raise InvalidParameters("Missing parameter \"num_cycles\"!")

    @abstractmethod
    def before_start(self):
        """
        This method is called to initialize a color program.
        A particular subclass could setup variables, or even light the strip in an initial color.
        """
        pass

    def shutdown(self):
        """ called before termination of the lightshow """
        pass

    @abstractmethod
    def update(self, current_step: int, current_cycle: int) -> bool:
        """
        This method paints one subcycle. It must be implemented

        :param current_step:  This goes from zero to numStepsPerCycle-1, and then back to zero. It is up to the subclass
                              to define what is done in one cycle. One cycle could be one pass through the rainbow.
                              Or it could be one pixel wandering through the entire strip (so for this case,
                              the numStepsPerCycle should be equal to num_leds).
        :param current_cycle: Starts with zero, and goes up by one whenever a full cycle has completed.
        :return: Is it necessary to invoke strip.show() after the update() method is finished?
        """
        raise NotImplementedError("Please implement the update() method")

    def cleanup(self):
        self.shutdown()
        self.strip.sync_up()

    def run(self):
        """ start the actual work """
        self.before_start()  # Call the subclasses before_start method
        self.strip.show()
        current_cycle = 0
        while True:  # Loop forever (for would not work for num_cycles = infinity)
            for currentStep in range(self.p['num_steps_per_cycle']):
                need_repaint = self.update(currentStep, current_cycle)  # Call the subclasses update method
                if need_repaint:
                    self.strip.show()  # Display, only if required
                self.sleep(self.p['pause_sec'])  # Pause until the next step
            current_cycle += 1
            if current_cycle >= self.p['num_cycles']:
                break
        # Finished, cleanup everything
        self.cleanup()
