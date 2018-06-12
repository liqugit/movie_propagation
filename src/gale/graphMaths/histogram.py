#! /usr/bin/python
import os,sys,random,numpy

def parser(file):
    infile=open(file)
    indata=infile.readlines()
    infile.close()
    data=[float(x.strip('\n')) for x in indata]
    return data

def create_histogram(data,bins):
    hist=Histogram(data,bins)
    for datum in data:
        if datum >= bins[0]:
            hist.SortDatum(datum)
    return hist

class Histogram:
    def __init__(self,data,bins):
        #Sort the bins into ascending order, make sure not nonetype
        qbins=bins.sort()
        if qbins!=None:
            self.BinArray=qbins
        else:
            self.BinArray=bins
        self.DataTotal=len(data)
        self.HistogramData={}
        self.GraceDataSet=[]

        for a in range(len(self.BinArray)):
            if a+1<len(self.BinArray):
                self.HistogramData[self.BinArray[a]]=Bin(self.BinArray[a],self.BinArray[a+1])
            else:
                imposed_ub=self.BinArray[a]+(self.BinArray[a]-self.BinArray[a-1])
                self.HistogramData[self.BinArray[a]]=Bin(self.BinArray[a],imposed_ub)
    
    def SortDatum(self,datum):
        DataPlacement=None
        min_index,mid_index,max_index=0,(len(self.BinArray)-1)/2,len(self.BinArray)-1
        while not DataPlacement:
            min_index,mid_index,max_index,DataPlacement=self.EvalBin(datum,min_index,mid_index,max_index,DataPlacement)

    def EvalBin(self,datum,min,mid,max,DataPlacement):
        if datum >= self.HistogramData[self.BinArray[min]].LB and \
           datum < self.HistogramData[self.BinArray[mid]].UB:
            
            newmid=(min+mid)/2
            if newmid==min:
                min,mid,max,DataPlacement=self.PlaceDatum(datum,min,mid,DataPlacement)
                return min,mid,max,DataPlacement
            else:
                return min,newmid,mid,DataPlacement
        else:
            newmid=(mid+max)/2
            if newmid==mid:
                min,mid,max,DataPlacement=self.PlaceDatum(datum,mid,max,DataPlacement)
                return min,mid,max,DataPlacement
            else:
                return mid,newmid,max,DataPlacement

    def PlaceDatum(self,datum,min,mid,DataPlacement):
        if datum>=self.HistogramData[self.BinArray[min]].LB and \
           datum<self.HistogramData[self.BinArray[min]].UB:
            self.HistogramData[self.BinArray[min]].Count+=1
        elif datum>=self.HistogramData[self.BinArray[mid]].LB and \
             datum<self.HistogramData[self.BinArray[mid]].UB:
            self.HistogramData[self.BinArray[mid]].Count+=1
        DataPlacement='True'
        return 0,0,0,DataPlacement

    def GenGraceDataset(self,norm=True):
        gdset=[]
        bins=self.HistogramData.keys()
        bins.sort()
        for bin in bins:
            if norm==True:
                gdset.append([bin,float(self.HistogramData[bin].Count)/float(self.DataTotal)])
            else:
                gdset.append([bin,float(self.HistogramData[bin].Count)])
            #self.GraceDataSet.append([bin,self.HistogramData[bin].Count])
        return gdset

class Bin:
    def __init__(self,cbin,nbin):
        self.LB=cbin
        self.UB=nbin
        self.Count=0

def write_histogram(hist,bins):
    outf=open('histogram.dat','w')
    for bin in bins:
        outf.write('%s\t%s\n' % (bin,hist[bin].Count))
    outf.close()

if __name__=='__main__':
    error='''This program produces histogram data for a series of data points.  
It requires an input file of data (argument 1) and the bins that are wanted, 
including end point (argument 2)'''
    
    if len(sys.argv)==1:
        print error
    else:
        if sys.argv[1]=='test':
            #BinList=range(100)
            #DataList=[random.randrange(0,100,1) for x in range(100000)]
            BinList=numpy.arange(0,10.01,0.1)
            DataList=[random.uniform(0.0,10.0) for x in range(100000)]
        else:
            DataList=parser(sys.argv[1])
            BinList=parser(sys.argv[2])
        hist_obj=create_histogram(DataList,BinList)
        write_histogram(hist_obj.HistogramData,BinList)
