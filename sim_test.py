import numpy as np

a = np.random.randint(5, size=5)
# a = [3,3,0,0,0]
ba = ''.join(np.binary_repr(e, width=3) for e in a)
mask = [3, 3, 0, 0, 0]
bmask = list2bin(mask)
def list2bin(li):
    return ''.join(np.binary_repr(e, width=3) for e in a)

def comp(a, b):
    return a xor b
print(a)
print(ba)

