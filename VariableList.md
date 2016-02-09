IN PROGRESS

  * **correct** (0/1) Tells Hooke to correct a velocity clamp force curve for deﬂection or not. The default is 1 (true). By typing 'set correct 0' Hooke stops correcting to give the true tip-surface extension and returns the piezo-setpoint extension.
  * **flatten** (0/1) Toggles on and off the automatic flattening of the force curve. When enabled, the _flatten_ plot manipulator fits a polynomial to the non-contact part of the extension force curve and subtracts it, effectively erasing artefacts like optical interference.
  * **medfilt** (integer) Tells Hooke to smooth the curve shown with a simple median ﬁlter. The value of the variable is the amplitude of the running window: a larger window means a smoother ﬁlter. By default, medﬁlt is set to 0 (_i. e._ no ﬁltering). Try for example 'set medﬁlt 7' or larger to clearly see the effects.
  * **xaxes** (0/1) and **yaxes** (0/1) ﬂip the X and Y axes, respectively. By default they are set to 0. Try setting them to 1 to ﬂip the plot (Bug warning: sometimes the default orientation can come back after zooming)

See also Brief\_Autopeak\_HowTo to look at the meaning of variables related to the **autopeak** command.