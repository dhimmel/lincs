'''
classes for determinate and indeterminate update bars
Created on Apr 10, 2012

@author: cflynn
'''
import sys
import blessings
from threading import Timer

class DeterminateProgressBar(object):
    '''
    provides an interface for determinate progress bars
    '''


    def __init__(self,name):
        '''
        Constructor
        '''
        self.name = name
        self.term = blessings.Terminal()
    
    def update(self,message, progress, total):
        '''
        update the update displayed on screen
        '''
        percent = float(progress)/total*100
        name_string = self.term.yellow(self.name)
        sys.stdout.write('\r' + name_string + ':%s  [%s] %.2f%%' %(
                                                 message,
                                                  '#'*(int(round(percent/10))), 
                                                  percent))
        sys.stdout.flush()
        
    def show_message(self,message):
        '''
        displays the current message on screen until cleared by another class method
        '''
        self.clear()
        name_string = self.term.yellow(self.name)
        sys.stdout.write('\r' + name_string + ':%s' %(message,))
        sys.stdout.flush()
    
    def clear(self):
        '''
        clears the screen
        '''
        try:
            sys.stdout.write('\r' +  ' ' * self.term.width)
        except TypeError:
            sys.stdout.write('\r' +  ' ' * 1000)
        sys.stdout.flush()

class IndeteriminateProgressBar(object):
    '''
    provides an interface for indeterminate progress bars
    '''
    
    def __init__(self,name):
        '''
        Constructor
        '''
        self.name = name
        self.on = False
    
    def start(self):
        '''
        start the indeterminate progress bar
        '''
        self.on = True
        self.animate(0)
        
    
    def animate(self,i):
        '''
        underlying animate function for the progress bar
        '''
        while self.on:
            sys.stdout.write( '\r' + ( '.' * i ) + '   ' )
            sys.stdout.flush()
            Timer( 2, self.animate, ( 0 if i == 3 else i + 1, ) ).start()
    
    def stop(self):
        '''
        stop the indeterminate progress bar
        '''
        self.on = False
    
    def test(self):
        '''
        test the progress bar
        '''
        self.start()
        self.animate(0)
        for i in range(10000): #@UnusedVariable
            pass
        self.stop()