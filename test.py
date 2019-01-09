import os
process = {}
path = os.listdir('/proc')
for p in path:
  if p.isdigit():
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
    process[p] = (cwd,exe,cmdline)
print(process)