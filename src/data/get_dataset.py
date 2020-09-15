
import subprocess
import os

import pandas as pd
import numpy as np

from datetime import datetime

import requests
import json

def get_data_jh():
    ''' To get data by a git pull request and the source code has to be pulled first.
        The result is stored in the predifined csv structure.
    '''
    dir_path=os.path.join(os.path.dirname(__file__),r'..\..\data\raw\COVID-19')
    print(dir_path)
    git_pull=subprocess.Popen('git init & git reset --hard & git pull https://github.com/CSSEGISandData/COVID-19.git' ,cwd=dir_path,shell=True,
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out,error)=git_pull.communicate()
    print('ERROR:', str(error))
    print('out:', str(out))




