'''
  A collection of functions for making publication-ready
  plots from root inputs.

  M. Nelson, 2019 <michael.edward.nelson@cern.ch

'''

import os
import sys
import ROOT as r
from ROOT import gROOT
from array import array
import collections
from math import sqrt
import yaml

def createUpperPad(doRatio=True, logOn=False):

    if doRatio: 
        padhigh = r.TPad("padhigh","padhigh",0.0,0.3,1.,1.)
        padhigh.SetBottomMargin(0.02)
    else:
        #r.gStyle.SetPadLeftMargin(0.20)
        padhigh = r.TPad("padhigh","padhigh",0.0,0.0,1.,1.)
        padhigh.SetBottomMargin(0.15)

    if logOn: 
        padhigh.SetLogy()

    padhigh.SetGrid(0,0)

    return padhigh

def createLowerPad():

    padLow = r.TPad("padlow","padlow",0.0,0.0,1.,0.3)
    padLow.SetTopMargin(0.03)
    padLow.SetBottomMargin(0.35)
    padLow.SetFillStyle(4000)
    padLow.SetGrid(0,0)

    return padLow

def initializeLegend( x1=0.3, y1=0.1, x2=.9, y2=.9): 
#def initializeLegend(x1=0.1, y1=0.55, x2=0.90, y2=0.95):

    aLegend = r.TLegend(x1, y1, x2, y2)
    aLegend.SetLineColor(r.kWhite)
    aLegend.SetFillColorAlpha(r.kWhite, 0.7)
    aLegend.SetNColumns(1)
    aLegend.SetTextSize(0.09)
    #aLegend.SetTextSize(0.115)
    #aLegend.SetTextSize(0.12)
    aLegend.SetBorderSize(0)
    aLegend.SetTextFont(42) # Remove bold text
    
    return aLegend
       
def getScaledHistogram(name, theHistos, scale=1):
    histo = theHistos.Get(name)
    histo.Scale(1/scale)
    return histo

def shape(histo, color, legend, legendText):
    histo.SetFillColor(color)
    histo.SetMarkerColor(color)
    histo.SetLineColor(r.kBlack)
    legend.AddEntry(histo, legendText, "f")

def shape_alt(histo, color):
    histo.SetFillColor(color)
    histo.SetMarkerColor(color)
    histo.SetLineColor(r.kBlack)

def defineHistos(histo, sampleDict, samplesToStack):
    # histomap append "name" : histo_{name}
    histomap = {}
    for sample in samplesToStack:
        histoname = sampleDict[sample]['histoname']
        legendtxt = sampleDict[sample]['legend description']

        if histoname not in histomap:
            histomap[histoname] = histo.Clone(histoname)
            histomap[histoname].Reset()
            histomap[histoname].Sumw2()
            colors = gROOT.GetColor(1)
            histomap[histoname].SetFillColor(colors.GetColor(*sampleDict[sample]['color']))
            histomap[histoname].SetLineColor(r.kBlack)
            histomap[histoname].SetLineWidth(0)
            histomap[histoname].SetTitle(legendtxt)
    
    return histomap

def addSignalStack(histo, stack, color, legend, legendText):
    histo.SetLineWidth(2)
    histo.SetLineStyle(r.kDashed)
    histo.SetLineColor(color)
    stack.Add(histo)
    legend.AddEntry(histo, legendText, "l")

def addRatio(ratioHist, numeratorHist, denominatorHist):
    ratioHist = numeratorHist.Clone()
    ratioHist.Divide(denominatorHist)
    #ratioHist.Sumw2()
    
def getSumHist(histo, sumHist):
    nBins = histo.GetNbinsX()
    uBin = histo.GetXaxis().GetXmax()
    dBin = histo.GetXaxis().GetXmin()
    sumHist.SetBins(nBins, dBin, uBin)
    sumHist.Add(histo)


def rebin_hist(histo, bins_array):
    newname = histo.GetName()+'_rebinned'
    newhist = histo.Rebin(len(bins_array)-1, newname, bins_array)
    newhist.SetDirectory(0)
    newhist.GetYaxis().SetRangeUser(0.1,100000)

    return newhist


def rebin_THStack(stack, bins_array):
    tempStack = THStack('Background stack rebinned','')
    histList = stack.GetHists()
    
    for hist in histList:
        if type(bins_array) == int:
            tempHist = hist.Rebin(bins_array)
        else:
            tempHist = rebin_plot(hist, bins_array)
        tempHist.SetDirectory(0)
        tempStack.Add(tempHist)
    
    return tempStack

def GetYtitle(stackHist, units):
    theHisto = stackHist.GetStack().Last()
    bins = theHisto.GetNbinsX()
    xmin = theHisto.GetXaxis().GetXmin()
    xmax = theHisto.GetXaxis().GetXmax()
    res = (xmax-xmin)/bins

    y_title = "Events / " + str(round(res,1))+" "+units

    return y_title

