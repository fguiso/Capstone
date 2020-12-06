import pandas as pd 
import matplotlib as plt 

y = pd.read_csv("y.csv")
y_next = y.iloc[1:y.shape[0]]

y_sim6507=y[0:1724]
y_next_sim6507 = y_next[0:1724]
y_simTIA=y[1725:y.shape[1]]
y_next_simTIA = y_next[1725:y.shape[1]]

print(y_sim6507.shape,y_simTIA.shape)

label_6507 = []
for i in range(y_next_sim6507.shape[0]):
  label_6507.append(sum(y_next_sim6507.iloc[i]!=y_sim6507.iloc[i]))

plt.hist(label_6507)
plt.ylabel("Number of Occurences")
plt.xlabel("Number of Wires which Changed States")
plt.title("Histogram of the Number of Wires which Changed States after one Step for Sim6507")
plt.savefig("sim6507_hist1.png")
plt.show()

label_tia = []
for i in range(y_next_simTIA.shape[0]):
  label_tia.append(sum(y_next_simTIA.iloc[i]!=y_simTIA.iloc[i]))
  
plt.hist(label_tia)
plt.ylabel("Number of Occurences")
plt.xlabel("Number of Wires which Changed States")
plt.title("Histogram of the Number of Wires which Changed States after one Step for SimTIA")
plt.savefig("simtia_hist1.png")
plt.show()


