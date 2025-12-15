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

import os
import ipywidgets as ui


class PathSelector():
    """
    The PathSelector widget allows the user to choose a path in the server (container).  It cannot access files
    from the user's computer.

    :param start_dir: The directory to display.
    :param select_file: True for file select.  False for directory select.
    """

    def __init__(self, start_dir, select_file=True):
        self.file = None
        self.select_file = select_file
        self.value = start_dir
        self.select = ui.SelectMultiple(options=['init'], value=(), rows=10, description='')
        self.accord = ui.Accordion(children=[self.select])

        self.accord.selected_index = None  # Start closed (showing path only)
        self.refresh(self.value)
        self.select.observe(self.on_update, 'value')

    def on_update(self, change):
        if len(change['new']) > 0:
            self.refresh(change['new'][0])

    def refresh(self, item):
        path = os.path.abspath(os.path.join(self.value, item))

        if os.path.isfile(path):
            if self.select_file:
                self.accord.set_title(0, path)
                self.file = path
                self.accord.selected_index = None
            else:
                self.select.value = ()

        else:  # os.path.isdir(path)
            self.file = None
            self.value = path

            # Build list of files and dirs
            keys = ['[..]']
            for item in os.listdir(path):
                if item[0] == '.':
                    continue
                elif os.path.isdir(os.path.join(path, item)):
                    keys.append('[' + item + ']')
                else:
                    keys.append(item)

            # Sort and create list of output values
            keys.sort(key=str.lower)
            vals = []
            for k in keys:
                if k[0] == '[':
                    vals.append(k[1:-1])  # strip off brackets
                else:
                    vals.append(k)

            # Update widget
            self.accord.set_title(0, path)
            self.select.options = list(zip(keys, vals))
            with self.select.hold_trait_notifications():
                self.select.value = ()

    def _ipython_display_(self):
        from IPython.display import display
        display(self.accord)

    @property
    def disabled(self):
        return self.select.disabled

    @disabled.setter
    def disabled(self, newval):
        self.accord.disabled = newval
        self.select.disabled = newval

    @property
    def visible(self):
        return self.accord.layout.visibility

    @visible.setter
    def visible(self, newval):
        if newval:
            self.accord.layout.visibility = 'visible'
            return
        self.accord.layout.visibility = 'hidden'
