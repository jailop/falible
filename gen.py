#!/usr/bin/python

# Static website generator
#
# This script review updated files in an source path and convert
# markdown files using a HTML template. Next, copy all updted files from
# the source to a target path.
#
# (2019) Jaime Lopez <jailop AT gmail DOT com>

import os
import re
from shutil import copyfile
from markdown import markdown
from jinja2 import Template

SOURCE = './src'
TARGET = './output'

class Generator:
    """
    Class to generate static websites
    """
    def __init__(self):
        """
        Loads in memory the default HTML template
        """
        with open('templates/basic.html', 'r') as fd:
            self.template = Template(fd.read())
    def preprocess(self, filename, text):
        """
        Resolves paths and inclusions
        """
        while True:
            begin = text.find('%include')
            if begin < 0:
                break
            end = text.find('\n', begin)
            sentence = text[begin:end]
            file_to_include = sentence.split(':')[1].strip()
            file_to_include = filename[0:filename.rfind('/') + 1] + file_to_include
            with open(file_to_include, 'r') as fd:
                include = fd.read()
            text = text.replace(sentence, include)
        return text
    def mkd(self, filename):
        """
        Converts markdown source files to html
        """
        with open(filename, 'r') as fd:
            text = fd.read()
            text = self.preprocess(filename, text)
            text = text.replace('.md', '.html')
            m = markdown(text)
            html = self.template.render(content=m)
        outname = filename.replace(SOURCE, TARGET)
        outname = outname.replace('.md', '.html')
        with open(outname, 'w') as fd:
            fd.write(html)
    def walker(self, directory):
        """
        Looks for new or updated files in the source path
        making required conversions. Copy to the
        destination path converted files.
        """
        for filename in os.listdir(directory):
            longname = directory + '/' + filename
            outname = longname.replace(SOURCE, TARGET)
            if outname[-3:] == '.md':
                outname = outname.replace('.md', '.html')
            if os.path.isfile(longname):
                if os.path.exists(outname):
                    trgtime = os.path.getmtime(outname)
                    srctime = os.path.getmtime(longname)
                    if trgtime >= srctime:
                        continue
                if longname[-3:] == '.md':
                    self.mkd(longname)
                else:
                    copyfile(longname, outname)
                print(longname)
            else:
                if not os.path.exists(outname):
                    os.makedirs(outname)
                self.walker(longname)

if __name__ == '__main__':
    Generator().walker(SOURCE)
