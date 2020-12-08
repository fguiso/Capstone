import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np

y = pd.read_csv("y.csv")
y_next = y.iloc[1:y.shape[0]]

print(y.shape)
y_sim6507=y.iloc[:,0:1725]
y_next_sim6507 = y_next.iloc[:,0:1725]
y_simTIA=y.iloc[:,1725:y.shape[1]]
y_next_simTIA = y_next.iloc[:,1725:y.shape[1]]

print(y_sim6507.shape,y_simTIA.shape)

label_6507 = []
for i in range(y_next_sim6507.shape[0]):
  label_6507.append(sum(y_next_sim6507.iloc[i]!=y_sim6507.iloc[i]))

(unique, counts) = numpy.unique(label_6507, return_counts=True)
print((unique, counts))

fig, axs = plt.subplots(2,1,figsize=(15,15))
fig.suptitle('Histogram of the Number of Wires which Changed States after one Step')
axs[0].hist(label_6507,bins=20)
axs[0].set_ylabel("Number of Occurences")
axs[0].set_xlabel("Number of Wires which Changed States")
axs[0].set_title("Sim6507")

label_tia = []
for i in range(y_next_simTIA.shape[0]):
  label_tia.append(sum(y_next_simTIA.iloc[i]!=y_simTIA.iloc[i]))

(unique, counts) = numpy.unique(label_tia, return_counts=True)
print((unique, counts))
  
axs[1].hist(label_tia,bins=20)
axs[1].set_ylabel("Number of Occurences")
axs[1].set_xlabel("Number of Wires which Changed States")
axs[1].set_title("SimTIA")
fig.savefig("hist1.png")

label_2_6507= []
for i in range(y_next_sim6507.shape[0]):
    label_2_6507.append(np.where(y_next_sim6507.iloc[i,:]!=y_sim6507.iloc[i,:])[0])
label_2_6507= np.concatenate(label_2_6507,axis=0)

(unique, counts) = numpy.unique(label_2_6507, return_counts=True)
print((unique, counts))

fig2, axs2 = plt.subplots(2,1,figsize=(15,15))
fig2.suptitle('Histogram of the Number of Times Each Wire Changed State')
axs2[0].hist(label_2_6507,bins=500)
axs2[0].set_ylabel("Number of Times Changed")
axs2[0].set_xlabel("Wires")
axs2[0].set_title("Sim6507")

label_2_tia= []
for i in range(y_next_simTIA.shape[0]):
    label_2_tia.append(np.where(y_next_simTIA.iloc[i,:]!=y_simTIA.iloc[i,:])[0])
label_2_tia= np.concatenate(label_2_tia,axis=0)

(unique, counts) = numpy.unique(label_2_tia, return_counts=True)
print((unique, counts))

axs2[1].hist(label_2_tia,bins =500)
axs2[1].set_ylabel("Number of Times Changed")
axs2[1].set_xlabel("Wires")
axs2[1].set_title("SimTIA")
fig2.savefig("hist2.png")



