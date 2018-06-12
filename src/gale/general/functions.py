def paired_list_generator(tlist):
    '''
    Takes a list and returns a list of the iterative element pairs
    input:
        list
    output:
        paired_list
    '''
    paired_list =[]
    for i in range(len(tlist)-1):
        paired_list.append([tlist[i], tlist[i+1]])
    return paired_list

def tex_sanitizer(tstr):
    '''
    Takes in a string and sanitizes it for LaTeX
    '''
    import re
    tstr = re.sub('_', ' ', tstr)
    return tstr

def labelifier(tstr):
    import re
    tstr = re.sub('_', ' ', tstr)
    tstr = re.sub('-', ' ', tstr)
    tstr = ' '.join(map(lambda x: x.capitalize(), tstr.split(' ')))
    return tstr
