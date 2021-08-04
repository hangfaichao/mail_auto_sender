import smtplib
from email.mime.text import MIMEText
import markdown
import codecs
from configparser import ConfigParser
import sys
import os
from enum import Enum, unique

@unique
class TextType(Enum):
    TXT = 0
    MD = 1
    HTML = 2


class AutoMail:

    def __init__(self, config_file_path, content_file_path):

        self.load_config_info(config_file_path)
        self.load_content_info(content_file_path)

    def load_config_info(self, file_path):

        config = ConfigParser()
        config.read(file_path, encoding="utf-8")
        self.mail_host = config["email"]["mail_host"]
        self.mail_user = config["email"]["mail_user"]
        self.mail_pass = config["email"]["mail_pass"]
        self.mail_sender = config["email"]["sender"]
        self.to_receivers \
            = [receiver.strip() for receiver in config["email"]["to_receivers"].split(",")]
        self.cc_receivers \
            = [receiver.strip() for receiver in config["email"]["cc_receivers"].split(",")] \
            if "cc_receivers" in config["email"] \
            else []

    def load_content_info(self, file_path):
        
        file_type = file_path.split(".")[-1].upper()
        self.check_content_file_type(file_type)
        file_name = file_path.split("/")[-1][:file_path.split("/")[-1].rindex(".")]
        raw_text = self.load_text(file_path)

        self.subject = file_name
        self.content_type, self.content = self.content_transfer(file_type, raw_text)

    def load_text(self, file_path):
        input_file = codecs.open(file_path)
        return input_file.read()

    def markdown2html(self, text):
        return markdown.markdown(text)

    def check_content_file_type(self, content_file_type):
        if content_file_type not in TextType._member_names_:
            raise Exception(print("Error: Content file type: '" + content_file_type + "' not support"))

    def content_transfer(self, text_type, raw_text):
        if text_type == TextType.MD.name:
            return "html", self.markdown2html(raw_text)
        if text_type == TextType.HTML.name:
            return "html", raw_text.strip()
        if text_type == TextType.TXT.name:
            return "plain", raw_text.strip()

    def run(self):
        
        #设置email信息
        #邮件内容设置
        message = MIMEText(self.content, self.content_type, 'utf-8')
        #邮件主题       
        message['Subject'] = self.subject
        #发送方信息
        message['From'] = self.mail_sender 
        #接受方信息     
        message['To'] = ",".join(self.to_receivers)
        message['Cc'] = ",".join(self.cc_receivers)
        receivers = self.to_receivers + self.cc_receivers

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


    if len(sys.argv) < 3:
        raise Exception(print("Error: please give config file path and content file path"))

    config_file_path = sys.argv[1]
    content_file_path = sys.argv[2]
    
    auto_mail = AutoMail(config_file_path, content_file_path)
    auto_mail.run()