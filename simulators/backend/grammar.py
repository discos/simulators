import re

REQUEST = '?'
REPLY = '!'
SEPARATOR = ','
OK = "ok"
FAIL = "fail"
INVALID = "invalid"

type_re = r"(?P<type>(\%s|\%s))" % (REQUEST, REPLY)
type_pattern = re.compile(type_re)
name_re = r"(?P<name>[a-zA-Z][a-zA-Z0-9-]*)"
name_pattern = re.compile(name_re)
code_re = r",(?P<code>(%s|%s|%s))" % (OK, FAIL, INVALID)
code_pattern = re.compile(code_re)
arguments_re = r"(,(?P<arguments>[^\r\n]+))?"
arguments_pattern = re.compile(arguments_re)
linefeed_re = r"(?P<linefeed>\r\n)?"
linefeed_pattern = re.compile(linefeed_re)
request_re = r"^(?P<type>\%s)" % (REQUEST,) + \
    name_re + \
    arguments_re + \
    linefeed_re + \
    "$"
request_pattern = re.compile(request_re)
reply_re = r"^(?P<type>\%s)" % (REPLY,) + \
    name_re + \
    code_re + \
    arguments_re + \
    linefeed_re + \
    "$"
reply_pattern = re.compile(reply_re)

argument_re = r""


class GrammarException(Exception):
    pass


class Message(object):
    def __init__(self, **kwargs):
        self.message_type = kwargs["message_type"]
        self.name = kwargs["name"]
        self.code = kwargs["code"] if "code" in kwargs else ""
        self.arguments = kwargs["arguments"] if "arguments" in kwargs else []

    def is_request(self):
        return self.message_type == REQUEST

    def is_reply(self):
        return self.message_type == REPLY

    def __str__(self):
        """Transforms the message object into a correct message string, the CR
        LF trailing is omitted."""
        return_str = ""
        args_str = "," + ",".join(self.arguments) if self.arguments else ""
        if self.is_reply():
            return_str = "%s%s,%s%s" % (
                self.message_type,
                self.name,
                self.code,
                args_str
            )
        else:
            return_str = "%s%s%s" % (
                self.message_type,
                self.name,
                args_str
            )
        return return_str + '\r\n'


def parse_message(message_string):
    """Parses a message.

    @param message: the message to be parsed
    @return the grammar.Message object resulting from the parsing
    @raises GrammarException if the message syntax is invalid"""
    match = None
    if not message_string:
        raise GrammarException('empty message is not valid')
    if message_string.startswith(REPLY):
        match = reply_pattern.match(message_string)
    elif message_string.startswith(REQUEST):
        match = request_pattern.match(message_string)
    else:
        raise GrammarException(
            "invalid message type '%s'" % (message_string[0],)
        )

    try:
        if match.groupdict()["arguments"]:
            arguments = match.groupdict()["arguments"].split(",")
        else:
            arguments = []
    except:
        raise GrammarException('wrong arguments separator')
    code = match.groupdict()["code"] if "code" in match.groupdict() else ""
    return Message(
        message_type=match.groupdict()["type"],
        name=match.groupdict()["name"],
        code=code,
        arguments=arguments
    )
