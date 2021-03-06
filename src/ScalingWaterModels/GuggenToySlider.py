import numpy as np 
import matplotlib.pyplot as plt
from matplotlib import rc  
from matplotlib.widgets import Slider, Button, RadioButtons
from load_data import *

classic = False

if classic:
	Data1 = load_data(filename="../Data/a2_01_3.pkl")
	Data2 = load_data(filename="../Data/a2_03_3.pkl")
else:
	Data1 = load_data_and_rescale(filename="../Data/a2_01_3.pkl",a2=-0.1)
	Data2 = load_data_and_rescale(filename="../Data/a2_03_3.pkl",a2=-0.3)

rc('ytick',labelsize=20)
rc('xtick',labelsize=20)

def find_intersection(x01,y01,x02,y02,mT2=-np.inf):
	mymin = 20.
	min = lambda x,y : x if x <= y else y
	t1m,p1m = 0.,0.#np.mean(x01),np.mean(y01)
	t2m,p2m = 0.,0.#np.mean(x41),np.mean(y41)
	for T1,P1 in zip(x01,y01):
		t1,p1 = T1-t1m, P1-p1m
		for T2,P2 in zip(x02,y02):
			t2,p2 = T2-t2m,P2-p2m
			newmin = min(mymin,(t1-t2)**2/min(t1**2,t2**2) + (p1-p2)**2/min(p1**2,p2**2))
			if newmin < mymin and P2 < 5. and P2 > -5. and T2 > mT2:
				res = np.array([newmin,T2,P2])
				mymin = newmin
	return res

x01,y01 = Data1["TMD"]
x02,y02 = Data2["TMD"]

x11,y11 = Data1["LLT"]
x12,y12 = Data2["LLT"]

x21,y21 = Data1["LLW"]
x22,y22 = Data2["LLW"]

x31,y31 = Data1["LVS"]
x32,y32 = Data2["LVS"]

x41,y41 = Data1["KtM"]
x42,y42 = Data2["KtM"]

x51,y51 = Data1["LLCP"]
x52,y52 = Data2["LLCP"]

x61,y61 = Data1["VLCP"]
x62,y62 = Data2["VLCP"]

#x61 = y61 = 1.0
#x62 = y62 = 1.0

i1x51=j1y51=i2x52=j2y52=0.



#k1=l1=k2=l2=1.

#k1,l1 = np.max(x01)-x51, y51-np.min(y01)
#k2,l2 = np.max(x02)-x52, y52-np.min(y02)

k1=l1=k2=l2=1.
r, i1x51, j1y51 = find_intersection(x01,y01,x41,y41)
r, i2x52, j2y52 = find_intersection(x02,y02,x42,y42)

#i1x51,j1y51 = x61,y51
#i2x52,j2y52 = x62,y52

k1,l1 =(x61-i1x51),(y51-j1y51)
k2,l2 =(x62-i2x52),(y52-j2y52)

#i2x52, j2y52 = 5.49715723e-01,  -1.20040080e+00

fig, ax = plt.subplots(figsize=(10,10),facecolor="white")
plt.subplots_adjust(left=0.25,bottom=0.30)

plt.plot((x01-i1x51)/k1,(y01-j1y51)/l1,'-',color="#e41a1c",lw=3, label="TMD")
plt.plot((x11-i1x51)/k1,(y11-j1y51)/l1,'-',color="#377eb8",lw=3,label="LLT")
plt.plot((x21-i1x51)/k1,(y21-j1y51)/l1,'-',color="#4daf4a",lw=3,label="LLW")
plt.plot((x31-i1x51)/k1,(y31-j1y51)/l1,'-',color="#984ea3",lw=3,label="LVS")
plt.plot((x41-i1x51)/k1,(y41-j1y51)/l1,'-',color="#ff7f00",lw=3,label="KtM")
plt.plot((x51-i1x51)/k1,(y51-j1y51)/l1,'ro',color="#ffff33",ms=12,label="LLCP")
plt.plot((x61-i1x51)/k1,(y61-j1y51)/l1,'ro',color="#a65628",ms=12,label="VLCP")


al1,=plt.plot((x02-i2x52)/k2,(y02-j2y52)/l2,'-.',color="#e41a1c",lw=3)
al2,=plt.plot((x12-i2x52)/k2,(y12-j2y52)/l2,'-.',color="#377eb8",lw=3)
al3,=plt.plot((x22-i2x52)/k2,(y22-j2y52)/l2,'-.',color="#4daf4a",lw=3)
al4,=plt.plot((x32-i2x52)/k2,(y32-j2y52)/l2,'-.',color="#984ea3",lw=3)
al5,=plt.plot((x42-i2x52)/k2,(y42-j2y52)/l2,'-.',color="#ff7f00",lw=3)
al6,=plt.plot((x52-i2x52)/k2,(y52-j2y52)/l2,'ro',color="#ffff33",ms=12)
al7,=plt.plot((x62-i2x52)/k2,(y62-j2y52)/l2,'ro',color="#a65628",ms=12)

plt.xlabel('Temperature',fontsize=24)
plt.ylabel('Pressure',fontsize=24)
plt.legend(frameon=False,loc='upper right')

#ax.set_ylim(-2,4.)
#ax.patch.set_facecolor('white')
#ax.set_xlim(-1.2,1.2)

axcolor = 'lightgoldenrodyellow'
axPscale = plt.axes([0.25,0.15,0.65,0.03],axisbg=axcolor)
axTscale = plt.axes([0.25,0.05,0.65,0.03],axisbg=axcolor)

Pinit = 1.0
Tinit = 1.0


axPfreq = Slider(axPscale,'ps',-5,5.,valinit=Pinit)
axTfreq = Slider(axTscale,'ts', -5.,5.,valinit=Tinit)

def update(val):
	Ps, Ts = axPfreq.val, axTfreq.val
	al1.set_ydata(Ps*(y02-j2y52)/l2)
	al2.set_ydata(Ps*(y12-j2y52)/l2)
	al3.set_ydata(Ps*(y22-j2y52)/l2)
	al4.set_ydata(Ps*(y32-j2y52)/l2)
	al5.set_ydata(Ps*(y42-j2y52)/l2)
	al6.set_ydata(Ps*(y52-j2y52)/l2)
	al7.set_ydata(Ps*(y62-j2y52)/l2)

	al1.set_xdata(Ts*(x02-i2x52)/k2)
	al2.set_xdata(Ts*(x12-i2x52)/k2)
	al3.set_xdata(Ts*(x22-i2x52)/k2)
	al4.set_xdata(Ts*(x32-i2x52)/k2)
	al5.set_xdata(Ts*(x42-i2x52)/k2)
	al6.set_xdata(Ts*(x52-i2x52)/k2)
	al7.set_xdata(Ts*(x62-i2x52)/k2)

axPfreq.on_changed(update)
axTfreq.on_changed(update)

resetax = plt.axes([0.05,0.1,0.1,0.04])
button  = Button(resetax, 'Reset', color=axcolor)

def reset(event):
	axTfreq.reset()
	axPfreq.reset()

button.on_clicked(reset)


plt.show()








