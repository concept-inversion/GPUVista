#!/bin/bash
# remove all lines in a file that doesn't start with number 1.
grep -e '^1,' $1 &> temp
# remove lines that contains the word 'dumped'
grep -v 'dumped' temp &> $1