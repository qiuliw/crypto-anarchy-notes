f = open("c.txt","w")
for i in range(100):
    f.write("{:03d}".format(i+1))
    f.write("\n")
f.close()