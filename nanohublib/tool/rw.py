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

from papermill.iorw import load_notebook_node
import papermill as pm
import yaml
import os
import shutil
import copy
import numpy as np
import json
import plotly
import IPython
from IPython.display import display as idisplay, Video, Image
from base64 import b64decode, b64encode
from .input_types import parse

class DB(object):

    def __init__(self, outputs):
        self.out = parse(outputs)

    def save(self, name, value, display=False):
        if not name in self.out:
            raise ValueError('\"%s\" not in output schema!' % name)
        otype = self.out[name]['type']

        if otype == 'Image':
            if type(value) is str:
                # filename
                value = Image(value)
            if type(value) is Image:
                if display:
                    idisplay(value)
                data, _metadata = IPython.core.formatters.format_display_data(
                    value)
                pm.record(name, data)
                return

        if display:
            idisplay(value)

        if otype == 'Array' and type(value) is np.ndarray:
            sval = json.dumps(value, cls=plotly.utils.PlotlyJSONEncoder)
            pm.record(name, sval)
            return

        pm.record(name, value)

# deprecated
def save(name, value, display=False):
    if display:
        idisplay(value)

    if type(value) is np.ndarray:
        sval = json.dumps(value, cls=plotly.utils.PlotlyJSONEncoder)
        pm.record(name, sval)
        return
    
    if type(value) is Video or type(value) is Image:
        data, _metadata = IPython.core.formatters.format_display_data(value)
        pm.record(name, data)
        return

    pm.record(name, value)

def read(nb, name):
    data = nb.data[name]
    if type(data) is str:
        try:
            data = json.loads(data)
        except:
            pass
    try:
        if 'image/jpeg' in data:
            return b64decode(data['image/jpeg'])
        if 'image/png' in data:
            return b64decode(data['image/png'])
    except:
        pass
    return data

def rdisplay(nb, name):
    data = nb.data[name]
    if type(data) is str:
        try:
            data = json.loads(data)
        except:
            pass
    try:
        if 'image/jpeg' in data \
            or 'image/png' in data \
            or 'image/gif' in data \
            or 'text/html' in data:
            idisplay(data, raw=True)
            return
    except:
        pass

    idisplay(data)

def _get_dict(inputs):
    if type(inputs) == dict:
        return inputs
    d = {}
    for i in inputs:
        try:
            d[i] = inputs[i].value
        except:
            pass
    return d

def run_simtool(nb, outname, inputs, outdir=None, append=True, parallel=False):
    inputs = _get_dict(inputs)
    if outdir is not None:
        if append:
            if not os.path.exists(outdir):
                os.makedirs(outdir)
        else:
            if os.path.exists(outdir):
                shutil.rmtree(outdir)
            os.makedirs(outdir)
    pm.execute_notebook(nb, os.path.join(outdir, outname), parameters=inputs)

