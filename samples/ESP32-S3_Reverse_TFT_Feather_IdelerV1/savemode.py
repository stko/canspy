import microcontroller
import supervisor

if supervisor.runtime.safe_mode_reason != USER:
	microcontroller.reset()
