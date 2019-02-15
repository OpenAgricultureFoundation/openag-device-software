""" 
    Simple implementation of a Proportional-Integral-Derivative 
    (PID) Controller in the Python Programming Language.  
    Copied from: https://github.com/ivmech/ivPID
    Copyright (C) 2015 Ivmech Mechatronics Ltd. <bilgi@ivmech.com>
    Author: Caner Durmusoglu
    GNU General Public License v3.

    http://en.wikipedia.org/wiki/PID_controller
"""
import time

""" PID Controller """


class PID:

    # --------------------------------------------------------------------------
    # Class instance vars
    Kp: float = 0.0
    Ki: float = 0.0
    Kd: float = 0.0
    windup_guard: float = 20.0
    set_point: float = 0.0
    sample_time: float = 0.0
    current_time: float = 0.0
    last_time: float = 0.0
    PTerm: float = 0.0
    ITerm: float = 0.0
    DTerm: float = 0.0
    last_error: float = 0.0
    output: float = 0.0

    # --------------------------------------------------------------------------
    def __init__(self, P: float = 0.2, I: float = 0.0, D: float = 0.0) -> None:
        """Initialize class instance"""
        self.setKp(P)
        self.setKi(I)
        self.setKd(D)
        self.setSampleTime(0.0)
        self.setSetPoint(0.0)
        self.current_time = time.time()
        self.last_time = self.current_time
        self.clear()

    # --------------------------------------------------------------------------
    def clear(self) -> None:
        """Clears PID computations and coefficients"""
        self.setSetPoint(0.0)
        self.setWindup(20.0)
        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0
        self.output = 0.0

    # --------------------------------------------------------------------------
    def setSetPoint(self, set_point: float) -> None:
        self.set_point = set_point

    # --------------------------------------------------------------------------
    def getSetPoint(self) -> float:
        return self.set_point

    # --------------------------------------------------------------------------
    def getOutput(self) -> float:
        return self.output

    # --------------------------------------------------------------------------
    def update(self, feedback_value: float) -> None:
        """Calculates PID value for given reference feedback
           u(t) = K_p e(t) + K_i \int_{0}^{t} e(t)dt + K_d {de}/{dt}
        """
        error: float = (self.getSetPoint() - feedback_value)

        self.current_time = time.time()
        delta_time: float = self.current_time - self.last_time
        delta_error: float = error - self.last_error

        if delta_time >= self.sample_time:
            self.PTerm = self.Kp * error
            self.ITerm += error * delta_time

            if self.ITerm < -self.windup_guard:
                self.ITerm = -self.windup_guard
            elif self.ITerm > self.windup_guard:
                self.ITerm = self.windup_guard

            self.DTerm = 0.0
            if delta_time > 0:
                self.DTerm = delta_error / delta_time

            # Remember last time and last error for next calculation
            self.last_time = self.current_time
            self.last_error = error

            self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)

    # --------------------------------------------------------------------------
    def setKp(self, proportional_gain: float) -> None:
        """Determines how aggressively the PID reacts to the current error
        with setting Proportional Gain"""
        self.Kp = proportional_gain

    # --------------------------------------------------------------------------
    def setKi(self, integral_gain: float) -> None:
        """Determines how aggressively the PID reacts to the current error
        with setting Integral Gain"""
        self.Ki = integral_gain

    # --------------------------------------------------------------------------
    def setKd(self, derivative_gain: float) -> None:
        """Determines how aggressively the PID reacts to the current error
        with setting Derivative Gain"""
        self.Kd = derivative_gain

    # --------------------------------------------------------------------------
    def setWindup(self, windup: float) -> None:
        """Integral windup, also known as integrator windup or reset windup,
        refers to the situation in a PID feedback controller where
        a large change in setpoint occurs (say a positive change)
        and the integral terms accumulates a significant error
        during the rise (windup), thus overshooting and continuing
        to increase as this accumulated error is unwound
        (offset by errors in the other direction).
        The specific problem is the excess overshooting.
        """
        self.windup_guard = windup

    # --------------------------------------------------------------------------
    def setSampleTime(self, sample_time: float) -> None:
        """PID that should be updated at a regular interval.
        Based on a pre-determined sample time, the PID decides if it should
        compute or return immediately.
        """
        self.sample_time = sample_time
