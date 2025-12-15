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
from IPython.display import display, Javascript


# recommended icons: download, arrow-circle-down, cloud-download
# icons come from http://fontawesome.io/icons/
# won't be visible on ipywidgets <  6.0

# success = green
# info = blue
# warning = orange
# danger = red

class Download(object):

    def __init__(self, filename, **kwargs):

        label = kwargs.get('label', filename)
        icon = kwargs.get('icon', '')
        tooltip = kwargs.get('tooltip', '')
        style = kwargs.get('style', '')
        bcb = kwargs.get('cb', None)

        self.w = widgets.Button(
            description=label,
            icon=icon,
            tooltip=tooltip,
            button_style=style
            )

        def button_cb(filename):

            js = Javascript("window.open('%s')" % filename)

            def cb(x):
                if bcb is not None:
                    bcb()
                display(js)
            return cb

        self.w.on_click(button_cb(filename))

    def _ipython_display_(self):
        self.w._ipython_display_()
