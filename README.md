![License](https://img.shields.io/github/license/hagenfritz/mass-email-sender)
![Contrib](https://img.shields.io/github/contributors/hagenfritz/mass-email-sender)
![Last commit](https://img.shields.io/github/last-commit/hagenfritz/mass-email-sender)
![GitHub top language](https://img.shields.io/github/languages/top/hagenfritz/mass-email-sender)

# Sending Mass Emails with Python
This project rose out of the need for the office team at [Austin Learning Center](http://austinlearningcenter.com) to update their process of sending work schedules to tutors. Their old system was contained in a "black box" so they had no idea to how to debug issues. 

### Purpose
The purpose of this project is to be able to send out mass emails to addresses provided in a file and include attachments in each email that correspond to the individual. Additionally, we want:
* **robust and easy-to-understand documentation** so anyone can easily diagnose and debug issues _if_ they arise
* **an executable or single command** to run the program
* **to provide a teaching opportunity** for those interested in learning how Python can automate simple tasks with relative ease
* **to integrate testing and code coverage** so that we can understand the moment something goes awry

# Running the Program
The latest release [v1.0.0]() contains two executable files for Mac-OS and Windows which run the `send_schedule.py` script. For a successful run, ensure the folder structure is left intact and the following files are located in the **same folder as the `send_schedule.exe` file**:
* "ALC Schedule.pdf": single PDF containing all the tutor schedules
* "Employees.txt": text file in a json-like format containing the tutor names and their emails
* "body.txt": file which holds the text to include in the body of the email

If these files and the folders `/logs/` and `/processed_schedules/` are in the same location, then simply: 
1. Click the `send_schedule.exe` icon
2. A command prompt will open asking the user to input a gmail account and password. Enter the correct credentials, pressing enter after each.
3. A series of messages will display on the command prompt indicating sucessful and unsuccessful email deliveries.
4. After an email has been sent to each of the employees in the list, the program terminates. 
5. The log file in the `/logs/` directory contains copies of the messages shown on the display when the program is running. Each log file is named for the day and keeps a history of the messages for each time the program has been executed that day.  

# How the Program Works
This program has two main components:
* ✂️ **Split an Aggregate PDF Schedule**: Tutor schedules can only be saved in one file so the first step is to split this file into individual PDFs that correspond to each tutor.
* 📧 **Email Schedules to Tutors**: Sent the schedules to tutors using a text file that links the tutor name with their email. 

Each of these components is separated into two classes stored within the `send_schedule.py` script and are descirbed in more detail below.

## Splitting the PDF
The [PyPDF2]() library can be used to read in PDF page content and extract important meta data from a PDF. We use this package to loop through each page and read the first character from each page. If the character is a letter, that indicates a tutor's name. If the character is a space or a number, then the program identifies this page as a continuation of the schedule for the most current tutor. As the program loops through each page, it builds a Python `dict` which stores the tutors' names and the page number(s) (zero-indexed) that their schedule corresponds to from the aggregate document. With this information saved, we loop through the tutors and their pages and create separate documents using only the pages for that tutor, saving the document as the tutors name in the `/processed_schedules/` folder. 

For more code examples, please see the [Create Individual Schedules Notebook](https://github.com/HagenFritz/mass-email-sender/blob/main/notebooks/1.0.0-hef-create_individual_schedules-examples.ipynb) in this repository. 

## Emailing Attachments to a List of Employees
We borrow much of the code from this [article](https://realpython.com/python-send-email/) which also provides some nice details regarding the process. The program uses the [SMTP]() library to make a connection with the Gmail server to send emails. We use the [MIME]() package to create the message which allows the addition of text for the email body and attaches the tutor's PDF. 

For more code examples, please see the [Emailing Attachments](https://github.com/HagenFritz/mass-email-sender/blob/main/notebooks/2.0.0-hef-emailing_attachments-examples.ipynb) in this repository. 

## Resources
Some the articles and other resources used to help construct the code in this repository
* [Shields](https://shields.io/category/activity)
* [Working with PDFs in Python](https://realpython.com/pdf-python/#how-to-extract-document-information-from-a-pdf-in-python)
* [Sending Emails with Python](https://realpython.com/python-send-email/)
* [Testing in Python](https://realpython.com/python-testing/)
* Code Coverage
  * [Quick Start](https://docs.codecov.com/docs)
  * [Tutorial](https://docs.codecov.com/docs/github-tutorial)
  * [Python+Github+Codecov Example](https://about.codecov.io/blog/python-code-coverage-using-github-actions-and-codecov/)
