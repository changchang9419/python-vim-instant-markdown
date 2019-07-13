#!/usr/bin/env python3
#coding: utf-8

import time
import md_instant
from markdown import markdown

if __name__ == '__main__':
    md_instant.main()
    md_instant.startbrowser()
    while True:
        x = input('Enter some markdown text for test(enter quit for quit: ')
        if x == 'quit':
            print('stop server and stop...')
            break

        x = markdown(x)
        md_instant.sendall(x)

    md_instant.stopserver()

