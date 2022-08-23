import argparse
import pathlib
import logging
import os
import sys

import ast

import PyPDF2
import argparse
import pathlib

import smtplib
import ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import datetime

from settings import USERNAME, EMAIL_KEY

# Needed for conversion to .exe
application_path = os.path.dirname(sys.executable)

class CreateSchedules:

    def __init__(self, aggregate_schedule, path_to_top="cli") -> None:
        """
        Creates the individualized PDF schedules

        Parameters
        ----------
        aggregate_schedule : str
            pdf filename contaning the aggregated schedule
        path_to_top : str, "cli" or absolute path
            path to the top of the directory structure
            "cli" tells the program that you are running from the CLI and should use the project's structure

        Creates
        -------
        path_to_top : str
            path to the top directory
        pdf : PyPDF2 object
            the base pdf 
        
        """
        if path_to_top == "cli":
            self.path_to_top = f"{pathlib.Path(__file__).resolve().parent}"
        else:
            self.path_to_top = path_to_top

        self.pdf = PyPDF2.PdfFileReader(f"{self.path_to_top}/{aggregate_schedule}.pdf")

    def get_pages_per_tutor(self):
        """
        Finds the pages corresponding to each tutor

        Returns
        -------
        pages_per_tutor : dict
            keys as tutors with values as the pages of the original document corresponding to them
        """
        # creating the result variable
        pages_per_tutor = {}

        # getting the first tutor from page 0 
        current_tutor = self.pdf.pages[0].extractText().split("\n")[0].strip()
        pages_per_tutor[current_tutor] = [0]

        # looping through the remaining pages 
        num_pages = self.pdf.getNumPages()
        for pg_no in range(1,num_pages):
            # getting page content
            page = self.pdf.pages[pg_no]
            page_content = page.extractText()
            # pages that start with a space, number, or "App" are continuations from same tutor
            if page_content[0] == " " or page_content[0] in [str(num) for num in range(0,10)] or page_content[0:3].lower() == "app" or "," in page_content.split("\n")[0].strip():
                pages_per_tutor[current_tutor].append(pg_no)
            # pages that start with letter mean that the page corresponds to a new tutor
            else:
                current_tutor = page.extractText().split("\n")[0].strip()
                pages_per_tutor[current_tutor] = [pg_no]

        return pages_per_tutor

    def split_pdf(self,pages_per_tutor):
        """
        Splits the class PDF into the individualzed documents

        Parameters
        ----------
        pages_per_tutor : dict
            keys as tutors with values as the pages of the original document corresponding to them
        """
        # looping throug each of the tutors and their pages
        for tutor, pgs in pages_per_tutor.items():
            # pdf writer object
            pdf_writer = PyPDF2.PdfFileWriter()
            # for each page for a tutor, add their page to a new document
            for pg in pgs:
                pdf_writer.addPage(self.pdf.getPage(pg))
                
            # save the new pdf to the processed directory with the tutors name
            output = f"{self.path_to_top}/processed_schedules/{tutor}.pdf"
            with open(output, 'wb') as output_pdf:
                pdf_writer.write(output_pdf)

