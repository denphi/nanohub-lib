#  Copyright 2025 HUBzero Foundation, LLC.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

#  HUBzero is a registered trademark of Purdue University.

#  Authors:
#  Daniel Mejia (denphi), Purdue University (denphi@denphi.com)

"""
Line magic to allow the 'use' command to load hub environment modules.
This works on the current environment, so we cannot simply fork a shell.
Maybe some trick to fork a shell and return the modified environment would work?
For now lets see how this works.  Just implement "setenv", "prepend", and "use".
Works for all currently installed modules except two old ones that use local shell variables.
"""

import sys
import os
import subprocess
from string import Template
from IPython.core.magic import register_line_magic

EPATH = os.environ['ENVIRON_CONFIG_DIRS'].split()
d = {}


def setenv(line):
    name = line[0]
    val = ' '.join(line[1:])
    try:
        completedProcess = subprocess.run("""/bin/bash -c 'echo %s'""" % (val),stdout=subprocess.PIPE,shell=True)
    except:
        pass
    else:
        if completedProcess.returncode == 0:
            try:
                os.environ[name] = completedProcess.stdout.strip().decode('utf-8')
                _set(name, os.environ[name])
            except:
                pass

def prepend(line):
    global d
    name, val = line
    val = Template(val).safe_substitute(d)

    try:
        completedProcess = subprocess.run("""/bin/bash -c 'echo %s'""" % (val),stdout=subprocess.PIPE,shell=True)
    except:
        pass
    else:
        if completedProcess.returncode == 0:
            try:
                val = completedProcess.stdout.strip().decode('utf-8')
            except:
                pass

    try:
        oldval = os.environ[name]
        val = '%s:%s' % (val, oldval)
    except:
        pass
    os.environ[name] = val

    if name == 'PYTHONPATH':
        for p in reversed(val.split(':')):
            sys.path.insert(1,p)


def _set(a, b):
    global d
    t = Template(b)
    b = t.safe_substitute(d)
    d[a] = b

def _use(name):

    fname = None
    for e in EPATH:
        ename = os.path.join(e, name)
        if os.path.isfile(ename):
            fname = ename
            break
    if fname is None:
        raise ValueError(f'use: could not find module: {name}')
    
    with open(fname) as fp:
        for line in fp:
            sline = line.strip().split()
            if sline == []:
                continue
            if sline[0] == 'prepend':
                prepend(sline[1:])
                continue
            if sline[0] == 'setenv':
                setenv(sline[1:])
                continue
            if sline[0] == 'use':
                _use(sline[-1])
                continue
            line = line.split("=")
            if len(line) == 2:
                _set(line[0].strip(), line[1].strip())

try:
    get_ipython()

    @register_line_magic
    def use(name):
        _use(name)

    # We delete this to avoid name conflicts for automagic to work
    del use
except:
    pass
