
from os.path import isfile, isdir, normcase, normpath, abspath, join, basename, split, splitext
from os import walk
from logger import *

def get_input_output_list(files, recursive, output):
    input_files = []
    for code in files:
        if isfile(code):
            input_files.append(code)
        elif isdir(code):
            if not recursive:
                error("Folders are only supported with the --recursive option")
            for root, dirs, files in walk(code):
                for fil in files:
                    input_files.append(join(root, fil))
        else:
            error(code, ": No such file or directory", sep="")

    if len(input_files) == 0:
        error("No input files")

    input_files = [normcase(x) for x in input_files]

    file_dict = {abspath(x):normpath(x) for x in input_files}
    input_files = list(file_dict.values())

    def infilter(filename):
        if not filename.endswith("svg"):
            warning("Ignoring non-svg file: '", filename, "'", sep="")
        elif "kerfed" in filename:
            warning("Ignoring kerfed file: '", filename, "'", sep="")
        else:
            return True
        return False

    input_files = filter(infilter, input_files)

    def output_of_input(inp):
        if "%" in output and ".." in inp:
            error("Can't use % formating in output when input files are outside of cwd:", fil)
        direc, fil = split(inp)
        return output.replace("%", join(direc, splitext(basename(fil))[0]))

    return [(inp,output_of_input(inp)) for inp in input_files]

