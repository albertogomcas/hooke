# The Hooke backbone #

Hooke is composed of three different types of components. The ﬁrst is the Hooke backbone. The backbone functionality by itself is very limited: it manages the basic
command interpretation, general plot drawing and interaction facilities, a few very basic
commands (like measuring the distance between two points) and other very basic stuff like
loading playlists and conﬁguration ﬁles (see below). The backbone per se is useless as an
application. Its purpose is to create the common infrastructure on top of which functionality is added.

Also, the Hooke backbone is intrinsically modular. It consists of two concurrent threads,the command-line interface (CLI) and the graphical user interface (GUI). The CLI and the GUI are independent programs and communicate by passing messages: this means
that, in principle, one could substitute one or the other if the message passing protocol is kept the same. However, one cannot run without the other. The CLI thread runs in a
command line terminal of the operating system. The GUI consists, as of today, of a simple
window displaying the plot(s). The GUI is however based on the multiplatform and powerful
wxWidgets library, and is therefore already designed to allow sophisticated interfaces
to be built upon this minimal foundation.

Hooke functionality, apart from the bare backbone facilities, is implemented as drivers and plugins. Plugins implement additional functionality, where drivers implement support for input ﬁle formats. Both are coded as completely separate ﬁles. Hooke reads from the conﬁguration ﬁle what plugins and drivers have to be loaded at startup and loads them automatically. The conﬁguration ﬁle is a plain-text XML ﬁle which contains the conﬁgurable variables of the software: these can be easily set by the user with a text editor before the program starts or online when using the program, with the **set** command.

# Plugins #

Plugins are coded as Python classes deﬁning methods encoding CLI commands or GUI
extensions. Plugins act by adding methods to the base Python classes encoding the CLI and the GUI interface, respectively. Each plugin has access to the whole runtime Hooke data structures, including these of other plugins -in this way, plugins can build their functionality upon other plugins. Each plugin is a Python class containing additional
methods and functions that are recognized as commands based on function definition syntax.

Plugins can also deﬁne what we call plot manipulators. These are functions that take a
plot, process it, and transparently return the processed plot. For example, a plot manipulator can automatically apply a ﬁlter on data, every time they are displayed. Several plot manipulators can work in sequence, the output of one being the input to the next. The order in which they are called is deﬁned by the user in the conﬁguration ﬁle.

Plot manipulators usually take advantage of environmental variables (deﬁned again in the conﬁguration ﬁle),that can be modiﬁed online by the user using the **set** command.

A tutorial plugin example is available in the Hooke source distribution.


# Drivers #

Drivers are a bit different, since their main purpose is not to encode additional functionality, but to provide a common interface to different data formats (see Figure 1). Each driver must contain two essential methods. The ﬁrst method, **is\_me()**, allows the data format to be self-identiﬁed. When Hooke meets a new data ﬁle in the playlist, it feeds it, sequentially, to the **is me()** function of each driver, which sees if it can be correctly assigned to that driver. The first driver recognizing the ﬁle format takes control, reads the file and transforms it in data vectors containing the plot informations: these are accessed by Hooke using the method **default\_plots()**. Of course each data format can encode additional information, and consequently each driver can implement additional, custom methods. Since the data structure describing each curve is an instance of the driver class itself, the appropriate plugins can call and use those methods. The advantages of drivers is that a common interface to all data formats is provided, while the Hooke user has no need of previous knowledge of the data type he has to analyze (or to convert it to a custom data type); however the whole interface of the driver -and therefore, in principle, the whole content of the data file- is always available and can be accessed with appropriate plugins, if needed.

Again, a tutorial driver example is available in the Hooke source distribution.