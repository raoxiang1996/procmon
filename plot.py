import matplotlib
import numpy as np  
from scipy.interpolate import spline  
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def plot(x1,y1):
   plt.figure(figsize=(20, 5))
   plt.xlim((0, 300))
   plt.ylim((0.0, 1.0))

   #xnew = np.linspace(min(x1),max(x1),len(x1)*15) 
   #power_smooth = spline(x1,y1,xnew) 
   #plt.plot(xnew ,power_smooth,linewidth = '2',color = "red")
   
   plt.plot(x1,y1,linewidth = '2',color = "red")
   plt.xlabel('time')
   plt.ylabel('cpu usage')
   plt.title('name')
   plt.savefig("cpu.png")
   plt.close()

def plot_pro(x1,y1,x2,y2,x3,y3,name):
   plt.figure(figsize=(20, 5))
   plt.xlim((0,300))
   plt.ylim((0.0, 1.0))
      
   #xnew = np.linspace(min(x1),max(x1),len(x1)*15) 
   #power_smooth = spline(x1,y1,xnew) 
   #plt.plot(xnew ,power_smooth,linewidth = '3',color = "red")

     
   plt.plot(x1,y1,linewidth = '3',color = "red")
   plt.plot(x2, y2, linewidth='2', color="green")
   plt.plot(x3, y3, linewidth='3', color="blue")
   plt.xlabel('time')
   plt.ylabel('%s usage' %(name))
   plt.title('name')
   plt.savefig("%s.png" %(name))
   plt.close()


def plot_net(x1,y1,x2,y2,name):
   plt.figure(figsize=(20, 5))
   plt.xlim((0,300))
   plt.ylim((0.0, 200000))
      
   #xnew = np.linspace(min(x1),max(x1),len(x1)*15) 
   #power_smooth = spline(x1,y1,xnew) 
   #plt.plot(xnew ,power_smooth,linewidth = '3',color = "red")

     
   plt.plot(x1,y1,linewidth = '2',color = "red")
   plt.plot(x2, y2, linewidth='2', color="blue")
   plt.xlabel('time')
   plt.ylabel('%s usage' %(name))
   plt.title('name')
   plt.savefig("%s.png" %(name))
   plt.close()