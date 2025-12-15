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

import ipywidgets as widgets


class FormValue(widgets.HBox):

    def __init__(self, name, widget, **kwargs):
        self.name = name
        width = kwargs.get('width', 'auto')
        self._ncb = kwargs.get('cb')
        self._widget = widget

        # accept either 'description' or 'desc'
        desc = kwargs.get('desc', kwargs.get('description', ''))
        
        form_item_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            border='solid 1px lightgray',
            justify_content='space-between',
            padding='3px',
            width=width
        )

        self._widget.layout = {'width': 'initial'}
        self._widget.disabled = kwargs.get('disabled', False)
        self._widget.observe(self._cb, names='value')

        popup = '<div data-toggle="popover" title="%s" data-container="body">%s</div>' % (desc, name)
        label = widgets.HTML(value=popup, layout=widgets.Layout(flex='2 1 auto'))
        widgets.HBox.__init__(self, [label, self._widget], layout=form_item_layout)

    def _cb(self, w):
        if self._ncb is not None:
            return self._ncb(self, w['new'])

    @property
    def cb(self):
        return self._ncb

    @cb.setter
    def cb(self, newcb):
        self._ncb = newcb
    
    @property
    def value(self):
        return self._widget.value

    @value.setter
    def value(self, newval):
        self._widget.value = newval

    @property
    def disabled(self):
        return self._widget.disabled

    @disabled.setter
    def disabled(self, newval):
        self._widget.disabled = newval

    @property
    def visible(self):
        return self.layout.visibility

    @visible.setter
    def visible(self, newval):
        self.layout.visibility = 'visible' if newval else 'hidden'


class String(FormValue):
    def __init__(self, name, value, **kwargs):
        _widget = widgets.Text(value=value)
        FormValue.__init__(self, name, _widget, **kwargs)


class Dropdown(FormValue):
    def __init__(self, name, options, value, **kwargs):
        _widget = widgets.Dropdown(options=options, value=value)
        mw = '{}ch'.format(max(map(len, _widget.options))+4)
        _widget.layout =  {'width':'auto', 'min_width': mw}
        FormValue.__init__(self, name, _widget, **kwargs)


class Checkbox(FormValue):
    def __init__(self, name, **kwargs):
        value = kwargs.get('value', False)
        _widget = widgets.Checkbox(value=value)
        FormValue.__init__(self, name, _widget, **kwargs)


class Radiobuttons(FormValue):
    def __init__(self, name, options, value, **kwargs):
        _widget = widgets.RadioButtons(options=options, value=value)
        FormValue.__init__(self, name, _widget, **kwargs)


class Togglebuttons(FormValue):
    def __init__(self, name, options, value, **kwargs):
        _widget = widgets.ToggleButtons(options=options, value=value)
        # self.dd.style.button_width='{}ch'.format(max(map(len, self.dd.options))+4)
        _widget.style={'button_width': 'initial'}
        FormValue.__init__(self, name, _widget, **kwargs)


class Text(FormValue):
    def __init__(self, name, value='', **kwargs):
        _widget = widgets.Textarea(value=value)
        FormValue.__init__(self, name, _widget, **kwargs)
