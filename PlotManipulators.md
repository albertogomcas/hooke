## correct ##

Many instruments give in output the constant speed SMFS curves as Z piezo position _versus_ force. This is often not what is needed. The **correct** plot manipulator transforms the coordinates so to have the Z distance between tip and surface in the X axis.

It acts by subtracting to each X coordinate point the corresponding Y _deflection_.

It is activated by the flag **correct** (see VariableList).

## median ##

A simple median window filter. Activation and window size are defined by the flag **median** (see VariableList).

## flatten ##

"Flats" a constant speed SMFS curve. In some cases (e.g. when working on gold surfaces), optical interference can create a smooth, annoying sinusoidal artefact superimposed to both the retraction and the approaching curve. To avoid that, a polynomial fit is made on the non-contact part of the approaching curve and the resulting fit is subtracted to both non-contact parts. Activation defined by the flag **flatten** (see VariableList)

## centerzero ##

Shifts the curves vertically in order to match the free cantilever area of the retraction with the 0 in y axis. Commands like `multifit` or `review` expect this manipulator to be activated.

## clamp ##

Handles some viewing options for the "force clamp" data format, depending on the state of these configuration variables:
  * If the flag **fc\_showphase** != 0, the 'phase' data column (i.e. the 2nd) is shown in the 0th graph (else it isn't)
  * If the flag **fc\_showimposed** != 0, the 'imposed deflection' data column (i.e. the 5th) is shown in the 1st graph (else it isn't)
  * If the flag **fc\_interesting** == 0, the entire curve is shown in the graphs; if it has a non-zero value N, only phase N is shown.

Note that this implementation depends quite strictly on the force clamp data format.