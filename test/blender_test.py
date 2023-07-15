import os
import sys
local_module_path = "/Users/zakaton/Documents/GitHub/ukaton-mission-python-sdk"
if local_module_path not in sys.path:
    sys.path.append(local_module_path)

local_module_path = "/usr/local/lib/python3.10/site-packages"
if local_module_path not in sys.path:
    sys.path.append(local_module_path)

filename = "/Users/zakaton/Documents/GitHub/ukaton-mission-python-sdk/examples/basic.py"
exec(compile(open(filename).read(), filename, 'exec'))
