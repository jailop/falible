#!/usr/bin/python

import os
import re
from shutil import copyfile
from markdown import markdown
from jinja2 import Template

SOURCE = './src'
TARGET = './output'

class Generator:
    def __init__(self):
        with open('templates/basic.html', 'r') as fd:
            self.template = Template(fd.read())
    def preprocess(self, filename, text):
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
