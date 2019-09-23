#!/usr/bin/python3

import sys
import re

print_queue = []

# Output management
# We queue output to allow pasting to stdin
#  without interleaving the paste with the output

def printq(message):
    print_queue.append(message)

def flushPrintQueue():
    print("")

    for line in print_queue:
        print(line)

def printc(colour, message):
    printq("\033[%i;1m%s\033[0m" % (colour, message) )

def printd(message):
    pass #printc(35, message)

# Ingest management

class ReadBufferException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class InvalidLineException(ReadBufferException):
    def __init__(self, message):
        ReadBufferException(self, message)

class ReadBuffer:
    # Headers can be comprised of multiple lines
    #  this buffer allows accessing each header as a whole

    def __init__(self, instream):
        self.__in = instream
        self.__next_line = None

    def loadNextLine(self):
        # "Next" line is empty (as opposed to None, which would mean 'ready to load new line') - end of headers
        if self.__next_line == '':
            return None

        if self.__next_line == None: # Line has not been read, or previous line has been consumed
            self.__next_line = self.__in.readline()
            printd("Loaded [%s]" % self.__next_line)

        return self.__next_line

    def readLine(self):
        if self.loadNextLine() == None: # Load and check, individually
            return None

        the_line = self.__next_line
        self.__next_line = None

        self.loadNextLine()

        return the_line.strip()

    def __nextLineHangs(self):
        self.loadNextLine()

        return re.match('\\s', self.__next_line)
        

    def readSingleHeader(self):
        header_lines = []

        if self.loadNextLine() == None:
            return None

        if self.__nextLineHangs():
            raise InvalidLineException("Initial line must not hang: [%s]" % self.__next_line)

        header_lines.append( self.readLine() )

        while self.__nextLineHangs():
            header_lines.append( self.readLine() )

        return ' '.join( header_lines )

# Main procedures

def getReceivedByHeaders(read_buffer):
    while True:
        header = read_buffer.readSingleHeader()
        if header == None:
            return

        if not re.match("(Received|X-Received):", header):
            continue

        # Indices of from and by sections
        ix_f = header.lower().find("from")
        ix_b = header.lower().find("by")


        # Print green when both are found
        if ix_f > 0 and ix_b > 0:
            if ix_f < ix_b:
                bytext = header[ix_b:]
                fromtext = header[ix_f:ix_b]
            else:
                bytext = header[ix_b:ix_f]
                fromtext = header[ix_f]

            printc(32, "By  : %s" % bytext)
            printc(32, "From: %s" % fromtext)


        # Print yellow when only one is found
        #  this indicates some sort of internal masking is happening
        elif ix_f > 0:
            printc(33, "From: %s" % header[ix_f:])

        elif ix_b > 0:
            printc(33, "By  : %s" % header[ix_b:])

        else:
            printc(31, "Anomaly: no from/by in 'Received*' section: %s " % header)

        printc(0, "----------")

def main():
    try:
        rb = ReadBuffer(sys.stdin)

        getReceivedByHeaders(rb)

    except KeyboardInterrupt as e:
        pass #print(e)

    finally:
        flushPrintQueue()

if __name__ == '__main__':
    main()