def CheckXrange(theHisto, new_xmin, new_xmax):
    xmin = theHisto.GetXaxis().GetXmin()
    xmax = theHisto.GetXaxis().GetXmax()
    status = False
    if ((new_xmin < xmin) or (new_xmax > xmax)):
        print("WARNING x-min and/or x-max is outside the histogram range. Using TH1F edges instead")
    elif ((new_xmin > xmin) or (new_xmax < xmax)):
        print("Zooming in a sub-range of the original TH1F using x-min and x-max edges")
        status = True

    return status


def MergeBackgrounds(MergeBkgList, Reg, Bkg, yields):

    Merge = []
    Merge_unc = []
    NoHBkg = []
    for r in Reg:
        events = 0
        unc = 0
        for b in Bkg:
            if (b in MergeBkgList):
                events += yields[b][r][0]
                unc +=  yields[b][r][1]**2

        Merge.append(events)
        Merge_unc.append(sqrt(unc))

    for b in Bkg:
        if (b not in MergeBkgList): NoHBkg.append(b)

    return (Merge, Merge_unc, NoHBkg)
def drawATLASLabel(legend, include_ratio=False, atlastext="Internal", run3=False, btag=None, btag_exact=False, btag_wp=85, pt_bin_label=None):
    l = r.TLatex()
    l.SetNDC()
    l.SetTextColor(r.kBlack)
    l.SetTextFont(42)


    energy = "13 TeV" if not run3 else "13.6 TeV"
    luminosity = "140 fb^{-1}" if not run3 else "168 fb^{-1}"

    btag_symbol = "=" if btag_exact else "#geq"

    if include_ratio:
        l.SetTextSize(0.04)
        l1, l2 = 0.22, 0.83
        r.ATLASLabel(l1,l2, atlastext, 1, 0.08)
        l.DrawLatex(l1, 0.74, "#sqrt{#it{s}} = "f"{energy}, {luminosity}")
        l.DrawLatex(l1, 0.67, "HH#rightarrowb#bar{b}#gamma#gamma")
        l.DrawLatex(l1, 0.60, legend['legend upper'])
        l.DrawLatex(l1, 0.55, legend['legend lower'])
        _y = 0.50
        if btag is not None:
            l.DrawLatex(l1, _y, "%s%d b-jets @ %d%% WP" % (btag_symbol, btag, btag_wp))
            _y -= 0.05
        elif btag_wp != 85:
            l.DrawLatex(l1, _y, "%d%% WP b-tagging" % btag_wp)
            _y -= 0.05
        if pt_bin_label is not None:
            l.DrawLatex(l1, _y, pt_bin_label)
    else:
        l.SetTextSize(0.045)
        l1, l2 = 0.22, 1
        r.ATLASLabel(l1,l2, atlastext, 1)
        l.DrawLatex(l1, 0.82, "#sqrt{#it{s}} = "f"{energy}, {luminosity}")
        l.DrawLatex(l1, 0.76, "HH#rightarrowb#bar{b}#gamma#gamma")
        l.DrawLatex(l1, 0.69, legend['legend upper'])
        l.DrawLatex(l1, 0.64, legend['legend lower'])
        _y = 0.59
        if btag is not None:
            l.DrawLatex(l1, _y, "%s%d b-jets @ %d%% WP" % (btag_symbol, btag, btag_wp))
            _y -= 0.05
        elif btag_wp != 85:
            l.DrawLatex(l1, _y, "%d%% WP b-tagging" % btag_wp)
            _y -= 0.05
        if pt_bin_label is not None:
            l.DrawLatex(l1, _y, pt_bin_label)


def setBlindedValuestoZero(dataHist, signficance_ratios, BLIND_THRESHOLD=0.01):
    for i in range(dataHist.GetNbinsX()):
        for s_histo in signficance_ratios:
            if signficance_ratios[s_histo].GetBinContent(i+1) > BLIND_THRESHOLD:
                dataHist.SetBinContent(i+1, 0)
                dataHist.SetBinError(i+1, 0)
    return dataHist

def setBlindedValuesmyy(dataHist):
    for i in range(dataHist.GetNbinsX()):
        myy = dataHist.GetBinCenter(i+1)
        if myy>120 and myy<130:
            dataHist.SetBinContent(i+1, 0)
            dataHist.SetBinError(i+1, 0)
    return dataHist


def ExtractBinning(signal):

    binning = []

    try:

        with open('/afs/cern.ch/work/l/lapereir/public/HH/SH_PNN_binning/histograms_h027_TransfoJ_1BinsInBkgRegion_TunedParameters_SR_pre_fit_'+signal+'.yaml', 'r') as stream:
            try:
                d=yaml.safe_load(stream)
            except yaml.YAMLError as e:
                print(e)

        for b in d['binning']:
            binning.append(round(b, 4))

        return binning


    except:
        print(signal," PNN binning file not available will use default from the config file")

        return 0
