'''
Created on 2014-3-6

@author: Administrator
'''
import MySQLdb
import sys

MAX = 128

def createDB():
    #create database callgraph
    print 'Im here!'
    try:
        
        conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='test',port=3306)
        cur=conn.cursor()
        cur.execute('create database if not exists callgraph;')
        conn.select_db('callgraph')
        cur = conn.cursor()
        
        conn.commit()
        cur.close()
        conn.close()
        
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1]) 
        
# vertex implies each graph's node info
# seperated by flowgraph and function-callgraph 
class Vertex(object):
    '''
    ID identifies a vertex
    title implies the vertex number in the gdl files
    label implies the vertex name in the gdl files
    vertextype classifies a vertex by range
    into 'subroutine'(within an exclusive sub) and 'program'(within whole program)
    
    
    '''
    def __init__(self, title, label, vertextype, indegree, outdegree):
        
        self.title = title        
        self.label = label
        self.vertextype = vertextype
        self.indegree = indegree
        self.outdegree = outdegree
    
    def addData(self, filename, fileType):
        
        #filename = "_"+filename[filename.rfind("\\")+1:]
        try:
            conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph', port=3306)
            #conn.select_db('callgraph')
            cur=conn.cursor()
            #function call graph
            if "function_call_graph" in fileType:          
                cur.execute("insert into vertex%s(title, label, vertextype, indegree, outdegree) \
                        values(%d, '%s', '%s', %d, %d);" 
                % (str(filename+"_fc"), self.title, self.label, self.vertextype, self.indegree, self.outdegree))
            #flow graph
            elif "flow_graph" in fileType:
                cur.execute("insert into vertex%s(title, label, vertextype, indegree, outdegree) \
                        values(%d, '%s', '%s', %d, %d);" 
                % (str(filename+"_fg"), self.title, self.label, self.vertextype, self.indegree, self.outdegree))
            #add a line in FlowGraphVertex
            conn.commit()
            cur.close()
            conn.close()
            
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    
    @staticmethod        
    def createTable(filename, fileType):
        
        #filename = filename[filename.rfind('\\')+1:]
        try:
            print "Here is %s" % str(filename+"_fc")   
            conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph',port=3306)
            cur = conn.cursor()
            
            '''
            #funcion call graph
            if "function_call_graph" in fileType:
                cur.execute("create table if not exists vertex%s (ID INTEGER NOT NULL auto_increment, title INTEGER NOT NULL,\
                        label VARCHAR(50), vertextype VARCHAR(20), indegree INTEGER, outdegree INTEGER, \
                        PRIMARY KEY(ID));" 
                         % str(filename+"_fc"))
            '''
            
            #flow graph
            if "flow_graph" in fileType:
                cur.execute("create table if not exists vertex%s (ID INTEGER NOT NULL auto_increment, title INTEGER NOT NULL,\
                        label VARCHAR(50), vertextype VARCHAR(20), indegree INTEGER, outdegree INTEGER, \
                        PRIMARY KEY(ID));" 
                         % str(filename+"_fg"))

            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            sys.exit()
 
# edge implies each edge's info
# seperated by flowgraph and function-callgraph           
class Edge(object):
    '''
     fromID is source
     toID is target
     type implies flow streams
     '''
    
    def __init__(self, fromID, toID, type=0):
        
        self.fromID = fromID
        
        # In fg edge, this is the real toID
        # In fc edge, this is the objID         
        self.toID = toID
        
        # Only flow graphs have type attribute
        # In fc edge, this is optID
        self.type = type
    
    def addData(self, filename, fileType):
        
        filename = filename.replace('.gdl','')
        try:
            conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph', port=3306)
            cur=conn.cursor()
            #function call graph
            if "function_call_graph" in fileType:
                print "insert in function_call_graph"
                cur.execute('insert into edge%s(blockID, objID, optID) values(%d, %d, %d);' 
                        % (str(filename+"_fc"), self.fromID, self.toID, self.type))
            #flow graph
            elif "flow_graph" in fileType:
                cur.execute('insert into edge%s(Source, Target, switchType) values(%d, %d, %d);' 
                        % (str(filename+"_fg"), self.fromID, self.toID, self.type))
                
            conn.commit()
            cur.close()
            conn.close()
            
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            
    
    @staticmethod            
    def createTable(filename,fileType):
        
        filename = filename.replace('.gdl','')
        print "filename in create edge is %s" % filename
        print "fileType is %s" % fileType
        try:
            
            conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph',port=3306)
            cur = conn.cursor()
            #FunCallEdge
            if "function_call_graph" in fileType:                
                cur.execute("create table if not exists edge%s \
                        (blockID INTEGER NOT NULL REFERENCES vertex%s(title), \
                        objID INTEGER NOT NULL, \
                        optID INTEGER NOT NULL, \
                        PRIMARY KEY(blockID, objID, optID));" 
                        % (str(filename+"_fc"), str(filename+"_fg")))
            #FlowGraphEdge
            elif "flow_graph" in fileType:
                cur.execute("create table if not exists edge%s \
                        (Source INTEGER NOT NULL REFERENCES vertex%s(title), \
                        Target INTEGER NOT NULL REFERENCES vertex%s(title), \
                        switchType INTEGER, PRIMARY KEY(Source,Target));" 
                        % (str(filename+"_fg"), str(filename+"_fg"), str(filename+"_fg")))
            conn.commit()
            cur.close()
            conn.close()
            
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            sys.exit()
    
    @staticmethod
    def getAll(filename, fileType):
        
        #filename =  "_"+filename[filename.rfind('\\')+1:]
        print "filename in getall is %s" % filename
        try:
            conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph', port=3306)
            cur = conn.cursor()
            
            if "flow_graph" in fileType:
                sql = "select * from edge%s" % str(filename+"_fg")
            elif "function_call_graph" in fileType:
                sql = "select * from edge%s" % str(filename+"_fc")
                
            cur.execute(sql)
            results = cur.fetchall()
                        
            for each in results:
                print each                   
                
            conn.commit()
            cur.close()
            conn.close()
            
            print results.__class__
            
            return results
            
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

