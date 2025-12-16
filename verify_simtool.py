import sys
import os
sys.path.append(os.getcwd())

from nanohublib.simtool.params import Boolean, Integer, Text, Choice, Number

print("Testing Boolean widget...")
b = Boolean(description="Test Bool", value=True)
w_b = b.widget()
print(f"Boolean widget created: {w_b}")

print("Testing Integer widget...")
i = Integer(description="Test Int", value=10, min=0, max=100)
w_i = i.widget()
print(f"Integer widget created: {w_i}")

print("Testing Text widget...")
t = Text(description="Test Text", value="Hello")
w_t = t.widget()
print(f"Text widget created: {w_t}")

print("Testing Choice widget...")
c = Choice(description="Test Choice", value="A", options=["A", "B"])
w_c = c.widget()
print(f"Choice widget created: {w_c}")

print("Testing Number widget...")
n = Number(description="Test Num", value=3.14, min=0, max=10, units="m")
w_n = n.widget()
print(f"Number widget created: {w_n}")

print("All SimTool widgets verification passed!")
