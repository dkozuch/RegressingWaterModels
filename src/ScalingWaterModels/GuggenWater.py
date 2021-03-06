from TData import CriticalParams
import numpy as np
from numpy.polynomial.polynomial import polyval2d,polyval
from numpy import poly1d
import warnings

class TIP4P2005:
	def __init__(self,CP=CriticalParams(182.,170.,0.05645)):
		assert isinstance(CP,CriticalParams)
		self.CriticalParams = CP
		self.spinodal = np.array([-462.,475.02,-215.306])
		L0, a, b, d, f = 1.55607, 0.154014, 0.125093, 0.0085418, 1.14576
		self.widom = np.array([[0., a*L0, d*L0],[L0, b*L0, 0.], [f*L0, 0., 0.]])
		self.model_name = "TIP4P2005"

	def getSpinodalCriticalPointOffset(self):
		return self.CriticalParams.Pc - self.spinodal[0]

	def WidomLine(self,T,P):
		That, Phat = self.CriticalParams.reduceTandP(T,P)
		return polyval2d(That,Phat,self.widom)

	def WidomLine_T(self,T,P):
		"""Derivative of Widom Line with respect to temperature"""
		That,Phat = self.CriticalParams.reduceTandP(T,P)
		return polyval2d(That,Phat,polyder(self.widom,axis=0))

#	@classmethod
	def SpinodalPressure(self,T):
		That = self.CriticalParams.reduceT(T)
		return polyval(That,self.spinodal)

#	@classmethod
	def WidomTemperature(self,P):
		Phat = self.CriticalParams.reduceP(P)
		Thatroots = ((poly1d(polyval(Phat,np.transpose(self.widom))[::-1])).r) #roots for temperature
		Troots = self.CriticalParams.invertT(Thatroots)

		#check for good root
		T = np.extract(np.isreal(Troots),Troots)

		if len(T) == 0:
			raise ValueError("No real roots found for Pressure as %f" % P)
		elif len(T) == 1:
			return float(T)
		else:
			newT = np.extract(np.array([x >= 100. and x <= 600. for x in T]),T)
			if len(newT) > 1:
				warnings.warn("Too many values returned for WidomT. I will pick largest.")
				return float(newT[-1])
			else:
				return float(newT)

	def writeWidomLine(self,filename="Widom.dat",P=[]):
		import pandas as pd
		data = [[self.WidomTemperature(p),p,"Widom","TSEOS"] for p in P]
		df = pd.DataFrame(data,columns=['Temperature(K)',
			'Pressure (MPa)', 'Feature', 'Source'])
		df.to_csv(filename,sep="\t",index=False,header=False)



class ST2I_mean_field(TIP4P2005):
	def __init__(self,CP=CriticalParams(253.5,160.,0.052478)):
		assert isinstance(CP,CriticalParams)
		self.CriticalParams = CP
		self.spinodal = np.array([-234.38-50.,628.41,-720.12])
		L0, a, b, d, f = 3.4915, 0.085811, 0., 0., 0.
		self.widom = np.array([[0., a*L0, d*L0],[L0, b*L0, 0.], [f*L0, 0., 0.]])
		self.model_name = "ST2"


class TIP5P(TIP4P2005):
	def __init__(self,CP=CriticalParams(213.,338.,0.0595)):
		assert isinstance(CP,CriticalParams)
		self.CriticalParams = CP
		self.spinodal = np.array([-496.40292951,  1503.16997588, -1632.66291085])
		L0, a, b, d, f = 1.86946, 0.09801, 0.19569, 0.00517, 3.13075
		self.widom = np.array([[0., a*L0, d*L0],[L0, b*L0, 0.], [f*L0, 0., 0.]])
		self.model_name = "TIP5P"



