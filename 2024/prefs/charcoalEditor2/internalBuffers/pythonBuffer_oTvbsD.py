import os
from pathlib import Path
from threading import Thread
from multiprocessing import Process


def usdstitchclips(out_path='aa', clip_path='bb', regex_template='file.####.usdc', debug=True):
    command_string = "usdstitchclips --out {0} --clipPath {1} --templateMetadata --templatePath {2}".format(out_path, clip_path, regex_template)
    
    if debug:
        print(command_string)
    else:
        os.system(command_string)
    
def usdstitchclips_process_run(out_path='aa', clip_path='bb', regex_template='file.####.usdc', debug=True):
    p = Process(target=usdstitchclips, args=(out_path, clip_path, regex_template, debug,))
    
    p.start()
    #p.join()
    
def usdstitchclips_thread_run(out_path='aa', clip_path='bb', regex_template='file.####.usdc', debug=True):
    t1 = Thread(target=usdstitchclips, args=(out_path, clip_path, regex_template, debug,))
    
    t1.start()
    #t1.join()

if __name__ == '__main__':
    #usdstitchclips('hello')
    #usdstitchclips_process_run()
    usdstitchclips_thread_run()