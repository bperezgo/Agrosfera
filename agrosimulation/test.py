import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import time
"""
result = []
parameter = 0.2
loc = 15.18
scale = 16.20
for i in range(1000):
    result.append(np.random.logistic(loc, scale))
x = np.arange(1000) - 500
x = (x - loc) / scale
#pdf = lambda x: parameter * np.exp(- parameter * x)
pdf = lambda x: np.exp(-(x - loc) / scale) / ( scale*( 1 + np.exp(-(x - loc) / scale) )**2)
y = np.array(list(map(pdf, x)))

plt.plot(x, y, label = 'model')
sns.distplot(result)
plt.show()
"""
#"""
def student_ecuation(params):
    x1 = ( -params[1] - np.sqrt( params[1]*params[1] - 4 * params[0] * params[2] ) ) / ( 2 * params[0])
    x2 = ( -params[1] + np.sqrt( params[1]*params[1] - 4 * params[0] * params[2] ) ) / ( 2 * params[0])
    return [x1, x2]
#"""