class GuggenheimWater:
	def __init__(self,model=TIP4P2005()):
		self.model = model
		self.havefigure = False
		self.Trescale = []
		self.Prescale = []
		self.Property = []
		self.Source = []
		self.PropertyDict = {}
		self.Rescalings = {}
		self.l = 1.

	def rescale(self,T,P,offsetCriticalPt=1.,off2=1.,mode="V0"):
		Tw, Ps =  self.model.WidomTemperature(P),self.model.SpinodalPressure(T)
		Tc, Pc = self.model.CriticalParams.Tc, self.model.CriticalParams.Pc
		off = offsetCriticalPt
		if mode == "V0":
			Tr, Pr = off*(T-Tw)/Tc, off2*(P-Ps)/(Pc-Ps)
		else:
			if (P-Ps) < 0.75*(Pc-Ps):
				Tr, Pr = (T-Tw)/100.,(P-Ps)/644
			else:
				Tr, Pr = (T-Tw)/100., P/Pc
		return Tr, Pr

	def classic(self,T,P):
		Tc,Pc = self.model.CriticalParams.Tc, self.model.CriticalParams.Pc
		return T/Tc, P/Pc

	def classicAndWidom(self,T,P):
		Tc,Pc = self.model.CriticalParams.Tc, self.model.CriticalParams.Pc
		return (T-self.model.WidomTemperature(P)), P/Pc

	def delineateKT(self,T,P):
		pass

	def delineateSpinodal(self,T,P):
		return T, P - self.model.SpinodalPressure(T)

	def delineateWidomLine(self,T,P):
		return T-self.model.WidomTemperature(P), P

	def delineateSpinodalandWidomLine(self, T, P):
		return T-self.model.WidomTemperature(P), P - self.model.SpinodalPressure(T)

	def delineateCriticalPoint(self,T,P,l=1.):
		Ps = self.model.SpinodalPressure(T)
		PPs = P - Ps
		TTw = T - self.model.WidomTemperature(P)
		Tc = self.model.CriticalParams.Tc
		Pc = self.model.CriticalParams.Pc
		PsTc = self.model.SpinodalPressure(Tc)
		if PPs <= self.PPst : return T-Tc, P-Pc #TTw/Tc, PPs/Pc 
		else: 
			return T-Tc, P-Pc #TTw/Tc, PPs/(Pc) #

	def identity(self,T,P):
		return T,P

	def findScalingConstantPerProperty(self, Pt, PPst,Tt):
		Pc,Tc = self.model.CriticalParams.Pc, self.model.CriticalParams.Tc
		PsTc = self.model.SpinodalPressure(Tc)
		PsTt = self.model.SpinodalPressure(Tt)
		print("My (Pt, PPst, Tt) is %f, %f, %f"%(Pt,PPst,Tt))
		self.K = (Pc - PsTc)/((Pt-PsTc)*PPst)
		self.PPst = PPst
		self.l = (Pt - 0.5*Pc)/(PsTt*(1+0.5))

	def clearAll(self):
		mymodel = self.model
		self.__init__(model=mymodel)


	def addPoint(self,T,P,Property="Unknown",Source="Unknown",offsetCriticalPt=1.,off2=1.,callback="rescale"):
		try:
			func = getattr(self,str(callback))
		except:
			print("Callback function error, valid options are:\ndelineateSpiondal\ndelineateWidomLine\n"\
				"delineateSpinodalandWidomLine\ndelineateCriticalPoint\nclassic\nclassicAndWidom\n")
			exit(-1)
		if callback == "rescale":
			x,y = func(T,P,offsetCriticalPt,off2=off2)
		else:
			x,y = func(T,P)
		self.Trescale.append(x)
		self.Prescale.append(y)
		self.Property.append(Property)
		self.Source.append(Source)

		if Property not in self.PropertyDict: self.PropertyDict[Property] = []
		self.PropertyDict[Property].append([x,y,Source,T,P])




	def writetoFile(self,filename="RescaledTIP4P2005.dat",isnew=True, add_critical_pt=True,offsetCriticalPt=1.,callback="rescale"):
		if add_critical_pt: self.addPoint(self.model.CriticalParams.Tc, self.model.CriticalParams.Pc,"LLCP","TSEOS",offsetCriticalPt,callback)
		if not self.PropertyDict:
			print("No entries have been added to dictionary. Drops mic!")
		else:
			model_name = self.model.model_name
			with open(filename,'a') as fn:
				if isnew: fn.write('Temperature\tPressure\tProperty\tSource\tModel\n')
				for myproperty in self.PropertyDict:
					T,P,S = np.transpose(np.array(self.PropertyDict[myproperty]))[0:3]
					for i in np.arange(len(T)):
						fn.write('%f\t%f\t%10s\t%10s\t%10s\n'%(float(T[i]),float(P[i]),myproperty,S[i],model_name))
			fn.close()



	def plot(self,savefig=False,skip=[],style='fivethirtyeight',wait=False,marker='o',
			xlim=None,ylim=None,xlabel='Spinodal Line',ylabel='Widom Line'):
		try:
			import matplotlib.pyplot as plt
			hsv = plt.get_cmap()
			colors = hsv(np.linspace(0,1.0,len(self.PropertyDict)))
			with plt.style.context(style):
				for myproperty,color in zip(self.PropertyDict,colors):
					T = np.array(self.PropertyDict[myproperty])[:,0]
					P = np.array(self.PropertyDict[myproperty])[:,1]
					if myproperty not in skip: 
						plt.plot(T,P,marker,label=myproperty, markersize=6,color=color, linewidth=2)
					else:
						plt.plot(T,P,'-',label=myproperty, linewidth=2, color=color)

				plt.legend(numpoints=1,frameon=False,fontsize=10,loc='upper right')
				plt.xlabel(xlabel,fontsize=20)
				plt.ylabel(ylabel,fontsize=20)
				if ylim is not None: plt.axes().set_ylim(ylim)
				if xlim is not None: plt.axes().set_xlim(xlim)
				#plt.axes().set_aspect('equal','datalim')
				if not wait: plt.show() if not savefig else plt.savefig('RescaledPhaseDiagram.png',bbox_inches='tight',dpi=300)

		except:
			print("Plotting error")

if __name__ == "__main__":
	GW = GuggenheimWater()
	GW.addPoint(200,140,'Kt')
	GW.addPoint(230,120,'Kt')
	GW.addPoint(320,110,'Cp')
	GW.plot(savefig=True)
