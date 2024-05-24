
# Import libraries
import matplotlib.pyplot as plt
import pandas as pd
 
 
# df= pd.read_csv("./plot/fineness.csv")
df= pd.read_csv("./plot/runtime.csv")



list1 = df['PTdetector'].tolist()
list2 = df['Wappalyzer'].tolist()
list3 = df['LDC'].tolist()
list4 = df['PTV'].tolist()


# Create the plot with different colors for each group
boxplot = plt.boxplot(x=[list1, list2, list3, list4],
                    labels=['PTdetector','Wappalyzer', 'LDC', 'extended PTdetector\n+ PTV'],
                    patch_artist=True,
                    medianprops={'color': 'black'},
                    widths=0.35
                    ) 

# Define colors for each group
colors = ["#9FC5E9", "#9FC5E9", "#9FC5E9", "#F5CCCC"]

plt.ylabel('runtime (seconds)')

# Assign colors to each box in the boxplot
for box, color in zip(boxplot['boxes'], colors):
    box.set_facecolor(color)



plt.show()