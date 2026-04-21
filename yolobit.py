from yolobit import *
button_a.on_pressed = None
button_b.on_pressed = None
button_a.on_pressed_ab = button_b.on_pressed_ab = -1
from aiot_lcd1602 import LCD1602
from aiot_rgbled import RGBLed
import time
import sys
import uselect
import music

aiot_lcd1602 = LCD1602()

# Mô tả hàm này...
def Sensor2():
  global globalLight, th_C3_B4ng_tin, led, aiot_lcd1602, tiny_rgb
  globalLight = round(translate((pin0.read_analog()), 0, 4095, 0, 100))
  aiot_lcd1602.move_to(0, 0)
  aiot_lcd1602.putstr(('Ambient: ' + str(globalLight)))

tiny_rgb = RGBLed(pin1.pin, 4)

# Mô tả hàm này...
def LED2():
  global globalLight, th_C3_B4ng_tin, led, aiot_lcd1602, tiny_rgb
  if globalLight <= 25:
    tiny_rgb.show(0, hex_to_rgb('#ffffff'))
    aiot_lcd1602.move_to(0, 1)
    aiot_lcd1602.putstr('Light: 100%')
    led = 'Lights: 100'
  else:
    if globalLight <= 50:
      tiny_rgb.show(4, hex_to_rgb('#000000'))
      tiny_rgb.show(1, hex_to_rgb('#ffffff'))
      tiny_rgb.show(2, hex_to_rgb('#ffffff'))
      tiny_rgb.show(3, hex_to_rgb('#ffffff'))
      aiot_lcd1602.move_to(0, 1)
      aiot_lcd1602.putstr('Light:  75%')
      led = 'Lights: 75'
    else:
      if globalLight <= 65:
        tiny_rgb.show(3, hex_to_rgb('#000000'))
        tiny_rgb.show(4, hex_to_rgb('#000000'))
        tiny_rgb.show(1, hex_to_rgb('#ffffff'))
        tiny_rgb.show(2, hex_to_rgb('#ffffff'))
        aiot_lcd1602.move_to(0, 1)
        aiot_lcd1602.putstr('Light:  50%')
        led = 'Lights: 50'
      else:
        if globalLight <= 80:
          tiny_rgb.show(2, hex_to_rgb('#000000'))
          tiny_rgb.show(3, hex_to_rgb('#000000'))
          tiny_rgb.show(4, hex_to_rgb('#000000'))
          tiny_rgb.show(1, hex_to_rgb('#ffffff'))
          aiot_lcd1602.move_to(0, 1)
          aiot_lcd1602.putstr('Light:  25%')
          led = 'Lights: 25'
        else:
          tiny_rgb.show(0, hex_to_rgb('#000000'))
          aiot_lcd1602.move_to(0, 1)
          aiot_lcd1602.putstr('Light:   0%')
          led = 'Lights: 0'

def read_terminal_input():
  spoll=uselect.poll()        # Set up an input polling object.
  spoll.register(sys.stdin, uselect.POLLIN)    # Register polling object.

  input = ''
  if spoll.poll(0):
    input = sys.stdin.read(1)

    while spoll.poll(0):
      input = input + sys.stdin.read(1)

  spoll.unregister(sys.stdin)
  return input

# Mô tả hàm này...
def Emote_and_buzzer2():
  global globalLight, th_C3_B4ng_tin, led, aiot_lcd1602, tiny_rgb
  if th_C3_B4ng_tin == '0':
    display.show(Image.CONFUSED)
    music.stop()
  else:
    if th_C3_B4ng_tin == '1':
      display.show(Image("00000:04040:00000:40004:04440"))
      music.stop()
    else:
      if th_C3_B4ng_tin == '2':
        display.show(Image.SAD)
        for count in range(3):
          music.pitch(550, 700)

if True:
  globalLight = 0
  led = 0
  aiot_lcd1602.move_to(0, 0)
  aiot_lcd1602.putstr('Hello')
  display.show(Image.ASLEEP)
  print('Hello!')
  time.sleep_ms(2000)
  tiny_rgb.show(0, hex_to_rgb('#000000'))

while True:
  Sensor2()
  th_C3_B4ng_tin = read_terminal_input()
  LED2()
  Emote_and_buzzer2()
  print((str(led) + str('   Ambient: ' + str(globalLight))))
  time.sleep_ms(1000)
  time.sleep_ms(10)