# systemCall implies all system calls info
class SystemCall(object):
    '''
     ID identifies the instruction auto_increment
     objID implies the referenced object ID in the 32
     optID implies the referenced operation ID int the 4
     name is the instruction's name
     '''
    def __init__(self, objID, optID, sysCallName):
        
        self.objID = objID
        self.optID = optID
        self.sysCallName = sysCallName
        
    def addData(self, filename):
        
        filename = "_"+filename[filename.rfind('\\')+1:].replace('.gdl','')
        try:
            conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph', port=3306)
            #conn.select_db('callgraph')
            cur=conn.cursor()
            #function call graph
            cur.execute("insert into systemCall%s(objID, optID, sysCallName) values(%d,%d,'%s');" 
            % (filename, self.objID, self.optID, self.sysCallName))            
            
            conn.commit()
            cur.close()
            conn.close()
            
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    
    @staticmethod
    def searchData(sysCallFile, sysCallName):
        
        sysCallFile = "_"+sysCallFile[sysCallFile.rfind('\\')+1:].replace('.gdl','')
        print "sysCallFile is %s" % sysCallFile
        try:
            conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph', port=3306)
            #conn.select_db('callgraph')
            cur=conn.cursor()
            #function call graph
            cur.execute("select objID, optID from systemcall%s where sysCallName='%s'" 
            % (sysCallFile, sysCallName))
            results = cur.fetchall()
            
            conn.commit()
            cur.close()
            conn.close()
            
            return results
            
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            sys.exit(0)
        
        
    
    @staticmethod
    def getAll(filename):
        
        try:
            conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph', port=3306)
            #conn.select_db('callgraph')
            cur=conn.cursor()
            #function call graph
            cur.execute("select * from systemCall%s;" % filename)            
            results = cur.fetchAll()
            
            conn.commit()
            cur.close()
            conn.close()
            
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        
        return results
                   
    @staticmethod
    def createTable(filename):
        
        filename = "_"+filename[filename.rfind('\\')+1:].replace('.gdl','')
        try:
            conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph',port=3306)
            cur = conn.cursor()
             
            cur.execute("create table if not exists systemCall%s\
                    (ID INTEGER NOT NULL auto_increment, \
                    objID INTEGER NOT NULL REFERENCES extractedInstruction(objID),\
                    optID INTEGER NOT NULL REFERENCES extractedInstruction(optID),\
                    sysCallName VARCHAR(50) NOT NULL UNIQUE, PRIMARY KEY (ID));" % filename)
            print "systemCall table created!!!"
            
            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

# extractedInstruction implies the extracted 32*4
class ExtractedInstruction(object):
    '''
     objID implies the object in the pool of 32
     optID implies the operation divided in 4
     objectName is the object name in 32
     operation implies is the operation in 4 
    
     '''
    def __init__(self, objID, optID, objectName, operation):        
        self.objID = objID
        self.optID = optID
        self.objectName = objectName
        self.operation = operation
    
    def addData(self):
        
        try:
            conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph', port=3306)
            #conn.select_db('callgraph')
            cur=conn.cursor()
            #function call graph
            cur.execute("insert into extractedInstruction(objID,optID,objectName,operation) values(%d, %d,'%s','%s');" 
            % (self.objID, self.optID, self.objectName, self.operation))
            
            conn.commit()
            cur.close()
            conn.close()
            
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])    
            
    @staticmethod
    def createTable():
        
        try:
           
            conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph',port=3306)
            cur = conn.cursor()
            #function call graph
            cur.execute("create table if not exists extractedInstruction (objID INTEGER NOT NULL, \
                    optID INTEGER NOT NULL, objectName VARCHAR(50) not null, operation VARCHAR(50) not null,\
                    PRIMARY KEY(objID, optID));")
            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])   

