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

from ipywidgets import VBox, Dropdown, FloatText, Text, Tab, IntSlider
import puq

class UQVar:

    def __init__(self, name, label, state, a, b=1):
        self.name = name
        self.label = label
        self.w = Dropdown(
            options=['Exact', 'Gaussian', 'Uniform'],
            description='%s:' % label,
            value=state)

        self.w1 = FloatText(value=a, description='mean:')
        self.w2 = FloatText(value=b, description='dev:')
        self.form = VBox(children=[self.w, self.w1, self.w2],
                         padding=10,
                         border_width=5)
        self.w.on_trait_change(self.on_value_change, 'value')
        self.on_value_change('')

    def on_value_change(self, v):
        value = self.w.value
        if value == 'Exact':
            self.w2.visible = False
            self.w1.description = 'value:'
        elif value == 'Gaussian':
            self.w1.description = 'mean:'
            self.w2.description = 'dev:'
            self.w2.visible = True
        else:
            self.w1.description = 'min:'
            self.w2.description = 'max:'
            self.w2.visible = True

    @property
    def value(self):
        value = self.w.value
        if value == 'Exact':
            return [self.name, self.label, self.w1.value]
        if value == 'Gaussian':
            return puq.NormalParameter(self.name, self.label, mean=self.w1.value, dev=self.w2.value)
        if value == 'Uniform':
            return puq.UniformParameter(self.name, self.label, min=self.w1.value, max=self.w2.value)
        return None

def uqrun(**kwargs):
    u = UQRun(kwargs)
    return u

class UQRun:
    def __init__(self, uq_type, uq_args, cmd, varlist, outfiles=[], newdir=False):
        self.fname = 'foo.hdf5'

        cmd_t = Template(cmd)
        newlist = []
        for v in varlist:
            if not isinstance(v, puq.Parameter):
                cmd = cmd_t.safe_substitute({v[0]: v[2]})
                cmd_t = Template(cmd)
            else:
                newlist.append(v)
        varlist = newlist
        uq = puq.Smolyak(varlist, level=uq_args)
        host = puq.InteractiveHost()
        prog = puq.TestProgram(exe=cmd, outfiles=outfiles, newdir=newdir)
        sw = puq.Sweep(uq, host, prog)
        sw.run(self.fname, overwrite=True)
        self.hf = h5py.File(self.fname, 'r')

    def plot_responses(self):
        names = puq.hdf.get_output_names(self.hf)
        for n in names:
            rf = puq.hdf.get_response(self.hf, n)
            rf.plot(title=False)
        plt.show()

    def plot_pdfs(self):
        names = puq.hdf.get_output_names(self.hf)
        for n in names:
            rf = puq.hdf.get_response(self.hf, n)
            rf.pdf(fit=False).plot()
        plt.show()

    def plotly_pdfs(self):
        names = puq.hdf.get_output_names(self.hf)
        for n in names:
            rf = puq.hdf.get_response(self.hf, n)
            pdf = rf.pdf(fit=False)
            trace1 = Scatter(
                x=pdf.x,
                y=pdf.y,
                mode='lines'
            )
        data = Data([trace1])
        return py.iplot(data, filename='PDF')

    def plotly_responses(self):
        names = puq.hdf.get_output_names(self.hf)
        for n in names:
            rf = puq.hdf.get_response(self.hf, n)
            return plot_ly(rf)

    def __del__(self):
        self.hf.close()
