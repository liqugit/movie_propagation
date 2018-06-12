'''
File: classification.py
Author: Adam Pah
Description: 
classification statistics, written with pandas
'''


def calculate_classification_statistics(known, predicted):
    '''
    input:
        known - dictionary
        predicted - dictionary
        keyed identicially
    output:
        dictionary containing:
        ['tp', 'tn', 'fp', 'fn', 'sens', 'spec', 'prec', 'npv', 'fpr', 'fdr', 'acc', 'f1']
    '''

    def iterate_stat_functions(result):
        funcs = ['calc_sensitivity','calc_specificity','calc_precision','calc_npv','calc_fpr','calc_fdr','calc_acc','calc_f1']
        for func_name in funcs:
            result =  globals()[func_name](result)
        return result

    def calc_sensitivity(tdict):
        '''
        returns with sensitivity added
        '''
        tdict['sens'] = tdict['tp']/float(tdict['tp'] + tdict['fn']) 
        return tdict

    def calc_specificity(tdict):
        '''
        returns with specificity added
        '''
        tdict['spec'] = tdict['tn']/float(tdict['tn'] + tdict['fp'])
        return tdict

    def calc_precision(tdict):
        tdict['prec'] = tdict['tp']/float(tdict['tp'] + tdict['fp'])
        return tdict

    def calc_npv(tdict):
        tdict['npv'] = tdict['tn']/float(tdict['tn'] + tdict['fn'])
        return tdict

    def calc_fpr(tdict):
        tdict['fpr'] = tdict['fp']/float(tdict['fp'] + tdict['tn'])
        return tdict

    def calc_fdr(tdict):
        tdict['fdr'] = tdict['fp']/float(tdict['fp'] + tdict['tp'])
        return tdict

    def calc_acc(tdict):
        tdict['acc'] = (tdict['tn'] + tdict['tp'])/float(tdict['total'])
        return tdict

    def calc_f1(tdict):
        tdict['f1stat'] = 2*(tdict['tp']/float(tdict['tp'] + tdict['fp'] + tdict['fn']))
        return tdict

