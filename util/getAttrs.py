'''
This is the main method
'''
import os

import getAttr1, extractPaths, models, refinedData

# Globals

# All system calls from the call flow graph ordered by mapped number in edge field
allSysCalls = {}
# All subroutine calls from the call flow graph
allSubCalls = {}
# 32 objects
instructObjects = []
# 4 operations
instructOperations = []
# Each line shows the specific operations in the system calls of the whole program 
# mapped to the 4 object is the same
operationMap = [[]for i in range(4)]
objectMap = [[]for i in range(32)]
instructMatrix = [[]for i in range(128)]
# subroutine numbers
subCount = 0

utils = getAttr1.MyUtils()
# Configuration
configDir = os.getcwd()+r"\..\config\\"
configFile = configDir+"conf.cfg"
flowGraphFile = configDir+"Files_a"
instructionFile = configDir+"InstructionInfo"
instructionMapFile = configDir+"object_operationMap"
# Graph configuration
subGraphDir = os.getcwd()+r"\..\graph\flowGraph\netsky-a\\"
subGraphDir = subGraphDir[:-1]

# 1. Get all system calls from the whole program
allSysCalls = utils.getAllSysCalls(configFile)
print "allsys length is %d" % allSysCalls.__len__()

# Get the 4 oprations and 32 objects from InstructionInfo
print instructionFile
utils.initMap(instructionFile, instructionMapFile)


refinedData.Instruction.createTable(configFile)


utils.generateExtractedSysCall(instructionFile)
instructionObjects = utils.extractedObjects
instructionOperations = utils.extractedOperations
# Convert the system calls into 32*4 mapping table
utils.sysToExtMap(utils.getFile(configFile).get("file","call_flow"))


operationMap = utils.operationMap
objectMap = utils.objectMap
instructObjects = utils.objectItem
instructOperations = utils.operationItem

print "instructObjects are as below"
print instructObjects

print "instructOperations are as below"
print instructOperations

print "operationMap are as below"
print operationMap

print "objectMap are as below"
print objectMap

# 2. Get all subroutine's system calls
allFiles = utils.traverseDir(subGraphDir)

# write all flow graph files into /config directory
utils.writeAllFiles(subGraphDir, "a", "function_call_graph")

print "2500"
count = int(utils.getFile(flowGraphFile).get("count", "fileCount"))
for cursor in range(0,count):
    
    utils.getSysCallsFromDB(utils.getFile(configFile).get("file", "call_flow"), \
                            utils.getFile(flowGraphFile).get("file", "filename"+str(cursor)))

print "2501"

fileCount = allFiles.__len__()
# each element of the list stores a subroutine's system calls 
subSysCalls = [{} for i in range(0,fileCount)]

print 0
i = 0
for eachFile in allFiles:
    print "eachFile is %s" % eachFile
    subSysCalls[i] = utils.getCalls(eachFile, "syscall")
    i += 1


'''
print "before init"
for cursor in range(0, fileCount):
    print flowGraphFile
    utils.edge_fc_Init(flowGraphFile, cursor)
print "after init"


paths = extractPaths.graphPath()
fileDir = configDir+"Files_a"
print "fileDir is %s" % fileDir
instructMatrix = paths.mergeCrossInfo(fileDir)
# calculate the count of each edge
countRight = paths.instructCount


for i in range(0,models.MAX):    
    for j in range(0,instructMatrix[i].__len__()):
        instruction = refinedData.Instruction(i,instructMatrix[i][j],countRight[i][int(instructMatrix[i][j])])
        instruction.addData(configFile)
    
       
#path = extractPaths.TopologicalSort(paths.crossFrom, paths.crossToNoLoop)

print "next is path"
for each in instructMatrix:
    print each
print "prev is path"

for eachCount in countRight:
    print eachCount
'''
#paths.setCrossInfo(fileDir)

'''
paths.removeLoops()
path = extractPaths.TopologicalSort(paths.crossFrom, paths.crossToNoLoop)
print "next is path"
print path
print "prev is path"
'''