class EmailWithAttachment:
    
    def __init__(self, employee_email_list, path_to_top="cli") -> None:
        """
        Emails list of employees and their emails an attachment

        Parameters
        ----------
        employee_email_list : str
            filename of the tutor emails in a json-like format but saved as a txt
        path_to_top : str, "cli" or absolute path
            path to the top of the directory structure
            "cli" tells the program that you are running from the CLI and should use the project's structure

        Creates
        -------
        tutors_and_emails : dict
            keys as tutor name (first initial and last name) and values as email addresses
        """
        if path_to_top == "cli":
            self.path_to_top = f"{pathlib.Path(__file__).resolve().parent}"
        else:
            self.path_to_top = path_to_top

        with open(f"{self.path_to_top}/{employee_email_list}.txt") as f:
            data = f.read()

        self.tutors_and_emails = ast.literal_eval(data)

    def email_attachment(self):
        """
        Emails out the attaced schedules to tutors
        """
        with open(f'{self.path_to_top}/email_body.txt') as f:
            body = f.read()
        
        from_address = USERNAME#"alcschedule1@gmail.com"#input("Type the email account: ")
        password = EMAIL_KEY#"wcctjlwvjjyzvneu"#input("Type your password and press enter: ")

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(from_address, password)
            
            log.info("----------------")
            log.info("Sending Schedule")
            log.info("----------------")
            for name, email in self.tutors_and_emails.items():
                # Create a multipart message and set headers
                message = MIMEMultipart()
                message["From"] = from_address

                log.info(f"{name}")
                lines = "-"*len(name)
                log.info(lines)
                log.info(f"Employee Name: {name}")
                log.info(f"Email Address: {email}")
                log.info(f"Looking for file: {name}.pdf")
                message["To"] = email
                message["Subject"] = f"ALC Schedule {datetime.strftime(datetime.now(),'%m.%d.%Y')}"
                message.attach(MIMEText(body.format(name=name), "plain"))
                
                filename = f"{self.path_to_top}/processed_schedules/{name}.pdf"

                # Open PDF file in binary mode
                try:
                    with open(filename, "rb") as attachment:
                        # Add file as application/octet-stream
                        # Email client can usually download this automatically as attachment
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())

                    # Encode file in ASCII characters to send by email    
                    encoders.encode_base64(part)

                    # Add header as key/value pair to attachment part
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={name}.pdf",
                    )

                    # Add attachment to message and convert message to string
                    message.attach(part)
                    text = message.as_string()

                    server.sendmail(
                        from_address,
                        email,
                        text,
                    )
                    log.info("Success: email sent")
                except FileNotFoundError:
                    log.warning(f"Error: No file for {name} in {self.path_to_top}/processed_schedules/")

            log.info(f"{lines}")

def setup_logging(log_file_name):
    """
    Creates a logging object

    Parameters
    ----------
    log_file_name : str
        how to name the log file
    stream : boolean, default False
        whether to include output in a Stream

    Returns
    -------
    logger : logging object
        a logger to debug
    """
    # Create a custom logger
    logger = logging.getLogger(__name__)

    # Clearing log instances
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create handler
    try:
        f_handler = logging.FileHandler(f'{application_path}/logs/{log_file_name}.log',mode='a')
    except FileNotFoundError:
        # means that we are running from CLI
        dir_path = f"{pathlib.Path(__file__).resolve().parent}"
        f_handler = logging.FileHandler(f'{dir_path}/logs/{log_file_name}.log',mode='a')
    
    logging.getLogger().setLevel(logging.INFO)

    # Create formatter and add it to handler
    f_format = logging.Formatter('%(asctime)s: (%(lineno)d) - %(levelname)s:\t%(message)s',datefmt='%m/%d/%y %H:%M:%S')
    f_handler.setFormatter(f_format)

    # Add handler to the logger
    logger.addHandler(f_handler)

    # repeat the above steps but for a StreamHandler
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)
    c_format = logging.Formatter('%(asctime)s: %(levelname)s:\t%(message)s',datefmt='%m/%d/%y %H:%M:%S')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    return logger

def main(aggregate_schedule, employee_email_list, path_to_top):
    """
    Gets the individualized schedules and emails them out to tutors
    """
    # create the individualized schedules
    create_pdfs = CreateSchedules(aggregate_schedule=aggregate_schedule,path_to_top=path_to_top)
    pages_per_tutor = create_pdfs.get_pages_per_tutor()
    create_pdfs.split_pdf(pages_per_tutor=pages_per_tutor)

    # email out the schedules
    email_tutors = EmailWithAttachment(employee_email_list=employee_email_list,path_to_top=path_to_top)
    email_tutors.email_attachment()

log = setup_logging(f"send_schedule_{datetime.strftime(datetime.now(),'%m%d%Y')}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', help="aggregate pdf schedule name", default="ALC Schedule", type=str)
    parser.add_argument('-e', help="filename of employee names and their emails", default="Employees", type=str)
    parser.add_argument('-p', help="path to the top of the project's directory", default=application_path, type=str)
    args = parser.parse_args()

    main(aggregate_schedule=args.s,employee_email_list=args.e,path_to_top=args.p)