import logging
from djehouty.libgelf.handlers import GELFTCPSocketHandler


class sendgraylog(object):

    def send_to_graylog(self, loghost, logport, logfile):
        gelf_logger = logging.getLogger('QLS wifi agent')
        gelf_logger.setLevel(logging.INFO)
        gelf_logger.addHandler(GELFTCPSocketHandler(
            host=loghost,
            port=logport,
            #static_fields={"app": 'djehouty-gelf'},
            use_tls=False,
            level=logging.INFO,
            null_character=True,
        ))
        gelf_logger.info('-',extra=logfile)
        gelf_logger.

        return

