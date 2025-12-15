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
from IPython.display import HTML, Javascript, display
from string import Template
from traitlets import Unicode, Bool, Int

# NOT FINISHED.  DO NOT USE

# https://ace.c9.io/build/kitchen-sink.html

import anywidget

css_template = """
<style type="text/css" media="screen">
#${editor} {
    margin-left: 15px;
    margin-top: 15px;
    height: ${height};
    width: ${width};
    border-style: ${border};
}
</style>
"""

class EditorWidget(anywidget.AnyWidget):
    _esm = """
    function loadScript(src) {
        return new Promise((resolve, reject) => {
            if (document.querySelector(`script[src="${src}"]`)) {
                if (window.ace) return resolve();
            }
            let script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    export default {
        render({ model, el }) {
            let div = document.createElement('div');
            div.setAttribute('id', model.get('name'));
            el.appendChild(div);

            let editor = null;
            let ignorex = false;
            let ignorev = false;

            function initEditor() {
                editor = ace.edit(div);
                
                editor.setTheme("ace/theme/" + model.get('theme'));
                editor.getSession().setMode("ace/mode/" + model.get('mode'));
                editor.setShowPrintMargin(model.get('showmargin'));
                div.style.fontSize = model.get('fontsize');

                // Initial value
                if (model.get('value2')) {
                    editor.setValue(model.get('value2'));
                }

                editor.getSession().on('change', function(e) {
                    if (ignorev === true) { return; }
                    ignorex = true;
                    model.set('value2', editor.getValue());
                    model.save_changes();
                    ignorex = false;
                });

                // Listeners
                model.on('change:theme', () => {
                   editor.setTheme("ace/theme/" + model.get('theme')); 
                });
                model.on('change:mode', () => {
                    editor.getSession().setMode("ace/mode/" + model.get('mode'));
                });
                model.on('change:value2', () => {
                    if (ignorex === true) { return; }
                    let val = model.get('value2');
                    ignorev = true;
                    editor.setValue(val);
                    ignorev = false;
                });
                model.on('change:showmargin', () => {
                    editor.setShowPrintMargin(model.get('showmargin'));
                });
                model.on('change:fontsize', () => {
                    div.style.fontSize = model.get('fontsize');
                });
            }

            loadScript('//cdnjs.cloudflare.com/ajax/libs/ace/1.2.6/ace.js')
                .then(() => {
                    if (window.ace) {
                        initEditor();
                    } else {
                         let interval = setInterval(() => {
                             if (window.ace) {
                                 clearInterval(interval);
                                 initEditor();
                             }
                         }, 100);
                    }
                });
        }
    }
    """
    name = Unicode('').tag(sync=True)
    theme = Unicode('').tag(sync=True)
    mode = Unicode('').tag(sync=True)
    showmargin = Bool(True).tag(sync=True)
    fontsize = Unicode('').tag(sync=True)
    state = Unicode('').tag(sync=True)
    value2 = Unicode('').tag(sync=True)

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.errors = widgets.CallbackDispatcher(accepted_nargs=[0, 1])
        self.on_msg(self._handle_custom_msg)

    def _handle_custom_msg(self, content):
        if 'event' in content and content['event'] == 'error':
            self.errors()
            self.errors(self)


class Editor(widgets.DOMWidget):
    num = 0

    def __init__(self, **kwargs):
        self.name = 'editor' + str(Editor.num)
        Editor.num += 1
        height = kwargs.get('height', '500px')
        width = kwargs.get('width', 'auto')
        border = kwargs.get('border', 'solid')
        self._theme = kwargs.get('theme', 'xcode')
        self._mode = kwargs.get('mode', 'python')
        self._fontsize = kwargs.get('fontsize', '14px')

        d = dict(height=height,
                 width=width,
                 border=border,
                 editor=self.name)
        temp = Template(css_template).substitute(d)
        display(HTML(temp))
        self.ed = EditorWidget()
        self.ed.name = self.name
        # self.ed.observe(self.value_loading, names='value2')

    @property
    def value(self):
        return self.ed.value2

    @value.setter
    def value(self, val):
        self.ed.value2 = val

    @property
    def theme(self):
        return self.ed.theme

    @theme.setter
    def theme(self, val):
        self.ed.theme = val

    @property
    def mode(self):
        return self.ed.mode

    @mode.setter
    def mode(self, val):
        self.ed.mode = val

    @property
    def fontsize(self):
        return self.ed.fontsize

    @fontsize.setter
    def fontsize(self, val):
        self.ed.fontsize = val

    def _ipython_display_(self):
        self.ed._ipython_display_()
        self.ed.state = 'start'
        self.ed.theme = self._theme
        self.ed.mode = self._mode
        self.ed.showmargin = False
        self.ed.fontsize = self._fontsize
        self.ed.state = ''
