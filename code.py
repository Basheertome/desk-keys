#  ----- Imports -----  #
import time
import board
import usb_hid
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
import adafruit_led_animation.color as color
import neopixel
import rotaryio

#  ----- Lil' fix for race conditions -----  #
time.sleep(1)

#  ----- Keyboard setup -----  #
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)
cc = ConsumerControl(usb_hid.devices)

#  ----- Key setup -----  #
keys_out = [
	[Keycode.GUI, Keycode.OPTION, Keycode.POWER], # Lock computer
	ConsumerControlCode.PLAY_PAUSE, # Play / Pause
	[Keycode.GUI, Keycode.CONTROL, Keycode.OPTION, Keycode.SHIFT, Keycode.D], # Toggle Do Not Disturb
	[Keycode.GUI, Keycode.SHIFT, Keycode.D], # Toggle Mic
	[Keycode.GUI, Keycode.SHIFT, Keycode.E]] # Toggle Camera

keys_in = [
	DigitalInOut(board.GP1),
	DigitalInOut(board.GP2),
	DigitalInOut(board.GP3),
	DigitalInOut(board.GP4),
	DigitalInOut(board.GP5)]
for key in keys_in:
	key.pull = Pull.UP
keys = [
	Debouncer(keys_in[0]),
	Debouncer(keys_in[1]),
	Debouncer(keys_in[2]),
	Debouncer(keys_in[3]),
	Debouncer(keys_in[4])]

# ----- Colors ----- #
# Available:
# 	RED, YELLOW, ORANGE, GREEN, TEAL, CYAN, BLUE, PURPLE, MAGENTA,
# 	WHITE, BLACK, GOLD, PINK, AQUA, JADE, AMBER, OLD_LACE
colors = [
	color.WHITE,
	color.AQUA,
	color.PURPLE,
	color.RED,
	color.GREEN]

# ----- NeoPixel setup ----- #
pixels = neopixel.NeoPixel(board.GP0, 5, brightness=0.15)
pixels.fill(color.BLACK)

# ----- Rotary encoder setup ----- #
encoder_button = DigitalInOut(board.GP6)
encoder_button.direction = Direction.INPUT
encoder_button.pull = Pull.UP
encoder_button_last = encoder_button.value

encoder = rotaryio.IncrementalEncoder(board.GP7, board.GP8)
encoder_last = 0

# ----- Main loop ----- #
while True:
	# Keyboard Keys Subloop
	for index, key in enumerate(keys):
		key.update()
		if key.fell:
			if type(keys_out[index]) == list:
				for output in keys_out[index]:
					keyboard.press(output)
			else:
				cc.send(keys_out[index])
			pixels[index] = colors[index]
		if key.rose:
			if type(keys_out[index]) == list:
				for output in keys_out[index]:
					keyboard.release(output)
			pixels[index] = color.BLACK

	# Encoder Button Subloop
	encoder_state = encoder_button.value
	if encoder_state != encoder_button_last:
		if not encoder_state:
			cc.send(ConsumerControlCode.MUTE) # Audio Mute / Unmute
		else:
			pass
	encoder_button_last = encoder_state

	# Encoder Turn Subloop
	encoder_position = encoder.position
	if encoder_position > encoder_last:
		cc.send(ConsumerControlCode.VOLUME_INCREMENT) # Increase Volume
	elif encoder_position < encoder_last:
		cc.send(ConsumerControlCode.VOLUME_DECREMENT) # Decrease Volume
	encoder_last = encoder_position
