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
'''
    Getting params from user
'''
try:
    _fileName=sys.argv[1]
except:
    print("First argument is mandatory, and should be the 'fileName' contain all required classes")
    exit()
try:
    _prodNumber=sys.argv[2]
except:
    print("Second argument is mandatory, and should be 'PROD/SD number'")
    exit()
try:
    _buildNumber=sys.argv[3]
except:
    print("Third argument is mandatory, and should be 'Build number'")
    exit()


'''
    Initialize the log file
'''
log_file = open(logFile,"w")
sys.stdout = log_file
print()
print("Start to create a Patch by %s file, PROD/SD=%s, BUILD=%s]"%(_fileName, _prodNumber, _buildNumber))


'''
    Start Here
'''
if not isFileExist(_fileName.strip()):
    print("File name {} doesn't exist in current directory!\nFAILED".format(_fileName))
    exit()

# create base directory for the patch
_baseDir = "Patch.PROD_" + str(_prodNumber) + ".build_" + str(_buildNumber) + "." + _datetime
if not createDir(_baseDir):
    print( "couldn't create a new directory {}\nFAILED".format(_baseDir))
# open file and loop over classes name
with open(_fileName) as f:
    classFiles = f.readlines()
    print("Packing the following Classes:\n")
    # Validate the classFile exist
    for className in classFiles:
        classFile = className.strip()
        if not isFileExist(classFile):
            print("Java class in path: {} doesn't exist!\nFAILED ".format(classFile) )
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
                print("Couldn't create a new directory {}\nFAILED".format(targetFullDir))
                exit()

    shutil.move(logFile, "{}/{}".format(_baseDir, logFile.replace(".log", ".txt"))
    print("\nArchive Patch to: {}.zip".format(_baseDir))
    archiveFolder(_baseDir, _baseDir)
    print("Delete the src Directory\nPATCH - SUCCESS")
    deleteFolder(_baseDir)

log_file.close()
