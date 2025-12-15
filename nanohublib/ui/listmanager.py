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
import base64
import sys
from IPython.display import display, Javascript, HTML
from string import Template

from traitlets import List, Unicode, Bool, Int

css_template = """
<style type="text/css">

.lmheader {
    border: solid;
    display: table;
    width: ${width};
}

.lmheader:after {
    content: "";
    display: table;
    clear: both;
}

.lmaddBtn {
    padding: 10px;
    background: #d9d9d9;
    color: #555;
    float: right;
    text-align: center;
    cursor: pointer;
    transition: 0.3s;
}

.lmaddIcon {
    padding: 10px;
    background: #d9d9d9;
    color: #555;
    float: right;
    text-align: center;
    cursor: pointer;
    transition: 0.3s;
}

.lmaddBtn:hover {
    background-color: #bbb;
}
.lmaddIcon:hover {
    background-color: #bbb;
}

/* Remove margins and padding from the list */
.lmUL {
    margin: 0;
    padding: 0;
}

/* Style the list items */
.lmUL li {
    cursor: pointer;
    position: relative;
    padding: 12px 8px 12px 40px;
    background: #eee;
    transition: 0.2s;
    width: ${width};

    /* make the list items unselectable */
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
}

/* Set all odd list items to a different color (zebra-stripes) */
.lmUL li:nth-child(odd) {
    background: #f9f9f9;
}

/* Darker background-color on hover */
.lmUL li:hover {
    background: #ddd;
}

</style>

"""


import anywidget

class ListManager(anywidget.AnyWidget):

    _esm = """
    export default {
        render({ model, el }) {
            let div = document.createElement('div');
            div.setAttribute('class', 'lmheader');
            
            let input = document.createElement('input')
            input.setAttribute('type', 'text');
            input.setAttribute('placeholder', model.get('list_text'));
            input.setAttribute('style', 'border: none; float: left; width: 90%; padding: 10px');
            
            let span = document.createElement('span')

            if (model.get('button_text') === ''){
                span.setAttribute('class', 'lmaddIcon fa fa-plus fa-1g');
            } else {
                span.innerHTML = model.get('button_text');
                span.setAttribute('class', 'lmaddBtn');
            }

            div.appendChild(input);
            div.appendChild(span);
            el.appendChild(div);
            
            let ul = document.createElement('ul');
            ul.setAttribute('class', 'lmUL');
            el.appendChild(ul);

            let lm_list = [];

            function update_lm_list() {
                lm_list = [];
                let children = ul.childNodes;
                for (let i = 0; i < children.length; i++) {
                    let item = children[i];
                    if (item.style.display != "none") {
                        lm_list.push(item.textContent.slice(0,-1));
                    }
                }

                model.set('value', lm_list);
                model.save_changes();
            }

            function add_list_element(val) {
                if (val === '') {
                    return
                }
                let li = document.createElement("li");
                let t = document.createTextNode(val);
                li.setAttribute('class', 'lmValue');
                li.appendChild(t);

                // clear name from input box
                input.value = "";

                let closeSpan = document.createElement("SPAN");
                let txt = document.createTextNode("\u00D7");
                closeSpan.className = "close";
                closeSpan.appendChild(txt);
                li.appendChild(closeSpan);
                ul.appendChild(li);

                closeSpan.onclick = function() {
                    let li_parent = this.parentElement;
                    li_parent.style.display = "none";
                    update_lm_list();
                }
            }

            function value_changed() {
                // remove the old list
                ul.innerHTML = '';

                let vals = model.get('value');
                for (let i = 0; i < vals.length; i++){
                    add_list_element(vals[i]);
                }
            }

            function handle_lm_change(evt) {
                // value added from UI
                if (lm_list.indexOf(evt.target.value) === -1) {
                    add_list_element(evt.target.value);
                    update_lm_list();
                }
            }

            // set initial values
            value_changed();

            model.on('change:value', value_changed);
            input.addEventListener('change', handle_lm_change);
        }
    }
    """
    value = List([]).tag(sync=True)
    button_text = Unicode('Add').tag(sync=True)
    list_text = Unicode('New Value...').tag(sync=True)

    # skipped = List([]).tag(sync=True)
    # multiple = Bool(False).tag(sync=True)
    # maxsize = Int(1024*1024).tag(sync=True)

    def __init__(self, **kwargs):

        """Constructor"""
        super(self.__class__, self).__init__(**kwargs)


        # Allow the user to register error callbacks with the following signatures:
        #    callback()
        #    callback(sender)
        self.errors = widgets.CallbackDispatcher(accepted_nargs=[0, 1])

        # Listen for custom msgs
        self.on_msg(self._handle_custom_msg)


        width = kwargs.get('width', '100%')
        d = dict(width=width)
        temp = Template(css_template).substitute(d)
        display(HTML(temp))

        self.value = kwargs.get('value', [])

        self.in_cb = False
        self.cb = kwargs.get('cb')
        if self.cb:
            self.observe(self._cb, names='value')


    def _cb(self, change):
        if self.in_cb:
            return
        self.in_cb = True
        self.cb(change['name'], change['new'])
        self.in_cb = False

    def _handle_custom_msg(self, content):
        """Handle a msg from the front-end.

        Parameters
        ----------
        content: dict
            Content of the msg."""
        if 'event' in content and content['event'] == 'error':
            self.errors()
            self.errors(self)


    @property
    def visible(self):
        return self.layout.visibility

    @visible.setter
    def visible(self, newval):
        if newval:
            self.layout.visibility = 'visible'
            return
        self.layout.visibility = 'hidden'
