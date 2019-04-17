from logger import *

class BaseOption:
    def __init__(self, names):
        self.names = names

    def takes(self, arg):
        return arg in self.names

class NormalOption(BaseOption):
    def __init__(self, names, arg_names, desc, default_val=None, custom_func=None, allow_multiple=False):
        super().__init__(names)
        self.arg_names = arg_names
        self.desc = desc
        self.default_val = default_val
        self.custom_func = custom_func
        self.allow_multiple = allow_multiple

        self.called = False
        self.values = ([default_val] if default_val else []) if allow_multiple else default_val

    def get_desired_args(self):
        return len(self.arg_names)

    def call(self, option_name, args):
        if self.called and not self.allow_multiple:
            error("Option '", option_name, "' already set", sep="")

        self.called = True
        if self.custom_func:
            return self.custom_func(args)

        if len(args) == 1:
            args = args[0]

        if self.allow_multiple:
            self.values.append(args)
        else:
            self.values = args

        return len(args) #How many args we used

    def get_help_row(self):
        return [", ".join(self.names), " ".join(self.arg_names), self.desc]

    def is_set(self):
        return self.called

    def get_option(self):
        return self.values

class DictOption(BaseOption):
    def __init__(self, names, key_name, val_name, key_parser, val_parser, desc):
        super().__init__(names)
        self.key_name = key_name
        self.val_name = val_name
        self.key_parser = key_parser
        self.val_parser = val_parser
        self.desc = desc
        self.dikt = {}

    def get_desired_args(self):
        return 1

    def call(self, option_name, args):
        arg = args[0]
        split = arg.split("=", 1)
        if len(split) != 2:
            error("Expected an '=' between key an value in '", option_name, "' option. Got: '", arg, "'", sep="")
        key_str, val_str = split
        key = self.key_parser(key_str)
        val = self.val_parser(val_str)
        if key in self.dikt:
            error("Duplicate definiton of '", key_str, "' for option '", option_name, "'", sep="")
        self.dikt[key] = val
        return 1

    def get_help_row(self):
        return [", ".join(self.names), self.key_name+"="+self.val_name, self.desc]

    def get_dict(self):
        return self.dikt

class ArgParser:
    def __init__(self, usage_str, info):
        self.usage_str = usage_str
        self.info = info
        self.options = []
        self.options.append(NormalOption(["-h", "--help"], [], "Display this help message", custom_func=lambda _:self.print_help_message(0)))
        self.the_rest = []

    def add(self, *option):
        self.options += list(option)

    def take_args(self, args):
        while len(args) > 0:
            arg = args[0]
            args = args[1:]

            used = False

            for o in self.options:
                if o.takes(arg):
                    subargs_wanted = o.get_desired_args()
                    if len(args) < subargs_wanted:
                        error("Option '", arg, "' requires ", subargs_wanted, " parameters, ", len(args), " were given")
                    used_c = o.call(arg, args[:subargs_wanted])
                    used_c = used_c if used_c else 0
                    args = args[used_c:]
                    used = True
                    break

            if not used:
                if arg.startswith("-"):
                    error("Unknown option '", arg, "'", sep="")
                self.the_rest += [arg]

    def get_the_rest(self):
        return self.the_rest

    def print_help_message(self, exit_code=0):
        print("Usage:", self.usage_str)
        print(self.info)
        print()
        print("Options:")
        table = [o.get_help_row() for o in self.options]
        widths = [max([len(row[i]) for row in table]) for i in range(3)]
        for row in table:
            print("\t", " \t".join([row[i].ljust(widths[i]) for i in range(3)]), sep="")
        print()
        exit(exit_code)
