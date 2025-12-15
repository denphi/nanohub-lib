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

from __future__ import print_function
import ipywidgets as widgets
from IPython.display import display, HTML, Javascript
from string import Template
from traitlets import Unicode, Int, List

# A Really simple modal dialog widget using the bootstrap modal dialog.

css_template = """
<style type="text/css">

.modal-dialog {
    width: ${width};
}
"""

import anywidget

class Modal(anywidget.AnyWidget):
    _esm = """
    export default {
        render({ model, el }) {
            let modal = document.createElement('div');
            modal.style.cssText = "position: fixed; z-index: 1050; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4); display: flex; align-items: flex-start; justify-content: center; padding-top: 50px;";
            
            let content = document.createElement('div');
            // We use 'modal-dialog' class to pick up the width from the injected CSS
            content.className = "modal-dialog";
            content.style.cssText = "background-color: #fff; margin: auto; padding: 0; border: 1px solid #888; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2),0 6px 20px 0 rgba(0,0,0,0.19); border-radius: 6px; display: flex; flex-direction: column; background-clip: padding-box; border: 1px solid rgba(0,0,0,.2); outline: 0;";
            
            let header = document.createElement('div');
            header.style.cssText = "padding: 15px; border-bottom: 1px solid #e5e5e5; min-height: 16.43px;";
            let title = document.createElement('h4');
            title.style.margin = "0";
            title.textContent = model.get('title');
            header.appendChild(title);
            
            let body = document.createElement('div');
            body.style.cssText = "padding: 15px; position: relative;";
            body.innerHTML = model.get('body');

            let footer = document.createElement('div');
            footer.style.cssText = "padding: 15px; text-align: right; border-top: 1px solid #e5e5e5;";

            let buttons = model.get('buttons');
            let bprim = model.get('bprim');
            
            buttons.forEach((btnLabel, i) => {
                let btn = document.createElement('button');
                btn.textContent = btnLabel;
                // Basic bootstrap-like styles
                let baseStyle = "display: inline-block; margin-bottom: 0; font-weight: 400; text-align: center; vertical-align: middle; cursor: pointer; border: 1px solid transparent; white-space: nowrap; padding: 6px 12px; font-size: 14px; line-height: 1.42857143; border-radius: 4px; margin-left: 5px;";
                
                if (i === bprim) {
                    btn.setAttribute('class', 'btn btn-primary');
                    btn.style.cssText = baseStyle + "color: #fff; background-color: #337ab7; border-color: #2e6da4;";
                } else {
                    btn.setAttribute('class', 'btn btn-default');
                    btn.style.cssText = baseStyle + "color: #333; background-color: #fff; border-color: #ccc;";
                }
                
                btn.onclick = () => {
                    model.set('value', i);
                    model.save_changes();
                    modal.style.display = "none";
                };
                footer.appendChild(btn);
            });

            content.appendChild(header);
            content.appendChild(body);
            content.appendChild(footer);
            modal.appendChild(content);
            el.appendChild(modal);
        }
    }
    """
    value = Int(-1).tag(sync=True)
    buttons = List(['OK']).tag(sync=True)
    bprim = Int(0).tag(sync=True)
    body = Unicode('').tag(sync=True)
    title = Unicode('').tag(sync=True)

    def __init__(self, **kwargs):

        """Constructor"""
        super(self.__class__, self).__init__(**kwargs)
        bcb = kwargs.get('cb', None)
        self.bprim = self.check_primary(kwargs.get('primary', 'OK'))
        self.cb = kwargs.get('cb')
        if self.cb:
            self.observe(self._cb, names='value')

        width = kwargs.get('width', '50%')
        d = dict(width=width)
        temp = Template(css_template).substitute(d)
        display(HTML(temp))

    def _cb(self, change):
        self.cb(change['new'])

    def check_primary(self, p):
        # primary sets the highlighted dialog button.
        # it must be valid index or name of a button
        if p in self.buttons:
            return self.buttons.index(p)

        if type(p) == int and p >= 0 and p < len(self.buttons):
            return p

        raise ValueError('Primary must by an index or button string.')
