'''
Created on 2014-3-17

@author: Administrator
'''
#from getAttrs import getFile
import models

import ConfigParser
import copy



class graphPath(object):
    
    crossFrom = [i for i in range(0,models.MAX)] 
    crossTo = [[] for i in range(models.MAX)]
    crossToNoLoop = [[] for i in range(models.MAX)]
    corners = 0
    instructCount = [[0 for j in range(128)]for i in range(128)]
    
    def __init__(self, crossTo=[[]], crossToNoLoop=[[]], corners=0):
        
        self.crossTo = crossTo
        self.crossToNoLoop = crossToNoLoop
        self.corners = corners
        
        
        '''
        crossFrom is source vertex
        crossTo id target vertex
        '''
        
    def setCrossInfo(self, cfg):
        conf = ConfigParser.ConfigParser()
        #fetch the configuration which includes filename 
        conf.read(cfg)
        
        filename = conf.get("file", "filename")
        #fileType = conf.get("type", "graphtype")
        #filename = conf.get("file", "call_flow")
        fileType = conf.get("type", "graphtype")
        
        filename = filename[filename.rfind('\\')+1:].replace('.gdl','')
        print "file is %s\n" % filename
        
        results = models.Edge.getAll(filename,fileType)
        print results
        
        if "flow_graph" not in conf.get("type", "graphtype"):            
            return False
        #flow_graph
        else:
            cur = 0
            for each in results:
                if each[0]==cur:
                    pass
                # get the number of crossCorners
                else:
                    # each[0] is the source vertex
                    cur = each[0]
                    self.corners += 1
            print "corner is %d " % self.corners   
            
            self.crossTo = [[] for i in range(models.MAX)]
            self.crossToNoLoop = [[] for i in range(models.MAX)]
            
            i = 0            
            row = 0
            # i is each row of the results from sql
            while i < len(results):
                #print "curNode is %d" % curNode
                print "i is %d" % i                
                # next result has the same source
                # results[i][0] is the i'th edge's source vertex
                if results[i][0]==row:
                    self.crossTo[row].append(int(results[i][1]))                        
                    i += 1
                else:
                    # the results of curNode+1 does not exist
                    # not consequential case should assign null to the values between them
                    if int(results[i][0]) > row+1:                        
                        for j in range(row+1,int(results[i][0])):
                            self.crossTo[j]=[]
                            row += 1
                        #row = int(results[i][0])
                    # consequential case a new node is added   
                    else:    
                        #print "lenth %d is %d" % (row, len(self.crossTo[row]))
                        row = int(results[i][0])                    
                        self.crossTo[row].append(int(results[i][1]))  
                        #print self.crossTo                                       
                        # row steps forward
                    i += 1
                #print "self.crossFrom.count(-1) is %d" %self.crossFrom.count(-1)
            
            print "self.crossTo is"
            print self.crossTo
            ''' 
            for eachRow in self.crossTo:
                    print eachRow
                    for eachElement in eachRow:
                        if self.crossFrom.count(eachElement)==0:
                            print "no source case"
                            self.crossFrom.append(eachElement)
                            self.crossTo[eachElement]=[]
            
            '''
            # we should deep copy the elements of crossTo
            self.crossToNoLoop = copy.deepcopy(self.crossTo)
            print "now crossToNoLoop is"
            print self.crossToNoLoop
            
                
    def mergeCrossInfo(self, cfg):
        
        self.crossTo = [[] for i in range(models.MAX)]
                
        conf = ConfigParser.ConfigParser()
        #fetch the configuration which includes filename 
        conf.read(cfg)
        # get the count of sub files in the configuration
        fileCount = conf.get("count", "fileCount")
        print "fileCount is %d" %int(fileCount)
        for subCount in range(0,int(fileCount)):
            
            filename = conf.get("file", "filename"+str(subCount))
            fileType = conf.get("type", "graphtype")
            
            variantOffset = filename[filename.rfind('-'):filename.rfind('\\')]
            variantOffset = variantOffset.replace('-','_')
            
            filename = filename[filename.rfind('\\')+1:].replace('.gdl','')
            filename += variantOffset
            
            results = models.Edge.getAll(filename,fileType)
            
            if "flow_graph" not in conf.get("type", "graphtype"):            
                return False
            #flow_graph
            else:
                cur = 0
                for each in results:
                    if each[0]==cur:
                        pass
                    # get the number of crossCorners
                    else:
                        # each[0] is the source vertex
                        cur = each[0]
                        self.corners += 1
                i = 0            
                row = 0
                # i is each row of the results from sql
                while i < len(results):
                    #print "curNode is %d" % curNode
                    # next result has the same source
                    # results[i][0] is the i'th edge's source vertex
                    
                    if results[i][0]==row:
                        if int(results[i][1]) not in self.crossTo[row]:
                            self.crossTo[row].append(int(results[i][1]))
                        self.instructCount[row][int(results[i][1])] += 1                    
                        i += 1
                    else:
                        # the results of curNode+1 does not exist
                        # not consequential case should assign null to the values between them
                        if int(results[i][0]) > row+1:
                            pass    
                            '''              
                            for j in range(row+1,int(results[i][0])):
                                self.crossTo[j]=[]
                                row += 1
                            '''
                            #row = int(results[i][0])
                        # consequential case a new node is added   
                        else:    
                            #print "lenth %d is %d" % (row, len(self.crossTo[row]))
                            
                            row = int(results[i][0])                    
                            if int(results[i][1]) not in self.crossTo[row]:
                                self.crossTo[row].append(int(results[i][1]))  
                            self.instructCount[row][int(results[i][1])] += 1                                       
                            # row steps forward
                        i += 1
                    #print "self.crossFrom.count(-1) is %d" %self.crossFrom.count(-1)
                
                print "self.crossTo is"
                print self.crossTo
            ''' 
            for eachRow in self.crossTo:
                    print eachRow
                    for eachElement in eachRow:
                        if self.crossFrom.count(eachElement)==0:
                            print "no source case"
                            self.crossFrom.append(eachElement)
                            self.crossTo[eachElement]=[]
            
            # remove redundant list numbers
            for i in range(len(self.crossFrom),models.MAX):
                #print "rm loop i is %d" % i
                self.crossTo.pop()
            
            # we should deep copy the elements of crossTo
            self.crossToNoLoop = copy.deepcopy(self.crossTo)
            print "now crossToNoLoop is"
            print self.crossToNoLoop 
            '''
        return self.crossTo           
            
        
    def removeLoops(self,condition=1):
        # condition = 1 means upper omission
        #            -1 means lower omission
        for i in range(len(self.crossFrom)):
            print "remove i is %d" % i
            for j in range(len(self.crossTo[i])):
                print "remove j is %d" % j,
                print ''
                print 'crossTo[%d][%d] is %d' % (i,j,self.crossTo[i][j])
                if condition==1:
                    if self.crossTo[i][j] <= self.crossFrom[i]:
                        self.crossToNoLoop[i].remove(self.crossTo[i][j])
                elif condition==-1:
                    if self.crossTo[i][j] >= self.crossFrom[i]:
                        self.crossToNoLoop[i].remove(self.crossTo[i][j])
        print "current crossToNoLoop is"
        print self.crossToNoLoop
           
    def getPathFromMatrix(self):
        
        matrix = [[0 for i in range(len(self.crossFrom)+1)] for j in range(len(self.crossFrom)+1)]
        path = []
        
        for i in range(len(self.crossFrom)):
            for j in range(len(self.crossTo[i])):
                matrix[self.crossFrom[i]][self.crossTo[i][j]] = 1
                
        for i in range(len(self.crossFrom)+1):
            for j in range(len(self.crossFrom)+1):
                # , will avoid print /n
                print matrix[i][j],                
            print ''
        '''
        row = 0        
        column = len(self.crossFrom)
        print len(self.crossFrom)
        while row <= len(self.crossFrom):
            if row == len(self.crossFrom):
                break
            column = len(self.crossFrom)
            while column > row :
                print "row is %d" % row
                print "column is %d" % column                
                if matrix[row][column]==1:
                    path.append(column)
                    row = column
                    break
                else:
                    column -= 1
        print path
        '''
        return matrix
    
    def getPath(self):
        matrix = self.getPathFromMatrix()
        path = [[0 for m in range(len(self.crossFrom))] for n in range(len(self.crossFrom))]
        for i in range(len(self.crossFrom)):
            path[0][i] = matrix[0][i]
        for j in range(len(self.crossFrom)-1):
            path[j][0] = matrix[j][0]
        for i in range(1,len(self.crossFrom)):
            for j in range(1,len(self.crossFrom)):
                for k in range(len(self.crossFrom)):
                    path[i][j] += path[i][k]*path[k][j]
        print path

