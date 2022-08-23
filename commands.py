# Reboot Circuitpython into Safe Mode
import microcontroller
microcontroller.on_next_reset(microcontroller.RunMode.SAFE_MODE)
microcontroller.reset()

# Reboot back to normal
import microcontroller
microcontroller.reset()
