'''
File: graph_fragments.py
Author: Adam Pah
Description:
Reusable graphs and graph components
'''

def set_labels(ax, xlabel=None, ylabel=None, title=None):
    '''
    Sets the labels on a subplot
    '''
    #xlabel
    if xlabel:
        ax.set_xlabel(xlabel)
    #If ylabel
    if ylabel:
        ax.set_ylabel(ylabel)
    #Title
    if title:
        ax.set_title(title)
    return ax

def _internal_save(wfname=None):
    '''
    Internal check and save function
    '''
    if wfname:
        plt.savefig(wfname)

def _generate_symmetry_line(ax, data=None):
    '''
    Generates a line of symmetry from teh data
    if no data, then 0-1
    '''
    if not data:
        dmin, dmax = 0.0, 1.0
    else:
        dmin = min(data)
        dmax = max(data)
    drange = [dmin, dmax]
    ax.plot(drange, drange)
    return ax

def barplot(data, ax=None, xlabels=None, ylabel=None, title=None, wfname=None, width=1.0):
    '''
    Input:
        required ---
        data in dictionary form ({'label': dpoint, ...})
        optional ---
        ax, the matplotlib subgrpah to place the axis
        ylabel,
        title
        width, the width of the bars
        wfname, the savename. will save if not none
    Output: 
        ax
    '''
    #First establish whether the is an axis object or not
    import numpy as np
    if not ax:
        import matplotlib.pyplot as plt
        ax = plt.subplot(111)
    #Set up the keys
    lset = data.keys()
    ind = np.arange(len(lset))
    #Now graph the data
    ax.bar(ind, [data[l] for l in lset], width) 
    #Now the axis labels
    if xlabels:
        ax.set_xticks(ind+width/2.0)
        ax.set_xticklabels(lset, rotation='vertical')
    else:
        ax.xaxis.set_ticklabels([])
    #Handle the axis
    ax.set_xlim(ind[0], ind[-1]+1)
    ax = set_labels(ax, ylabel=ylabel, title=title)
    #Saving
    _internal_save(wfname)
    return ax

def scatter(xdata, ydata, ax=None, xlabel=None, ylabel=None, title=None, wfname=None):
    '''
    Makes a scatter plot
    input:
        required ---
        xdata, list
        ydata, list
        optional ---
        ax, the matplotlib subgrpah to place the axis
        ylabel,
        title
        width, the width of the bars
        wfname, the savename. will save if not none
    output:
        ax
    '''
    if not ax:
        import matplotlib.pyplot as plt
        ax = plt.subplot(111)
    ax.scatter(xdata, ydata)
    ax = set_labels(ax, xlabel=xlabel, ylabel=ylabel, title=title)
    #Generate the symmetry line
    ax = _generate_symmetry_line(ax, xdata+ydata)
    #Saving
    _internal_save(wfname)
    return ax
