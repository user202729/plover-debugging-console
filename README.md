# plover-debugging-console
A IPython debugging console for Plover.

See also:

* [`plover-run-py` plugin](https://github.com/user202729/plover-run-py) for
executing a Python command with a stroke.

### Usage

* Install the plugin.
* Enable the extension plugin in Plover.
* Run the command `plover-debugging-console-connect` (or `plover -s plover-debugging-console-connect`)
in a terminal.

The global variable `engine` is given. Other objects can be accessed from `engine` as public
or private members.

Alternatively, `plover-debugging-console-connect qtconsole` can be used to launch a console-style application using Qt.
See documentation of `jupyter qtconsole` for more details.

### Note

* Once started, the kernel is not stopped until Plover exits.
* Any `print` commands are printed on Plover's console, not IPython's console.
* On some operating systems, the plugin may set `PAGER` environment variable. (see [issue #2 of `plover-run-shell` repository](https://github.com/user202729/plover_run_shell/issues/2))

### Implementation details

* The kernel can be connected to manually with `ipython console --existing <file>`
or `jupyter console --existing <file>`.
* The IPython/Jupyter connection file path is stored in `connection_path_container`, which is
`plover_debugging_console_path` in the temp folder in the current version.
* `background_zmq_ipython` package is used, which requires `jupyter`