'''       
    def getMyPaths(self):
        allNum = 1
        # this is auxiliary diction for the map of source and it's position 
        auxList = {}
        # This is the current sum of each cursor of crossTo[fromCursor]
        fromEach = []
        for i in range(len(self.crossFrom)):
            auxList[str(self.crossFrom[i])]= str(i)            
            fromEach.append(int(0))
        print auxList
        
        print "auxList is %s" % auxList
        
        for i in range(len(self.crossFrom)):
            eachNum = len(self.crossTo[i])
            allNum *= eachNum
        print "all number is %d" % allNum
        start = self.crossFrom[0]
        end = self.crossTo[len(self.crossFrom)-1][0]
        path = [[] for i in range(allNum)]  
        # fromCursor memorizes current position of source       
        fromCursor = start
        tmpCursor = 0
        cross = 0
        
        while cross < allNum:
            while fromCursor < len(self.crossFrom)-1:
                print "tmpCursor is %d " % tmpCursor
                
                print "p fromCursor is %d" % fromCursor
                
                # if the continuous 3 are same then break
                if len(path[cross])>=3 and \
                path[cross][len(path[cross])-2]==path[cross][len(path[cross])-3]\
                        ==path[cross][len(path[cross])-1]:
                    fromCursor = tmpCursor
                    
                else:
                    # add the source to the path
                    path[cross].append(self.crossFrom[fromCursor])
                # traverse every target in crossTo
                print "len is %d" % len(self.crossTo[fromCursor])            
                #for fromEach in range(len(self.crossTo[fromCursor])):
                
                while fromEach[fromCursor] < len(self.crossTo[fromCursor]):
                    print "each is %d" % fromEach[fromCursor]
                    print "fromCursor is %d" % fromCursor
                    # if the continuous 3 are same then break
                    if self.crossTo[fromCursor][fromEach[fromCursor]]\
                    ==path[cross][len(path[cross])-1]:                   
                        
                        if len(path[cross]) >= 3\
                        and path[cross][len(path[cross])-2]==path[cross][len(path[cross])-3]\
                            ==path[cross][len(path[cross])-1]:
                            fromCursor = tmpCursor
                            if tmpCursor==fromCursor:
                                fromEach[fromCursor] += 1     
                                            
                    # add the target to the path
                    path[cross].append(self.crossTo[fromCursor][fromEach[fromCursor]])
                    #fromEach[fromCursor] += 1
                    
                    if not auxList.get(str(self.crossTo[fromCursor][fromEach[fromCursor]])):
                        cross += 1
                        fromEach[fromCursor] += 1
                        path[cross].append(start)
                        print "if"
                        continue
                    else:
                    #get the position of the target which is the next path's start                    
                        tmpCursor = fromCursor                    
                        fromCursor = int(auxList.get(str(self.crossTo[fromCursor][fromEach[fromCursor]])))                    
                        fromEach[tmpCursor] += 1
                        if tmpCursor==fromCursor:
                            fromEach[fromCursor] = 0
                        
                        print "fromCursor is %d" % fromCursor
                    print "in path"
                    print path[cross]
                
            print path[cross]
            cross += 1
            fromCursor = start
''' 
        
