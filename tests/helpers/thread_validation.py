import threading


def verify_all_threads_closed(allowable_threads=None):
	"""Verify that all threads have been closed, aside from allowable threads.

	Borrowed this function from the test helper functions in this repo:
	https://github.com/opencv/open_vision_capsules
	:return:
	"""
	allowable_threads = allowable_threads or []
	allowable_threads += ['pydevd.Writer',
						  'pydevd.Reader',
						  'pydevd.CommandThread',
						  'profiler.Reader',
						  'MainThread']

	open_threads = [t.name for t in threading.enumerate()
					if t.name not in allowable_threads]

	if len(open_threads) != 0:
		raise EnvironmentError(
			"Not all threads were shut down! Currently running threads: "
			+ str(open_threads))
