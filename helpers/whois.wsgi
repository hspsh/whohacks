#import sys
#sys.path.insert(0,'/root/.local/lib/python3.5/site-packages/')
#import flask
#
#def application(environ, start_response):
#    status = '200 OK'
#
#    output = u''
#    output += u'sys.version = %s\n' % repr(sys.version)
#    output += u'sys.prefix = %s\n' % repr(sys.prefix)
#
#    response_headers = [('Content-type', 'text/plain'),
#                        ('Content-Length', str(len(output)))]
#    start_response(status, response_headers)
#
#    return [output.encode('UTF-8')]
#exit(0)
import sys
sys.path.insert(0, '/home/whois')
from whois.web import app as application

