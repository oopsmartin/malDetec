'''
Created on 2014-5-16
    
@author: oopsmartin
'''
import os,re
import ConfigParser, copy
import models, extractPaths
    #import pickle, StringIO
    
class MyUtils(object):
    
    # globals
    extractedObjects = {}
    extractedOperations = {}
    allSysCalls = []    
    objectItem = []
    operationItem = []
    
    operationMap = [[]for i in range(4)]
    objectMap = [[]for i in range(32)]
    
    specInstructionMap = {}
    specObjMap = {}
    specOptMap = {}
    
    def __init__(self):
        print "initialed!!!"
    
    @staticmethod
    def getFile(filename):
        #print os.getcwd()
        conf = ConfigParser.ConfigParser()
        #fetch the configuration which includes filename     
        conf.read(filename)
        
        return conf
    
    # callType is the type of calls between system-call and subroutine-call 
    
    def getCalls(self,filename, callType):
        
        print "in getCalls %s" % filename
        mapping = {}
        if ":" not in filename:
            print "getCalls %s" % os.getcwd()+filename[1:-1]
            f = open(os.getcwd()+filename[1:-1],'rb')
            
        else:
            f = open(filename, 'rb')
        
        
        allLines = f.readlines()
        eachCalls = []
        
        for eachLine in allLines:
            
            # get the vertexID of each block
            if ("{" in eachLine) and ("title" in eachLine):
                titleStart = eachLine.find('title:')
                #print "start is %d" % (titleStart+"title:".__len__())
                titleEnd = eachLine.find('label:')
                #print "end is %d" % titleEnd
                title = int(eachLine[titleStart+"title:".__len__()+2:titleEnd-2])
                #print "title is %s" % title
                eachCalls = []
            # find the calls
            if "call" in eachLine:
                
                callStart = eachLine.find('call')
                
                if '}' in eachLine:
                    callEnd = eachLine.find('"')
                else:
                    callEnd = -1
                content = eachLine[callStart+"call".__len__():callEnd].lstrip().rstrip()
                
                # get the system calls
                if "syscall" in callType:
                    # Omit subroutines
                    if "sub" in content:
                        pass
                    # call edi,esi,eax... closeActions
                    elif ";" in content:
                        callStart = content.find(";")
                        realContent = content[callStart+1:].lstrip().rstrip()
                        print "realContent is %s" % realContent
                        eachCalls.append(realContent)
                        mapping[title] = eachCalls
                    # generic call e.g call WSAStartup...
                    else:
                        eachCalls.append(content)
                        mapping[title] = eachCalls
                
                # get the subroutine calls
                else:                
                    # call subroutines e.g call sub_30104
                    if "sub" in content:
                        callStart = content.find("sub_")
                        realContent = content[callStart:].lstrip().rstrip()
                        print "realContent is %s" % realContent
                        eachCalls.append(realContent)
                        mapping[title] = eachCalls
                    # operational call e.g call edi.esx...
                    # and generic call e.g call WSAStartup...
                    else:
                        pass
                        
        return mapping
    
    # collect all system calls appeared in flow graph files named filename
    
    def getAllSysCalls(self,filename):
        print "filename is %s" % filename    
        conf = self.getFile(filename)
        s = conf.sections()
        attrFile = conf.get("file", "call_flow")
        f = open(os.getcwd()+attrFile,'rb')
        allLines = f.readlines()
        
        for eachLine in allLines:
            if "node:" in eachLine:
                if "green" in eachLine:
                    continue;
                colorStart = eachLine.find("color:")
                colorEnd = eachLine.find("textcolor:")
                colorEnd1 = eachLine.find("bordercolor:")
                if colorEnd > 0:
                    color = int(eachLine[colorStart+"color:".__len__():colorEnd].rstrip().lstrip())
                elif colorEnd1 > 0:
                    color = int(eachLine[colorStart+"color:".__len__():colorEnd1].rstrip().lstrip())
                else:
                    color = 76
                # 76 represents black which represents subroutines
                # exclude all subroutines so system calls remain
                if color != 76:
                    IDstart = eachLine.find("label:")
                    IDend = eachLine.find("color:")
                    content = eachLine[IDstart+"label:".__len__():IDend].lstrip().rstrip()
                    self.allSysCalls.append(content[1:-1])    
        print "all sys calls size is:"
        print self.allSysCalls
        '''
        # create table in it
        attrFile = attrFile.replace('.gdl','')
        models.callSys.createTable(attrFile)
        '''
        return self.allSysCalls
        
      
    
    
    # get the extracted info from configure InstructionInfo
    
    def initMap(self,filename,mapFile):
        
        #setExtractedCall(filename):    
        models.ExtractedInstruction.createTable()    
        
        conf = self.getFile(filename)    
        for i in range(0,4):
            self.extractedOperations[i] = conf.get("operation", "%d" % i)
        for j in range(0,32):
            self.extractedObjects[j]=conf.get("object", "%d" % j)
        
        for k in range(0,4):
            for m in range(0,32):
                extInstruction = \
                models.ExtractedInstruction\
                (m,k,self.extractedObjects.get(m),\
                 self.extractedOperations.get(k))
                
                extInstruction.addData()
        
        
        mapfile = open(mapFile)
        lines = mapfile.readlines()
        flag = -1
        for eachLine in lines:
            if "[instruction]" in eachLine:
                flag = 0
            elif "[object]" in eachLine:
                flag = 1
            elif "[operation]" in eachLine:
                flag = 2
            else:
                # spec instruction
                if flag==0:
                    splitPos = eachLine.find("=")                
                    specInstruction = eachLine[:splitPos]
                    specNumber = int(eachLine[splitPos+1:])
                    print "spec instruction number are:"
                    print "%s %d" % (specInstruction, specNumber)
                    self.specInstructionMap[str(specInstruction)] = specNumber
                # spec object
                elif flag==1:
                    splitPos = eachLine.find("=")                
                    specObject = eachLine[:splitPos]
                    specNumber = int(eachLine[splitPos+1:])
                    print "spec object number are:"
                    print "%s %d" % (specObject, specNumber)
                    self.specObjMap[str(specObject)] = specNumber
                #spec operation
                elif flag==2:
                    splitPos = eachLine.find("=")
                    specOperation = eachLine[:splitPos]
                    specNumber = int(eachLine[splitPos+1:])
                    print "spec operation number are:"
                    print "%s %d" % (specOperation, specNumber)
                    self.specOptMap[str(specOperation)] = specNumber
    
    # Set system calls to extracted instructions and store them in database
    def sysToExtMap(self,filename):
        
        print "allSysCalls length is %d" % self.allSysCalls.__len__()
        print self.extractedObjects
        models.SystemCall.createTable(filename)
           
        if (self.allSysCalls.__len__()!=0) and len(self.extractedObjects)>0:
            
            cursor = 0
            objectFlag = False
            operationFlag = False     
            while cursor < len(self.allSysCalls):
                objectFlag = False
                operationFlag = False  
                objCursor = -1
                optCursor = -1       
                print "syscall is "+self.allSysCalls[cursor]
                for j in range(0,32):
                    if re.search(str(self.extractedObjects.get(j)) , self.allSysCalls[cursor], re.IGNORECASE):
                        self.objectMap[j].append(cursor)
                        objectFlag = True
                        objCursor = j
                        print "obj in objectMap ++"
                        break
                        
                for j in range(0,4):
                    if re.search(str(self.extractedOperations.get(j)) , self.allSysCalls[cursor], re.IGNORECASE):
                        self.operationMap[j].append(cursor)
                        operationFlag = True
                        optCursor = j
                        print "opt in operationMap ++"
                        break
                
                if objectFlag == False or operationFlag == False:
                    flagInstruct = False
                else:
                    flagInstruct = True
                
                # specific instructions the key and values are reversed
                if (objectFlag==False) or (operationFlag==False):
                    for key,value in self.specInstructionMap.items():
                        if re.search(str(key), self.allSysCalls[cursor], re.IGNORECASE):
                            if cursor not in self.objectMap[value/10]:
                                self.objectMap[value/10].append(cursor)
                                objCursor = value/10
                            if cursor not in self.operationMap[value%10]:
                                self.operationMap[value%10].append(cursor)
                                optCursor = value%10
                            print "spec  ++"
                            flagInstruct = True
                            break
                if (flagInstruct==False) and (objectFlag==False):
                    for key,value in self.specObjMap.items():
                        if re.search(str(key), self.allSysCalls[cursor], re.IGNORECASE):
                            self.objectMap[value].append(cursor)
                            objCursor = value
                            objectFlag = True
                            print "spec obj ++"
                            break
                if (flagInstruct==False) and (operationFlag==False):           
                    for key,value in self.specOptMap.items():
                        if re.search(str(key), self.allSysCalls[cursor], re.IGNORECASE):
                            self.operationMap[value].append(cursor)
                            optCursor = value
                            operationFlag = True
                            print "spec opt ++"
                            break
                
                # not all are included in object nor operation then delete it            
                if (operationFlag==False) or (objectFlag==False):
                    print "remove case"
                    for each in self.objectMap:
                        if cursor in each:
                            each.remove(cursor)
                            objectFlag = False
                            print "object removed"
                    for each in self.operationMap:
                        if cursor in each:
                            each.remove(cursor)
                            operationFlag = False
                            print "operation removed"
                print flagInstruct
                print objectFlag
                print operationFlag
                if flagInstruct==True or objectFlag==True:
                    
                    systemCall = models.SystemCall(objCursor, optCursor, self.allSysCalls[cursor])
                    systemCall.addData(filename)
                    
                cursor += 1
    
    # get system calls from database
    def getSysCallsFromDB(self, sysCallFile, filename):
        
        
        print "filname is %s" % filename
        sysCallNames = self.getCalls(filename, "syscall")
        print "sysCallNames are"
        print sysCallNames
        filename = "_"+filename[filename.rfind('-')+1:]
        filename = filename.replace('\\','_')
       
        for eachKey in sysCallNames.keys():
            for systemCall in sysCallNames.get(eachKey):
                print systemCall
                print filename
                models.Edge.createTable(filename, "function_call_graph")
                print "already"
                callInfo = models.SystemCall.searchData(sysCallFile, systemCall)
                if callInfo.__len__() > 0 :
                    
                    print callInfo                    
                    fc_edge = models.Edge(int(eachKey), int(callInfo[0][0]), int(callInfo[0][1]))
                    fc_edge.addData(filename, "function_call_graph")
                    print "ok"
        
    # get the call sequence of the file named filename
    def callSequence(self, filename, fileType, callType):
        order = []
        callMapping = self.getCalls(filename,callType)
        
        callResults = models.CallSys.getAll(filename, fileType)
        for eachLine in callResults:
            print eachLine
            order.append(self.path.index(int(eachLine[0])))
        print order
        
        # get the call sequence
        callSequence = []
        
        while order.count(100)<len(order):
            tmpMin = order[0]
            i = 0
            while i<len(order):
                if order[i] < tmpMin:
                    tmpMin = order[i]            
                    #print "i is %d " % i             
                else:
                    i += 1
            #100 is a flag var
            
            while (order.count(tmpMin)!=0) and (tmpMin != 100):
                order[order.index(tmpMin)] = 100;
                print order
            #print "order.count(100) is %d" % order.count(100)
            #print "path.index(tmpMin) is",
            #print path.index(tmpMin)
            callSequence.append(callMapping.get(self.path[tmpMin]))
        return callSequence
    
    # generate extracted system calls table
    
    def generateExtractedSysCall(self, syscallConfig):
        
        conf = self.getFile(syscallConfig)
        
        for i in range(0,32):
            self.objectItem.append(conf.get("object", "%s" % str(i)))
        for i in range(0,4):
            self.operationItem.append(conf.get("operation", "%s" % str(i)))
        
        models.ExtractedInstruction.createTable()
        
        for j in range(0,4):
            for k in range(0,32):
                extractedInstruction = models.ExtractedInstruction\
                (k,j,self.objectItem[k], self.operationItem[j])
                extractedInstruction.addData()
    
    # traverse the directory of flow graph to get all fg files separated by 
    # subroutines in a variant
    def traverseDir(self, rootDir):
        
        allFiles = []
        
        count = 0
        for lists in os.listdir(rootDir): 
            print lists
            path = os.path.join(rootDir, lists) 
            #print path
            allFiles.append(path)
            count += 1
        
        return allFiles        
    
    def getSubSysCalls(self, rootDir):
                
        count = self.traverseDir(rootDir).__len__()
        
        subSysCalls = [{}for i in range(0,count)]
        
        i = 0
        for lists in os.listdir(rootDir):
            lists = "\""+rootDir[rootDir.find('\..'):]  +lists+"\""
            subSysCalls[i] = self.getCalls(lists,"syscall")
            i += 1
                
        return subSysCalls
    
    def writeAllFiles(self, rootDir, variant, fileType):
        print "250"
        print rootDir
        allFiles = self.traverseDir(rootDir)
        print os.getcwd()+"\\..\\config\\Files_"+variant
        confFile = open(os.getcwd()+"\\..\\config\\Files_"+variant,'wb')
        
        confFile.write("[file]")
        confFile.write("\n")
        i = 0
        for each in allFiles:
            each.replace('\\\\','\\')
            fileDeclare = "filename"+str(i)+"="+each
            confFile.writelines(fileDeclare)
            confFile.write("\n")
            i += 1
        confFile.writelines("[type]")
        confFile.write("\n")
        if "flow_graph" in fileType:
            confFile.write("graphtype=flow_graph")
        else:
            confFile.write("graphtype=function_call_graph")
        confFile.write("\n")
        confFile.writelines("[count]")
        confFile.write("\n")
        confFile.write("fileCount="+str(i))
    
    def callSysInit(self, filename, fileType):
        
        configDir = os.getcwd()+r"\..\config\\"
        sysCallDir = configDir+"conf.cfg"
        sysCallMapping = copy.deepcopy(self.getCalls(sysCallDir,"syscall"))
        
        models.CallSys.createTable(filename)
        
        
    # initialize fg edge and fg vertex
    
    def edge_vertexInit(self, filename, count):
        
        # Inde/Outde represents the list of all InDegrees/OutDegrees
        Inde = [0 for i in range(0,100)]
        Outde = [0 for i in range(0,100)]
        sourceVertex = [-1 for i in range(0,200)]
        targetVertex = [-1 for i in range(0,200)]
        # dict consists the key:vertexID and the value:vertexName
        dict = {}
        
        '''
        edge types is for flow control:
        True: 1(for if  condition and this is true case) 
        pass: 0(for only flow which pass by without switch cases)
        False:-1
        '''
        edgeType = [0 for i in range(0,200)]
        edgeNum = 0
        
        conf = self.getFile(filename)        
        
        attrFile = conf.get("file", "filename"+str(count))
        attrType = conf.get("type", "graphtype")
        
        variantOffset = "_"+attrFile[attrFile.rfind('-')+1:attrFile.rfind('-')+2]+"_"
        
        #f = open(os.getcwd()+attrFile[1:-1],'rb')
        f = open(attrFile,'rb')
        
        #filename = attrFile.replace('\\..\\graph\\','').replace('.gdl','')
        
        attrFile = attrFile[attrFile.rfind('\\')+1:].replace('.gdl','')
        attrFile = variantOffset+attrFile
        #attrFile = "_"+variantOffset+"_"+attrFile
        
        
        print "attrFile in 1 is %s" % attrFile
        print "attrType in 1 is %s" % attrType
        #print "3144 filename is %s" % filename
        models.Edge.createTable(attrFile, attrType)
        models.Vertex.createTable(attrFile, attrType)
        
        allLines = f.readlines()
        i = 0
        for eachLine in allLines:
            
            #get the vertexID -> vertexName
            if 'node:' in eachLine:
                #get the node information
                IDstart = eachLine.find('label:')
                IDend = eachLine.find('color:')
                numS = eachLine.find('title:')
                #-1 consider there is a block
                ID = eachLine[numS+'title:'.__len__():IDstart].lstrip().rstrip()
                print "ID is " + ID       
                #content represents vertexName
                content = eachLine[IDstart+'label:'.__len__():IDend].lstrip().rstrip()
                #save the temporary diction of vertexID and vertexName
                dictTMP = {ID:str(content)}
                #append to the whole dict
                dict.update(dictTMP)
            #get the edge information
            if 'edge:' in eachLine:
                #get the edge information
                start1 = eachLine.find('sourcename:')
                end1 = eachLine.find('targetname:')    
                    
                OutNode = eachLine[start1+'sourcename:'.__len__():end1].lstrip().rstrip()
                print OutNode
                
                if eachLine.find('label:') > 0:
                    end2 = eachLine.find('label:')
                    colorTag = eachLine.find('color:')
                    InNode = eachLine[end1+'targetname:'.__len__():end2].lstrip().rstrip()
                    edgeLabel = eachLine[end2+'label:'.__len__():colorTag].lstrip().rstrip()
                    
                    if 'true' in edgeLabel:
                        edgeType[edgeNum] = 1
                        print 1
                    else:
                        edgeType[edgeNum] = -1
                        print -1
                else:
                    end2 = eachLine.find('}')
                    InNode = eachLine[end1+'targetname:'.__len__():end2].lstrip().rstrip()
                    edgeType[edgeNum] = 0
                
                print InNode
                
                sourceVertex[i] = int(OutNode[1:-1])
                targetVertex[i] = int(InNode[1:-1])
                
                Outde[int(OutNode[1:-1])] += 1        
                Inde[int(InNode[1:-1])] += 1 
                
                i += 1                
                edgeNum += 1
        
        
        print "dict length is %d" %dict.__len__()
        # get each vertex and edge assigned    
        for i in dict.iterkeys():
            print i
            cursor = int(i[1:-1])
            print "cursor is %d" % cursor
            label = dict.get(i)
            mytype = 'notype'
            indegree = Inde[cursor]
            outdegree = Outde[cursor]
            vertex = models.Vertex(cursor, label, mytype, indegree, outdegree)     
            vertex.addData(attrFile,attrType)
            print "vertex added"
            
        for i in range(0,edgeNum):
            edge = models.Edge(sourceVertex[i],targetVertex[i],edgeType[i])
            edge.addData(attrFile,attrType)
            print "edge added"
    
    def getMaxSimilar(self, matrixA, matrixB):
        
        matrix = [[0 for j in range(0,128)] for i in range(0,128)]
        
        for k in (0,128):
            cursor = 0
            if matrixA[k].__len__() >0 or matrixB[k].__len__() > 0:
                for eachA in matrixA[k]:
                    if eachA in matrixB[k]:
                        # get the common element
                        matrix[k][cursor] = eachA
                        cursor += 1
                
        return matrix
    
    # generate system call matrix
    
    def generateSyscallMatrix(self, filename):
        
        filename = "_"+filename[filename.find('-')+1:]
        filename = filename.replace('\\','_').replace('.gdl','')
        print "filename now is %s" % filename
        '''
        PartialOrder = [[0 for i in range(128)]for j in range(128)]
        i = 0
        while(i<32):
            while(j<4):
                pass
        '''
        SourceMap = {}
        TargetMap = {}
        
        edge_fg = models.Edge.getAll(filename, "flow_graph")
        edge_fc = models.Edge.getAll(filename, "function_call_graph")
        
        for each_fg in edge_fg:
            for each_fc in edge_fc:
                if each_fg[0]==each_fc[0]:
                    SourceMap[each_fg[0]] = [each_fc[1],each_fc[2]]
        
        print edge_fg
            
    
    
    ''' 
    configDir = os.getcwd()+r"\..\config\\"
    configFile = configDir+"conf.cfg"
    instructionCFGFile = configDir+"InstructionInfo"
    specCFGMapFile = configDir+"object_operationMap"
    
    models.createDB()
    #getAllSysCalls(configFile)
    
    #initMap(instructionCFGFile,specCFGMapFile)
    
    print "extractedObjects",
    print extractedObjects
    print "extractedOperation",
    print extractedOperations
    #generateExtractedSysCall(instructionCFGFile)
    
    #sysToExtMap(configFile)
    
    #graphDir = configDir+"conf.cfg"
    
    #conf = getFile(graphDir)
    
    #attrFile = conf.get("file", "filename")
    #attrType = conf.get("type", "graphtype")
    
    #f = open(os.getcwd()+attrFile[1:-1],'rb')
    #allLines = f.readlines()
    
    # callTypes are divided into syscall and subroutine
    
    # sysCallMapping is system call mapping
    # subroutineMapping is subroutine mapping
    
    #sysCallDir = configDir+"conf.cfg"
    
    #sysCallMapping = copy.deepcopy(getCalls(sysCallDir,"syscall"))
    
    #print 'subroutines are'
    #subCallDir = configDir+"conf.cfg"
    
    #subroutineMapping = copy.deepcopy(getCalls(subCallDir,"subroutine"))
    #print "mapping length is %d" % subroutineMapping.__len__()
    
    
    if (sysCallMapping.__len__() ==0) and (subroutineMapping.__len__()==0):
        print "None"
        os._exit(0)
    else:
        #initialization
        #dict consists the key:vertexID and the value:vertexName
        dict = {}
        #edgeNum represents the number of edges
        edgeNum = 0
        #Inde/Outde represents the list of all InDegrees/OutDegrees
        Inde = [0 for i in range(0,50)]
        Outde = [0 for i in range(0,50)]
    
        edge types is for flow control:
            True: 1(for if  condition and this is true case) 
            pass: 0(for only flow which pass by without switch cases)
            False:-1
        
        edgeType = [0 for i in range(0,100)]
        sourceVertex = [-1 for i in range(0,50)]
        targetVertex = [-1 for i in range(0,50)]
        
        
        #create database callgraph
        #models.vertex.createDB()    
        
        
        #filename = attrFile.replace('\\..\\graph\\','').replace('.gdl','')
        
        #create tables
        
        models.vertex.createTable(filename, attrType)
        models.edge.createTable(filename, attrType)
        models.callSys.createTable(filename)
        
        
        i = 0
        for eachLine in allLines:    
            #get the vertexID -> vertexName
            if 'node:' in eachLine:
                #get the node information
                IDstart = eachLine.find('label:')
                IDend = eachLine.find('color:')
                numS = eachLine.find('title:')
                #-1 consider there is a block
                ID = eachLine[numS+'title:'.__len__():IDstart].lstrip().rstrip()       
                #content represents vertexName
                content = eachLine[IDstart+'label:'.__len__():IDend].lstrip().rstrip()
                #save the temporary diction of vertexID and vertexName
                dictTMP = {ID:str(content)}
                
                #append to the whole dict
                dict.update(dictTMP)
                
            #get the edge information
            if 'edge:' in eachLine:
                #get the edge information
                start1 = eachLine.find('sourcename:')
                end1 = eachLine.find('targetname:')    
                    
                OutNode = eachLine[start1+'sourcename:'.__len__():end1].lstrip().rstrip()
                print OutNode
                
                if eachLine.find('label:') > 0:
                    end2 = eachLine.find('label:')
                    colorTag = eachLine.find('color:')
                    InNode = eachLine[end1+'targetname:'.__len__():end2].lstrip().rstrip()
                    edgeLabel = eachLine[end2+'label:'.__len__():colorTag].lstrip().rstrip()
                    
                    if 'true' in edgeLabel:
                        edgeType[edgeNum] = 1
                        print 1
                    else:
                        edgeType[edgeNum] = -1
                        print -1
                else:
                    end2 = eachLine.find('}')
                    InNode = eachLine[end1+'targetname:'.__len__():end2].lstrip().rstrip()
                    edgeType[edgeNum] = 0
                
                print InNode
                
                sourceVertex[i] = int(OutNode[1:-1])
                targetVertex[i] = int(InNode[1:-1])
                i += 1
                
                Outde[int(OutNode[1:-1])] += 1        
                Inde[int(InNode[1:-1])] += 1 
                edgeNum += 1
            
        #print dict
        
        i=0
        #file = StringIO.StringIO()
        vertexNum = dict.__len__()
        #get the first node and create table    
        for i in range(0,vertexNum):
            name = dict.get('"'+str(i)+'"')
            mytype = 'notype'
            indegree = Inde[i]
            outdegree = Outde[i]
            vertex = models.vertex(i,mytype,name,indegree,outdegree)     
            vertex.addData(filename,attrType)
            
        for i in range(0,edgeNum):
            edge = models.edge(sourceVertex[i],targetVertex[i],edgeType[i])
            edge.addData(filename,attrType)
            print "edge: s:%d t:%d style:%d" %(sourceVertex[i],targetVertex[i],edgeType[i])
           
        
        for i in range(0,vertexNum):
            print dict.get('"'+str(i)+'"')
            #print "InDegree is %d" % Inde[i]
            #print "OutDegree is %d" % Outde[i]
        
        
        paths = extractPaths.graphPath()
        print "filename is %s" % filename
        fileDir = configDir+"conf.cfg"
        print "fileDir is %s" % fileDir
        paths.setCrossInfo(fileDir)
        #paths.getPath()
        paths.removeLoops()
        #paths.getMyPaths()
        #paths.getPathFromMatrix()
        path = extractPaths.TopologicalSort(paths.crossFrom, paths.crossToNoLoop)
        print "next is path"
        print path
        print "prev is path"
        
        print "sys call mapping is ",
        print sysCallMapping
        
        print "subroutine mapping is ",
        print subroutineMapping    
        
        for key in sysCallMapping.keys():
            for each in sysCallMapping[key]:
                
                syscall = models.callSys(key,each)
                print "attrFile is %s" % attrFile
                syscall.addData(attrFile)
        
        order = []
        callResults = models.callSys.getAll(filename)
        for eachLine in callResults:
            print eachLine
            order.append(path.index(int(eachLine[0])))
        print order
        
        # get the call sequence
        callSequence = []
        
        while order.count(100)<len(order):
            tmpMin = order[0]
            i = 0
            while i<len(order):
                if order[i] < tmpMin:
                    tmpMin = order[i]            
                    print "i is %d " % i             
                else:
                    i += 1
            print "tmpMin is %d" % tmpMin
            
            while (order.count(tmpMin)!=0) and (tmpMin != 100):
                order[order.index(tmpMin)] = 100;
                print order
            print "order.count(100) is %d" % order.count(100)
            print "path.index(tmpMin) is",
            print path.index(tmpMin)
            callSequence.append(sysCallMapping.get(path[tmpMin]))
        
        print callSequence
    '''