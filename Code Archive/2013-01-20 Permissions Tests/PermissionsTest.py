import sys
import os
import time

File1 = os.open("permissions-test-8.txt", os.O_RDWR | os.O_CREAT, int("0664", 8))

#os.setgid(1601)
os.setuid(11830)
#os.fchown(File1, -1, 1601)

FileObject1 = os.fdopen(File1, "w")
FileObject1.write(str(time.time()))
FileObject1.close()

#File2 = os.open("permissions-test-6.txt", os.O_RDONLY)

#os.fdopen(File2, "r")

print os.getgroups()
print os.getuid()

#File2.close()
