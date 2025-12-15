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
import os
import sys
from IPython.display import display, Javascript
from traitlets import List, Unicode, Bool, Int


def to_bytes(numstr): 
    try: 
        if isinstance(numstr, int): 
            return numstr 
        last = numstr[-1] 
        if last == 'B': 
            numstr = numstr[:-1] 
            last = numstr[-1] 
        num = int(numstr[:-1]) 
        if last == 'G': 
            num *= 1024**3 
        elif last == 'M': 
            num *= 1024**2 
        elif last == 'K': 
            num *= 1024 
        else:
            num = int(numstr)
        return num 
    except: 
        raise ValueError("Cannot parse '%s'" % numstr) 


import anywidget

class FileWidget(anywidget.AnyWidget):
    _esm = """
    export default {
        render({ model, el }) {
            let file = document.createElement('input');
            file.setAttribute('class', 'fileinput');
            let cid = "upload-" + Math.random().toString(36).substr(2, 9);
            file.setAttribute('id', cid);
            file.multiple = model.get('multiple');
            file.required = true;
            file.setAttribute('type', 'file');
            file.setAttribute('style', 'display:none');

            let label = document.createElement('label');
            label.setAttribute('for', cid);
            label.setAttribute('style', 'border: 1px solid; border-radius: 5px; display: inline-block; padding: 6px 12px');

            let icon = document.createElement('i');
            icon.setAttribute("class", "fa fa-upload");

            let labelstr;
            if (file.multiple) {
                labelstr = "  Upload Files";
            } else {
                labelstr = "  Upload File";
            }
            label.innerHTML = labelstr;
            label.prepend(icon);
            el.appendChild(label);
            el.appendChild(file);

            let stored_files = [];

            function reset() {
                label.innerHTML = labelstr;
                label.prepend(icon);
                file.removeAttribute("disabled");
            }

            function send_changed() {
                var send = model.get('send');
                var fnum = send[0];
                var offset = send[1];
                var chunk_size=64*1024;
                var reader;

                if (fnum == -1) {
                    return
                }

                if (offset == 0) {
                    model.set('sent', -1);
                    model.save_changes();
                }

                function tob64( buffer ) {
                    var binary = '';
                    var bytes = new Uint8Array( buffer );
                    var len = bytes.byteLength;
                    for (var i = 0; i < len; i++) {
                        binary += String.fromCharCode( bytes[ i ] );
                    }
                    return window.btoa( binary );
                }

                var reader_done = function (event) {
                    if (event.target.error == null) {
                        var b64 = tob64(event.target.result);
                        model.set('data', b64);
                        model.set('sent', offset);
                        model.save_changes();
                    } else {
                        console.log("Read error: " + event.target.error);
                        model.set('data', '');
                        model.set('sent', -2);
                        model.save_changes();
                    }
                    model.save_changes();
                }

                var chunk_reader = function (_offset, _f) {
                    reader = new FileReader();
                    var chunk = _f.slice(_offset, chunk_size + _offset);
                    reader.readAsArrayBuffer(chunk);
                    reader.onload = reader_done;
                }

                chunk_reader(offset, stored_files[fnum]);
            }

            function handle_file_change(evt) {
                var _files = evt.target.files;
                var filenames = [];
                stored_files = [];

                for (var i = 0; i < _files.length; i++) {
                    var f = _files[i];
                    console.log("Filename: " + f.name);
                    console.log("Type: " + f.type);
                    console.log("Size: " + f.size + " bytes");
                    stored_files.push(f);
                    filenames.push([f.name, f.size]);
                };

                model.set('filenames', filenames);
                model.save_changes();

                if (filenames.length == 0) {
                    label.innerHTML = labelstr;
                    file.removeAttribute("disabled");
                } else if (filenames.length == 1) {
                    label.innerHTML = "  " + filenames[0][0];
                    file.setAttribute('disabled', 'true');
                } else {
                    label.innerHTML = "  " + filenames.length + " files selected";
                    file.setAttribute('disabled', 'true');
                };
                label.prepend(icon);
            }

            model.on('change:send', send_changed);
            model.on('change:reset', reset);
            file.addEventListener('change', handle_file_change);
        }
    }
    """
    filenames = List([]).tag(sync=True)
    multiple = Bool(False).tag(sync=True)
    data = Unicode().tag(sync=True)
    send = List([]).tag(sync=True)
    sent = Int().tag(sync=True)
    reset = Bool(False).tag(sync=True)

    def __init__(self, **kwargs):
        """Constructor"""
        super(self.__class__, self).__init__(**kwargs)

        # Allow the user to register error callbacks with the following signatures:
        #    callback()
        #    callback(sender)
        self.errors = widgets.CallbackDispatcher(accepted_nargs=[0, 1])

        # Listen for custom msgs
        self.on_msg(self._handle_custom_msg)

    def _handle_custom_msg(self, content):
        """Handle a msg from the front-end.

        Parameters
        ----------
        content: dict
            Content of the msg."""
        if 'event' in content and content['event'] == 'error':
            self.errors()
            self.errors(self)


