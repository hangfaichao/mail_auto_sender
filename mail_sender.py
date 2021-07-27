import smtplib
from email.mime.text import MIMEText
import markdown
import codecs
from configparser import ConfigParser
import sys

class AutoMail:

    def __init__(self, mail_host, mail_user, mail_pass, mail_sender, to_receivers, cc_receivers, content_type, file_path):
        self.mail_host = mail_host
        self.mail_user = mail_user
        self.mail_pass = mail_pass
        self.mail_sender = mail_sender
        self.to_receivers = to_receivers
        self.cc_receivers = cc_receivers
        self.content_type = content_type
        self.content = ""
        self.file_path = file_path
        self.subject = ""

    def markdown2html(self, text):
        return markdown.markdown(text)

    def is_markdown(self, file_path):
        return file_path[-3:] == ".md"

    def check_file_type(self, file_path):
        if not self.is_markdown(file_path):
            raise Exception(print("Error: File not markdown"))

    def load_content(self, file_path, content_type):
        input_file = codecs.open(file_path)
        text = input_file.read()

        content = ""
        if content_type == "html":
            content = self.markdown2html(text)
        elif content_type == "plain":
            content = text
        else:
            raise Exception(print("Error: CONTENT_TYPE '" + content_type + "' not support"))
        return content

    def get_subject_from_markdown_file_name(self, file_path):
        return file_path.split("/")[-1][:-3]

    def run(self):

        self.check_file_type(self.file_path)

        self.subject = self.get_subject_from_markdown_file_name(self.file_path)

        self.content = self.load_content(self.file_path, self.content_type)
        
        #设置email信息
        #邮件内容设置
        message = MIMEText(self.content, self.content_type, 'utf-8')
        #邮件主题       
        message['Subject'] = self.subject
        #发送方信息
        message['From'] = self.mail_sender 
        #接受方信息     
        message['To'] = ",".join(self.to_receivers)
        receivers = self.to_receivers

        if self.cc_receivers is not None and len(self.cc_receivers) > 0:
            message['Cc'] = ",".join(self.cc_receivers)
            receivers += self.cc_receivers

        #登录并发送邮件
        try:
            #连接到服务器
            smtpObj = smtplib.SMTP_SSL(self.mail_host, 465) 
            #登录到服务器
            smtpObj.login(self.mail_user, self.mail_pass) 
            #发送
            smtpObj.sendmail(
                self.mail_sender, receivers, message.as_string()) 
            #退出
            smtpObj.quit() 
            print('Success')
        except smtplib.SMTPException as e:
            print('Error', e) #打印错误

if __name__ == "__main__":


    if len(sys.argv) < 2:
        raise Exception(print("Error: please give the file path"))

    file_path = sys.argv[1]

    
    config = ConfigParser()
    config.read("property.conf", encoding="utf-8")
    mail_host = config["email"]["mail_host"]
    mail_user = config["email"]["mail_user"]
    mail_pass = config["email"]["mail_pass"]
    mail_sender = config["email"]["sender"]
    to_receivers = [receiver.strip() for receiver in config["email"]["to_receivers"].split(",")]
    cc_receivers = [receiver.strip() for receiver in config["email"]["cc_receivers"].split(",")]
    content_type = config["email"]["content_type"]
    
    auto_mail = AutoMail(mail_host, mail_user, mail_pass, mail_sender, to_receivers, cc_receivers, content_type, file_path)

    auto_mail.run()
    # send_mail(file_path, CONTENT_TYPE, mail_host, mail_user, mail_pass, sender, to_receivers, cc_receivers)