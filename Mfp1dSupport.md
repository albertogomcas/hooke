Support for the MFP 1D is highly experimental. Testing and bug reporting is much appreciated.

Currently, support for the Asylum MFP is _indirect_ : Hooke (still) can't read the binary MFP files directly.

However, a nice Igor script and menu for Hooke export has been provided by Rolf Schmidt (Concordia University, Canada). You can find the scripts in the mfp\_igor\_scripts directory in your SVN source distribution.

## Exporting ##

**Note**: It works correctly under Igor Pro 5. Igor Pro 4 seems to have still problems.

Put the scripts in a folder (somewhere convenient and outside of the Igor installation folder), then create a shortcut to that folder in the "Igor Procedures" folder.

On my computer, this folder is located at:
C:\Program Files\WaveMetrics\Igor Pro Folder\Igor Procedures

The latest export macro comes with its own 'hooke' menu and two menu items:
  * Export folder
  * Export waves

The first one lets you choose a folder that contains Igor binary waves and exports all these waves (**killing all open waves first** , so if you have waves you care about, **save them before running the script!**).

The second one exports all currently open waves into the save folder.

Obviously, you can rename the menu entry and/or place it somewhere else by
editing 'ExportMFP1DMenu.ipf'.

## Usage ##
The exported text files can now be opened by Hooke with the **mfp1dexport** driver activated.

## Troubleshoot ##
  * Usually it's better if you disable the _flatten_ plot manipulator. Just edit hooke.conf and put 0 in the flatten variable value , or type `set flatten 0` at startup. For the same reason, use autopeak with the (new) **noflatten** option