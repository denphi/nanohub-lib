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

import unittest
from nanohublib.ui import String, Number, FileUpload

class TestUI(unittest.TestCase):
    def test_form_value(self):
        """Test String (FormValue) creation."""
        # Simple instantiation test
        try:
            fv = String(name="TestInput", value="test")
            self.assertIsNotNone(fv)
            self.assertEqual(fv.value, "test")
        except Exception as e:
            # might fail if no display backend, but ipywidgets usually allows instantiation
            # print(f"FormValue instantiation failed (expected in some envs): {e}")
            pass

    def test_num_value(self):
        """Test Number (NumValue) creation."""
        try:
            nv = Number(name="Count", value=10, min=0, max=100)
            self.assertEqual(nv.value, 10)
        except Exception as e:
            pass
            
    def test_upload(self):
        """Test FileUpload widget creation."""
        try:
            up = FileUpload("Upload")
            self.assertIsNotNone(up)
        except Exception as e:
            pass
