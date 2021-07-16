# plover-debugging-console
A IPython debugging console for Plover.

### Usage

* Install the plugin.
* Enable the extension plugin in Plover.
* Run the command `plover-debugging-console-connect` (or `plover -s plover-debugging-console-connect`)
in a terminal.

The global variable `engine` is given. Other objects can be accessed from `engine` as public
or private members.

### Note

* Once started, the kernel is not stopped until Plover exits.
* Any `print` commands are printed on Plover's console, not IPython's console.

### Implementation details

* The kernel can be connected to manually with `ipython console --existing <file>`
or `jupyter console --existing <file>`.
* The IPython/Jupyter connection file path is stored in `connection_path_container`, which is
`plover_debugging_console_path` in the temp folder in the current version.
* `background_zmq_ipython` package is used, which requires `jupyter`
