Project Description
-------------------

Ant Colony Simulation Project by Malte Lichtenberg and Lucas Tittmann under GNU GPL v3 is a project to simulate a colony of ants, represented in 2d in Python using PyGame.

Check out the latest version at Github: https://github.com/Andarin/Ant-Colony-Simulation-Python
Operating system: Tested under Windows 7 64bit

How to play
-----------

Ant food searching is simulated. Ants spawn automatically with time, while food must be added manually. It is possible to create wall to see if the ants find a way arround obstacles. Ants will gather food from the food source until it is depleated, and during that process (hopefully) optimize their way.
  
Controls  
--------  
 
Left Mouse Button - Clicking on buttons and clicking on the field will drop the items. To create a wall, click on the wall button, then click on to points in the field. A linear wall between the points will be created.

Compiling information
---------------------

Besides the pure Python code, which needs PyGame to run, there is an optimized version using Cython. Furthermore, an executable for Windows is also included.