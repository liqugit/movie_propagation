"""
File: utilities.py
Author: Joao Moreira
Creation Date: Dec 18, 2012

Description:
Contains several helper functions to read/write files and to manipulate data
"""
import json
import unicodedata
from itertools import groupby, zip_longest
from math import log10

##############################################################################
#######
#######                     IMPORTING/EXPORTING DATA
#######
##############################################################################

def import_json(file_name, **kwargs):
    data_file = open(file_name, 'r')
    data = json.load(data_file, **kwargs)
    data_file.close()
    return data


def export_json(data, file_name, **kwargs):
    data_file = open(file_name, 'w')
    json.dump(data, data_file, **kwargs)
    data_file.close()
    return


##############################################################################
#######
#######                     PLOTTING
#######
##############################################################################

# Better poster context RC params
bpc_rc = {
    "axes.labelsize": 25,
    "axes.titlesize": 25,
    "legend.fontsize": 20,
    "xtick.labelsize": 20,
    "ytick.labelsize": 20,
    "font.size": 30,
}


##############################################################################
#######
#######                     MISC UTILITIES
#######
##############################################################################

def round_int(x):
    """
    Rounds integers to nearest multiple of 10**int(log10(x))
    """
    return int(round(x, - int(log10(x))))


def binary_search(data, record, lower, upper):
    """
    Performs a binary search to find the bin in data to which record belongs to.
    The function allways operates on the first dimension of the list.

    It computes the median of the interval [data[lower], data[upper]) and
    narrows the right bin down recursivelly, either taking the left half
    [data[lower], data[median]) or the right half [data[median], data[upper])
    of the interval.
    """
    upper, lower = map(int, (upper, lower))

    # check if data[i] is a sublist or not
    def value(element):
        if isinstance(element, list):
            return element[0]
        else:
            return element

    size = upper - lower
    # if there is only two bins in the interval we have reached the
    # end of the search
    if size < 2:
        if record < value(data[upper]):
            return lower
        else:
            return upper
    # if the interval has an even number of bins
    if (size+1)%2 == 0:
        med_low = (size-1)/2
        med_upp = ((size-1)/2)+1
        median = (value(data[lower+med_low]) + value(data[lower+med_upp])) / 2.
    # if the interval has an odd number of bins
    else:
        med_low = size/2
        med_upp = size/2
        median = value(data[lower + med_low])

    # if the record is smaller than the median
    if record < median:
        #  we take the left half of the interval
        bin_index = binary_search(data, record, lower, lower + med_upp)
    # otherwise we take the right half
    else:
        bin_index = binary_search(data, record, lower + med_low, upper)

    return bin_index


def grouper_keys(data, keyfunc):
    internal_data = sorted(data, key=keyfunc)
    for key, g in groupby(internal_data, keyfunc):
        yield (key, list(g))


def len_grouper(iterable, length, fillvalue=None):
    """
    Divide data into chunks or blocks of fixed length.
    len_grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    Modififed from: https://docs.python.org/2/library/itertools.html#recipes
    """
    args = [iter(iterable)]*length
    return zip_longest(fillvalue=fillvalue, *args)


def bin_grouper(iterable, bins):
    """
    Divide data into a fixed number of bins.
    """
    bin_size = int((float(len(iterable))/float(bins)) + 0.5)
    for i in range(0, bins-1):
        yield iterable[i*bin_size:(i+1)*bin_size]
    yield iterable[(bins-1)*bin_size:]


def unpack_lists(record):
    """
    key: [val]                          --> key: val
    key: [val1, val2]                   --> key: [val1, val2]
    key1: {key2: [val]}                 --> key1: {key2: val}
    key1: [{key2: [val]}]               --> key1: {key2: val}
    key1: [{key2: [v1]}, {key2: [v2]}]  --> key1: [{key2: v1}, {key2: v2}]
    """
    if isinstance(record, list):
        if len(record) == 1:
            return unpack_lists(record[0])
        else:
            un_record = [unpack_lists(v) for v in record]
            return un_record
    elif isinstance(record, dict):
        un_record = {k: unpack_lists(v) for k, v in record.items()}
        return un_record
    else:
        return record


def uni2str(uni):
    """
    Removes accents and converts unicode dashes to spaces.
    """
    uni = uni.replace(u"\u2013", u" ")
    # removing accents and converting to string
    uni = unicodedata.normalize('NFKD', uni)
    return uni.encode("ascii", "ignore").decode()
