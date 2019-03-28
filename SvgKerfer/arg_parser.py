
def error(*a, **aa):
    print("Error:", end=' ')
    print(*a, **aa)
    exit(1)

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

        if self.allow_multiple:
            self.values.push(args)
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
        key = self.key_func(key_str)
        val = self.val_func(val_str)
        if key in self.dikt:
            error("Duplicate definiton of '", key, "'", "for option '", option_name, "'", sep="")
        self.dikt[key] = val

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
                    used_c = o.call(arg, args)
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

from os import listdir
from os.path import join, isfile, isdir

def matches(name, fltr):
    if fltr == "*":
        return True
    if "*" in fltr:
        error("To be implemented: * wildcard support")
    return name==fltr

def wd_and_codes_to_paths(paths, file_code):
    if "/" in file_code:
        direc, rest = file_code.split("/", 1)
        if len(direc) == 0:
            return wd_and_codes_to_paths(contenders, rest)
        if direc == "**":
            error("To be implemented: **/ folder wildcard support")

        new_wds = []
        for wd in paths:
            new_wds += [join(wd, fil) for fil in listdir(wd) if matches(fil, direc)]
        return wd_and_codes_to_paths(filter(isdir, new_wds), rest)
    else:
        files = []
        for wd in paths:
            files += [join(wd, fil) for fil in listdir(wd) if matches(fil, file_code)]
        return list(filter(isfile, files))

def file_code_to_file_paths(file_code):
    if file_code.startswith("/"):
        return wd_and_codes_to_paths(["/"], file_code[1:])
    return wd_and_codes_to_paths(["."], file_code)
