{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "bf41ab89",
   "metadata": {},
   "source": [
    "# Smart Locker with Intruder Alerts \n",
    "\n",
    "This project aims to simulate a smart locker system with intruder alerts using Proteus, VSPE, and Python. The system detects authorized and unauthorized users through face recognition and sends email alert with intruder image if unauthorized access is attempted.\n",
    "\n",
    "## Project Components:\n",
    "1. **Proteus Simulation**: Simulates the smart locker hardware setup.\n",
    "\n",
    "\n",
    "2. **VSPE (Virtual Serial Port Emulator)**: Configures serial communication on COM1, enabling data exchange between Proteus and Python.\n",
    "\n",
    "\n",
    "3. **Python Code**: Processes serial data, performs face recognition using the DeepFace library, and sends email alerts when unauthorized access is detected.\n",
    "\n",
    "\n",
    "\n",
    "## Setup Instructions:\n",
    "\n",
    "1. **Run the Simulation in Proteus**\n",
    "   - Start the Proteus simulation for the smart locker system. This simulation includes components for face detection and access control, which will interact with the Python script.\n",
    "   - Ensure that the simulation is active before proceeding, as the code depends on the simulated environment to function correctly.\n",
    "   \n",
    "\n",
    "\n",
    "\n",
    "2. **Configure VSPE for COM1**\n",
    "   - Use the Virtual Serial Port Emulator (VSPE) to configure COM1 for serial communication.\n",
    "   - This setup links the Proteus simulation to the Python code, allowing the Python script to send and receive signals from the simulated locker system.\n",
    "   \n",
    "  \n",
    "  \n",
    "\n",
    "3. **Run the Python Code**\n",
    "   - With Proteus and VSPE running, execute the Python code.\n",
    "   - The code listens for signals from COM1, processes face recognition,control the access control through Proteus simulation and sends an email alert with intruder image if an unauthorized face is detected."
   ]
  },
  {
   "cell_type": "markdown",
   "id": "41268623",
   "metadata": {},
   "source": [
    "## Detailed Expanation of Code"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "edc97ad1",
   "metadata": {},
   "source": [
    "## Importing necessary modules\n",
    "\n",
    "Importing necessary modules for email sending, serial communication, file handling, and DeepFace"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e7fd8d29",
   "metadata": {},
   "outputs": [],
   "source": [
    "import smtplib\n",
    "import serial\n",
    "import os\n",
    "import json\n",
    "import shutil\n",
    "from email.mime.text import MIMEText\n",
    "from email.mime.multipart import MIMEMultipart\n",
    "from email.mime.base import MIMEBase\n",
    "from email import encoders\n",
    "from deepface import DeepFace"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "d046c6b0",
   "metadata": {},
   "source": [
    "## Serial Communication Setup\n",
    "\n",
    "Initializing serial communication on COM1 with a baud rate of 9600"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "913f437c",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Initialize serial communication on COM1 with a baud rate of 9600\n",
    "s = serial.Serial('COM1', 9600)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "e2228427",
   "metadata": {},
   "source": [
    "## Authorized Target Images\n",
    "\n",
    "Defining  a list of authorized target images for verification and initializing Detection flag to track if detection has occurred"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "337847d1",
   "metadata": {},
   "outputs": [],
   "source": [
    "# List of authorized target images\n",
    "target_images = [\"nayana.jpg\", \"alan.jpg\", \"nebu.jpg\"]\n",
    "\n",
    "# Variable to track if detection occurred\n",
    "Detection = False"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "ae860829",
   "metadata": {},
   "source": [
    "### SMTP Server Configuration for Sending Email Alerts\n",
    "\n",
    "The following section sets up the necessary details for sending email alerts via SMTP.\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d71af962",
   "metadata": {},
   "outputs": [],
   "source": [
    "# SMTP server and port details for sending email alerts\n",
    "smtp_port = 587  # Standard secure SMTP port\n",
    "smtp_server = \"smtp.gmail.com\"  # Google SMTP Server\n",
    "\n",
    "# Sender and receiver email addresses\n",
    "email_from = \"smartlockersender@gmail.com\"\n",
    "email_to = \"smartlockerreceiver@gmail.com\"\n",
    "\n",
    "# Application-specific password for sender's email\n",
    "pswd = \"**********\" "
   ]
  },
  {
   "cell_type": "markdown",
   "id": "04fc6cd3",
   "metadata": {},
   "source": [
    "## Email Sending Function\n",
    "\n",
    "This function sends an email with an image attachment in case of a theft alert."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c6c7005c",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Function to send email with an image attachment \n",
    "def send_emails(email_to):\n",
    "    \n",
    "     # Email body content\n",
    "    body = \"\"\"\n",
    "    Theft Detected before Smart Locker\n",
    "    Theft Image Attached!\n",
    "    \"\"\"\n",
    "    \n",
    "    # Create MIME object for email content\n",
    "    msg = MIMEMultipart()\n",
    "    msg['From'] = email_from\n",
    "    msg['To'] = email_to\n",
    "    msg['Subject'] = \"Theft Detected!!!\"\n",
    "    \n",
    "    # Attach the email body to the MIME object\n",
    "    msg.attach(MIMEText(body, 'plain'))\n",
    "\n",
    "    # Define the image filename(captured image) to attach\n",
    "    filename = \"image_selected.jpg\"\n",
    "    \n",
    "    # Open the image file in binary mode\n",
    "    attachment= open(filename, 'rb')  \n",
    "   \n",
    "    # Encode attachment as base64\n",
    "    attachment_package = MIMEBase('application', 'octet-stream')\n",
    "    attachment_package.set_payload((attachment).read())\n",
    "    encoders.encode_base64(attachment_package)\n",
    "    attachment_package.add_header('Content-Disposition', \"attachment; filename= \" + filename)\n",
    "    msg.attach(attachment_package)\n",
    "    \n",
    "    # Convert message to string format\n",
    "    text = msg.as_string()\n",
    "\n",
    "    # Connect to the SMTP server\n",
    "    print(\"Connecting to server...\")\n",
    "    TIE_server = smtplib.SMTP(smtp_server, smtp_port)\n",
    "    TIE_server.starttls() # Start TLS for security\n",
    "    TIE_server.login(email_from, pswd) # Log in to the email server\n",
    "    print(\"Succesfully connected to server\")\n",
    "    print()\n",
    "\n",
    "    # Send email to the specified recipient\n",
    "    print(f\"Sending email to: {email_to}...\")\n",
    "    TIE_server.sendmail(email_from, email_to, text)\n",
    "    print(f\"Email sent to: {email_to}\")\n",
    "    print()\n",
    "\n",
    "    # Close the SMTP server connection\n",
    "    TIE_server.quit()    "
   ]
  },
  {
   "cell_type": "markdown",
   "id": "b6d88e3d",
   "metadata": {},
   "source": [
    "## Face Comparison Function\n",
    "\n",
    "This function compares two images using the **DeepFace** library to verify if the person in the captured image matches any of the authorized faces. The function returns \"Match\" if a match is found, \"Not Match\" if the face is unauthorized and \"Failed\" if a face can't be detected in one of the images."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d5f525dc",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Function to compare captured image with target images using DeepFace\n",
    "def compare_images(img1_path, img2_path):\n",
    "    try:\n",
    "        # Perform facial verification using DeepFace\n",
    "        result = DeepFace.verify(\n",
    "            img1_path=img1_path,\n",
    "            img2_path=img2_path,\n",
    "            model_name=\"Facenet\",\n",
    "        )\n",
    "        Detection=True # Set detection flag to True if any face is detected\n",
    "    except ValueError as e:\n",
    "        # Handle error if face is not detected properly    \n",
    "        print(f\"Face not detected properly: {e}\")\n",
    "        Detection=False # Set detection flag to False\n",
    "        \n",
    "    if Detection:\n",
    "        print(json.dumps(result, indent=2)) # Print verification result in JSON format\n",
    "        if result['verified']:\n",
    "            print(\"The person is not a Theft.\")\n",
    "            return \"Match\"\n",
    "        else:\n",
    "            return \"Not Match\"\n",
    "    else:\n",
    "        return \"Failed\""
   ]
  },
  {
   "cell_type": "markdown",
   "id": "41a6bcd7",
   "metadata": {},
   "source": [
    "## Smart Locker System Monitoring Loop\n",
    "\n",
    "This section of the code runs in an infinite loop to continuously check for locker access requests. \n",
    "\n",
    "Waiting for Serial Signal: The code first waits to receive data via serial communication. If the signal 'a' is received, it indicates that the Raspberry Pi has captured an image.\n",
    "\n",
    "Image Retrieval: The code then searches for the captured image in a specific directory. Once located, it copies the image to a predefined location (image_selected.jpg) for further processing.\n",
    "\n",
    "Face Verification Process: The code iterates over each target image in the list of authorized images and calls compare_images to compare the captured image with each target image.\n",
    "\n",
    "Based on the result of the comparison: \n",
    "\n",
    "- If the captured face matches an authorized user, the system sends 'b' (face detected) and 'c' (face matched) signals via UART   to the Proteus, indicating successful authentication and allowing access to the locker.\n",
    "\n",
    "- If no face is detected (i.e., compare_images returns \"Failed\"), the system sends 'd' to indicate that the face detection         failed, prompting the user to try again.\n",
    "\n",
    "Unauthorized Access Handling: If the captured face does not match any authorized user (i.e., compare_images returns \"Not Match\"), the system interprets this as an unauthorized access attempt. It responds by:\n",
    "\n",
    "- Sending 'b' (face detected) and 'e' (potential theft detected) to the Raspberry Pi to activate the security alarm.\n",
    "\n",
    "- Calling send_emails to notify the locker owner of the unauthorized attempt, attaching the captured image of the unauthorized     user to the email.\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "27a4b8f8",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Infinite loop to keep checking for locker access requests            \n",
    "while True:\n",
    "      print(\"Smart Locker System\")\n",
    "      serial_data = s.read() # Read serial data\n",
    "\n",
    "      # If signal indicating an image is captured is received\n",
    "      if(serial_data == b'a'):\n",
    "          # Define the root path where captured image is stored\n",
    "          root_path = r\"C:\\Users\\HP\\AppData\\Local\\Temp\\VSM Studio\"\n",
    "          image_file = None # Initialize variable to hold image file path\n",
    "\n",
    "          # Search for the captured image in the specified directory\n",
    "          for root, dirs, files in os.walk(root_path):\n",
    "              for file in files:\n",
    "                  if file == 'image00000.jpg':\n",
    "                      image_file = os.path.join(root, file)\n",
    "                      break\n",
    "              if image_file:\n",
    "                  break\n",
    "\n",
    "          # Copy the captured image to a new location for comparison      \n",
    "          if image_file:\n",
    "              source_image = r\"C:\\Users\\HP\\image_selected.jpg\"\n",
    "              shutil.copy(image_file, source_image)\n",
    "              \n",
    "          # Compare the captured image with each target image\n",
    "          for target_image in target_images:\n",
    "              status=compare_images(source_image, target_image)\n",
    "              if status==\"Match\":\n",
    "                  s.write(b'b') # Send confirmation signal to indicate a face is detected\n",
    "                  s.write(b'c') # Send confirmation signal to unlock locker\n",
    "                  break\n",
    "              if status==\"Failed\":\n",
    "                  s.write(b'd') # Send signal indicating failure in detecting a face\n",
    "                  break\n",
    "             \n",
    "          # If no match is found\n",
    "          if status==\"Not Match\":            \n",
    "              s.write(b'b') # Send confirmation signal to indicate a face is detected\n",
    "              s.write(b'e') # Send signal indicating potential theft\n",
    "              print(\"Theft detected sending image on mail\")\n",
    "              send_emails(email_to) # Call function to send email alert\n",
    "\n",
    "        "
   ]
  }
 ],
 "metadata": {
  "celltoolbar": "Raw Cell Format",
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
