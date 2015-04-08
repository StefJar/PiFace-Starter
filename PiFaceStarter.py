#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 03.04.2015

@author: stj
'''

import os
import sys
import distutils.spawn
import pifacecad
import time
import threading
import stat
import argparse

def checkExecutableProgram(filename):
    executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
    if os.path.isfile(filename):
        if os.path.isfile(filename):
            st = os.stat(filename)
            mode = st.st_mode
            if mode & executable:
                return filename
    return None

def getExecutableFileList (searchPath, extra=['py']):
    print('crawl '+searchPath)
    pL = []
    for (dirpath, dirnames, filenames) in os.walk(searchPath):
        for f in filenames:
            fn = os.path.join(dirpath,f)
            if (checkExecutableProgram(fn) is not None):            
                pL.append((f,fn))
    print('executables:')
    for (f, fp) in pL:
        print('{f} @ {fp}'.format(f=f, fp=str(fp)))
    return pL


def printToLCD(line1, line2):
    global cad
    
    prtStr = line1 + '\n' + line2
    cad.lcd.clear()
    cad.lcd.write(prtStr)
    
def updateDisplayFiles():
    global gIndx
    global gFL
    global gFLlen
    
    if gIndx < 0:
        printToLCD('<none>','<none>')
        return
    l1 = '> ' + gFL[gIndx][0]
    l2 = '<none>' if (gIndx+1 >= gFLlen) else gFL[gIndx+1][0]
    printToLCD(l1,l2)

def moveUp(e):
    global gIndx
    
    if gIndx > 0:
        gIndx -= 1
    updateDisplayFiles()

def moveDown (e):
    global gIndx
    
    if gIndx < gFLlen-1:
        gIndx += 1
    else:
        gIndx = gFLlen - 1
    updateDisplayFiles()

def execute(e):
    global gIndx
    global cad
    
    if gIndx < 0:
        printToLCD('nothing to execute','')
    else:
        printToLCD('execute','wait ...')
    
    # del display
    printToLCD('', '')
    cad.lcd.backlight_off()
    exf = gFL[gIndx][1]
    print("executing "+ exf)
    os.system( exf)
        
    cad.lcd.backlight_on()
    printToLCD('starter v.1.0', 'select file')
    time.sleep(1)    
    updateDisplayFiles()
    

def printEvent(e):
    print(e)


def exitCB (e):
    global gEndBarrier
    global exitFlag
    
    print("exit")
    exitFlag = True
    gEndBarrier.wait()
    print("exitied")

def initPiFace():
    global cad
    global listener
    global actionHandler
    global gEndBarrier
    
    if gEndBarrier != None:
        gEndBarrier.wait()
        listener.deactivate()
        del gEndBarrier
        del listener
        gEndBarrier = None
        listener = None
        
    if cad != None:
        del cad
        cad = None
    
    gEndBarrier = threading.Barrier(2)
    cad = pifacecad.PiFaceCAD()
    cad.lcd.backlight_on()
    printToLCD('starter v.1.0', 'select file')
    time.sleep(2)
    
    updateDisplayFiles()
    
    listener = pifacecad.SwitchEventListener(chip=cad)
    for i in range(8):
        h = actionHandler.get(i, printEvent)
        listener.register(i, pifacecad.IODIR_FALLING_EDGE, h)
    listener.activate()
    

if __name__ == '__main__':
    global actionHandler
    global cad
    global listener
    global actionHandler
    global gEndBarrier
    global exitFlag


    print('PiFace Comand and Control Starter\nenter "python PiFaceStarter.py -h" for help')
    
    parser = argparse.ArgumentParser(description='PiFace Comand and Control Starter')
    parser.add_argument('-p','--path', help='the search path for the executabels. Default is the user dir.', default=os.path.expanduser("~"))
    
    args = vars(parser.parse_args())


    cad = None
    listener = None
    
    gFL = getExecutableFileList(args['path'])
    gFLlen = len(gFL)
    gIndx = -1 if gFLlen < 1 else 0
    gEndBarrier = None
    exitFlag = False

    actionHandler ={
        6 : moveUp,
        7 : moveDown,
        5 : execute,
        4 : exitCB
        }

    initPiFace()     
    
    updateDisplayFiles()
    
    
    try:
        while exitFlag == False:
            gEndBarrier.wait()
    except Exception as e:
        print(e)
    
    listener.deactivate()
    
    printToLCD('', '')
    cad.lcd.backlight_off()