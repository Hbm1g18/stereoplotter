import numpy as np
import mplstereonet
import matplotlib.pyplot as plt
import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'

data = pd.read_csv('data.csv')

data['Colour']='0'

fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111, projection='stereonet')
for i in range(len(data)):
        if data.loc[i][2].upper() == 'BEDDING':
                data['Colour'][i]='k'
        elif data.loc[i][2].upper() == 'CLEAVAGE':
                data['Colour'][i]='g'
        elif data.loc[i][2].upper() == 'FAULT':
                data['Colour'][i]='r'

        chosen=data.loc[i][3]
        colour=chosen
        ax.plane(data.loc[i][0], data.loc[i][1], c=colour, label=data.loc[i][2].title() + ' %03d/%02d' % (data.loc[i][0], data.loc[i][1],))
ax.legend(loc='best')

ax.grid()
print(data)


bin_edges = np.arange(-5, 366, 10)

strikes = data['strike']
dips = data['dip']

number_of_strikes, bin_edges = np.histogram(strikes, bin_edges)

number_of_strikes[0] += number_of_strikes[-1]

half = np.sum(np.split(number_of_strikes[:-1], 2), 0)
two_halves = np.concatenate([half, half])

fig2 = plt.figure(figsize=(16,8))

ax2 = fig2.add_subplot(121, projection='stereonet')

ax2.pole(strikes, dips, c='k', label='Pole of the Planes')
ax2.density_contourf(strikes, dips, measurement='poles', cmap='Reds')
ax2.set_title('Density coutour of the Poles', y=1.10, fontsize=15)
ax2.grid()

ax2 = fig2.add_subplot(122, projection='polar')

ax2.bar(np.deg2rad(np.arange(0, 360, 10)), two_halves, 
       width=np.deg2rad(10), bottom=0.0, color='.8', edgecolor='k')
ax2.set_theta_zero_location('N')
ax2.set_theta_direction(-1)
ax2.set_thetagrids(np.arange(0, 360, 10), labels=np.arange(0, 360, 10))
ax2.set_rgrids(np.arange(1, two_halves.max() + 1, 2), angle=0, weight= 'black')
ax2.set_title('Rose Diagram"', y=1.10, fontsize=15)

fig.tight_layout()

plt.show()