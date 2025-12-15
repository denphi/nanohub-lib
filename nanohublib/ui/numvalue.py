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
from .. import ureg



# xpr - pint quantity, pint unit or str
# may be unicode string
# 
# Returns string for description and
# a string for unit label, which may be latex.


def parse_units(xpr):
    if xpr is None or xpr == '':
        return '', ''
    try:
        u = xpr.units
        us = str(u)
        ul = '{:~L}'.format(u)
    except:
        try:
            u = ureg.parse_expression(xpr).units
            us = str(u)
            ul = '{:~L}'.format(u)
        except:
            try:
                us = str(xpr)
                ul = '{:~L}'.format(xpr)
            except:
                return xpr, xpr
    if ul.startswith('\\'):
        ul = '$' + ul + '$'
    return us, ul


class NumValue(widgets.HBox):

    def _create_widget(self, ntype, value, min, max):

        if min is not None and max is None:
            raise ValueError("Min is set but not Max.")
        if min is None and max is not None:
            raise ValueError("Max is set but not Min.")

        if ntype == 'int':
            if min is not None:
                return widgets.BoundedIntText(value=value, min=min, max=max)
            return widgets.IntText(value=value)
        if min is not None:
            return widgets.BoundedFloatText(value=value, min=min, max=max)
        return widgets.FloatText(value=value)

    def _parse(self, x):
        if x is None:
            return None
        if isinstance(x, (int, float)):
            return x
        try:
            p = ureg.parse_expression(str(x))
            if hasattr(p, 'units'):
                if self.units_str:
                    return p.to(self.units_str).magnitude
                return p.magnitude
            return float(p)
        except:
            return x

    def __init__(self, ntype, name, value, **kwargs):

        width = kwargs.get('width', 'auto')
        self._ncb = kwargs.get('cb')

        # accept either 'description' or 'desc'
        self._desc = kwargs.get('desc', '')
        if self._desc == '':
            self._desc = kwargs.get('description', '')

        self.units_str, self.units_tex = parse_units(kwargs.get('units'))

        self.name = name
        _min = self._parse(kwargs.get('min'))
        _max = self._parse(kwargs.get('max'))
        value = self._parse(value)

        self._widget = self._create_widget(ntype, value, _min, _max)
        self._widget.layout = {'width': 'auto'}
        self._widget.disabled = kwargs.get('disabled', False)
        self._widget.observe(self._cb, names='value')
        self._widget.min = _min
        self._widget.max = _max

        form_item_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            border='solid 1px lightgray',
            justify_content='space-between',
            padding='5px',
            width=width
        )
        self.label = None
        self._update()
        widgets.HBox.__init__(self, [self.label, self._widget, self.unit_label], layout=form_item_layout)

    def _update(self):
        desc = self._desc
        if self.units_str != '':
            desc += "\nValues must be in units of %s." % self.units_str

        if self._widget.min is not None:
            desc += "\nMin: %s\tMax: %s\n" % (self._widget.min, self._widget.max)
        
        popup = '<div data-toggle="popover" title="%s" data-container="body">%s</div>' % (desc, self.name)
        if self.label is None:
            self.label = widgets.HTML(value=popup, layout=widgets.Layout(flex='2 1 auto'))
            self.unit_label = widgets.HTMLMath(value=self.units_tex, layout={'min_width': '6ch'})
            return
        self.label.value = popup
        self.unit_label.value = self.units_tex

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
    def min(self):
        return self._widget.min

    @min.setter
    def min(self, val):
        self._widget.min = val
        self._update()

    @property
    def max(self):
        return self._widget.max

    @max.setter
    def max(self, val):
        self._widget.max = val
        self._update()

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


class Number(NumValue):
    def __init__(self, name, value, **kwargs):
        NumValue.__init__(self, 'float', name, value, **kwargs)


class Integer(NumValue):
    def __init__(self, name, value, **kwargs):
        NumValue.__init__(self, 'int', name, value, **kwargs)
