#!/usr/bin/python3

import sys
import re

class ReadBufferException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class InvalidLineException(ReadBufferException):
    def __init__(self, message):
        ReadBufferException(self, message)

class ReadBuffer:

    def __init__(self, instream):
        self.__in = instream
        self.__next_line = None

    def loadNextLine(self):
        if self.__next_line == '':
            return None

        if self.__next_line == None:
            self.__next_line = self.__in.readline()
            printd("Loaded [%s]" % self.__next_line)

        return self.__next_line

    def readLine(self):
        if self.loadNextLine() == None:
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

def printq(message):
    print_queue.append(message)

def printc(colour, message):
    printq("\033[%i;1m%s\033[0m" % (colour, message) )

def printd(message):
    pass #printc(35, message)

def getReceivedByHeaders(read_buffer):
    while True:
        header = read_buffer.readSingleHeader()
        if header == None:
            return

        if not re.match("(Received|X-Received):", header):
            continue

        ix_f = header.find("from")
        ix_b = header.find("by")

        if ix_f > 0 and ix_b > 0:
            printc(32, "By  : %s" % header[ix_b:])
            printc(32, "From: %s" % header[ix_f:ix_b])

        elif ix_f > 0:
            printc(33, "From: %s" % header[ix_f:])

        elif ix_b > 0:
            printc(33, "By  : %s" % header[ix_b:])

        else:
            printc(31, "Anomaly: no from/by: %s " % header)

        printc(0, "----------")
            

def flushPrintQueue():
    for line in print_queue:
        print(line)

print_queue = []

def main():
    rb = ReadBuffer(sys.stdin)

    getReceivedByHeaders(rb)

    flushPrintQueue()

if __name__ == '__main__':
    main()
