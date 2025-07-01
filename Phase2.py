{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "e360b286",
   "metadata": {},
   "source": [
    "# SECULOCK: SMART LOCKER SYSTEM"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "f9c1d09f",
   "metadata": {},
   "source": [
    "This project implements a smart locker security system using Raspberry Pi, Face Recognition, OTP Verification, and Intrusion Detection Mechanisms. The system ensures secure access control by verifying the user's identity through facial recognition using the DeepFace library and the FaceNet model. If face recognition fails, an OTP (One-Time Password) is sent to the owner's registered email for secondary authentication.\n",
    "\n",
    "Additionally, the system incorporates vibration sensors to detect unauthorized access attempts. If a security breach is detected, an alert email with an intruder's photo is sent to the owner, and a buzzer is activated to deter the intruder."
   ]
  },
  {
   "cell_type": "markdown",
   "id": "65a6e909",
   "metadata": {},
   "source": [
    "## Key Features\n",
    "\n",
    "✅ Face Recognition using DeepFace (FaceNet)\n",
    "\n",
    "✅ OTP-based Authentication in case of face mismatch\n",
    "\n",
    "✅ Intrusion Detection with vibration sensors\n",
    "\n",
    "✅ Email Alert with intruder photo for unauthorized access\n",
    "\n",
    "✅ LCD Display for real-time system status updates"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "781093ea",
   "metadata": {},
   "source": [
    "This Jupyter Notebook contains the Python implementation of the SecuLock system, interfacing various hardware components like Raspberry Pi, USB Camera, 16x2 I2C LCD, 4x4 Matrix Keypad, Vibration Sensors, and Relays for real-time security monitoring."
   ]
  },
  {
   "cell_type": "markdown",
   "id": "9ac98957",
   "metadata": {},
   "source": [
    "## Detailed Explanation of Code"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "0bea58c8",
   "metadata": {},
   "source": [
    "### Importing Libraries\n",
    "This section imports all the necessary Python libraries used throughout the project for functionalities like image processing, face recognition, email communication, GPIO pin control, I2C-based LCD interaction, and system cleanup."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f7eeebbd",
   "metadata": {},
   "outputs": [],
   "source": [
    "import json                 # For handling JSON data structures if needed\n",
    "import cv2                  # OpenCV library for image processing and face capture\n",
    "import numpy as np          # Useful for numerical operations (used in image handling)\n",
    "import time                 # Provides delay/timer functions like time.sleep()\n",
    "import smtplib              # For sending emails via SMTP (used for OTP & alerts)\n",
    "import random               # To generate random OTPs\n",
    "import lgpio as GPIO        # Library for GPIO control using lgpio (better for multitasking than RPi.GPIO)\n",
    "import smbus2 as smbus      # For I2C communication with devices like the LCD\n",
    "from deepface import DeepFace    # Face recognition using FaceNet model\n",
    "from email.mime.text import MIMEText              # For plain text email content\n",
    "from email.mime.multipart import MIMEMultipart    # For email with attachments\n",
    "from email.mime.base import MIMEBase              # Base class for attachments\n",
    "from email import encoders                        # For encoding attachments\n",
    "import atexit               # To register cleanup functions on program exit"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "a1433966",
   "metadata": {},
   "source": [
    "### Email Configuration\n",
    "This section sets up the email parameters including SMTP server details, sender and receiver email addresses, authentication password, and the default image used for face verification."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d2b1db05",
   "metadata": {},
   "outputs": [],
   "source": [
    "# SMTP configuration\n",
    "smtp_port = 587  # Port for TLS encryption\n",
    "smtp_server = \"smtp.gmail.com\"  # Gmail's SMTP server\n",
    "\n",
    "# Sender and receiver information\n",
    "email_from = \"smartlockersender@gmail.com\"  \n",
    "email_to = \"owner@gmail.com\" \n",
    "\n",
    "pswd = \"*********\" # App-specific password for the sender email (generated from Google account settings)\n",
    "subject = \"Theft detected !!\"  # Subject of the alert email\n",
    "\n",
    "SOURCE_IMAGE = \"owner.jpeg\"  # Authorized user's reference image\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "789ba13c",
   "metadata": {},
   "source": [
    "### LCD Display Setup\n",
    "This section initializes the I2C communication for a 16x2 LCD display, setting up the necessary parameters such as I2C address, command/data modes, line addresses, and control bits."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c793b590",
   "metadata": {},
   "outputs": [],
   "source": [
    "# I2C address of the LCD\n",
    "I2C_ADDR = 0x27  \n",
    "\n",
    "# Initialize I2C bus (1 indicates /dev/i2c-1 on Raspberry Pi)\n",
    "bus = smbus.SMBus(1)\n",
    "\n",
    "# LCD command/data flags\n",
    "LCD_CHR = 1  # Mode - Sending data to display\n",
    "LCD_CMD = 0  # Mode - Sending command to LCD\n",
    "\n",
    "# LCD RAM addresses for each line\n",
    "LINE_1 = 0x80  # Address of the first line\n",
    "LINE_2 = 0xC0  # Address of the second line\n",
    "\n",
    "# LCD control bits\n",
    "ENABLE = 0b00000100     # Enable bit\n",
    "BACKLIGHT = 0b00001000  # Backlight control bit"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "d0ca8e76",
   "metadata": {},
   "source": [
    "### LCD Control Functions\n",
    "This section defines the core functions needed to operate an I2C-based LCD. It includes sending commands/data, toggling the enable pin, initializing the LCD, and displaying messages."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "65f8dfea",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Sends data or commands to the LCD\n",
    "def lcd_write(bits, mode):\n",
    "    try:\n",
    "        # Extract high and low 4 bits from the byte and add mode & backlight\n",
    "        high_bits = mode | (bits & 0xF0) | BACKLIGHT\n",
    "        low_bits = mode | ((bits << 4) & 0xF0) | BACKLIGHT\n",
    "\n",
    "        # Write high bits to LCD\n",
    "        bus.write_byte(I2C_ADDR, high_bits)\n",
    "        lcd_toggle_enable(high_bits)\n",
    "        time.sleep(0.0005)\n",
    "\n",
    "        # Write low bits to LCD\n",
    "        bus.write_byte(I2C_ADDR, low_bits)\n",
    "        lcd_toggle_enable(low_bits)\n",
    "        time.sleep(0.0005)\n",
    "    except Exception as e:\n",
    "        print(\"LCD write error:\", e)\n",
    "\n",
    "# Triggers the LCD enable pin to latch data\n",
    "def lcd_toggle_enable(bits):\n",
    "    time.sleep(0.0005)\n",
    "    bus.write_byte(I2C_ADDR, bits | ENABLE)     # Set ENABLE high\n",
    "    time.sleep(0.0005)\n",
    "    bus.write_byte(I2C_ADDR, bits & ~ENABLE)    # Set ENABLE low\n",
    "    time.sleep(0.0005)\n",
    "\n",
    "# Initializes the LCD with standard settings\n",
    "def lcd_init():\n",
    "    try:\n",
    "        time.sleep(0.1)  # Wait for power up\n",
    "        lcd_write(0x33, LCD_CMD)  # Initialization\n",
    "        time.sleep(0.005)\n",
    "        lcd_write(0x32, LCD_CMD)  # 4-bit mode\n",
    "        time.sleep(0.005)\n",
    "        lcd_write(0x28, LCD_CMD)  # 2-line display, 5x8 dots\n",
    "        time.sleep(0.005)\n",
    "        lcd_write(0x0C, LCD_CMD)  # Display ON, cursor OFF\n",
    "        time.sleep(0.005)\n",
    "        lcd_write(0x06, LCD_CMD)  # Cursor moves to right\n",
    "        time.sleep(0.005)\n",
    "        lcd_write(0x01, LCD_CMD)  # Clear screen\n",
    "        time.sleep(0.005)\n",
    "    except Exception as e:\n",
    "        print(\"LCD initialization error:\", e)\n",
    "\n",
    "# Displays text on the specified LCD line (LINE_1 or LINE_2)\n",
    "def lcd_display(text, line):\n",
    "    lcd_write(line, LCD_CMD)  # Set line address\n",
    "    for char in text.ljust(16):  # Pad or truncate to 16 characters\n",
    "        lcd_write(ord(char), LCD_CHR)\n",
    "\n",
    "# Initialize the LCD\n",
    "lcd_init()"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "a0417ade",
   "metadata": {},
   "source": [
    "### Email Sending and OTP Generation Functions\n",
    "This section handles sending alert emails with captured intruder images and generating/sending OTPs to the user's registered email."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e0706bca",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Sends an alert email with the captured face image attached\n",
    "def send_emails(email_to):\n",
    "    try:\n",
    "        body = \"Unauthorized access attempt detected.\"  # Email body text\n",
    "\n",
    "        msg = MIMEMultipart()  # Create multipart email container\n",
    "        msg['From'], msg['To'], msg['Subject'] = email_from, email_to, subject  # Set email headers\n",
    "\n",
    "        msg.attach(MIMEText(body, 'plain'))  # Attach plain text body\n",
    "\n",
    "        filename = \"captured_face.jpg\"  # Image to attach\n",
    "        with open(filename, 'rb') as attachment:\n",
    "            attachment_package = MIMEBase('application', 'octet-stream')  # Prepare attachment container\n",
    "            attachment_package.set_payload(attachment.read())  # Read image content\n",
    "            encoders.encode_base64(attachment_package)  # Encode for safe transmission\n",
    "            attachment_package.add_header('Content-Disposition', f\"attachment; filename= {filename}\")  # Attachment header\n",
    "            msg.attach(attachment_package)  # Attach image to email\n",
    "\n",
    "        with smtplib.SMTP(smtp_server, smtp_port) as server:  # Connect to SMTP server\n",
    "            server.starttls()  # Start TLS encryption\n",
    "            server.login(email_from, pswd)  # Login to sender email\n",
    "            server.sendmail(email_from, email_to, msg.as_string())  # Send email\n",
    "            print(f\"Email sent to: {email_to}\")  # Confirm sending\n",
    "\n",
    "    except Exception as e:\n",
    "        print(\"Email sending error:\", e)  # Print error if any\n",
    "\n",
    "\n",
    "# Sends an OTP email without attachments\n",
    "def otp_sent(subject, body):\n",
    "    try:\n",
    "        msg = MIMEText(body)  # Create plain text message\n",
    "        msg['From'], msg['To'], msg['Subject'] = email_from, email_to, subject  # Set headers\n",
    "\n",
    "        with smtplib.SMTP(smtp_server, smtp_port) as server:  # Connect to SMTP server\n",
    "            server.starttls()  # Secure connection\n",
    "            server.login(email_from, pswd)  # Login sender email\n",
    "            server.send_message(msg)  # Send OTP email\n",
    "\n",
    "    except Exception as e:\n",
    "        print(\"Email error:\", e)  # Print error if any\n",
    "\n",
    "\n",
    "# Generates and sends a 6-digit OTP, then returns it\n",
    "def send_otp():\n",
    "    otp = str(random.randint(100000, 999999))  # Generate random 6-digit OTP\n",
    "    otp_sent(\"Your OTP for Verification\", f\"Your OTP is: {otp}\")  # Send OTP email\n",
    "    return otp  # Return OTP string"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "136555d9",
   "metadata": {},
   "source": [
    "### Face Capture and Comparison\n",
    "This section captures a face from a video frame and compares it with a stored source image using the FaceNet model to verify identity."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a1acc29d",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Capture the first detected face from the frame and save it as an image file\n",
    "def capture_face(frame):\n",
    "    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + \"haarcascade_frontalface_default.xml\") # Load face detector\n",
    "    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert frame to grayscale for detection\n",
    "    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))  # Detect faces\n",
    "\n",
    "    if len(faces) > 0:  # If at least one face detected\n",
    "        x, y, w, h = faces[0]  # Get coordinates of first face\n",
    "        face_roi = frame[y:y + h, x:x + w]  # Extract face region from frame\n",
    "        path = \"captured_face.jpg\"  # Define path to save face image\n",
    "        cv2.imwrite(path, face_roi)  # Save face image to disk\n",
    "        return path  # Return saved image path\n",
    "    return None  # Return None if no face detected\n",
    "\n",
    "\n",
    "# Compare the saved face image with the source image using DeepFace FaceNet model\n",
    "def compare_faces(source, captured):\n",
    "    try:\n",
    "        # Verify if two images are of the same person using FaceNet model\n",
    "        result = DeepFace.verify(img1_path=source, img2_path=captured, model_name=\"FaceNet\", enforce_detection=True)\n",
    "        return result.get('verified', False)  # Return True if verified, else False\n",
    "    except Exception as e:\n",
    "        print(\"Face comparison error:\", e)  # Print error if comparison fails\n",
    "        return False  # Return False on error"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "81ab3e4d",
   "metadata": {},
   "source": [
    "### GPIO Setup and Cleanup\n",
    "This section initializes the GPIO chip for controlling hardware pins and ensures resources are properly released when the program exits."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f71a4183",
   "metadata": {},
   "outputs": [],
   "source": [
    "chip = GPIO.gpiochip_open(0)  # Open GPIO chip 0 for pin control\n",
    "\n",
    "def cleanup():\n",
    "    print(\"Releasing GPIO resources...\")  \n",
    "    GPIO.gpiochip_close(chip)  # Close GPIO chip to free resources\n",
    "\n",
    "atexit.register(cleanup)  # Register cleanup() to run automatically on program exit"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "96bec353",
   "metadata": {},
   "source": [
    "### Keypad Initialization and Reading\n",
    "This section configures GPIO pins for a 4x4 keypad matrix and defines a function to detect which key is pressed by scanning rows and columns."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f5c7b4b0",
   "metadata": {},
   "outputs": [],
   "source": [
    "ROWS = [17, 27, 22, 10]  # GPIO pins connected to keypad rows\n",
    "COLS = [9, 11, 5, 6]     # GPIO pins connected to keypad columns\n",
    "\n",
    "KEYPAD = [               # Key layout corresponding to rows and columns\n",
    "    ['1', '2', '3', 'A'],\n",
    "    ['4', '5', '6', 'B'],\n",
    "    ['7', '8', '9', 'C'],\n",
    "    ['*', '0', '#', 'D']\n",
    "]\n",
    "\n",
    "# Configure row pins as outputs (initially HIGH)\n",
    "for row in ROWS:\n",
    "    GPIO.gpio_claim_output(chip, row, 1)  # Claim output with initial HIGH\n",
    "\n",
    "# Configure column pins as inputs with pull-up resistors\n",
    "for col in COLS:\n",
    "    GPIO.gpio_claim_input(chip, col, GPIO.SET_PULL_UP)  # Claim input with pull-up\n",
    "\n",
    "def read_keypad():\n",
    "    for row_index, row_pin in enumerate(ROWS):\n",
    "        GPIO.gpio_write(chip, row_pin, 0)  # Set current row LOW to detect key press\n",
    "        for col_index, col_pin in enumerate(COLS):\n",
    "            if GPIO.gpio_read(chip, col_pin) == 0:  # If column reads LOW, key pressed\n",
    "                time.sleep(0.2)  # Debounce delay to avoid multiple detections\n",
    "                GPIO.gpio_write(chip, row_pin, 1)  # Reset row to HIGH\n",
    "                return KEYPAD[row_index][col_index]  # Return pressed key character\n",
    "        GPIO.gpio_write(chip, row_pin, 1)  # Reset row to HIGH if no key press detected\n",
    "    return None  # Return None if no key pressed"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "b0dcac77",
   "metadata": {},
   "source": [
    "### GPIO Pin Initialization for Relays and Sensors\n",
    "This section sets up GPIO pins for controlling the relay (lock and buzzer) as outputs and for reading vibration sensors as inputs with pull-up resistors."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b86c4f0e",
   "metadata": {},
   "outputs": [],
   "source": [
    "RELAY_LOCK_PIN, RELAY_BUZZER_PIN = 26, 19  # GPIO pins for lock relay and buzzer relay\n",
    "VIBRATION_SENSOR_1 = 23  # GPIO pin connected to Vibration Sensor 1\n",
    "VIBRATION_SENSOR_2 = 24  # GPIO pin connected to Vibration Sensor 2\n",
    "\n",
    "# Configure vibration sensors as input with pull-up resistors\n",
    "GPIO.gpio_claim_input(chip, VIBRATION_SENSOR_1, GPIO.SET_PULL_UP)  # Vibration Sensor 1 input\n",
    "GPIO.gpio_claim_input(chip, VIBRATION_SENSOR_2, GPIO.SET_PULL_UP)  # Vibration Sensor 2 input\n",
    "\n",
    "# Configure relay pins as output and set initial value to HIGH (1)\n",
    "GPIO.gpio_claim_output(chip, RELAY_LOCK_PIN, 1)    # Lock relay output pin\n",
    "GPIO.gpio_claim_output(chip, RELAY_BUZZER_PIN, 1)  # Buzzer relay output pin"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "c17cc6d4",
   "metadata": {},
   "source": [
    "### Buzzer Control and Vibration Sensor Monitoring\n",
    "This section defines functions to activate the buzzer for a specified duration and to monitor vibration sensors. If any sensor detects vibration (active low), the buzzer is triggered and an alert email is sent."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2a2be86e",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Activate the buzzer for a given duration (default 5 seconds)\n",
    "def trigger_buzzer(duration=5):\n",
    "    GPIO.gpio_write(chip, RELAY_BUZZER_PIN, 0)  # Turn buzzer ON (active low)\n",
    "    time.sleep(duration)                         # Wait for specified duration\n",
    "    GPIO.gpio_write(chip, RELAY_BUZZER_PIN, 1)  # Turn buzzer OFF\n",
    "\n",
    "# Monitor vibration sensors and respond if triggered\n",
    "def vibra():\n",
    "    sensor_1_state = GPIO.gpio_read(chip, VIBRATION_SENSOR_1)  # Read vibration sensor 1\n",
    "    sensor_2_state = GPIO.gpio_read(chip, VIBRATION_SENSOR_2)  # Read vibration sensor 2\n",
    "\n",
    "    if sensor_1_state == 0 or sensor_2_state == 0:             # If any sensor is activated (LOW)\n",
    "        trigger_buzzer()                                       # Activate buzzer alert\n",
    "        otp_sent(\"Theft Detected\", \"Vibration sensors activated\")  # Send theft alert email\n",
    "        time.sleep(0.1)                                        # Short delay to debounce/smooth sensor reading"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "1139044e",
   "metadata": {},
   "source": [
    "### I2C Bus Reset Function\n",
    "This function attempts to reset the I2C communication bus by closing and reopening it, helping to recover from any communication errors."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c1bc002e",
   "metadata": {},
   "outputs": [],
   "source": [
    "def reset_i2c():\n",
    "    try:\n",
    "        bus = smbus.SMBus(1)    # Open I2C bus 1\n",
    "        bus.close()             # Close the bus to reset connection\n",
    "        time.sleep(1)           # Wait for 1 second before reopening\n",
    "        bus = smbus.SMBus(1)    # Reopen the I2C bus\n",
    "
