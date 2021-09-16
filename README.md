# Speedy - Fast programming of Nordic nRF52840 dongles
## Summary
This is a relatively simple python program offering a GUI using PySimpleGui to front-end the command line applications provided by Nordic Semiconductor to program their nRF52840 dongles. It does nothing that you cannot do with those programs if you are a specialist. This program is to permit many (thousands?) of dongles to be programmed with non-secure binaries at the fastest rate which can be achieved by hand. At the moment it has been tested with a single USB port in use. Once set up, any dongle plugged in which is in bootloader mode will be programmed at the push of a button or, if the "auto" button has been set to "on", will be programmed immediately. As soon as the programming is complete the program searches for any other dongle plugged in and will program that immediately and so on. Although untested at speed, if a computer has 3 usb ports and the user is sufficiently alert, as fast as the dongles can be plugged in and unplugged, they will be programmed. Speedy was constructed for speed of programming the dongles by poorly trained staff. If you are a computer whizzo, you don't really need it. It is only practical for one person programming at any one time per computer.

On the other hand, there is no hand-holding in it's set up which is not very flexible in this version. You get the .py file and a configuration .json file and are told where to put them. Also the hex file has to be installed in a .zip file, renames as .piz and put where you are told to put it. The program is supposed to be easy to use, not easy to set up.

Speedy provides a log of the user name doing the programming, the time of each programming and the internal ID of the dongle programmed.
## Dependencies
Speedy requires nrfutil from Nordic. The version tested was 6.1.0. This must be installed and usable by the person doing the programming. The command line should be tested by programming a dongle prior to the use of Speedy.

Python 3.8 is required. Ensure that typing "python` returns it's version string higher than 3.8. Then type exit()<ret> to escape.
 
PySimpleGUI must be installed into the Python infrastructure.  Use pip list|grep PySimpleGUI to ensure that a version of PySimpleGUI greater than 4.46 is present.
## Installation

 Create a directory in the users home directory called `speedy`. Copy speedy.json into that directory. Create a directory called `uploads` in the directory `speedy`. Copy what .piz files you need to program into the `speedy/uploads` directory. Sorry about it all being fixed places...
 
 Put speedy.py anywhere that the user can access e.g. on the desktop. chmod +x speedy.py on a command line. Double click and the program will run. If it fails then call it from a command line e.g. ./speedy.py and consider what python tells you about missing or failing libraries.
 
 ## Operation
 A GUI should spring to life courtesy of PySimpleGUI (look it up on Github). It should be pretty obvious. Pick a file in the top left box (or if there is only one in the `speedy/uploads` directory, it will be already chosen), then wait for an announcement in the second box down on the left about having found a dongle. If you have plugged one in and it hasn't been found, then you probably need to push the hidden button to put it into bootloader mode. When the second button down tells you it has found a dongle, press it and the dongle will be programmed. Look at the 4th button down; it will tell you when it is safe to remove the dongle. If the "auto" button is pressed, as soon as a dongle is found, it will be programmed. No need to touch a mouse, just plug and unplug dongles. You should be able to figure out what the right hand column is for.
 
 In the directory `speedy`a log file `speedy_dongle_logfile` will be created at first run of the program, then have later logs appended. Move the file when it gets too big.
 Don't try to enlarge the GUI, you won't get any satisfaction. If you wish not to see the logs, drag it from the right.
 
 ## Fiddling
 It is possible to make some adjustments (at your own risk). The current .json file looks like:
 ```
 {
  "speedy_config" : {
    "header" :
    {
       "program_announce" : "Speedy2 Nordic nRF52840 Dongle Programmer"
    },
    "left_column" :
    {
      "font" : [ "FreeMono",28,"bold"],
      "width_in_chars" : 18,
      "file_select_button" :
      {
        "announce_no_file" : "choose file\nto upload",
        "announce_file" : "current file=\n***\npush to change"
      }
    },
    "right_column" : {
      "header_text" : "Below a record of activity, also in the log",
      "font" : [ "Yrsa",20,"bold"],
      "width_in_chars" : 55,
      "number_of_lines" : 16
    }
  }
}
 ```
 It is strongly suggested to keep the orginal safe but you can fiddle with things like the typeface and font sizes - these determine the overall size of the GUI so for persons of limited eyesight or attempting to use it on a micro-monitory, you might like to adjust them. Change **nothing** to the left of the colon on each line or bad things will happen. Changing the number of lines is likely to screw up the layout of the GUI. Any other fiddling will have to be done in the program.
