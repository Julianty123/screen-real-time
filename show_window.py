import win32gui
import os
import keyboard
import win32api, win32con
import cv2
import numpy as np
import win32ui
from ctypes import windll
from time import time

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

title_hwnd = dict()

def loadwindowslist(hwnd, topwindows):
    topwindows.append((hwnd, win32gui.GetWindowText(hwnd)))

def showwindowslist():
    topwindows = []
    win32gui.EnumWindows(loadwindowslist, topwindows)
    for hwin in topwindows:
        sappname = str(hwin[1])
        nhwnd = hwin[0]
        if sappname != "":
            title_hwnd[sappname] = nhwnd # Si la clave ya existe, se sobreescribe el valor
    print(title_hwnd)

showwindowslist()

# Default dimensions
width = 1280
height = 720

window_title = "NameWindowsHere" # 

def window_capture(window_title):
    global width, height
    hwnd = title_hwnd.get(window_title) # win32gui.FindWindow(None, window_title)
    
    if hwnd is None:
        return

    if not win32gui.IsIconic(hwnd):
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left - 14 # -14 y -37 Para eliminar el borde negro de la ventana
        height = bottom - top - 37

        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)

        saveDC.SelectObject(saveBitMap)
        windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
        # windll.gdi32.BitBlt(saveDC.GetSafeHdc(), 0, 0, width, height, hwndDC, 0, 0, win32con.SRCCOPY)
        
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        
        im = np.frombuffer(bmpstr, dtype='uint8')   # fromstring deprecated in numpy 1.19
        im.shape = (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)

        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        return cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) # COLOR_BGRA2BGR, COLOR_RGB2HSV, COLOR_BGRA2RGB or COLOR_BGR2GRAY
    else:
        print(f"La ventana {window_title} está minimizada")
        return np.zeros((height, width, 3), np.uint8)

loop_time = time() # No se como funciona esto muy bien
while True:
    # get an updated image of the game
    screenshot = window_capture(window_title)

    cv2.imshow('Screen in real time', screenshot)

    # debug the loop rate
    print('FPS {}'.format(1 / (time() - loop_time)))
    loop_time = time()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# close all windows
cv2.destroyAllWindows()