class Stack:
    def __init__(self,s=[],value=0,top=0):
        self.s = s
        self.value = value
        self.top = top
        
    def pop(self):
        value = int(self.s.pop())
        self.top -= 1
        return value
    
    def push(self,value):
        self.s.append(value)
        self.top += 1

def Indegree(crossFrom,crossTo):
    
    indegree = [0 for i in range(len(crossFrom))]
    
    print 'prev indegree',
    print indegree
    print 'crossFrom',
    print crossFrom
    print 'crossTo',
    print crossTo
    print len(crossTo)
    for i in range(0,len(crossFrom)):
        for j in range(0,len(crossTo[i])): 
            print "i is %d  j is %d" % (i,j)           
            indegree[crossTo[i][j]] += 1
    print 'after indegree',
    print indegree
    return indegree

def TopologicalSort(crossFrom,crossTo):
    path = []
    indegree = Indegree(crossFrom,crossTo)
    ss = Stack()
    for i in range(len(indegree)):
        if indegree[i]==0:
            ss.push(crossFrom[i])
    count = 0
    print ss.s
    while len(ss.s)>0:
        i = ss.pop()
        path.append(i)
        print i
        count += 1
        for j in range(len(crossTo[i])):
            indegree[crossTo[i][j]] -= 1
            if indegree[crossTo[i][j]] == 0:
                ss.push(crossTo[i][j])
    path.reverse()
    if count < len(crossFrom):
        return -1
    else:
        return path
'''
crossFrom = [0,1,2,3,4]
crossTo=[[1,2],[],[3,4],[4],[]]
TopologicalSort(crossFrom,crossTo)   
''' 
            
            
        
        