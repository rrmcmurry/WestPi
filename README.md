# Team 9668 - West Robotics

**West High School**  
Knoxville, TN

---

## Overview

This repository contains the Raspberry Pi coprocessor code for our test robots. The RoboRIO code is maintained in a [separate repository](https://github.com/rrmcmurry/9668_Swerve/).

The overall idea here is that the RoboRIO is essentially a remote control car with two drivers. There is the driver at the driver station... and there is the raspberry pi 4 running this application, 
acting like another driver. If you look in our robot code in the [separate repository](https://github.com/rrmcmurry/9668_Swerve/), you'll see that we have created a simulation of an XBox controller 
in NetworkTables and the robot just looks at the networkcontroller values and responds like it would if it received the same values from the actual XBox controller and the actual driver. 

This creates a nice separation of concerns between the robot that handles the hardware and the coprocessor that handles the game logic.





## Repository Structure

- `/`: Contains the current version of the raspberry pi code that can be uploaded and run on WPILibPi as an application
- `/WestPi.py`: This is the main executable application.  All other python classes should be uploaded using the file upload.
- `/Archive`: Contains earlier versions of the raspberry pi code that could be uploaded and run on WPILibPi as an application
- `/ComputerPythonExamples`: Contains test python code that can be run in Python from windows to test OpenCV and apriltag detection
- `/Raspberrypi WPILib imag`: Locally contains copies of the Raspberrypi images obtained from the [WPILibPi repository](https://github.com/wpilibsuite/WPILibPi/releases). 
These files are not uploaded to github to save space. We are currently using the 2024.1.1 Beta version of WPILibPi.

## Getting Involved

This repository is maintained by **Robby McMurry**, a robotics mentor who is diving into the world of robotics with a passion to learn.

Feel free to contribute or raise issues as we continuously improve our robot's performance!

---

*Special thanks to West High School and all team members for their dedication to the project.*

