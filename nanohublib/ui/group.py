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


class Tab(widgets.Tab):
    def __init__(self, wlist, **kwargs):
        titles = kwargs.get('titles')
        if titles is None:
            titles = {i: w.name for i, w in enumerate(wlist)}
        else:
            titles = {i: w for i, w in enumerate(titles)}
        self.wlist = wlist
        self._disabled = False
        widgets.Tab.__init__(self, wlist, _titles=titles, **kwargs)

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, newval):
        for w in self.wlist:
            w.disabled = newval
        self._disabled = newval


class Group(widgets.VBox):

    def __init__(self, wlist, **kwargs):
        """
        Creates a Group from a list of ui elements

        :param wlist: List of UI elements
        :param name: Optional string to show in a titlebar or tab.
        :param desc: Optional description that will show in a popup over the titlebar.
        :param width: Optional with of the form.
        :param show_name: Boolean. Show the name as a title. Default is True.
        :param border: CSS for the border. Default is None.
        :param collapsible: Boolean. Default is False.  If True, the Group
        shrink and expand like an accordion widget.
        """

        # FIXME: add background-color, font-size, 
        self.wlist = wlist
        self._name = kwargs.get('name', '')
        self._disabled = kwargs.get('disabled', False)
        self._width = kwargs.get('width', 'auto')
        self._desc = kwargs.get('desc', '')
        self._show_name = kwargs.get('show_name', True)
        self._border = kwargs.get('border', None)
        self._collapsible = kwargs.get('collapsible', False)

        self._update_desc()

        widgets.VBox.__init__(self, self.wlist, layout=widgets.Layout(
            display='flex',
            flex_flow='column',
            align_items='stretch',
            width=self._width
        ))

    def _update_desc(self):    
        if self._name and self._show_name:
            style = "style='background-color: #DCDCDC; font-size: 150%; padding: 5px'"
            if self._desc:
                desc = 'data-toggle="popover" title="%s"' % (self._desc)
            else:
                desc = ''
            lval = '<p  %s %s>%s</p>' % (desc, style, self.name)
            label = widgets.HTML(value=lval, layout=widgets.Layout(flex='2 1 auto'))
            self.wlist.insert(0, label)

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, val):
        if self._name and self._show_name:
            # remove old
            self.wlist = self.wlist[1:]
        self._desc = val
        self._update_desc()
        self.children = self.wlist

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        if self._name and self._show_name:
            # remove old
            self.wlist = self.wlist[1:]
        self._name = val
        self._update_desc()
        self.children = self.wlist
        
    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, val):
        self._width = val
        self.layout = widgets.Layout(
            display='flex',
            flex_flow='column',
            align_items='stretch',
            width=self._width
        )

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, newval):
        for w in self.wlist:
            w.disabled = newval
        self._disabled = newval

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, newval):
        for w in self.wlist:
            w.visible = newval
        self._visible = newval
