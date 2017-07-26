#!/usr/local/bin/python2.7
import os
import sys
import time

def ReadFile(i):
    with open(i) as f:
        lines = f.read().splitlines()
    return lines


def WriteFile(filename, data):
    with open(filename, 'w') as f:
        f.write("\n".join(data))   


def AppendFile(path, text):
    with open(path, "a") as f:
        f.write(text + "\n")


def AddSlash(i):
    if i[-1] not in ["/", "\\"]:
        return i + "\\"
    return i


class Automation:
    def __init__(self, imgFolder = 'img/'):
        self.GlobalFolderImg = imgFolder
        self.LogFile = "log.txt"
        self.ScriptFile = "script.ahk"
        self.CurrentDirectory = os.getcwd() + "\\"
        self.Script = []
        self.Log = []
        self.SetupImages()

    # http://stackoverflow.com/questions/18855048/get-image-file-dimensions-in-bat-file
    def GetImageDimensions(self, filename):
        if not os.path.isfile(filename):
            return 0, 0

        junk = "size.txt"
        if os.path.isfile(junk):
                os.remove(junk)
        os.system("tooltipinfo.bat " + filename + " > " + junk)
        for line in ReadFile(junk):
            if line.startswith("Dimensions:"):
                width, height = line.split("x")
                width = int("".join([x for x in width if x.isdigit()]))
                height = int("".join([x for x in height if x.isdigit()]))
                return width, height
        return 0, 0

    def SetupImages(self):
        folder = self.GlobalFolderImg
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder,f)) and f.endswith('.png')]
        self.ImgSize = {}
        for x in files:
            width, height = self.GetImageDimensions(os.path.join(folder, x))
            if width == 0 and height == 0:
                print "Could not get dimensions of: " + x
            else:
                print "Loaded: " + x
                self.ImgSize[x] = width, height



    def ClearScript(self):
        self.Script = []
        self.Log = []

    def ReadLog(self):
        self.Log = ['fail']
        if os.path.isfile(self.LogFile):
            self.Log = ReadFile(self.LogFile)
        if self.Log[0] == 'exit':
            sys.exit()

    def RunScript(self):
        for x in [self.LogFile, self.ScriptFile]:
            if os.path.isfile(x):
                os.remove(x)

        self.AppendExit()
        WriteFile(self.ScriptFile, self.Script)
        os.system("AutoHotkey.exe " + self.ScriptFile)
        self.ReadLog()
        self.Script = []

    def LogMessage(self, message):
        self.Script += ["FileAppend, " + message.replace(",", "") + ", " + self.CurrentDirectory + self.LogFile]

    def WinExists(self, title):
        self.ClearScript()
        self.Script += ["SetTitleMatchMode, 2"]
        self.Script += ["IfWinExist, " + title]
        self.Script += ["{"]
        self.LogMessage("True")
        self.Script += ["}"]
        self.Script += ["else"]
        self.Script += ["{"]
        self.LogMessage("False")
        self.Script += ["}"]
        self.RunScript()
        return True if self.Log[0] in ["True"] else False

    def WinGetTitle(self):
        self.ClearScript()
        self.Script += ["WinGetTitle, title, A"]
        self.LogMessage("%title%")
        self.RunScript()
        result = self.Log[0]
        return "" if result in ["fail"] else result

    def WinActivate(self, title):
        self.ClearScript()
        self.Script += ["SetTitleMatchMode, 2"]
        self.Script += ["winactivate, " + title]
        self.LogMessage("success")
        self.RunScript()
        return True if self.Log[0] in ['success'] else False


    def WinMaximize(self, title):
        self.ClearScript()
        self.Script += ["SetTitleMatchMode, 2"]
        self.Script += ["WinMaximize, " + title]
        self.LogMessage("success")
        self.RunScript()
        return True if self.Log[0] in ['success'] else False


    def ClickImageList(self, images, wait_for, offset_x = 0.5, offset_y = 0.5):
        time_left = wait_for

        for img in images:
            if img not in self.ImgSize:
                print "Image: " + img + " " + "file_not_found"
                return False

        result, x, y = '', 0, 0
        while result not in ['success']:
            if time_left <= 0:
                return False

            for img in images:
                img_width, img_height = self.ImgSize[img]
                result, x, y = self.FindImage(img)
                if result in ['success']:
                    x += int(img_width * offset_x)
                    y += int(img_height * offset_y)
                    self.MoveAndClick(x, y)
                    self.RunScript()
                    return True

            time.sleep(1)
            time_left -= 1

        return False


    def ClickImageMaxWait(self, img, wait_for, offset_x = 0.5, offset_y = 0.5):
        if img not in self.ImgSize:
            print "Image: " + img + " " + "file_not_found"
            return False

        img_width, img_height = self.ImgSize[img]

        result, x, y = self.FindImage(img)
        time_left = wait_for
        while result != 'success':
            if time_left <= 0:
                return False
            time.sleep(1)
            time_left -= 1
            result, x, y = self.FindImage(img)

        x += int(img_width * offset_x)
        y += int(img_height * offset_y)

        self.MoveAndClick(x, y)
        self.RunScript()
        return True

    def ImageOnScreenMaxWait(self, img, wait_for):
        result, x, y = self.FindImage(img)
        time_left = wait_for
        while result != 'success':
            if time_left <= 0:
                return False
            time.sleep(1)
            time_left -= 1
            result, x, y = self.FindImage(img)
        return True

    def GrabScreenText(self, wait_for):
        self.ClearScript()
        self.Script += ["clipboard = ; Empty the clipboard"]
        self.Script += ["Send, ^a"]
        self.Script += ["Send, ^c"]
        self.Script += ["ClipWait, {}".format(wait_for)]
        self.Script += ["if ErrorLevel"]
        self.Script += ["{"]
        self.LogMessage("clip_fail")
        self.Script += ["ExitApp"]
        self.Script += ["}"]
        self.LogMessage("clip_success`n")
        self.LogMessage("%clipboard%")
        self.RunScript()

        result = self.Log[0]
        if result in ["clip_success"]:
            if len(self.Log) > 1:
                return True, self.Log[1:]

        return False, []


    def ClickImageWhenAppears(self, img):
        result, x, y = self.FindImageCenter(img)
        while result != 'success':
            time.sleep(1)
            result, x, y = self.FindImageCenter(img)
        self.MoveAndClick(x, y)
        self.RunScript()

    def FindImageCenter(self, img):
        if img not in self.ImgSize:
            return "file_not_found", 0, 0

        result, width, height = self.FindImage(img)
        img_width, img_height = self.ImgSize[img]
        if result in ['success']:
            width += (img_width / 2)
            height += (img_height / 2)

        return result, width, height

    def FindImage(self, img):
        self.ClearScript()
        self.Script += ["ImageSearch, FoundX, FoundY, 0, 0, A_ScreenWidth, A_ScreenHeight, " + self.CurrentDirectory + self.GlobalFolderImg + img]
        self.Script += ["if ErrorLevel = 2"]
        self.Script += ["{"]
        self.LogMessage("search_failed")
        self.Script += ["ExitApp"]
        self.Script += ["}"]
        self.Script += ["else if ErrorLevel = 1"]
        self.Script += ["{"]
        self.LogMessage("not_found")
        self.Script += ["ExitApp"]
        self.Script += ["}"]
        self.Script += ["else"]
        self.Script += ["{"]
        self.LogMessage("success`n")
        self.LogMessage("%FoundX%`n")
        self.LogMessage("%FoundY%`n")
        self.Script += ["}"]
        self.RunScript()
        result = self.Log[0]
        if result in ['success']:
            return result, int(self.Log[1]), int(self.Log[2])
        else:
            print "Image: " + img + " " + result
            return result, 0, 0


    def MouseMove(self, x, y):
        self.Script += ["MouseMove {}, {}".format(x,y)]

    def Click(self, x, y):
        self.Script += ["Click {}, {}".format(x,y)]

    def ClickRight(self):
        #self.Script += ["Click {}, {} right".format(x,y)]
        self.Script += ["Click right"]

    def MoveAndClick(self, x, y):
        self.MouseMove(x, y)
        self.Click(x, y)

    def AppendExit(self):
        self.Script += ["ExitApp", "Escape::"]
        self.LogMessage("exit")
        self.Script += ["ExitApp", "Return"]


    def Send(self, text):
        self.Script += ["Send " + text]

    def SendTab(self):
        self.Script += ["Send {Tab}"]

    def SendSpace(self):
        self.Script += ["Send {Space}"]

    def SendEnter(self):
        self.Script += ["Send {Enter}"]

    def SendDown(self):
        self.Script += ["Send {Down}"]

    def SendUp(self):
        self.Script += ["Send {Up}"]

    def SendRight(self):
        self.Script += ["Send {Right}"]

    def SendLeft(self):
        self.Script += ["Send {Left}"]

    def SendCtrlA(self):
        self.Script += ["Send, ^a"]

    def SendCtrlC(self):
        self.Script += ["Send, ^c"]

    def SendCtrlV(self):
        self.Script += ["Send, ^v"]

    def SendPageDown(self):
        self.Script += ["Send {PgDn}"]

    def SendPageUp(self):
        self.Script += ["Send {PgUp}"]

    def SendF5(self):
        self.Script += ["Send {F5}"]

    def SendAltF4(self):
        self.Script += ["Send !{F4}"]

    # http://apple.stackexchange.com/questions/124134/deselect-text-using-keyboard-shortcut-or-prevent-selection-of-word-link-on-right
    # Ctrl - Shift - Home --> Deselects all text
    def DeselectAll(self):
        self.Script += ["Send ^+{Home}"]

    def Sleep(self, time):
        self.Script += ["Sleep, " + str(time)]