# objects extractedInstruction used which is classified by 32
class ObjectItem(object):
    '''
    ID identifies each object item
    name shows each item of the system-level objects 
    description implies each object's cropped information
    '''
    def __init__(self, ID, name, description):
        self.ID = ID
        self.name = name
        self.description = description
    
    def addData(self):
        
        try:
            conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph',port=3306)
            cur = conn.cursor()
            cur.execute("insert into objectItem(ID, name, description)\
                        values (%d,'%s','%s')" % (self.ID, self.name, self.description))
            conn.commit()
            cur.close()
            conn.close()
            
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    
    @staticmethod
    def getAll():
        
        try:
            conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph',port=3306)
            cur = conn.cursor()
            cur.execute("select * from objectItem")
            
            results = cur.fetchall()
            for each in results:
                print each
                
            conn.commit()
            cur.close()
            conn.close()
            
            return results
        
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            
    @staticmethod
    def createTable():
        
        try:
            conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph',port=3306)
            cur = conn.cursor()
            cur.execute("create table objectItem\
                        (ID INTEGER NOT NULL, name VARCHAR(50), \
                        description VARCHAR(200), PRIMARY KEY(ID));")
            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            
# operations extractedInstruction used which is classified by 4

class OperationItem(object):
    '''
    ID identifies each operation
    name shows each operation
    description implies related information
    '''
    def __init__(self, ID, name, description):
        self.ID = ID
        self.name = name
        self.description = description
    
    def addData(self):
        try:
            conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph',port=3306)
            cur = conn.cursor()
            cur.execute("insert into operationItem(ID, name, description) values\
                        (%d, '%s', '%s');" % (self.ID, self.name, self.description))
            conn.commit()
            cur.close()
            conn.close()
        
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        
    @staticmethod
    def createTable():
        try:
            conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph',port=3306)
            cur = conn.cursor()
            cur.execute("create table if not exists operationItem\
                        (ID INTEGER NOT NULL, name VARCHAR(20), \
                        description VARCHAR(100), PRIMARY KEY(ID));")
            conn.commit()
            cur.close()
            conn.close()
            
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            
# callSys implies calls for system-calls in a subroutine             
class CallSys(object):
    '''
     callerID implies the ID of current subroutine
     calleeID implies the ID of the called system call
     
     '''
    def __init__(self, callerID, calleeID):
        self.callerID = callerID
        self.calleeID = calleeID        
    
    def addData(self, filename):
        
        filename = filename[filename.rfind("\\")+1:]
        try:
            conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph',port=3306)
            #conn.select_db('callgraph')
            cur=conn.cursor()
            
            cur.execute("insert into callForSysCall%s(callerID,calleeID) values(%d,%d);" 
            % (str(filename), self.callerID, self.calleeID))
            
            #add a line in FlowGraphVertex
            conn.commit()
            cur.close()
            conn.close()
            
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    
            
    @staticmethod    
    def createTable(filename):
        
        filename = "_"+filename[filename.rfind("\\")+1:]
        try:
            
            conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph',port=3306)
            cur = conn.cursor()
            # only flow graph has this table               
            cur.execute("create table if not exists callForSysCall%s \
                    (callerID INTEGER NOT NULL, calleeID INTEGER NOT NULL\
                    REFERENCES systemCall(ID), PRIMARY KEY (callerID, calleeID));" 
                    % (str(filename)))
            # - means to count from right to left
            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            
    @staticmethod
    def getAll(filename, fileType):
        
        filename = filename[filename.rfind("\\")+1:]
        try:
            conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph', port=3306)
            cur = conn.cursor()
            # only flow graph table exists
            if "flow_graph" in fileType:
                sql = "select * from callForSysCall%s" % str(filename+"_fg")
                cur.execute(sql)
                results = cur.fetchall()
                        
                for each in results:
                    print each
            # function call graph with no operation
            elif "function_call_graph" in fileType:
                pass
                
            conn.commit()
            cur.close()
            conn.close()
            
            return results
            
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

class CallSub(object):
    
    def __init__(self, callerID, calleeID): 
        self.callerID = callerID
        self.calleeID = calleeID
    
    def addData(self, filename):
        
        filename = filename[filename.rfind("\\")+1:]
        try:
            conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph', port=3306)
            cur=conn.cursor()
            
            cur.execute("insert into callForSub%s(callerID, calleeID) values(%d, %d);" 
                        % (str(filename, self.callerID, self.calleeID)))
            
            conn.commit()
            cur.close()
            conn.close()
            
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            
    @staticmethod
    def createTable(filename, fileType):
        
        filename = "_"+filename[filename.rfind("\\")+1:]           
        try:
            conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph', port=3306)
            cur = conn.cursor()  
            
            cur.execute("create table if not exists callForSub%s\
                (callerID INTEGER NOT NULL ,calleeID INTEGER NOT NULL,\
                PRIMARY KEY(callerID, calleeID));" % filename)
              
            conn.commit()
            cur.close()
            conn.close()
            
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])                  