# plover-debugging-console
A IPython debugging console for Plover.

See also:

* [`plover-run-py` plugin](https://github.com/user202729/plover-run-py) for
executing a Python command with a stroke, or from the command-line.

### Usage

* Install the plugin.
* Enable the extension plugin in Plover.
* Run the command `plover-debugging-console-connect` (or `plover -s plover-debugging-console-connect`)
in a terminal.

The global variable `engine` is given. Other objects can be accessed from `engine` as public
or private members.

Alternatively, `plover-debugging-console-connect qtconsole` can be used to launch a console-style application using Qt.
See documentation of `jupyter qtconsole` for more details.

Or `plover-debugging-console-execute` can be used to execute a file non-interactively. See note below.

### Note

* Once started, the kernel is not stopped until Plover exits.
* The session (kernel, global variables) are persistent, and shared between consoles.
  
  However, `plover-debugging-console-execute <file>` uses a separate environment, see
  documentation of `%run` IPython magic command.
* Any `print` commands are printed on Plover's console, not IPython's console.
* Error messages might be hidden (if `plover-debugging-console-execute` is used),
  or displayed in a different console.

  To view the error messages, open an interactive console.
* On some operating systems, the plugin may set `PAGER` environment variable. (see [issue #2 of `plover-run-shell` repository](https://github.com/user202729/plover_run_shell/issues/2))

### Implementation details

* The kernel can be connected to manually with `ipython console --existing <file>`
or `jupyter console --existing <file>`.
* The IPython/Jupyter connection file path is stored in `connection_path_container`, which is
`plover_debugging_console_path` in the temp folder in the current version.
* `background_zmq_ipython` package is used, which requires `jupyter`
* Regarding `PAGER`, `GIT_PAGER`, `TERM`, `CLICOLOR` environment variables being set: Either
   * unset/reset them manually, or
   * update to a sufficiently new version of package `background-zmq-ipython`, at least commit [14d862848b7f5692412093642181718c29f57cad](https://github.com/albertz/background-zmq-ipython/commit/14d862848b7f5692412093642181718c29f57cad).
   (version currently not on PyPI)
* See https://stackoverflow.com/a/68769973/5267751 for the method used in `plover-debugging-console-execute`.
