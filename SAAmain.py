#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 12 13:57:56 2022

@author: ashleyhumpal
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 18:50:24 2022

@author: ashleyhumpal
"""

from pyb import UART
from SAA import SAA


## 1 for KR FEEDBACK, 2 FOR KP FEEDBACK
task2 = SAA(1) 


while True: 
    task2.run() #runs task
    