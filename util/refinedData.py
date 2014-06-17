'''
Created on 2014-6-2

@author: oopsmartin
'''
import MySQLdb
import getAttr1

class Instruction:
    
    def __init__(self, source=-1, target=-1, count=0):
        self.source = source
        self.target = target
        self.count = count
    
    def addData(self, filename):
        
        conf = getAttr1.MyUtils.getFile(filename)
        attrFile = conf.get("file", "call_flow")
        
        attrFile = "_"+attrFile[attrFile.rfind('\\')+1:].replace('_cfg.gdl','')
        try:
            conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph', port=3306)
            cur=conn.cursor()
            
            cur.execute("insert into insMatrix%s(source, target, count) values(%d, %d, %d);" 
                        % (attrFile, self.source, self.target, self.count))
            
            conn.commit()
            cur.close()
            conn.close()
            
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    
    @staticmethod        
    def createTable(filename):
        
        conf = getAttr1.MyUtils.getFile(filename)
        attrFile = conf.get("file", "call_flow")
        
        attrFile = "_"+attrFile[attrFile.rfind('\\')+1:].replace('_cfg.gdl','')
        try:
            print "Here is %s" % str(attrFile)   
            conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='8086W028C',db='callgraph',port=3306)
            cur = conn.cursor()
            
            cur.execute("create table if not exists insMatrix%s \
                        (source INTEGER NOT NULL,\
                        target INTEGER NOT NULL, \
                        count INTEGER NOT NULL, \
                        PRIMARY KEY(source,target));"
                         % attrFile)
            print 'created'
            
            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            