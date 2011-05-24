# Copyright (c) 2008, 2009, 2010 Friedrich Romstedt 
# <www.friedrichromstedt.org>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Developed since: Jul 2008
__version__ = (0, 1, 0)

import keyconf


class Layer(keyconf.Configuration):
    """Base class for a layer.  The class is derived from 
    keyconf.Configuration, to support the .configure() method seamlessly."""

    def __init__(self):
        """Sets the layer to has-changed."""

        keyconf.Configuration.__init__(self)

        self.set_changed()
    #
    # Tracking status ...
    #

    def configure(self, **kwargs):
        self.set_changed()
        keyconf.Configuration.configure(self, **kwargs)

    def unconfigure(self, *args):
        self.set_changed()
        keyconf.Configuration.unconfigure(self, *args)

    #
    # Changed-flag methods ...
    #

    def set_changed(self):
        """Flag that the layer has changed."""

        self.changed = True

    def unset_changed(self):
        """Flag that the layer is unchanged."""

        self.changed = False

    def has_changed(self):
        return self.changed

    # 
    # Comaprison ...
    #

    def __eq__(self, other):
        return id(self) == id(other)