class FileUpload(object):

    def __init__(self, 
                 name, 
                 desc, 
                 dir='tmpdir',
                 maxnum=1,
                 maxsize='1M', 
                 cb=None,
                 basic=False,
                 width='auto'):

        form_item_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            border='solid 1px lightgray',
            justify_content='space-between',
            width=width
        )
        basic_layout = widgets.Layout(
            flex='10 1 auto',
            width=width
        )
        self.input = FileWidget()
        if maxnum > 1:
            self.input.multiple = True
        self.maxnum = maxnum
        self.maxsize = to_bytes(maxsize)
        self.input.observe(self._filenames_received, names='filenames')
        self.input.observe(self._data_received, names='sent')
        self.basic = basic
        if basic:
            self.up = widgets.HBox([self.input], layout=basic_layout)
            self.w = widgets.HBox([self.up])
        else:
            label = widgets.HTML(value='<p data-toggle="popover" title="%s">%s</p>' % (desc, name),
                                 layout=widgets.Layout(flex='2 1 auto'))

            self.up = widgets.HBox([label, self.input], layout=form_item_layout)
            self.w = widgets.VBox([self.up])

        self.dir = dir
        self.cb = cb
        self.prog = None
        self.fnames = []

    def _filenames_received(self, change):
        # We have received a list of files from the widget.
        # print('FILENAMES', len(change['new']), change['new'])
        num = len(change['new'])
        if num == 0:
            return

        # clear old progress bars, if any
        if self.prog:
            self.w.children = [self.up]
            del self.prog
            self.prog = None
            del self.progress

        self.fnames = []
        sizes = []
        self.nums = []
        for i, (name, sz) in enumerate(self.input.filenames):
            if sz > self.maxsize:
                print('File "%s" larger than maxsize.' % name, file=sys.stderr)
                continue
            self.fnames.append(name)
            sizes.append(sz)
            self.nums.append(i)

        if sizes == []:
            self.reset()        
            return

        # truncate list if necessary
        if len(self.fnames) > self.maxnum:
            print('Too many files selected (%s). Truncating...' % len(self.fnames), file=sys.stderr)

        self.fnames = self.fnames[:self.maxnum]

        self.prog = [pwidget(self.fnames[i], sizes[i], self.basic) for i in range(len(self.fnames))]
        self.progress = widgets.VBox(self.prog, layout={'width': '100%'})
        self.w.children = [self.up, self.progress]

        mkdir_p(self.dir)
        self.fnames = [os.path.join(self.dir, n) for n in self.fnames]

        self.f = open(self.fnames[0], 'wb')
        self.fnum = 0
        self.fcnt = 0
        self.input.send = [-1, 0]
        self.input.send = [self.nums[0], self.fcnt]
        # data_changed callback will handle the rest

    def _data_received(self, change):
        # print("_data_received")
        # process received blocks of data and request the next one until done.
        if change['new'] == -1:
            return
        if change['new'] == -2:
            # unexpected error
            self.prog[self.fnum].bar_style = 'error'
            print("Error downloading %s" % self.fnames[self.fnum], file=sys.stderr)
            return

        data = base64.b64decode(self.input.data)
        dlen = len(data)
        # print("GOT DATA (%d) [%d] for file %d" % (dlen, self.fcnt, self.fnum))
        if dlen == 0:
            self.prog[self.fnum].bar_style = 'success'
            self.f.close()
            if self.fnum >= len(self.fnames) - 1:
                # done with all downloads
                if self.cb:
                    self.cb(self, self.fnames)
                return
            self.fnum += 1
            self.f = open(self.fnames[self.fnum], 'wb')
            self.fcnt = 0
            self.input.send = [self.nums[self.fnum], self.fcnt]
            return
        self.f.write(data)
        self.fcnt += dlen
        self.prog[self.fnum].value = self.fcnt
        self.input.send = [self.nums[self.fnum], self.fcnt]

    def reset(self):
        # print("RESET", self)
        # Clear the filenames and progress bar(s)
        # Re-enable the upload widget
        if self.prog:
            self.w.children = [self.up]
            del self.prog
            self.prog = None
            del self.progress
        self.input.reset = True
        self.input.reset = False

    def list(self):
        return self.fnames

    @property
    def visible(self):
        return self.w.layout.visibility

    @visible.setter
    def visible(self, newval):
        if newval:
            self.w.layout.visibility = 'visible'
            return
        self.w.layout.visibility = 'hidden'

    def _ipython_display_(self):
        from IPython.display import display
        display(self.w)


def pwidget(name, num, basic):
    if basic:
        return widgets.IntProgress(
            value=0,
            min=0,
            max=num,
            orientation='horizontal',
            layout=widgets.Layout(width='95%')
        )
    else:
        return widgets.IntProgress(
            value=0,
            min=0,
            max=num,
            description='%s:' % name,
            orientation='horizontal',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='95%')
        )


def mkdir_p(path):
    try:
        os.makedirs(path)
    except:
        if os.path.isdir(path):
            pass
        else:
            raise
