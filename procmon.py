#!/usr/bin/python
# -*- coding: UTF-8 -*-  
import time
import plot
import tornado.web
import tornado.ioloop
import tornado.httpserver
import os
import re
import daemon
import datetime
import database

class Procmon(object):
    def __init__(self):
        # system
        self.__process = {}
        self.__MemTotal = None
        self.__MemFree = None
        self.__Minor = None
        self.__Major = None
        self.__Version = None
        self.__Kernel = None
        self.__Disk = None
        self.__ClockTicksPerSecond = None
        self.__Cpu_usage = []
        self.__cpu_total_time = 0
        self.__cpu_idle_time = 0
        self.__cpu_user_time = 0
        self.__Cpu_user_usage = []
        self.__cpu_sys_time = 0
        self.__Cpu_sys_usage = []
        self.__receivebytes = []
        self.__last_receivebytes = 0
        self.__receivepackets = []  
        self.__last_receivepackets = 0     
        self.__sendbytes = []
        self.__last_sendbytes = 0
        self.__sendpackets = []  
        self.__last_sendpackets = 0  


        #process
        self.__Name = None
        self.__Pid = None
        self.__Started_at = None
        self.__Executable = None
        self.__Current_dir = None
        self.__State = None
        self.__User_time = None
        self.__System_time = None
        self.__VmSize = None
        self.__VmRSS = None
        self.__Threads = None
        self.__Priority = None
        self.__Nice = None
        self.__response = []
        self.__Process_cpu_usage = []
        self.__proc_cpu_total_time = 0
        self.__proc_cpu_use_time = 0
        self.__proc_cpu_user_time = 0
        self.__proc_cpu_user_usage = []
        self.__proc_cpu_sys_time = 0
        self.__proc_cpu_sys_usage = []
        

        #Thread
        self.__thread_cpu_total_time = 0
        self.__thread_cpu_use_time = 0
        self.__ip_db = database.db()

        
    def start(self):
        http_server = tornado.httpserver.HTTPServer(self.onRequest,True)  
        http_server.listen(1080)     
        tornado.ioloop.PeriodicCallback(self.tick,2000).start()
        tornado.ioloop.IOLoop.instance().start() 
        
        
    def tick(self):
        self.getCpuUsage()
        self.getNetUsage()
        self.getCpuImage()
        self.getNetImage()        
        
    def onRequest(self,request):
      if self.__ip_db.getbyIp(request.remote_ip) == False:
        if request.method == 'GET' and request.uri == '/':
            self.clear_process()                      
            message = self.fillindex()
            message = message.encode("utf-8")
            request.connection.write(("HTTP/1.1 200 OK\r\n"
                                 "Content-Length: %d\r\n\r\n" % len(message)).encode("utf-8"))
            request.connection.write(message)
            request.connection.finish()
         
         
        elif request.method == 'GET' and request.uri[0:8] == '/cpu.png':
           f = open('cpu.png','rb')
           data = f.read()
           f.close()
           request.connection.write(("HTTP/1.1 200 OK\r\n"
                                     "Content-type: image/png\r\n"
                                     "Content-Length: %d\r\n\r\n" % len(data)).encode("utf-8"))
           request.connection.write(data)
           request.connection.finish()
        

        elif request.method == 'GET' and request.uri[0:13] == '/net_eth0.png':
           f = open('net_eth0.png','rb')
           data = f.read()
           f.close()
           request.connection.write(("HTTP/1.1 200 OK\r\n"
                                     "Content-type: image/png\r\n"
                                     "Content-Length: %d\r\n\r\n" % len(data)).encode("utf-8"))
           request.connection.write(data)
           request.connection.finish()

         
        elif request.method == 'GET' and request.uri[0] == '/' and request.uri[1:].isdigit():
             if os.path.exists("/proc/%s/stat" %(request.uri[1:]))== False:
                message = "<head></head><body><h3>404 NOT FOUND</h3></body>"
                message = message.encode("utf-8")
                request.connection.write(("HTTP/1.1 200 OK\r\n"
                                         "Content-Length: %d\r\n\r\n" % len(message)).encode("utf-8"))
                request.connection.write(message)
                request.connection.finish()
             else: 
                #self.clear_cpu()
                #self.__Process_cpu_usage = []
                #self.__proc_cpu_sys_usage = []
                #self.__proc_cpu_user_usage = []
                self.getProcInfo(request.uri[1:])
                message = self.fillProc()
                message = message.encode("utf-8")
                request.connection.write(("HTTP/1.1 200 OK\r\n"
                                          "Content-Length: %d\r\n\r\n" % len(message)).encode("utf-8"))
                request.connection.write(message)
                request.connection.finish()

        
        elif request.method == 'GET' and request.uri[-4:] == '.png':
           if(request.uri[1:-4].isdigit()):
              self.getProcCpuUsage(request.uri[1:-4])
              self.getProcImage(request.uri[1:-4])
              f = open('%s.png' %(request.uri[1:-4]),'rb')
              data = f.read()
              f.close()
              request.connection.write(("HTTP/1.1 200 OK\r\n"
                                     "Content-type: image/png\r\n"
                                     "Content-Length: %d\r\n\r\n" % len(data)).encode("utf-8"))
              request.connection.write(data)
              request.connection.finish()
        

        elif request.method == 'GET':
            pattern = re.compile("[0-9]+\.png")
            res = pattern.findall(request.uri)
            if len(res) > 0:
               res = res[0]
            if res[-4:] == '.png' and res[0:-4].isdigit():
                  self.getProcCpuUsage(res[0:-4])
                  self.getProcImage(res[0:-4])
                  f = open('%s.png' %(res[0:-4]),'rb')
                  data = f.read()
                  f.close()
                  request.connection.write(("HTTP/1.1 200 OK\r\n"
                                     "Content-type: image/png\r\n"
                                     "Content-Length: %d\r\n\r\n" % len(data)).encode("utf-8"))
                  request.connection.write(data)
                  request.connection.finish()
        
         
          
    def fillindex(self):
        self.__response = []
        self.getMemInfo()
        self.getAllProc()
        self.__Disk = self.disk_stat()
        version = self.getVersion()
        self.__Version = version[0]
        self.__Kernel = version[1]

        self.__response.append("<html><head>"
                               "<title>Procmon on %s</title>\n" % (self.getHostname()))
        self.__response.append(
            "<script type=\"text/javascript\">"
            "function myrefresh() "
            "{ var i = Math.random();document.getElementById(\"cpu\").src=\"/cpu.png?i=\"+i;"
            "document.getElementById(\"eth0\").src=\"/net_eth0.png?i=\"+i;}var t=setInterval(myrefresh,2000);"
            "</script>\n")
        self.__response.append("</head><body>\n")
        self.__response.append("<h1>%s</h1>\n" % (self.getHostname()))
        self.__response.append("<p>Refresh <a href=\"?refresh=1\">1s</a> ")
        self.__response.append("<a href=\"?refresh=2\">2s</a> ")
        self.__response.append("<a href=\"?refresh=5\">5s</a> ")
        self.__response.append("<a href=\"?refresh=15\">15s</a> ")
        self.__response.append("<a href=\"?refresh=60\">60s</a>\n")
        self.__response.append("<p><a href=\"/cmdline\">Command line</a>\n")
        self.__response.append("<a href=\"/environ\">Environment variables</a>\n")
        self.__response.append("<a href=\"/threads\">Threads</a>\n")

        self.__response.append("<p><table>")
        self.__response.append("<tr><td>%s</td><td>%s</td></tr>" % ("Operating System", self.__Version))
        self.__response.append("<tr><td>%s</td><td>%s</td></tr>" % ("Kernel", self.__Kernel))
        self.__response.append("<tr><td>%s</td><td>%s</td></tr>" % ("MemTotal", self.__MemTotal))
        self.__response.append("<tr><td>%s</td><td>%s</td></tr>" % ("MemFree", self.__MemFree))
        self.__response.append("<tr><td>%s</td><td>%s</td></tr>" % ("Disk Capacity", self.__Disk["capacity"]))
        self.__response.append("<tr><td>%s</td><td>%s</td></tr>" % ("Disk Free", self.__Disk["available"]))
        self.__response.append(
            "<tr><td>%s</td><td>%s</td></tr>" % (
                "cpu usage", "<img src=\"/cpu.png\" height=\"300\" witdh=\"800\"  id='cpu'>"))
        self.__response.append(
            "<tr><td>%s</td><td>%s</td></tr>" % (
                "eth0 usage", "<img src=\"/net_eth0.png\" height=\"300\" witdh=\"800\"  id='eth0'>"))

        self.__response.append("</table>")
        self.__response.append("<table border=1>")
        self.__response.append("<tr><th>pid</th><th>name</th><th>cwd</th><th>exe</th><th>cmdline</th></tr>")
        for k,v in self.__process.items(): 
             self.__response.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" %(k,v[0][1:-1],v[1],v[2],v[3]))
        self.__response.append("</table>")
        self.__response.append("</body></html>")
        
        s = ''
        for i in self.__response:
           s += i
        return s


    def fillProc(self):
        self.__response = []
        self.__response.append("<html><head>"
                               "<title>%s on %s</title>\n" % (self.__Name, self.getHostname()))
        self.__response.append(
            "<script type=\"text/javascript\">"
            "var ad = null;"
            "function myrefresh() "
            "{var i = Math.random();"
            "if(ad == null){"
            "var str =  document.getElementById(\"pro\").src;"
            "ad = str.match(/\/[0-9]+\.png/)[0];}"
            "document.getElementById(\"pro\").src= ad+\"?i=\"+i;}  var t=setInterval(myrefresh,3000);"
            "</script>\n")
        self.__response.append("</head><body>\n")
        self.__response.append("<h1>%s on %s</h1>\n" % (self.__Name, self.getHostname()))
        self.__response.append("<p>Refresh <a href=\"?refresh=1\">1s</a> ")
        self.__response.append("<a href=\"?refresh=2\">2s</a> ")
        self.__response.append("<a href=\"?refresh=5\">5s</a> ")
        self.__response.append("<a href=\"?refresh=15\">15s</a> ")
        self.__response.append("<a href=\"?refresh=60\">60s</a>\n")
        self.__response.append("<p><a href=\"/cmdline\">Command line</a>\n")
        self.__response.append("<a href=\"/environ\">Environment variables</a>\n")
        self.__response.append("<a href=\"/threads\">Threads</a>\n")
        # self.__response.append("<p>Page generated at %s (UTC)", time.time())
        self.__response.append("<p><table>")
        self.__response.append("<tr><td>%s</td><td>%s</td></tr>" % ("PID", self.__Pid))
        self.__response.append("<tr><td>%s</td><td>%s</td></tr>" % ("State", self.__State))
        #self.__response.append("<tr><td>%s</td><td>%s</td></tr>" % ("User time (s)", self.__User_time))
        #self.__response.append("<tr><td>%s</td><td>%s</td></tr>" % ("System time (s)", self.__System_time))
        self.__response.append("<tr><td>%s</td><td>%s</td></tr>" % ("VmSize (KiB)", self.__VmSize))
        self.__response.append("<tr><td>%s</td><td>%s</td></tr>" % ("VmRSS (KiB)", self.__VmRSS))
        self.__response.append("<tr><td>%s</td><td>%s</td></tr>" % ("Threads", self.__Threads))
        self.__response.append("<tr><td>%s</td><td>%s</td></tr>" % ("Priority", self.__Priority))
        self.__response.append("<tr><td>%s</td><td>%s</td></tr>" % ("Nice", self.__Nice))
        self.__response.append(
            "<tr><td>%s</td><td>%s</td></tr>" % (
                "CPU usage", "<img src=\"/%s.png\" height=\"300\" witdh=\"800\"  id='pro'>") %(self.__Pid))
        self.__response.append("</table>")
        self.__response.append("</body></html>")

        s = ''
        for i in self.__response:
            s += i
        return s
    
    def fillRefresh(self):
        pass

    def getAllProc(self):
        self.__process = {}
        path = os.listdir('/proc')
        for p in path:
          if p.isdigit():
            f = open("/proc/%s/stat" % (p),"r")
            content = f.read()
            content = content.split()
            name = content[1]
            if  os.path.exists('/proc/%s/cwd' %(p)):
                cwd = os.readlink('/proc/%s/cwd' %(p))
            else:
                cwd = None
     
            if  os.path.exists('/proc/%s/exe' %(p)):
                exe = os.readlink('/proc/%s/cwd' %(p))
            else:
                exe = None

            if  os.path.exists('/proc/%s/cmdline' %(p)):
                f = open('/proc/%s/cmdline' %(p),'r')
                cmdline = f.readline().replace('\x00',' ')
                f.close()
            else:
                cmdline = None
            self.__process[p] = (name,cwd,exe,cmdline)


    def getProcInfo(self,pid):
        f = open("/proc/%d/stat" % (int(pid)),"r")
        content = f.read()
        content = content.split()
        self.__Pid = content[0]
        #self.__Name = content[1]
        self.__State = self.getState(content[2])
        self.__User_time = content[13]
        self.__System_time = content[14]
        self.__Priority = content[17]
        self.__Nice = content[18]
        self.__Threads = content[19]
        f.close()

        f = open("/proc/%d/status" % (int(pid)), "r")
        content = f.readline()
        content = content.split()
        self.__Name = content[1]
        
        for i in range(12):
           content = f.readline()
        content = content.split()
        self.__VmSize = content[1]
        for i in range(4):
           content = f.readline()
        content = content.split()
        self.__VmRSS = content[1]    
        f.close()


    def getState(self,state):
        if(state == 'R'):
            return  "Running"
        elif (state == 'S'):
            return "Sleeping"
        elif (state == "D"):
            return  "Disk sleep"
        elif (state == "Z"):
            return "Zombie"
        else:
            return  "Unknow"


    def getCpuUsage(self):
        f = open("/proc/stat","r")
        content = f.readline()
        f.close()
        content = content.split()
        content = content[1:]
        s=0
        for i in content:
          s += int(i)
        j=int(content[3])

        if len(self.__Cpu_usage) >= 300:
            del self.__Cpu_usage[0]

        if self.__cpu_total_time == 0 and self.__cpu_idle_time == 0:
            #for i in range(self.__kPeriod/1000):
               self.__Cpu_usage.append(0.0)
        elif s-self.__cpu_total_time < 0 or j-self.__cpu_idle_time < 0:
            #for i in range(self.__kPeriod/1000):
               self.__Cpu_usage.append(0.0)
        else:
            #for i in range(self.__kPeriod/1000):
               self.__Cpu_usage.append(1- (j - self.__cpu_idle_time)/(s - self.__cpu_total_time))
        self.__cpu_total_time = s
        self.__cpu_idle_time = j
            
    def getHostname(self):
        f = open("/proc/sys/kernel/hostname","r")
        content = f.read()
        f.close()
        return  content
    

    def getMemInfo(self):
        f = open("/proc/meminfo","r")
        content = f.readline()
        content = content.split()
        self.__MemTotal = content[1]
        content = f.readline()
        content = content.split()
        self.__MemFree = content[1]
        f.close()    


    def getProcCpuUsage(self,pid):
         f = open("/proc/stat","r")
         content = f.readline()
         f.close()
         content = content.split()
         content = content[1:]
         s=0
         for i in content:
            s += int(i)
         f = open("/proc/%s/stat" %(pid),"r")
         content = f.read()
         content = content.split()
         f.close()
         j = int(content[13])+int(content[14])+int(content[15])+int(content[16])
         user_time = int(content[13])
         sys_time =  int(content[14])

         if len(self.__Process_cpu_usage) >= 300:
             del self.__Process_cpu_usage[0]
         elif len(self.__proc_cpu_user_usage) >= 300:
             del self.__proc_cpu_user_usage[0]
         elif len(self.__proc_cpu_sys_usage) >= 300:
             del self.__proc_cpu_sys_usage[0]

         if self.__proc_cpu_total_time == 0 and self.__proc_cpu_use_time == 0:
              #for i in range(self.__kPeriod/1000):
                 self.__Process_cpu_usage.append(0.0)
         elif s - self.__proc_cpu_total_time < 0 or j - self.__proc_cpu_use_time < 0:
              #for i in range(self.__kPeriod/1000):
                 self.__Process_cpu_usage.append(0.0)
         else:
              #for i in range(self.__kPeriod/1000):
                 self.__Process_cpu_usage.append((j-self.__proc_cpu_use_time)/(s - self.__proc_cpu_total_time))
         
         if self.__proc_cpu_user_time  == 0 or self.__proc_cpu_total_time == 0:
              #for i in range(self.__kPeriod/1000):
                 self.__proc_cpu_user_usage.append(0.0)
         elif user_time - self.__proc_cpu_user_time < 0:
              #for i in range(self.__kPeriod/1000):
                 self.__proc_cpu_user_usage.append(0.0)
         else:
              #for i in range(self.__kPeriod/1000):
                 self.__proc_cpu_user_usage.append((user_time-self.__proc_cpu_user_time)/(s - self.__proc_cpu_total_time))
         
         if self.__proc_cpu_sys_time == 0 or self.__proc_cpu_total_time == 0:
              #for i in range(self.__kPeriod/1000):
                 self.__proc_cpu_sys_usage.append(0.0)
         elif sys_time - self.__proc_cpu_sys_time < 0:
              #for i in range(self.__kPeriod/1000):
                 self.__proc_cpu_sys_usage.append(0.0)
         else:
              #for i in range(self.__kPeriod/1000):
                 self.__proc_cpu_sys_usage.append((sys_time-self.__proc_cpu_sys_time)/(s - self.__proc_cpu_total_time))


         #print("user time:%d",(user_time-self.__proc_cpu_user_time)/self.__proc_cpu_total_time)
         #print("sys time:%d",(sys_time-self.__proc_cpu_sys_time)/self.__proc_cpu_total_time)
         self.__proc_cpu_user_time = user_time
         self.__proc_cpu_sys_time = sys_time
         self.__proc_cpu_total_time = s
         self.__proc_cpu_use_time = j 



    def getThreadCpuUsage(self):
        f = open("/proc/stat","r")
        content = f.readline()
        f.close()
        content = content.split()
        content = content[1:]
        s1=0
        for i in content:
          s1 += int(i)
        f.close()
        f = open("/proc/%s/stat" %(self.__Pid),"r")
        content = f.read()
        content = content.split()
        j1 = int(content[13])+int(content[14])+int(content[15])+int(content[16])
        time.sleep(0.1)
    
        f = open("/proc/stat","r")
        content = f.readline()
        f.close()
        content = content.split()
        content = content[1:]
        s2 = 0
        for i in content:
           s2 += int(i)

        f = open("/proc/%s/stat" %(self.__Pid),"r")
        content = f.read()
        f.close()
        content = content.split()
        j2 = int(content[15])+int(content[16])
        total = s2 - s1
        thread = j2 - j1
        return thread/total


    def getNetUsage(self):
        if len(self.__receivebytes) >= 300:
             del self.__receivebytes[0]
        elif len(self.__sendbytes) >= 300:
             del self.__sendbytes[0]
        
        net = self.net_stat()
        if(self.__last_receivebytes == 0):
            #for i in range(self.__kPeriod/1000):
               self.__receivebytes.append(0)
        elif (net[2]['ReceiveBytes'] - self.__last_receivebytes >=0):
            #for i in range(self.__kPeriod/1000):
               self.__receivebytes.append(net[2]['ReceiveBytes'] - self.__last_receivebytes)
        else:
            #for i in range(self.__kPeriod/1000):
               self.__receivebytes.append(0)
 
        if(self.__last_receivepackets == 0):
            #for i in range(self.__kPeriod/1000):
               self.__receivepackets.append(0)
        elif(net[2]['ReceivePackets'] - self.__last_receivepackets >= 0):
            #for i in range(self.__kPeriod/1000):
               self.__receivepackets.append(net[2]['ReceivePackets'] - self.__last_receivepackets)
        else:
            #for i in range(self.__kPeriod/1000):
               self.__receivepackets.append(0.0)
 
        if(self.__last_sendbytes == 0):
            #for i in range(self.__kPeriod/1000):
               self.__sendbytes.append(0)
        elif(net[2]['TransmitBytes'] - self.__last_sendbytes >= 0):
            #for i in range(self.__kPeriod/1000):
               self.__sendbytes.append(net[2]['TransmitBytes'] - self.__last_sendbytes)
        else:
            #for i in range(self.__kPeriod/1000):
               self.__sendbytes.append(0.0)
     
        if(self.__last_sendpackets == 0):
            #for i in range(self.__kPeriod/1000):
               self.__sendpackets.append(0.0)
        elif (net[2]['TransmitPackets'] - self.__last_sendpackets >= 0):
            #for i in range(self.__kPeriod/1000):
               self.__sendpackets.append(net[2]['TransmitPackets'] - self.__last_sendpackets) 
        else:
            #for i in range(self.__kPeriod/1000):
               self.__last_sendpackets.append(0.0)

        self.__last_receivebytes= net[2]["ReceiveBytes"]
        self.__last_receivepackets = net[2]["ReceivePackets"]
        self.__last_sendbytes = net[2]["TransmitBytes"]
        self.__last_sendpackets = net[2]["TransmitPackets"]


    def disk_stat(self):
        hd = {}
        disk = os.statvfs("/")
        hd['available'] = disk.f_bsize * disk.f_bavail
        hd['capacity'] = disk.f_bsize * disk.f_blocks
        hd['used'] = disk.f_bsize * disk.f_bfree
        return hd


    def net_stat(self):
        net = []
        f = open("/proc/net/dev")
        lines = f.readlines()
        f.close()
        for line in lines[2:]:
            con = line.split()
            """ 
            intf = {} 
            intf['interface'] = con[0].lstrip(":") 
            intf['ReceiveBytes'] = int(con[1]) 
            intf['ReceivePackets'] = int(con[2]) 
            intf['ReceiveErrs'] = int(con[3]) 
            intf['ReceiveDrop'] = int(con[4]) 
            intf['ReceiveFifo'] = int(con[5]) 
            intf['ReceiveFrames'] = int(con[6]) 
            intf['ReceiveCompressed'] = int(con[7]) 
            intf['ReceiveMulticast'] = int(con[8]) 
            intf['TransmitBytes'] = int(con[9]) 
            intf['TransmitPackets'] = int(con[10]) 
            intf['TransmitErrs'] = int(con[11]) 
            intf['TransmitDrop'] = int(con[12]) 
            intf['TransmitFifo'] = int(con[13]) 
            intf['TransmitFrames'] = int(con[14]) 
            intf['TransmitCompressed'] = int(con[15]) 
            intf['TransmitMulticast'] = int(con[16]) 
            """
            intf = dict(
                zip(
                    ('interface', 'ReceiveBytes', 'ReceivePackets',
                     'ReceiveErrs', 'ReceiveDrop', 'ReceiveFifo',
                     'ReceiveFrames', 'ReceiveCompressed', 'ReceiveMulticast',
                     'TransmitBytes', 'TransmitPackets', 'TransmitErrs',
                     'TransmitDrop', 'TransmitFifo', 'TransmitFrames',
                     'TransmitCompressed', 'TransmitMulticast'),
                    (con[0].rstrip(":"), int(con[1]), int(con[2]),
                     int(con[3]), int(con[4]), int(con[5]),
                     int(con[6]), int(con[7]), int(con[8]),
                     int(con[9]), int(con[10]), int(con[11]),
                     int(con[12]), int(con[13]), int(con[14]),
                     int(con[15]), int(con[16]),)
                )
            )
            net.append(intf)
        return net


    def cpu_stat(self):
        cpu = []
        cpuinfo = {}
        f = open("/proc/cpuinfo")
        lines = f.readlines()
        f.close()
        for line in lines:
            if line == '\n':
                cpu.append(cpuinfo)
                cpuinfo = {}
            if len(line) < 2: continue
            name = line.split(':')[0].rstrip()
            var = line.split(':')[1]
            cpuinfo[name] = var
        return cpu


    def load_stat(self):
        loadavg = {}
        f = open("/proc/loadavg")
        con = f.read().split()
        f.close()
        loadavg['lavg_1'] = con[0]
        loadavg['lavg_5'] = con[1]
        loadavg['lavg_15'] = con[2]
        loadavg['nr'] = con[3]
        loadavg['last_pid'] = con[4]
        return loadavg


    def uptime_stat(self):
        uptime = {}
        f = open("/proc/uptime")
        con = f.read().split()
        f.close()
        all_sec = float(con[0])
        MINUTE, HOUR, DAY = 60, 3600, 86400
        uptime['day'] = int(all_sec / DAY)
        uptime['hour'] = int((all_sec % DAY) / HOUR)
        uptime['minute'] = int((all_sec % HOUR) / MINUTE)
        uptime['second'] = int(all_sec % MINUTE)
        uptime['Free rate'] = float(con[1]) / float(con[0])
        return uptime


    def getVersion(self):
        f = open("/etc/issue","r")
        content = f.readline()
        f.close()
        content = content.split()
        version = ""
        for i in content[0:3]:
           version+=i
           version+=" " 
       
        f = open("/proc/version","r")
        content = f.readline()
        f.close()
        content = content.split()
        kernel = content[2]
        return version,kernel


    def getCpuImage(self):
        y = self.__Cpu_usage        
        x = [i for i in range(len(y))]
        plot.plot(x,y)


    def getProcImage(self,name):
        y1 = self.__Process_cpu_usage
        x1 = [i for i in range(len(y1))]
        y2 = self.__proc_cpu_user_usage
        x2 = [i for i in range(len(y2))]
        y3 = self.__proc_cpu_sys_usage
        x3 = [i for i in range(len(y3))]
        plot.plot_pro(x1, y1,x2,y2,x3,y3,name)

    def getNetImage(self):
        y1 = self.__receivepackets
        x1 = [i for i in range(len(y1))]
        y2 = self.__receivepackets
        x2 = [i for i in range(len(y2))]
        y3 = self.__sendbytes
        x3 = [i for i in range(len(y3))]
        y4 = self.__sendpackets
        x4 = [i for i in range(len(y4))]
        plot.plot_net(x1,y1,x3,y3,"net_eth0")
     
    def clear_cpu(self):
        self.__Cpu_usage = []
        self.__cpu_total_time = 0
        self.__cpu_idle_time = 0
        self.__cpu_user_time = 0
        self.__Cpu_user_usage = []
        self.__cpu_sys_time = 0
        self.__Cpu_sys_usage = []
        self.__receivebytes = []
        self.__last_receivebytes = 0
        self.__receivepackets = []  
        self.__last_receivepackets = 0     
        self.__sendbytes = []
        self.__last_sendbytes = 0
        self.__sendpackets = []  
        self.__last_sendpackets = 0 

    def clear_process(self):
        self.__Process_cpu_usage = []
        self.__proc_cpu_total_time = 0
        self.__proc_cpu_use_time = 0
        self.__proc_cpu_user_time = 0
        self.__proc_cpu_user_usage = []
        self.__proc_cpu_sys_time = 0
        self.__proc_cpu_sys_usage = []


def main():
    p = Procmon()
    p.start() 
if __name__ == "__main__":
   #daemon.daemon()
   main()
