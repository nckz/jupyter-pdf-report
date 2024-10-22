"""A class that handles PDF generation from within the calling notebook.

Author: Nick Zwart
Date: 2024oct22
"""

# stdlib
import os
import shutil
import subprocess
import re

# external
import ipynbname


class Report:

    LATEX_EXTS = [".aux", ".bbl", ".blg", ".out", ".tex"]
    LATEX_DIRS = ["_files"]

    def __init__(self, nb_basename=None):
        """Initialize notebook name and system commands.

        TODO:
            1. make a temp directory for processing
            2. search for system commands
            3. be more explicit about encoding (i.e. utf8)
            4. implement generic find and replace
        """
        # python notebook filenames
        self._nbbname = nb_basename if nb_basename is not None else ipynbname.name()
        self._nbfname = self._nbbname + ".ipynb"

        # class log files
        self._output_tex_log = self._nbbname + ".to-tex.log"
        self._build_tex_log = self._nbbname + ".build-tex.log"

        # system commands (may include spaces)
        self.pdflatex = "pdflatex"
        self.bibtex = "bibtex"
        self.nbconvert = "jupyter nbconvert"

    def to_latex(self):
        """Write notebook to latex files."""

        with open(self._output_tex_log, "w") as fil:
            proc = subprocess.Popen(
                (*self.nbconvert.split(), "--to", "latex", "--no-input", self._nbfname),
                stdout=fil,
                stderr=fil,
            )
            proc.wait()

    @staticmethod
    def last_line(lines, pattern):
        # find last pattern match
        last_line = 0
        for ind, line in enumerate(lines):
            if pattern in line:
                last_line = ind
        return last_line

    @staticmethod
    def insert_lines(burger, lineno, lines):
        # insert burger
        for meat in burger[::-1]:
            lines.insert(lineno, meat)

    def build_pdf(self, dirs={}, replace={}):
        """Convert nb to latex, rewrite latex directives and build the pdf and
        clean the directory.
        """
        self.to_latex()
        self.rewrite_tex(dirs=dirs, replace=replace)
        self._make_pdf()
        self.clean()

    def rewrite_tex(self, dirs={}, replace={}):
        """Rewrite the latex file by first replacing directives and second by
        doing a simple python search and replace.

         directives:
             title: (str) replace the title
             header: (list(str)) the fancyheader loc and string
             footer:  (list(str)) the fancyheader loc and string
             package: (list(str)) the package option and name
        """

        with open(self._nbbname + ".tex", "r") as fil:
            lines = fil.readlines()

        if "title" in dirs:
            new_title = r"\\title{{{title}}}".format(**dirs)

            for ind, line in enumerate(lines):
                pat = re.compile(r"\\title{.*}")
                if pat.search(line) is not None:
                    lines[ind] = pat.sub(new_title, line)

        if "author" in dirs:
            new_auth = []
            for auth in dirs["author"]:
                new_auth.append(r"\author{{{0}}}".format(auth) + "\n")

            last_line = self.last_line(lines, r"\title")
            self.insert_lines(new_auth, last_line + 1, lines)

        if "date" in dirs:
            new_date = r"\date{{{date}}}".format(**dirs)
            last_line = self.last_line(lines, r"\title")
            self.insert_lines([new_date + "\n"], last_line + 1, lines)

        if "header" in dirs or "footer" in dirs:

            fncy_cmd = []
            if "header" in dirs:
                for hdr in dirs["header"]:
                    fncy_cmd.append(r"\fancyhead[{0}]{{{1}}}".format(*hdr))
            if "footer" in dirs:
                for ftr in dirs["footer"]:
                    fncy_cmd.append(r"\fancyfoot[{0}]{{{1}}}".format(*ftr))

            fncy_pre = r"""
            \usepackage{lastpage}
            \usepackage{fancyhdr}
            \fancypagestyle{plain}{
            \fancyhf{}  % Clear header/footer
            """

            fncy_post = r"""
            }
            \pagestyle{plain}  % Set page style to plain.
            """

            # assemble burger
            burger = fncy_pre
            for cmd in fncy_cmd:
                burger += cmd + "\n"
            burger += fncy_post

            last_line = self.last_line(lines, "package")

            # insert burger
            self.insert_lines(burger, last_line + 1, lines)

        if "package" in dirs:

            pkg_cmd = []
            for pkg in dirs["package"]:
                pkg_cmd.append(r"\usepackage[{0}]{{{1}}}".format(*pkg))

            last_line = self.last_line(lines, "package")
            self.insert_lines(pkg_cmd, last_line + 1, lines)

        with open(self._nbbname + ".tex", "w") as fil:
            fil.write("".join(lines))

    def _make_pdf(self):
        """Build PDF from latex files."""

        pdf_cmd = (*self.pdflatex.split(), self._nbbname + ".tex")
        bib_cmd = (*self.bibtex.split(), self._nbbname + ".aux")

        with open(self._build_tex_log, "w") as fil:
            for cmd in (pdf_cmd, bib_cmd, pdf_cmd, pdf_cmd):
                proc = subprocess.Popen(cmd, stdout=fil, stderr=fil)
                proc.wait()

    def clean(self):
        """Clean all intermediate processing files."""

        # files generated by nbconvert
        for ext in self.LATEX_EXTS:
            cur = self._nbbname + ext
            if os.path.exists(cur):
                os.remove(cur)

        for ext in self.LATEX_DIRS:
            cur = self._nbbname + ext
            if os.path.exists(cur):
                shutil.rmtree(cur)
