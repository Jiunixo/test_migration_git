import configparser
from tkinter import Label, Entry, Frame, Tk, Button, StringVar, IntVar, DoubleVar, BooleanVar
import tkinter.ttk
import tkinter.font


_TKINTER_VARS = {'int': IntVar, 'float': DoubleVar, 'double': DoubleVar, 'bool': BooleanVar}


class ConfigWidget(Frame):
    """Tabbed widget allowing to handle a configuration"""

    def __init__(self, config, **kwargs):
        """Create config widget

        `config` should have the following structure:
            {category: {param1: {'type': type,
                                 'value': initial value,
                                 'help': information about param1},
                        param2: {....}}}
        """
        Frame.__init__(self, kwargs)
        self.config = config
        self.entry_variables = None
        self.master.title('Solver parameters')

    def display_config(self):
        """Display the tabbed frame (one tab per category -- `self.config` keys, and one text field
        per parameter)
        """
        # Tabbed frame with the parameters organized by category
        notebook = tkinter.ttk.Notebook(self.master)
        help_font = tkinter.font.Font(slant='italic', size=10)
        self.entry_variables = {}
        for tab, options in self.config.items():
            self.entry_variables[tab] = {}
            tab_frame = Frame(notebook)
            notebook.add(tab_frame, text=tab)
            for row, option in enumerate(options):
                Label(tab_frame, text=option).grid(row=row)
                # link a tk inter dedicated variable to the parameter entry
                self.entry_variables[tab][option] = _TKINTER_VARS[options[option]['type']]()
                self.entry_variables[tab][option].set(options[option]['value'])
                param = Entry(tab_frame, textvariable=self.entry_variables[tab][option])
                param.grid(row=row, column=1)
                help_msg = ''
                if 'help' in options[option]:
                    help_msg = options[option]['help'] + ' '
                help_msg += '(type: %s)' % options[option]['type']
                Label(tab_frame, text=help_msg, font=help_font).grid(row=row, column=2)
        notebook.pack(expand=True, fill='both')
        # Buttons
        buttons_frame = Frame(self.master)
        self.ok = Button(buttons_frame)
        self.ok['text'] = 'OK'
        self.ok['command'] = self.update_and_quit
        self.ok.grid(row=0, column=0)
        self.cancel = Button(buttons_frame)
        self.cancel['text'] = 'Annuler'
        self.cancel['command'] = self.quit
        self.cancel.grid(row=0, column=1)
        buttons_frame.pack()

    def update_and_quit(self):
        """Go through the widget text entries and retrieve their value to update `self.config` dict,
        before exiting HMI
        """
        for tab, options in self.entry_variables.items():
            for option in options:
                self.config[tab][option]['value'] = self.entry_variables[tab][option].get()
        self.quit()


def _update_config_with_user_values(config, user_config_parser):
    """Update `config`: add a 'value' key to the param dicts, containing the value read from
    the user config parser `user_config_parser`

    If user config is erroneous or absent, use default value instead.
    """
    converters = {
        'double': user_config_parser.getfloat,
        'float': user_config_parser.getfloat,
        'bool': user_config_parser.getboolean,
        'int': user_config_parser.getint
    }
    for section, options in config.items():
        for option in options:
            try:
                value = converters[options[option]['type']](section, option)
            except (ValueError, configparser.NoSectionError, configparser.NoOptionError):
                options[option]['value'] = options[option]['default']
            else:
                options[option]['value'] = value


def _update_user_config(config, user_config_parser):
    """Update `user_config_parser` with `config` values
    """
    for tab, options in config.items():
        for option in options:
            if options[option]['type'] == 'bool':
                value = bool(options[option]['value'])
            else:
                value = options[option]['value']
            if not user_config_parser.has_section(tab):
                user_config_parser.add_section(tab)
            user_config_parser.set(tab, option, str(value))
