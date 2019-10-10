import imaplib
import email
import configparser

class MyImap:
    def __init__(self):
        self.cfg = None
        self.conf = "/etc/jmail.conf"
        self.server = None

    def read_conf(self):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(self.conf)
        
    def login(self):
        conf = self.cfg['mail_server']
        self.server = imaplib.IMAP4_SSL(conf['addr'])
        self.server.login(conf['user'], conf['passwd'])
        self.server.select(conf['folder']) # connect to inbox.

    def get_latest_mail(self):
        result, data = self.server.search(None, "ALL")
        ids = data[0].split()
        result, data = self.server.fetch(ids[-1], "(RFC822)")
        mail = email.message_from_bytes(data[0][1])
        return mail

def main():
    obj = MyImap()
    obj.read_conf()
    obj.login()
    mail = obj.get_latest_mail()
    subject = email.header.decode_header(mail.get('subject'))
    if type(subject[0][0]) in (type(b' '),):
        print(subject[0][0].decode(subject[0][1]))
    else:
        print("Title：" + subject[0][0])

if __name__ == "__main__":
    main()
