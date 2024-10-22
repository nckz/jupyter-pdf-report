# jupyter-pdf-report
Tools to make a nice looking, no-code, report from Jupyter.

# HowTo
Add the following to the last cell in your Jupyter notebook.

```python
from jupyter_pdf_report.report import Report
Report().build_pdf({"title":"My Report",
                    "header":[["L", "Hello"]],
                    "footer":[["R", "Page \\thepage\ of \pageref{LastPage}"]],
                    "date":"Jan 1st, 1999",
                    "author":["me"]})
```

![example report](report-example.png)


## Content
The content is a 'plotly' plot and the body text is generated from the package
'lorem'.

# Advanced Discussion
The `build_pdf` function shown in the example usage is a dictionary that can
support several directives i.e. 'title', 'header', 'footer', 'date',  and
'author'.  These are all optional, if they aren't included in the argument to
`build_pdf`, the Jupyter defaults will be used.

The header and footer make use of the 'fancyhdr' package.
Both directives are nested lists, allowing [L]eft, [R]ight and
[C]enter to be used together.

The 'author' directive was meant to handle multiple authors, however, only a
single author seems to work at the moment.

# Installation
There is no pip package, yet; you must clone the repo and install it as
follows:

```bash
git clone git@github.com:nckz/jupyter-pdf-report.git
cd jupyter-pdf-report
pip install -e .
```

Or you could probably copy and paste the 'report.py' code into your
report-template-notebook.

# References
This work was motivated by the discussion here:
[GitHub:jupyter-nbconvert](https://github.com/jupyter/nbconvert/issues/249#issuecomment-2070337459).
