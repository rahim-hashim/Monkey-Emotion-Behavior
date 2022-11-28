'''
Adapted from: https://linuxtut.com/en/d9f63a8fe06eeb15cfed/
'''
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# Remove grey colormaps
all_colormap = matplotlib.pyplot.colormaps()
colormaps_remove = ['Greys', 'Greys_r']
colormap_list = [elem for elem in all_colormap if elem not in colormaps_remove]

def lyapunov_generator():

	ab=np.array([0,1])
	nab=len(ab)
	nm = np.random.randint(5,10)
	#nm=10
	#a0=2
	#a1=4
	#b0=2
	#b1=4
	list_range = np.arange(1,11)
	a0 = np.random.randint(1,5)
	a1_set = [i for i in list_range if i > a0]
	a1 = np.random.randint(min(a1_set),max(a1_set))
	b0 = np.random.randint(1,5)
	b1_set = [i for i in list_range if i > b0]
	b1 = np.random.randint(min(b1_set),max(b1_set))
	print('  nm: {}'.format(nm))
	print('  a0: {} | a1: {}'.format(a0,a1))
	print('  b0: {} | b1: {}'.format(b0,b1))

	irx=800
	iry=600

	x = np.linspace(a0,a1,irx+1)
	y = np.linspace(b0,b1,iry+1)
	X, Y = np.meshgrid(x, y)

	z=np.empty((iry+1,irx+1))
	for i in range(0,irx+1):
		a=a0+(a1-a0)/(irx)*i
		for j in range(0,iry+1):
			b=b0+(b1-b0)/(iry)*j
			s=0
			xx=0.5
			for n in range(0,nm):
				for m in range(0,nab):
					if ab[m]==0:
						rr=a
					else:
						rr=b
					xx=rr*xx*(1-xx)
					v=np.abs(rr*(1-2*xx))
					if 0<v: s=s+np.log(v)
			s=s/(nm*nab)
			if 2<s:
				z[j,i]=2
			elif s<-5:
				z[j,i]=-5
			else:
				z[j,i]=s

	z=-1.0*z
	plt.xlim(a0,a1)
	plt.ylim(b0,b1)
	random_colormap_index = np.random.randint(0,len(colormap_list))
	random_colormap = colormap_list[random_colormap_index]
	plt.pcolor(X, Y, z, cmap=random_colormap)
	plt.axis('equal')
	plt.axis('off')
	plt.show()

lyapunov_generator()