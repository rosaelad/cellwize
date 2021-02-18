import sys
import os, errno
from datetime import datetime
import shutil
import fnmatch

'''
    Helper Methods
'''
def getFullPathToFile(path):
    idx=path.rindex("/")
    return path[:idx].strip()

def getFileNameWithExtention(path):
    idx=path.rindex("/") + 1
    return path[idx:].strip()

def getFileName(path):
    fileName=getFileNameWithExtention(path)
    idx=fileName.rindex(".")
    return fileName[:idx].strip()

def getTargetLocation(path):
    idx=path.rindex("/com")
    return path[idx:].strip()

def createDir(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path, 0777)
        except:
            return False
    return True

def archiveFolder(outputName, pathToFolder):
    shutil.make_archive(outputName, 'zip', pathToFolder)

def deleteFolder(directory):
    shutil.rmtree(directory, ignore_errors=True)

def isFileExist(fileName):
    return os.path.exists(fileName)

def getListOfFilesByName(fname, dir):
    list = os.listdir(dir)
    returnList=[]
    for f in list:
        if fname in f:
            returnList.append(f)
    return returnList

def printInfoToLog(text):
    print("[INFO] - {}".format(text))

def printErrorToLog(text):
    print("[ERROR] - {}\nFAILED".format(text))


'''
# This Script Archive a list of Java classes
#
# Written by: Elad Rosenberger
# Date: 16.2.21
#
'''
_datetime=datetime.now().strftime("%d%m%Y_%H%M%S")
suffix = ".java"
logFile = "readme.log"
_type = "PROD"

'''
    Getting params from user
'''
try:
    _fileName=sys.argv[1]
except:
    printErrorToLog("First argument is mandatory, and should be the 'fileName' contain all required classes")
    exit()
try:
    _prodNumber=sys.argv[2]
except:
    printErrorToLog("Second argument is mandatory, and should be 'PROD/SD number'")
    exit()
try:
    _buildNumber=sys.argv[3]
except:
    printErrorToLog("Third argument is mandatory, and should be 'Build number'")
    exit()

'''
    Validate param inputs
'''
if not isFileExist(_fileName.strip()):
    printErrorToLog("File name {} doesn't exist in current directory!".format(_fileName))
    exit()
# Patch Type - SD or PROD
if "=" not in _prodNumber:
    printErrorToLog("Ticket number of the patch should be in p/s=xxxx format. (example p=0012 where p-PROD, s-SD)")
    exit()
else:
    _type = _prodNumber.split("=")[0].lower()
    if _type != "p" and _type != "s":
        printErrorToLog("Patch type must be from a type: s-SD / p-PROD")
        exit()
    _type = "PROD" if _type == "p" else "SD"
    _prodNumber = _prodNumber.split("=")[1]
    printInfoToLog("type: {}, number: {}".format(_type, _prodNumber))

if "=" not in _buildNumber:
    printErrorToLog("Build number of the patch should be in b=xxxx format. (example b=0012 where b-build number)")
    exit()
else:
    if _buildNumber.split("=")[0] != "b":
        printErrorToLog("Build number of the patch should be in b=xxxx format. (example b=0012 where b-build number )")
        exit()
    _buildNumber = _buildNumber.split("=")[1]
    printInfoToLog("build number: {}".format(_buildNumber))

'''
    Initialize the log file
'''
log_file = open(logFile,"w")
sys.stdout = log_file
printInfoToLog("Cellwize Patch Executer\n")
printInfoToLog("Created time: {}".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
printInfoToLog("Start to create a Patch by %s file. params [PROD/SD=%s, BUILD=%s]"%(_fileName, _prodNumber, _buildNumber))

'''
    Start Here
'''
# create base directory for the patch
_baseDir = "Patch.{}_{}.build_{}.{}".format(_type, str(_prodNumber), str(_buildNumber), _datetime)
if not createDir(_baseDir):
    printErrorToLog( "couldn't create a new directory {}".format(_baseDir))
# open file and loop over classes name
with open(_fileName) as f:
    classFiles = f.readlines()
    printInfoToLog("Packing the following Classes:\n")
    # Validate the classFile exist
    for className in classFiles:
        classFile = className.strip()
        if not isFileExist(classFile):
            printErrorToLog("Java class in path: {} doesn't exist!".format(classFile) )
            deleteFolder(_baseDir)
            exit()

    for classFile in classFiles:
        # get the full path to class name
        currDir = getFullPathToFile(classFile)
        # get the class name with extention
        currFileName = getFileNameWithExtention(classFile)
        # check if the file contain a .java/.class suffix and replece if required
        if currFileName.endswith(".java"):
            currDir = currDir.replace("/src/main/java/", "/target/classes/")
            currFile = getFileName(classFile)
            listOfFilesToImport = getListOfFilesByName(currFile, currDir)
        # loop over the .class files relates to .java class and import
        for fn in listOfFilesToImport:
            # full path to class name .class we would like to copy
            fullPathToClassFile = "{}/{}".format(currDir, fn)
            # target of the class name we want to copy
            target = getTargetLocation(fullPathToClassFile)
            targetDir = getFullPathToFile(target)
            # create dir if not exists
            targetFullDir = "{}{}".format(_baseDir,targetDir)
            # create hierarchy for class and copy
            if createDir(targetFullDir):
                print("{}/{}".format(targetFullDir, fn))
                shutil.copy2(fullPathToClassFile, "{}".format(targetFullDir))
            else:
                printErrorToLog("Couldn't create a new directory {}".format(targetFullDir))
                exit()

    shutil.move(logFile, "{}/{}".format(_baseDir, logFile.replace(".log", ".txt")))
    printInfoToLog("\nArchive Patch to: {}.zip".format(_baseDir))
    archiveFolder(_baseDir, _baseDir)
    printInfoToLog("Delete the src Directory\nPATCH - SUCCESS")
    deleteFolder(_baseDir)

log_file.close()
