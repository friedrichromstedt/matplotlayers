# Copyright (c) 2010 Friedrich Romstedt <friedrichromstedt@gmail.com>
# See also <www.friedrichromstedt.org> (if e-mail has changed)
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

# Developed since: Aug 2008

"""Defines the settings dialog class for accessing the details of a Stack."""

import Tkinter
import tkFileDialog
import ventry


class StackSettings(Tkinter.Toplevel):

    def __init__(self, master,
            stack,
            callback_update):
        """STACK is the matplotlayers.Stack to act upon."""

        Tkinter.Toplevel.__init__(self, master)
        self.stack = stack
        self.callback_update = callback_update

        # Create Settings widgets ...

        self.lframe_settings = Tkinter.LabelFrame(self, text = 'Settings')
        self.lframe_settings.pack(side = Tkinter.LEFT, anchor = Tkinter.N)

        # Create labeling widgets.
        self.lframe_labeling = Tkinter.LabelFrame(self.lframe_settings,
                text = 'Labeling')
        self.lframe_labeling.pack(side = Tkinter.TOP, anchor = Tkinter.W)
        self.frame_labeling = Tkinter.Frame(self.lframe_labeling)
        self.frame_labeling.pack(side = Tkinter.TOP)
        
        if self.stack.title is None:
            initial_title = ''
        else:
            initial_title = self.stack.title.replace('\n',r'\n')

        if self.stack.xlabel is None:
            initial_xlabel = ''
        else:
            initial_xlabel = self.stack.xlabel.replace('\n',r'\n')

        if self.stack.ylabel is None:
            initial_ylabel = ''
        else:
            initial_ylabel = self.stack.ylabel.replace('\n',r'\n')

        self.title = ventry.NamedVEntry(self.frame_labeling,
                name = 'Title:',
                column = 0, row = 0,
                initial = initial_title,
                width = 40)
        self.xlabel = ventry.NamedVEntry(self.frame_labeling,
                name = 'x label:',
                column = 0, row = 1,
                initial = initial_xlabel,
                width = 40)
        self.ylabel = ventry.NamedVEntry(self.frame_labeling,
                name = 'y label:',
                column = 0, row = 2,
                initial = initial_ylabel,
                width = 40)
        self.title.initialise()
        self.xlabel.initialise()
        self.ylabel.initialise()

        self.update_title()

        self.button_update_labeling = Tkinter.Button(self.lframe_labeling,
                text = 'Update Labeling',
                command = self.tk_update_labeling)
        self.button_update_labeling.pack(side = Tkinter.TOP,
                fill = Tkinter.X)

        # Create limit widgets.
        self.lframe_limits = Tkinter.LabelFrame(self.lframe_settings,
                text = 'Limits')
        self.lframe_limits.pack(side = Tkinter.TOP, anchor = Tkinter.W)
        self.frame_limits = Tkinter.Frame(self.lframe_limits)
        self.frame_limits.pack(side = Tkinter.TOP)

        (xlim0, xlim1) = self.stack.get_xlim()
        (ylim0, ylim1) = self.stack.get_ylim()

        self.xlim_left = ventry.NamedVEntry(self.frame_limits,
                name = 'x Limits:',
                column = 0, row = 0,
                initial = xlim0,
                validate = ventry.number)
        self.xlim_right = ventry.VEntry(self.frame_limits,
                initial = xlim1,
                validate = ventry.number)
        self.xlim_right.grid(column = 2, row = 0)
        self.xlim_left.initialise()
        self.xlim_right.initialise()

        self.ylim_bottom = ventry.NamedVEntry(self.frame_limits,
                name = 'y Limits:',
                column = 0, row = 1,
                initial = ylim0,
                validate = ventry.number)
        self.ylim_top = ventry.VEntry(self.frame_limits,
                initial = ylim1,
                validate = ventry.number)
        self.ylim_top.grid(column = 2, row = 1)
        self.ylim_bottom.initialise()
        self.ylim_top.initialise()

        self.autoscalex_on = Tkinter.BooleanVar(self.lframe_limits)
        self.autoscaley_on = Tkinter.BooleanVar(self.lframe_limits)
        self.autoscalex_on.set(self.stack.get_autoscalex_on())
        self.autoscaley_on.set(self.stack.get_autoscaley_on())

        self.checkbutton_autoscalex_on = Tkinter.Checkbutton(
                self.lframe_limits,
                text = 'x Autoscale',
                command = self.tk_autoscalex_on,
                variable = self.autoscalex_on)
        self.checkbutton_autoscalex_on.pack(side = Tkinter.TOP)

        self.checkbutton_autoscaley_on = Tkinter.Checkbutton(
                self.lframe_limits,
                text = 'y Autoscale',
                command = self.tk_autoscaley_on,
                variable = self.autoscaley_on)
        self.checkbutton_autoscaley_on.pack(side = Tkinter.TOP)

        self.button_update_limits = Tkinter.Button(self.lframe_limits,
                text = 'Update Scales',
                command = self.tk_update_limits)
        self.button_update_limits.pack(side = Tkinter.TOP,
                fill = Tkinter.X)

        self.update_autoscalex_accessibility()
        self.update_autoscaley_accessibility()

    def tk_update_labeling(self):
        self.stack.set_title(self.title.get().replace('\\n', '\n'))
        self.stack.set_xlabel(self.xlabel.get().replace('\\n', '\n'))
        self.stack.set_ylabel(self.ylabel.get().replace('\\n', '\n'))

        self.callback_update()
        self.update_title()

    def tk_update_limits(self):
           
        # Tells wheter an update is needed or not:
        update_needed = False

        if self.autoscalex_on.get():
            
            # We are in autoscale mode, thus update the values displayed ...

            (xlim0, xlim1) = self.stack.get_xlim()

            self.xlim_left.set(xlim0)
            self.xlim_right.set(xlim1)

        else:
            
            # We are in explicit mode, thus write the values typed in to
            # the stack ...

            self.stack.set_xlim(
                    (self.xlim_left.get(), self.xlim_right.get()))

            # Only in this branch update the stack.
            update_needed = True

        if self.autoscaley_on.get():

            # We are in autoscale mode, thus update the values displayed ...

            (ylim0, ylim1) = self.stack.get_ylim()

            self.ylim_bottom.set(ylim0)
            self.ylim_top.set(ylim1)

        else:
            
            # We are in explicit mode thus write the values typed in to
            # the stack ...

            self.stack.set_ylim(
                    (self.ylim_bottom.get(), self.ylim_top.get()))

            # Only in this branch update the stack.
            update_needed = True

        if update_needed:
            self.callback_update()

    def update_autoscalex_accessibility(self):
        """Enables / Disables widgets according to the X autoscale setting."""

        if self.autoscalex_on.get():

            # Disable the controls:
            self.xlim_left.disable()
            self.xlim_right.disable()
            
        else:

            # Enable the controls:
            self.xlim_left.enable()
            self.xlim_right.enable()
    
    def update_autoscaley_accessibility(self):
        """Enables / Disables widgets according to the Y autoscale setting."""

        if self.autoscaley_on.get():

            # Disable the controls:
            self.ylim_bottom.disable()
            self.ylim_top.disable()

        else:
            
            # Enable the controls:
            self.ylim_bottom.enable()
            self.ylim_top.enable()

    def tk_autoscalex_on(self):
        """Called on changes of the autoscale X checkbutton."""

        # Update the stack's settings ...

        if self.autoscalex_on.get():
            self.stack.set_autoscale_on(x_on=True)
        else:
            self.stack.set_autoscale_on(x_on=False)

        # Enable / disable the controls ...

        self.update_autoscalex_accessibility()

        # If the autoscaling has been disabled, update the limits
        # because they may have changed due to autoscaling under the way ...

        (xlim0, xlim1) = self.stack.get_xlim()

        self.xlim_left.set(xlim0)
        self.xlim_right.set(xlim1)

        self.callback_update()

    def tk_autoscaley_on(self):
        """Called on changes of the autoscale Y checkbutton."""

        # Update the stack's settings ...

        if self.autoscaley_on.get():
            self.stack.set_autoscale_on(y_on=True)
        else:
            self.stack.set_autoscale_on(y_on=False)

        # Enable / disable the controls ...

        self.update_autoscaley_accessibility()

        # If the autoscaling has been disabled, update the limits
        # because they may have changed due to autoscaling under the way ...

        (ylim0, ylim1) = self.stack.get_ylim()

        self.ylim_bottom.set(ylim0)
        self.ylim_top.set(ylim1)

        self.callback_update()

    def update_title(self):
        """Update the title of the window according to the title of the
        stack."""

        # Choose a title which is meaningful both if the title has been set
        # and also if not.
        self.wm_title('Stack Settings ' + self.title.get())
