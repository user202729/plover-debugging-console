import tempfile
from typing import Optional
from pathlib import Path
import logging


connection_path_container=Path(tempfile.gettempdir())/"plover_debugging_console_path"


class Main:
	def __init__(self, engine)->None:
		from background_zmq_ipython import IPythonBackgroundKernelWrapper  # type: ignore
		self._engine=engine
		self._kernel_wrapper: Optional[IPythonBackgroundKernelWrapper]=None

	def start(self)->None:
		from background_zmq_ipython import init_ipython_kernel  # type: ignore
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


def connect()->None:
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


def execute()->None:
	import argparse
	parser=argparse.ArgumentParser(usage="Execute Python code in the existing Plover debugging console kernel.")

	parser.add_argument("-s", "--set-args", action="store",
			default="",
			help="Where to store the command-line arguments for --command.")
	parser.add_argument("-c", "--command", action="store", help="Command to execute. "
			"If provided together with `file` argument, this will be put first. "
			"This is run before the redirection.")
	parser.add_argument("--suppress-newline", action="store_true",
			help="Suppress inserted newline at the end of command, if --command is provided.")

	parser.add_argument("--redirect-streams", action="store_true", default=True,
			help="Redirect stdout/stderr for file execution. Does not affect thrown errors.")
	parser.add_argument("--no-redirect-streams", action="store_false", dest="redirect_streams")
	parser.add_argument("file",
			help="File to execute. If empty, no file will be executed.")
	parser.add_argument("args", nargs="*",
			help="Arguments. See --set-args. For file execution it's stored in sys.argv.")
	args=parser.parse_args()

	if args.redirect_streams: assert args.file, "--redirect-streams requires --file"

	from jupyter_client.manager import KernelManager  # type: ignore
	manager=KernelManager(connection_file=connection_path_container.read_text())
	manager.load_connection_file()

	command=""

	escape_dict=str.maketrans({
			x: '\\'+x for x in r'\"'
			})  # type: ignore

	if args.command:
		if args.set_args:
			if args.set_args.startswith("sys."):
				command+="import sys\n"
			command+=f"{args.set_args}={args.args!r}\n"
		command+=args.command
		if not args.suppress_newline:
			command+='\n'

	if args.file:
		file_=Path(args.file).absolute()
		assert file_.is_file()
		command_escaped: str=' '.join(
				'"' + x.translate(escape_dict) + '"'
				for x in
				[str(file_)] + args.args
				)
		if args.redirect_streams:
			from multiprocessing.connection import Listener
			import random
			key=bytes((random.randint(0, 255) for _ in range(16)))
			
			for attempt_left in range(10-1, -1, -1):
				port=random.randint(4096, 8192)
				if port in (5000, 8000, 8080): continue  # exclude some common ports
				address=("127.0.0.1", port)
				try:
					listener=Listener(address, "AF_INET", authkey=key)
				except OSError:
					if attempt_left==0: raise
					continue
				break

			command+=f'''\
try:
	# set up stdout/stderr redirection
	import sys
	import io
	sys.stdout=io.StringIO()
	sys.stderr=io.StringIO()

	%run {command_escaped}
finally:
	# send the data
	from multiprocessing.connection import Client
	connection=Client({address!r}, "AF_INET", authkey={key!r})
	connection.send((sys.stdout.getvalue(), sys.stderr.getvalue()))
	connection.close()

	# restore stdout
	sys.stdout=sys.__stdout__
'''
		else:
			command+=f'%run {command_escaped}'

	manager.client().execute(command)

	if args.redirect_streams:
		import sys
		stdout_content, stderr_content=listener.accept().recv()
		sys.stdout.write(stdout_content)
		sys.stderr.write(stderr_content)
