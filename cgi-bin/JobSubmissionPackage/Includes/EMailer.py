#!/usr/bin/python

import smtplib, os
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

class EMailer:
    """
    Sends emails to users.

    Authors
    -------
        Ilan Smoly

    """
    
    fromAddress = "motifnetadmin@post.bgu.ac.il"
    host = "smtp.bgu.ac.il" #"smtp.bgu.ac.il"
    user = "smolyi" #temp
    pwd = "skupeR33" #temp
    
    def __init__(self,email,logger = None,user = None,pwd = None):
        '''
        @param root_dir: user's local root directory 
        @param email: user's email 
        '''
        self.logger = logger
        self.email = email
        self.adminEmail = "ilansmoly@gmail.com"
    
    
    def jobSubmitted(self, jobName):    
        
        link = "http://netbio.bgu.ac.il/motifnet/#/explorer/"+str(jobName)
        attachment = []
        subject = "MotifNet - job submitted"
        text = "<html><head><title>%s</title></head><body>"%subject
        
        text += "<p>Thank you for using MotifNet. The results of your job will be available <a href='%s' >here</a>. \
        You will be notified when they are ready. </p>"%link
        
        text += "</body></html>"
        self.__sendEmail(subject, text,attachment)
    
    def notify(self, jobName):    
        
        link = "http://netbio.bgu.ac.il/motifnet/#/explorer/"+str(jobName)
        attachment = []
        subject = "MotifNet - results are ready"
        text = "<html><head><title>%s</title></head><body>"%subject
        
        
        text += "<p>Your results are ready. You can view them <a href='%s' >here</a>. \n<br>"%link
        text += "\n<br>\n<br> Thank you for using MotifNet</p>"
        
        text += "</body></html>"
        self.__sendEmail(subject, text,attachment)
    
    def error(self, jobName, errorMsg):    
        
        attachment = []
        subject = "MotifNet - error notification"
        text = "<html><head><title>%s</title></head><body>"%subject
        
        text += "<p>An error occurred while handling job %s: </p>"%jobName
        text += "<p>%s</p>"%errorMsg
        
        text += "</body></html>"
        self.__mail(self.adminEmail, subject, text,attachment)

        
        
    def __sendEmail(self, subject, text, attach = []):
        self.__mail(self.email, subject, text,attach)
        self.__mail(self.adminEmail, subject, text,attach)
        
    def __mail(self,email, subject, text, attach = []):
        try:
            msg = MIMEMultipart()
            msg['From'] = "motifnetadmin"
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(text,'html'))
            
            if attach:
                for k in range(0,len(attach)):
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(open(attach[k], 'rb').read())
                    Encoders.encode_base64(part)
                    part.add_header('Content-Disposition','attachment; filename="%s"' % os.path.basename(attach[k]))
                    msg.attach(part)
                      
            self.__safeLog(1, "connecting to smtp-server...")
            mailServer = smtplib.SMTP(self.host, smtplib.SMTP_PORT)
            self.__safeLog(1, "connected. ")
            
            #if self.user: mailServer.login(self.user, self.pwd)
            self.__safeLog(1, "sending email from %s to %s" % (self.fromAddress, email))
            mailServer.sendmail(self.fromAddress, email , msg.as_string())
    
            self.__safeLog(1, "mail sent.")
            self.__safeLog(1, "disconnecting from smtp-server...")
            '''
            try: mailServer.quit()
            except: mailServer.close()
            '''
            mailServer.quit()
            self.__safeLog(1, "disconnected.")
        except Exception as inst:
            self.__safeLog(3, "Error in Emailer. - %s"%inst)
            
    def __safeLog(self, level, msg):
        if self.logger: self.logger.log(level, msg)

if __name__=="__main__":
    em = EMailer("ilansmoly@yahoo.com")
    em.notify(60)
