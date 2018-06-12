'''
File: convert_weighted_network_to_linklist.py
Author: Adam Pah
Description: 
Convert a weighted network to linklist
1 2 4
Where links 1 and 2 have weight 4
'''

#Standard path imports
from optparse import OptionParser

#Non-standard imports

#Global directories and variables

def convert_weighted_to_linklist(inputFile, outputFile=None):
    '''
    input: filename, outputFilename
    output: None
    '''
    import gale.fileIO.generic as fgen
    #Get the random name
    if not outputFile:
        outputFile = fgen.random_file_namer(__file__, 'dat')
    indata = [l.strip().split() for l in open(inputFile).readlines()]
    wfile = open(outputFile, 'w')
    for x,y,w in indata:
        w = int(w)
        for z in range(w):
            print >> wfile, '%s %s' % (x,y)
    wfile.close()

if __name__ == '__main__':
    usage = '%prog [options]'
    parser = OptionParser(usage = usage)
    (opt, args) = parser.parse_args()
