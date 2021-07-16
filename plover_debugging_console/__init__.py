from background_zmq_ipython import init_ipython_kernel, IPythonBackgroundKernelWrapper  # type: ignore
import tempfile
from typing import Optional
from pathlib import Path
import logging


connection_path_container=Path(tempfile.gettempdir())/"plover_debugging_console_path"


class Main:
	def __init__(self, engine)->None:
		self._engine=engine
		self._kernel_wrapper: Optional[IPythonBackgroundKernelWrapper]=None

	def start(self)->None:
		logging.getLogger("plover").propagate=False
		logging.getLogger("plover-strokes").propagate=False
		# tornado package calls logging.basicConfig() which creates a logger at the root level
		# this makes the behavior better match Plover's default (not log)
		if self._kernel_wrapper is None:
			self._kernel_wrapper=init_ipython_kernel(user_ns={
				"engine": self._engine
				},
				logger=logging.Logger("IPython", level=logging.INFO)
				# no handler
				# otherwise it will print "To connect another client to this IPython kernel" ...
				)
		connection_path_container.write_text(self._kernel_wrapper.connection_filename)

	def stop(self)->None:
		connection_path_container.unlink()


def connect():
	import subprocess
	import argparse
	parser=argparse.ArgumentParser(usage="Connect to existing Plover debugging console kernel.")
	parser.add_argument("command", nargs="?", choices=["qtconsole", "console"], default="console")
	args=parser.parse_args()
	subprocess.run([
		"jupyter",
		args.command,
		"--existing",
		connection_path_container.read_text()
		])
