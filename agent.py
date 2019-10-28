import sys, os
import subprocess
from queue import Queue, Empty
from threading import Thread
#TODO: Add logging
import logging

sendqueue = Queue()

class procwrapper():
    def __init__(self, args, sendqueue=sendqueue):
        self.proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #Mostly unused except for referencing
        self.stdin = self.proc.stdin
        self.stdout = self.proc.stdout
        self.stderr = self.proc.stderr
        self.returncode = None
        self.sendqueue = sendqueue
    def getData(self, text=None):
        data = None
        errs = None
        try:
            if text:
                data, errs = self.proc.communicate(input=text,timeout=0.1)
            else:
                data, errs = self.proc.communicate(timeout=0.1)
        except subprocess.TimeoutExpired:
            pass
        self.returncode = self.proc.returncode
        if data or errs:
            data = data.decode('utf-8')
            errs = errs.decode('utf-8')
        return data, errs
    def addToQueue(self):
        if self.returncode:
            return
        data = self.getData()
        if data[0] or data[1]:
            self.sendqueue.put(data)
    def threadable(self):
        while True:
            self.addToQueue()
            if self.returncode:
                return
    def launchownthread(self):
        self.procthread = Thread(target=self.threadable)
        self.procthread.start()

class downloader():
    def __init__(self, url):
        pass

class communicator():
    def __init__(self, url):
        pass

def testrun():
    proc = procwrapper("powershell -command \"Get-EventLog -LogName security\"")
    proc.stdin.write("exit\n".encode())
    proc.stdin.flush()
    proc.launchownthread()
    
    while True:
        try:
            data = sendqueue.get_nowait()
            print(data)
        except Empty:
            pass
        if proc.proc.returncode and sendqueue.empty():
            break

if __name__ == "__main__":
    testrun()
