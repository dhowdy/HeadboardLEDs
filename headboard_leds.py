#!/usr/bin/python
# this script turns on leds for bed when motion is detected between dusk and dawn

import time
import RPi.GPIO as GPIO
from neopixel import *
import pytz
import astral
import datetime
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler

GPIO.setmode(GPIO.BCM)

# Construct our location. Name, Country, Lat, Long, TZ, Elevation(M)
rolla = astral.Location(info=("Rolla", "USA", 37.948544, -91.771530, "US/Central", 342))

# Define our twilight type
rolla.solar_depression = "civil"

# Define our timezone for comparison
central = pytz.timezone('US/Central')

# Global variables necessary for interrupts to interact with the main program.
runLoop = 1
debug = 0
stripStatus = 0

# Define our interrupt functions
def button_on(channel):
   global runLoop
   global stripStatus
   runLoop = 0
   print "The on button has been pressed. Turning LEDs on."
   colorWipe(strip, Color(0, 255, 0), 200.0)
   print "on"
   runLoop = 1
   stripStatus = 1

def button_off(channel):
   global runLoop
   global stripStatus
   runLoop = 0
   print "The off button has been pressed. Turning LEDs off."
   colorWipe(strip, Color(0, 0, 0), 200.0)
   print "off"
   runLoop = 1
   stripStatus = 0



# LED strip configuration:
LED_COUNT      = 148      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, speed, wait_ms=.1):
   """Wipe color across display a pixel at a time."""
   for i in range(strip.numPixels()):
      strip.setPixelColor(i, color)
      strip.show()
 # Removing the sleep so this goes as fast as possible. May add it back later.
 #     time.sleep(wait_ms/speed)


# Function that fades the LEDs on
def fadeLEDs(status): # G R B
   if status == "on" and runLoop ==1:
      fadeLoop = 0
      ledSpeed = 0
      print "turning LEDs on."
      # Start at 0 and work our way up to turn on.
      while fadeLoop < 256 and runLoop == 1:
         colorWipe(strip, Color(int(round(fadeLoop * 0)), fadeLoop, int(round(fadeLoop * 0))), ledSpeed)
         fadeLoop += 15

   elif status == "off" and runLoop == 1:
      fadeLoop = 255
      ledSpeed = 0
      print "turning LEDs off."
      # Start at 255 and work our way down to turn off.
      while fadeLoop > 0 and runLoop == 1:
         colorWipe(strip, Color(int(round(fadeLoop * 0)), fadeLoop, int(round(fadeLoop * 0))), ledSpeed)
         fadeLoop -= 10
      colorWipe(strip, Color(0, 0, 0), ledSpeed)

   else:
      print "Invalid status passed to fadeLEDs() or runLoop is disabled when it should not be."
      exit(1)


HOST_NAME = "0.0.0.0"
HOST_PORT = 8080

class HttpServer(SimpleHTTPRequestHandler):
            
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        # Check For URL Stream "http://IPADDRESS/command?"
            
        if "/command?" in self.path:
            self._set_headers()
            junk,command = self.path.split("?")

            # Hack for Chrome reloading the same page
            redir = str("<html><head><meta http-equiv='refresh' content='3;url=.\' /></head><body><h1>Command received! <br>"+command+"</h1></body></html>")
            print(redir)

            self.wfile.write(redir.encode())
            self.command(str(notification))
            return
        
        else:
            SimpleHTTPRequestHandler.do_GET(self)
   
def command(self, notification):
        if command == "":
            notification = "No command"
              
        print("Command received.")

        ip_add = s.getsockname()[0]
        print (ip_add)
        s.close()
        self.Cast(ip_add)
        return



   # POST is for submitting data
    def do_POST(self):

        print( "incomming http: ", self.path )

        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        self.send_response(200)
    

httpServer = HTTPServer((HOST_NAME, HOST_PORT), HttpServer) #HTTP Server Stuff (Python Librarys)
print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, HOST_PORT))



try:
    httpServer.serve_forever()
except KeyboardInterrupt:
    pass

if __name__ == '__main__':
   runLoop = 1      #Enable loops to run


   stripStatus = 0  #Strip is off on startup

   # Create NeoPixel object with appropriate configuration.
   strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
   # Intialize the library (must be called once before other functions).
   strip.begin()

   print "turning strip off"
   colorWipe(strip, Color(0, 0, 0), 2000.0)

   waiting_sec = 0 # Initialize the variable


   while True:               # G, R, B



         # Get the date and current time.
         today = datetime.date.today()
         now = datetime.datetime.now(central)

         # Get our twilight info from Astral
         sun = rolla.sun(date=today)

         # Compare the current time to Astral's data (or if Debug mode is enabled)
         if now >= sun['dusk'] or now <= sun['dawn'] or debug == 1:
            print "It is dark out or debug mode is on."
            # Reset our counter
            waiting_sec = 0

            if stripStatus == 0:
               print "turning strip on"
               fadeLEDs("on")
               stripStatus = 1

         else:
            print "it is light out"

         time.sleep(sleep_sec)

      else:
         print "no motion detected in " + str(waiting_sec) + " seconds."
         waiting_sec += 1
         time.sleep(sleep_sec)


      if waiting_sec > time_on and stripStatus == 1 and runLoop == 1:
         stripStatus = 0
         print "turning strip off via fadeLEDs"
         fadeLEDs("off")
