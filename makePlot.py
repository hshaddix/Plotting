import os
import ROOT as r
from math import log, sqrt
from utils import *
from histoDict import *
from PlottingList import*

r.gROOT.LoadMacro("./AtlasStyle/AtlasStyle.C")
r.gROOT.LoadMacro("./AtlasStyle/AtlasLabels.C")
r.gROOT.LoadMacro("./AtlasStyle/AtlasUtils.C")

colors = gROOT.GetColor(1)

r.SetAtlasStyle()

r.gROOT.SetBatch(1)
r.gStyle.SetPalette(56) 


histoDict = PlottingDict()
sampleDict = SampleDict()
selectionDict = SelectionDict()
SignalDict = SignalDict()

user_name = "user.gdigrego"
version = "v9"
analysis_folder = "bbyy_output_ntuples_RUN_v9"
BLIND_THRESHOLD = 0.03

# PCBT score: integer 1-6 per jet, tightest WP it passes
#   6=65%, 5=70%, 4=77%, 3=85%, 2=90%, 1=fails all
# Require pcbt >= bin value to select at a given WP
PCBT_WP_BINS = {
    65: 6,
    70: 5,
    77: 4,
    85: 3,
    90: 2,
}


#### PLOT 1D
def main1D(UNBLIND=False, mcOnly=False, include_ratio=False, logOn=False, inputPath="", outputPath="./Plots/", dosignal=False, btag=None, btag_exact=False, btag_wp=85, unweighted=False):
    r.gStyle.SetPadLeftMargin(0.15) 
    r.gStyle.SetPadRightMargin(0.10)
    r.gStyle.SetPadBottomMargin(0.15)
    r.gStyle.SetPadTopMargin(0.05)
    r.gStyle.SetNumberContours(999)


    # Loop over selection required
    for selection in selectionToPlot:
        ## PUT Run2 or Run3 in the selection to Plot
        run3 = "Run3" in selection
        if run3:
            folder_name = analysis_folder.replace("RUN", "Run3")
            data_campaigns = ["22", "23", "24"]
            mc_campaigns = ["mc23a", "mc23d", "mc23e"]
        else:
            folder_name = analysis_folder.replace("RUN", "Run2")
            data_campaigns = ["15", "16", "17", "18"]
            mc_campaigns = ["mc20a", "mc20d", "mc20e"]

        if UNBLIND:
            print('WARNING: You have unblinded the analysis! Are you sure you want to do this?')

        input_extended = os.path.join(inputPath, f"ntuples_{version}/{folder_name}/")

        # cache once per selection to avoid repeated remote listdir calls
        all_files_cached = os.listdir(input_extended)

        r.gROOT.cd()
        # Create the cutlist
        cutlist = ""
        MCcutlist = "1" if unweighted else "weight_total_NOSYS"
        if "cuts" in selectionDict[str(selection)]:
            cutlist = " * ".join(selectionDict[str(selection)]['cuts'])
            MCcutlist += " * "+cutlist
        if btag is not None:
            btag_op = "==" if btag_exact else ">="
            pcbt_bin = PCBT_WP_BINS.get(btag_wp, PCBT_WP_BINS[85])
            npass_expr = "((bbyy_Jet1_pcbt_NOSYS >= %d) + (bbyy_Jet2_pcbt_NOSYS >= %d))" % (pcbt_bin, pcbt_bin)
            btag_cut = "(%s %s %d)" % (npass_expr, btag_op, btag)

            MCcutlist += " * " + btag_cut
            cutlist = (cutlist + " * " + btag_cut) if cutlist else btag_cut
        print("  [btag] MC cut  : %s" % MCcutlist)
        print("  [btag] data cut: %s" % cutlist)
        # Loop over histogram required
        for histo_name in histosToPlot:
            print("--- Plotting " + histo_name + " with selection " + selection + " ---")

            # Create the variable name
            variable = histoDict.get(histo_name, {}).get('variable', histo_name)
            if histoDict.get(histo_name, {}).get('toGeV', False):
                variable += "/1e3"

            # Create the canvas 
            canv =  r.TCanvas("canvas","canvas",800,600)
            canv.cd()
            
            # Create the upper pad if include_ratio leave space for ratio
            padhigh = createUpperPad(include_ratio,logOn)
            padhigh.Draw()
            padhigh.cd()

            # Create the histogram with specified binnings
            theHisto = r.TH1F("h", "h", histoDict[histo_name]['nBins'], histoDict[histo_name]['x-min'], histoDict[histo_name]['x-max'])

            #define histo to stack
            # Use jet flavor samples for m_jj (dijet mass) and angular variables
            stack_list = jetsSamplesToStack if histo_name in ["recojet_mjj_NOSYS", "deltaR_yy", "deltaR_jj", "bbyy_mbbyy_NOSYS"] else samplesToStack
            histos_to_stack = defineHistos(theHisto, sampleDict, stack_list)

            if dosignal:
                signal_histos = {s_name: theHisto.Clone("h_" + s_name) for s_name in signalName}

            # Stacked Histogram
            stackHist = r.THStack()

            # Data Histogram
            dataHist = theHisto.Clone("dataHist")
            dataHist.SetMarkerColor(r.kBlack)
            dataHist.SetMarkerStyle(r.kFullDotLarge)
            dataHist.SetLineColor(r.kBlack)
            dataHist.SetLineWidth(2)
            dataHist.Reset()
            
            # Ratio histogram
            ratioHist = theHisto.Clone("ratioHist")

            # Set up legend
            theLegend = initializeLegend()

            # run on Data
            if not mcOnly:
                theHisto.Reset()
                file_name = None
                for campaign in data_campaigns:
                    file_name = os.path.join(input_extended, f"data_0_data{campaign}_data.root")
                    file = r.TFile.Open(file_name, "r")
                    if not file or file.IsZombie():
                        continue
                    tree = file.Get("AnalysisMiniTree")
                    tree.SetCacheSize(100*1024*1024)  # 100 MB cache, helps a lot over EOS
                    tree.AddBranchToCache("*")
                    theHisto_data_tmp = theHisto.Clone("h_data_tmp")
                    tree.Draw(variable+">>h_data_tmp", cutlist)
                    dataHist.Add(theHisto_data_tmp)
                    theHisto_data_tmp.Delete()
                    file.Close()

            # Loop over the samples
            for sample in stack_list:
                print("Sample: ", sample)
                #reset theHisto
                theHisto.Reset()

                for campaign in mc_campaigns:
                    rootfile = None
                    for f in all_files_cached:
                        if (sample_map[sample] in f) and (campaign in f):
                            rootfile = f
                            break
                    if not rootfile:
                        continue
                    file_name = os.path.join(input_extended, rootfile)
                    file = r.TFile.Open(os.path.join(input_extended, file_name),"r")
                    if not file or file.IsZombie():
                        continue
                    tree = file.Get("AnalysisMiniTree")
                    tree.SetCacheSize(100*1024*1024)
                    tree.AddBranchToCache("*")
                    theHisto_tmp = theHisto.Clone("h_tmp")
                    if "extracut" in sampleDict[sample]:
                        MCcutlist_extra = MCcutlist + " * " + sampleDict[sample]["extracut"]
                    else:
                        MCcutlist_extra = MCcutlist
                    tree.Draw(variable + ">>h_tmp", MCcutlist_extra)
                    if sample in selectionDict[str(selection)]['sfs']:
                        theHisto_tmp.Scale(selectionDict[str(selection)]['sfs'][sample])
                    theHisto.Add(theHisto_tmp)
                    theHisto_tmp.Delete()
                    file.Close()
                histos_to_stack[sampleDict[sample]['histoname']].Add(theHisto)                

                if dosignal and sampleDict[sample]['histoname'] in signal_histos:
                    signal_histos[sampleDict[sample]['histoname']].Add(theHisto)

            theHisto.Delete()

            available_signals = [s for s in signalName if s in histos_to_stack]

            signficance_ratios = {s_name: ratioHist.Clone("ratioHist_"+s_name) for s_name in available_signals}
            significance_all   = {s_name: 0 for s_name in available_signals}

            for k, s_name in enumerate(available_signals):
                histos_to_stack[s_name].Sumw2()
                histo_allbkg = signficance_ratios[s_name].Clone("histo_allbkg")
                histo_allbkg.Reset()

                for hname in histos_to_stack:
                    if hname != s_name:
                        histo_allbkg.Add(histos_to_stack[hname])

                for i in range(histos_to_stack[s_name].GetNbinsX()):
                    if histo_allbkg.GetBinContent(i+1) > 0:
                        s = histos_to_stack[s_name].GetBinContent(i+1)
                        b = histo_allbkg.GetBinContent(i+1)
                        s_bin_square = 2*((s+b)*log(1+s/b)-s)
                        s_bin = sqrt(max(0, s_bin_square))
                        signficance_ratios[s_name].SetBinContent(i+1, s_bin)
                        signficance_ratios[s_name].SetBinError(i+1, s_bin)
                        significance_all[s_name] += s_bin*s_bin
                    else:
                        signficance_ratios[s_name].SetBinContent(i+1, 0)
                        signficance_ratios[s_name].SetBinError(i+1, 0)

                significance_all[s_name] = sqrt(significance_all[s_name])

            # BLINDING myy and all significant bins
            if not UNBLIND and "bbyy_myy_NOSYS"==histo_name:
                dataHist = setBlindedValuesmyy(dataHist)
            elif not UNBLIND:
                dataHist = setBlindedValuestoZero(dataHist, signficance_ratios, BLIND_THRESHOLD)
            # add data to legend
            if not mcOnly:
                if not UNBLIND:
                    datastring = "Data sidebands"
                elif UNBLIND:
                    datastring = "Data"
                theLegend.AddEntry(dataHist, datastring, "PE")

            #STACKING
            for histo in histos_to_stack:
                stackHist.Add(histos_to_stack[histo])

            for histo in reversed(list(histos_to_stack.keys())):
                theLegend.AddEntry(histos_to_stack[histo], histos_to_stack[histo].GetTitle(), "f")

            r.gROOT.cd()
            stackHist.Draw("HIST")

            # Add uncertainty band on the total MC:
            totalBkg = stackHist.GetStack().Last().Clone("totalBkg")
            #remove markers
            totalBkg.SetMarkerSize(0)
            totalBkg.SetFillColor(r.kBlack)  # choose an appropriate color for the band
            totalBkg.SetFillStyle(3004)       # a semi-transparent fill style
            totalBkg.Draw("E2 SAME")
            theLegend.AddEntry(totalBkg, "MC stat. unc.", "f")

            if not mcOnly:
                dataHist.Draw("SAME E1")

            if dosignal:
                for s_name in signal_histos:
                    signal_histos[s_name].SetLineWidth(2)
                    signal_histos[s_name].SetLineColor(colors.GetColor(*SignalDict[s_name]["color"]))
                    signal_histos[s_name].Scale(SignalDict[s_name]["multiplier"])
                    signal_histos[s_name].Draw("SAME HIST")
                    theLegend.AddEntry(signal_histos[s_name], SignalDict[s_name]["legend description"]+ " #times "+str(SignalDict[s_name]["multiplier"]), "l")

            # Define y-asis label
            if 'y-axis title' in histoDict:
                y_title = histoDict[histo_name]['y-axis title']
            else:
                y_title = GetYtitle(stackHist, histoDict[histo_name]['units'])

            stackHist.GetYaxis().SetTitle(y_title)
            stackHist.GetYaxis().SetTitleOffset(1)
            stackHist.GetYaxis().SetTitleSize(0.06)
            stackHist.GetYaxis().SetLabelSize(0.06)
            stackHist.GetXaxis().SetNdivisions(506)

            ymax_upper = max(stackHist.GetMaximum(), dataHist.GetMaximum())
            stackHist.SetMaximum(2.2*ymax_upper)

            # Draw x axis for top panel
            if not include_ratio:
                stackHist.GetXaxis().SetTitle(histoDict[str(histo_name)]['x-axis title'])
                stackHist.GetXaxis().SetTitleOffset(1)
                stackHist.GetXaxis().SetLabelFont(43)
                stackHist.GetXaxis().SetLabelSize(25)
                stackHist.GetYaxis().SetLabelFont(43)
                stackHist.GetYaxis().SetLabelSize(25) 
            else:
                stackHist.GetXaxis().SetTitleOffset(99)
                stackHist.GetXaxis().SetLabelSize(25)


            # Set up ATLAS label
            drawATLASLabel(selectionDict[str(selection)], include_ratio, "Internal", run3, btag=btag, btag_exact=btag_exact, btag_wp=btag_wp)

            # Draw Legend
            canv.cd()
            padside = r.TPad("padside","padside",0.5,0.52,0.85,0.96)
            padside.SetFillColorAlpha(0, 0.1)
            padside.Draw()
            padside.cd()
            theLegend.Draw("SAME")

            # RATIO PANEL
            if include_ratio:
                padLow = createLowerPad()
                canv.cd()
                padLow.Draw()
                padLow.cd()

                if mcOnly:
                    # if MC only -> Draw Significance
                    ratioHist.GetYaxis().SetTitle("Significance")
                    ratioHist.Scale(0)
                    ratioHist.SetLineWidth(0)
                    ratioHist.Draw("SAME")
                    ymax_lower  = max(signficance_ratios[s_name].GetMaximum() for s_name in signalName)

                    # create a pad for the significance
                    canv.cd()
                    padsig = r.TPad("padsig","padsig",0.6,0.17,0.85,0.28)
                    padsig.Draw()
                    padsig.cd()
                    ls = r.TLatex()
                    ls.SetNDC()
                    ls.SetTextColor(r.kBlack)
                    ls.SetTextFont(42)
                    ls.SetTextSize(0.2)
                    ls.DrawLatex(0.1, 1-(1)/(len(signalName)+1), "S_{i} = #sqrt{2((s+b)log(1+s/b)-s)}")
                    for k,s_name in enumerate(signalName):
                        padLow.cd()

                        signficance_ratios[s_name].SetLineWidth(2)
                        signficance_ratios[s_name].SetLineColor(colors.GetColor(*SignalDict[s_name]["color"]))

                        signficance_ratios[s_name].Draw("SAME HIST")

                        # print significance on the plot
                        padsig.cd()
                        ls.DrawLatex(0.1, 1-(k+2)/(len(signalName)+1), "Sig. "+s_name+": "+str(round(significance_all[s_name],2)))

                    padLow.cd()
                    ratioHist.SetMaximum(1.3*ymax_lower)

                # if not MC only -> Draw Data/MC
                else:
                    padLow.cd()
                    ratioHist = dataHist.Clone("ratioHist")
                    ratioHist.GetYaxis().SetTitle("Data/MC")
                    ratioHist.Divide(stackHist.GetStack().Last())
                    ratioHist.SetMarkerColor(r.kBlack)
                    ratioHist.SetMarkerStyle(r.kFullDotLarge)
                    ratioHist.SetLineColor(r.kBlack)
                    ratioHist.SetLineWidth(2)
                    # draw line at 1 
                    line = r.TLine(ratioHist.GetXaxis().GetXmin(), 1, ratioHist.GetXaxis().GetXmax(), 1)
                    line.SetLineColor(r.kBlack)
                    line.SetLineWidth(2)
                    
                    ratioHist.SetMaximum(2)
                    ratioHist.SetMinimum(0)
                    ratioHist.Draw("SAME E1")    
                    line.Draw("SAME")
                
                ratioHist.GetYaxis().CenterTitle()
                ratioHist.GetYaxis().SetNdivisions(303)
                ratioHist.GetYaxis().SetTitleSize(0.14)
                ratioHist.GetYaxis().SetLabelSize(0.14)
                ratioHist.GetYaxis().SetTitleOffset(0.4)
                ratioHist.GetYaxis().SetRangeUser(0.7,1.3)

                ratioHist.GetXaxis().SetTitleOffset(1)
                ratioHist.GetXaxis().SetNdivisions(506, True)
                ratioHist.GetXaxis().SetTitle(histoDict[str(histo_name)]['x-axis title'])
                ratioHist.GetXaxis().SetTitleSize(0.15)
                ratioHist.GetXaxis().SetLabelFont(43)
                ratioHist.GetXaxis().SetLabelSize(2)
                            

            if btag is not None:
                btag_suffix = "_btag%d_%s%db" % (btag_wp, "exact" if btag_exact else "geq", btag)
            elif btag_wp != 85:
                btag_suffix = "_btag%d" % btag_wp
            else:
                btag_suffix = ""
            print("Saving the canvas name : ", outputPath + "/hist1D_" + histo_name + "_" + selection + btag_suffix + ".png")
            canv.SaveAs(outputPath + "/hist1D_" + histo_name + "_" + selection + btag_suffix + ".png", "png")
            r.SetOwnership(canv, False)
            canv.Close()


#### SHAPE COMPARISON
# Normalized jet flavor overlays; --fitRatio adds ratio-to-bb panel with pol1 fits
# (pol1 skipped for mjj where a linear model doesn't make sense)
def mainShapeComparison(inputPath="", outputPath="./Plots/", dosignal=False, rebin=False, fitRatio=False, errorFit=False, btag=None, btag_exact=False, btag_wp=85):
    r.gStyle.SetPadLeftMargin(0.15)
    r.gStyle.SetPadRightMargin(0.10)
    r.gStyle.SetPadBottomMargin(0.15)
    r.gStyle.SetPadTopMargin(0.05)

    # Loop over selection required
    for selection in selectionToPlot:
        run3 = "Run3" in selection
        if run3:
            folder_name = analysis_folder.replace("RUN", "Run3")
            mc_campaigns = ["mc23a", "mc23d", "mc23e"]
        else:
            folder_name = analysis_folder.replace("RUN", "Run2")
            mc_campaigns = ["mc20a", "mc20d", "mc20e"]

        input_extended = os.path.join(inputPath, f"ntuples_{version}/{folder_name}/")

        r.gROOT.cd()
        # Create the cutlist
        MCcutlist = "weight_total_NOSYS"
        if "cuts" in selectionDict[str(selection)]:
            cutlist = " * ".join(selectionDict[str(selection)]['cuts'])
            MCcutlist += " * "+cutlist
        if btag is not None:
            btag_op = "==" if btag_exact else ">="
            pcbt_bin = PCBT_WP_BINS.get(btag_wp, PCBT_WP_BINS[85])
            npass_expr = "((bbyy_Jet1_pcbt_NOSYS >= %d) + (bbyy_Jet2_pcbt_NOSYS >= %d))" % (pcbt_bin, pcbt_bin)
            MCcutlist += " * (%s %s %d)" % (npass_expr, btag_op, btag)
        print("  [btag] MC cut  : %s" % MCcutlist)

        # Plot shape comparisons for all jet-flavor histograms
        # Mass histograms always get ratio-to-bb panel; deltaR gets it too when fitRatio is on
        mass_histos = ["bbyy_myy_NOSYS", "recojet_mjj_NOSYS", "bbyy_mbbyy_NOSYS"]
        all_shape_histos = mass_histos + ["deltaR_yy", "deltaR_jj"]
        for histo_name in all_shape_histos:
            do_ratio = fitRatio  # Only show ratio-to-bb panel when --fitRatio is used
            do_fit = fitRatio and histo_name != "recojet_mjj_NOSYS"  # mjj gets ratio but no pol1 fit
            print("--- Shape comparison for " + histo_name + " with selection " + selection + " ---")

            variable = histoDict.get(histo_name, {}).get('variable', histo_name)
            if histoDict.get(histo_name, {}).get('toGeV', False):
                variable += "/1e3"

            draw_shapes = not do_ratio or not fitRatio

            if draw_shapes and do_ratio:
                canv = r.TCanvas("canvas", "canvas", 800, 800)
            else:
                canv = r.TCanvas("canvas", "canvas", 800, 600)
            canv.cd()

            theHisto = r.TH1F("h", "h", histoDict[histo_name]['nBins'],
                             histoDict[histo_name]['x-min'], histoDict[histo_name]['x-max'])

            jet_histos = {}
            for sample in jetsSamplesToStack:
                jet_histos[sample] = theHisto.Clone("h_" + sample)
                jet_histos[sample].Reset()
                jet_histos[sample].Sumw2()

            for sample in jetsSamplesToStack:
                print("  Processing: ", sample)
                theHisto.Reset()

                for campaign in mc_campaigns:
                    all_files = os.listdir(input_extended)
                    rootfile = None
                    for f in all_files:
                        if (sample_map[sample] in f) and (campaign in f):
                            rootfile = f
                            break
                    if not rootfile:
                        continue
                    file_name = os.path.join(input_extended, rootfile)
                    file = r.TFile.Open(file_name, "r")
                    if not file or file.IsZombie():
                        continue
                    tree = file.Get("AnalysisMiniTree")
                    theHisto_tmp = theHisto.Clone("h_tmp")
                    if "extracut" in sampleDict[sample]:
                        MCcutlist_extra = MCcutlist + " * " + sampleDict[sample]["extracut"]
                    else:
                        MCcutlist_extra = MCcutlist
                    tree.Draw(variable + ">>h_tmp", MCcutlist_extra)
                    if sample in selectionDict[str(selection)]['sfs']:
                        theHisto_tmp.Scale(selectionDict[str(selection)]['sfs'][sample])
                    jet_histos[sample].Add(theHisto_tmp)
                    theHisto_tmp.Delete()
                    file.Close()

            theHisto.Delete()

            # Rebin histograms if requested (x2 fewer bins)
            if rebin:
                for sample in jetsSamplesToStack:
                    jet_histos[sample].Rebin(2)

            # Normalize all histograms to unit area
            for sample in jetsSamplesToStack:
                integral = jet_histos[sample].Integral()
                if integral > 0:
                    jet_histos[sample].Scale(1.0 / integral)

            signal_histo = None
            if dosignal:
                signal_histo = r.TH1F("h_signal", "h_signal", histoDict[histo_name]['nBins'],
                                      histoDict[histo_name]['x-min'], histoDict[histo_name]['x-max'])
                signal_histo.Reset()
                signal_histo.Sumw2()
                for sig_sample in ["ggFHHbbyy", "VBFHHbbyy"]:
                    print("  Processing signal: ", sig_sample)
                    for campaign in mc_campaigns:
                        all_files = os.listdir(input_extended)
                        rootfile = None
                        for f in all_files:
                            if (sample_map[sig_sample] in f) and (campaign in f):
                                rootfile = f
                                break
                        if not rootfile:
                            continue
                        file_name = os.path.join(input_extended, rootfile)
                        file = r.TFile.Open(file_name, "r")
                        if not file or file.IsZombie():
                            continue
                        tree = file.Get("AnalysisMiniTree")
                        theHisto_tmp = signal_histo.Clone("h_sig_tmp")
                        tree.Draw(variable + ">>h_sig_tmp", MCcutlist)
                        signal_histo.Add(theHisto_tmp)
                        theHisto_tmp.Delete()
                        file.Close()
                if rebin:
                    signal_histo.Rebin(2)
                sig_integral = signal_histo.Integral()
                if sig_integral > 0:
                    signal_histo.Scale(1.0 / sig_integral)
                signal_histo.SetLineColor(r.kRed)
                signal_histo.SetLineWidth(3)
                signal_histo.SetLineStyle(1)

            for sample in jetsSamplesToStack:
                jet_histos[sample].SetLineColor(colors.GetColor(*sampleDict[sample]['color']))
                jet_histos[sample].SetLineWidth(2)
                jet_histos[sample].SetFillStyle(0)

            if draw_shapes:
                if do_ratio:
                    padhigh = r.TPad("padhigh", "padhigh", 0, 0.35, 1, 1)
                    padhigh.SetBottomMargin(0.02)
                    padhigh.SetTopMargin(0.05)
                    padhigh.Draw()
                    padhigh.cd()

                theLegend = r.TLegend(0.65, 0.55, 0.88, 0.92)
                theLegend.SetBorderSize(0)
                theLegend.SetFillStyle(0)
                theLegend.SetTextSize(0.04)

                ymax = 0
                for i, sample in enumerate(jetsSamplesToStack):
                    if jet_histos[sample].GetMaximum() > ymax:
                        ymax = jet_histos[sample].GetMaximum()
                    theLegend.AddEntry(jet_histos[sample], sampleDict[sample]['legend description'], "l")

                # Include signal in ymax calculation if present
                if dosignal and signal_histo and signal_histo.GetMaximum() > ymax:
                    ymax = signal_histo.GetMaximum()

                # Draw first histogram to set axes
                jet_histos["jetsbb"].SetMaximum(1.5 * ymax)
                jet_histos["jetsbb"].SetMinimum(0)
                jet_histos["jetsbb"].GetYaxis().SetTitle("Normalized to unit area")
                jet_histos["jetsbb"].GetYaxis().SetTitleOffset(1.2)
                jet_histos["jetsbb"].GetYaxis().SetTitleSize(0.05)
                jet_histos["jetsbb"].GetYaxis().SetLabelSize(0.05)
                jet_histos["jetsbb"].GetXaxis().SetTitle(histoDict[str(histo_name)]['x-axis title'])
                if do_ratio:
                    jet_histos["jetsbb"].GetXaxis().SetLabelSize(0)  # Hide x-axis labels on top pad
                else:
                    jet_histos["jetsbb"].GetXaxis().SetTitleSize(0.05)
                    jet_histos["jetsbb"].GetXaxis().SetLabelSize(0.04)
                jet_histos["jetsbb"].Draw("HIST")

                # Draw the rest
                for sample in jetsSamplesToStack:
                    if sample != "jetsbb":
                        jet_histos[sample].Draw("HIST SAME")

                # Draw signal if requested
                if dosignal and signal_histo:
                    signal_histo.Draw("HIST SAME")
                    theLegend.AddEntry(signal_histo, "HH (SM)", "l")

                theLegend.Draw("SAME")

                # ATLAS label
                l = r.TLatex()
                l.SetNDC()
                l.SetTextFont(72)
                l.SetTextSize(0.045)
                l.DrawLatex(0.18, 0.85, "ATLAS")
                l.SetTextFont(42)
                l.DrawLatex(0.30, 0.85, "Internal")
                l.SetTextSize(0.035)
                l.DrawLatex(0.18, 0.80, selectionDict[str(selection)]['legend upper'])
                l.DrawLatex(0.18, 0.75, "Shape comparison (normalized)")
                if btag is not None:
                    btag_symbol = "=" if btag_exact else "#geq"
                    l.DrawLatex(0.18, 0.70, "%s%d b-jets @ %d%% WP" % (btag_symbol, btag, btag_wp))
                elif btag_wp != 85:
                    l.DrawLatex(0.18, 0.70, "%d%% WP b-tagging" % btag_wp)

                if do_ratio:
                    canv.cd()
                    padlow = r.TPad("padlow", "padlow", 0, 0, 1, 0.35)
                    padlow.SetTopMargin(0.02)
                    padlow.SetBottomMargin(0.3)
                    padlow.Draw()
                    padlow.cd()

            if do_ratio:
                ratio_histos = {}
                for sample in jetsSamplesToStack:
                    ratio_histos[sample] = jet_histos[sample].Clone("ratio_" + sample)
                    if jet_histos["jetsbb"].Integral() > 0:
                        ratio_histos[sample].Divide(jet_histos["jetsbb"])
                    ratio_histos[sample].SetLineColor(colors.GetColor(*sampleDict[sample]['color']))
                    ratio_histos[sample].SetMarkerColor(colors.GetColor(*sampleDict[sample]['color']))
                    ratio_histos[sample].SetMarkerStyle(20)
                    ratio_histos[sample].SetMarkerSize(0.8)
                    ratio_histos[sample].SetLineWidth(2)

                if do_fit:
                    _fit_ranges = {"bbyy_myy_NOSYS": (105, 160)}
                    xaxis_min, xaxis_max = _fit_ranges.get(histo_name, (histoDict[histo_name]['x-min'], histoDict[histo_name]['x-max']))
                else:
                    xaxis_min, xaxis_max = histoDict[histo_name]['x-min'], histoDict[histo_name]['x-max']

                # mjj ratio can have large deviations so auto-scale; others use fixed ±30%
                if histo_name == "recojet_mjj_NOSYS":
                    _rmin, _rmax = float('inf'), float('-inf')
                    for _s in jetsSamplesToStack:
                        _h = ratio_histos[_s]
                        for _b in range(1, _h.GetNbinsX() + 1):
                            _v = _h.GetBinContent(_b)
                            if _v > 0:
                                _rmin = min(_rmin, _v)
                                _rmax = max(_rmax, _v)
                    if _rmin == float('inf') or _rmin == _rmax:
                        _rmin, _rmax = 0.0, 2.0
                    _pad = 0.15 * (_rmax - _rmin)
                    ratio_y_lo = max(0.0, _rmin - _pad)
                    ratio_y_hi = _rmax + _pad
                else:
                    ratio_y_lo, ratio_y_hi = 0.7, 1.3

                # Configure ratio plot styling based on whether it's full canvas or lower pad
                if fitRatio and not draw_shapes:
                    ratio_histos["jetsbb"].GetYaxis().SetTitle("Ratio to bb")
                    ratio_histos["jetsbb"].GetYaxis().SetTitleOffset(1.0)
                    ratio_histos["jetsbb"].GetYaxis().SetTitleSize(0.05)
                    ratio_histos["jetsbb"].GetYaxis().SetLabelSize(0.04)
                    ratio_histos["jetsbb"].GetYaxis().CenterTitle()
                    ratio_histos["jetsbb"].GetYaxis().SetRangeUser(ratio_y_lo, ratio_y_hi)
                    ratio_histos["jetsbb"].GetXaxis().SetTitle(histoDict[str(histo_name)]['x-axis title'])
                    ratio_histos["jetsbb"].GetXaxis().SetTitleSize(0.05)
                    ratio_histos["jetsbb"].GetXaxis().SetTitleOffset(1.0)
                    ratio_histos["jetsbb"].GetXaxis().SetLabelSize(0.04)
                    ratio_histos["jetsbb"].GetXaxis().SetRangeUser(xaxis_min, xaxis_max)
                else:
                    ratio_histos["jetsbb"].GetYaxis().SetTitle("Ratio to bb")
                    ratio_histos["jetsbb"].GetYaxis().SetTitleOffset(0.5)
                    ratio_histos["jetsbb"].GetYaxis().SetTitleSize(0.08)
                    ratio_histos["jetsbb"].GetYaxis().SetLabelSize(0.08)
                    ratio_histos["jetsbb"].GetYaxis().CenterTitle()
                    ratio_histos["jetsbb"].GetYaxis().SetRangeUser(ratio_y_lo, ratio_y_hi)
                    ratio_histos["jetsbb"].GetXaxis().SetTitle(histoDict[str(histo_name)]['x-axis title'])
                    ratio_histos["jetsbb"].GetXaxis().SetTitleSize(0.1)
                    ratio_histos["jetsbb"].GetXaxis().SetTitleOffset(1.0)
                    ratio_histos["jetsbb"].GetXaxis().SetLabelSize(0.08)
                    ratio_histos["jetsbb"].GetXaxis().SetRangeUser(xaxis_min, xaxis_max)

                try:
                    r.gPad.SetClipToFrame(True)
                except AttributeError:
                    pass
                draw_err = "E" if errorFit else "HIST"
                ratio_histos["jetsbb"].Draw(draw_err)

                line = r.TLine(xaxis_min, 1, xaxis_max, 1)
                line.SetLineColor(r.kBlack)
                line.SetLineStyle(2)
                line.SetLineWidth(2)
                line.Draw("SAME")

                for sample in jetsSamplesToStack:
                    if sample != "jetsbb":
                        ratio_histos[sample].Draw(draw_err + " SAME")

                fit_results = {}
                if do_fit:
                    fit_legend = r.TLegend(0.55, 0.65, 0.88, 0.88)
                    fit_legend.SetBorderSize(0)
                    fit_legend.SetFillStyle(0)
                    fit_legend.SetTextSize(0.035)
                    for sample in jetsSamplesToStack:
                        if sample != "jetsbb":
                            fit_func = r.TF1("fit_" + sample, "pol1", xaxis_min, xaxis_max)
                            fit_func.SetLineColor(colors.GetColor(*sampleDict[sample]['color']))
                            fit_func.SetLineStyle(2)
                            fit_func.SetLineWidth(2)
                            ratio_histos[sample].Fit(fit_func, "QNR")
                            fit_func.Draw("SAME")
                            if errorFit:
                                p0 = fit_func.GetParameter(0)
                                p1 = fit_func.GetParameter(1)
                                p1_err = fit_func.GetParError(1)
                                fit_results[sample] = (p0, p1, p1_err)
                                fit_legend.AddEntry(fit_func, "%s: slope=%.4f#pm%.4f" % (sampleDict[sample]['legend description'], p1, p1_err), "l")
                            else:
                                fit_legend.AddEntry(fit_func, sampleDict[sample]['legend description'], "l")
                    fit_legend.Draw("SAME")

                if fitRatio:
                    l = r.TLatex()
                    l.SetNDC()
                    l.SetTextFont(72)
                    l.SetTextSize(0.04)
                    l.DrawLatex(0.18, 0.85, "ATLAS")
                    l.SetTextFont(42)
                    l.DrawLatex(0.28, 0.85, "Internal")
                    l.SetTextSize(0.03)
                    l.DrawLatex(0.18, 0.80, selectionDict[str(selection)]['legend upper'])
                    l.DrawLatex(0.18, 0.75, "Ratio to bb (pol1 fits)" if do_fit else "Ratio to bb")
                    if btag is not None:
                        btag_symbol = "=" if btag_exact else "#geq"
                        l.DrawLatex(0.18, 0.70, "%s%d b-jets @ %d%% WP" % (btag_symbol, btag, btag_wp))

            # Save with appropriate suffix
            suffix = ""
            if rebin:
                suffix += "_rebinned"
            if fitRatio and do_ratio:
                if do_fit:
                    suffix += "_withFitError" if errorFit else "_withFit"
                else:
                    suffix += "_withRatio"
            if btag is not None:
                btag_prefix = "exact" if btag_exact else "geq"
                suffix += "_btag%d_%s%db" % (btag_wp, btag_prefix, btag)
            elif btag_wp != 85:
                suffix += "_btag%d" % btag_wp
            short_name = {"bbyy_myy_NOSYS": "myy", "recojet_mjj_NOSYS": "mjj",
                          "deltaR_yy": "dR_yy", "deltaR_jj": "dR_jj",
                          "bbyy_mbbyy_NOSYS": "myyjj"}.get(histo_name, histo_name)
            outname = outputPath + "/" + short_name + "_" + selection + suffix
            print("Saving: ", outname + ".png")
            canv.SaveAs(outname + ".png", "png")
            r.SetOwnership(canv, False)
            canv.Close()


#### DEBUG: sanity check that a WP cut gives b-rich events
def debug_btag_wp(inputPath="", btag_wp=65, n_events=10):
    # prints truth labels + PCBT bins for first n_events passing >=2b at the chosen WP
    folder_name = analysis_folder.replace("RUN", "Run2")
    input_extended = os.path.join(inputPath, f"ntuples_{version}/{folder_name}/")

    pcbt_bin = PCBT_WP_BINS.get(btag_wp, PCBT_WP_BINS[85])
    print()
    print("[debug_btag_wp] =====================================================")
    print("[debug_btag_wp] WP=%d%%  pcbt_bin>=%d  cut: both jets >= bin" % (btag_wp, pcbt_bin))
    print("[debug_btag_wp] Printing first %d events that pass the cut" % n_events)
    print("[debug_btag_wp] =====================================================")

    # Locate a yy+jets MC file (Run2, prefer mc20a)
    try:
        all_files = os.listdir(input_extended)
    except OSError:
        print("[debug_btag_wp] ERROR: cannot list directory:", input_extended)
        return

    rootfile = None
    for campaign in ["mc20a", "mc20d", "mc20e"]:
        for f in all_files:
            if ("yyjets" in f) and (campaign in f) and f.endswith(".root"):
                rootfile = os.path.join(input_extended, f)
                break
        if rootfile:
            break

    if rootfile is None:
        # Fall back to any MC root file
        for f in all_files:
            if f.endswith(".root") and "data" not in f:
                rootfile = os.path.join(input_extended, f)
                break

    if rootfile is None:
        print("[debug_btag_wp] ERROR: no MC root file found in:", input_extended)
        return

    print("[debug_btag_wp] File:", rootfile)
    tfile = r.TFile.Open(rootfile, "r")
    if not tfile or tfile.IsZombie():
        print("[debug_btag_wp] ERROR: could not open file")
        return

    tree = tfile.Get("AnalysisMiniTree")
    if not tree:
        print("[debug_btag_wp] ERROR: AnalysisMiniTree not found")
        tfile.Close()
        return

    hdr = "%-8s  %-14s  %-14s  %-10s  %-10s"
    print("[debug_btag_wp] " + hdr % ("Entry", "Jet1_truthLabel", "Jet2_truthLabel", "Jet1_pcbt", "Jet2_pcbt"))
    print("[debug_btag_wp] " + "-" * 65)

    n_printed = 0
    max_scan = min(int(tree.GetEntries()), 500000)
    for i in range(max_scan):
        tree.GetEntry(i)

        try:
            s1 = int(tree.bbyy_Jet1_pcbt_NOSYS)
            s2 = int(tree.bbyy_Jet2_pcbt_NOSYS)
        except AttributeError:
            avail = [b.GetName() for b in tree.GetListOfBranches() if "pcbt" in b.GetName().lower() or "Jet1" in b.GetName() or "Jet2" in b.GetName()]
            print("[debug_btag_wp] ERROR: bbyy_Jet1/2_pcbt_NOSYS branches not found!")
            print("[debug_btag_wp] Candidate branches:", avail)
            break

        if not (s1 >= pcbt_bin and s2 >= pcbt_bin):
            continue

        try:
            lbl1 = int(tree.bbyy_Jet1_truthLabel_NOSYS)
            lbl2 = int(tree.bbyy_Jet2_truthLabel_NOSYS)
        except (AttributeError, Exception):
            lbl1 = lbl2 = -999

        print("[debug_btag_wp] " + hdr % (i, lbl1, lbl2, s1, s2))
        n_printed += 1
        if n_printed >= n_events:
            break

    tfile.Close()
    print("[debug_btag_wp] =====================================================")
    print("[debug_btag_wp] If Jet1/Jet2 labels are dominated by 5 -> WP is working.")
    print("[debug_btag_wp] Labels: b=5, c=4, light/gluon=0 (HadronConeExcl scheme)")
    print("[debug_btag_wp] =====================================================")
    print()


if __name__ == "__main__":

    # Adding an argument parser, which we might want to use
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-m", "--mcOnly", help="", action="store_true", default=False)
    parser.add_argument("-r", "--include_ratio", help="", action="store_true", default=False)
    parser.add_argument("-s", "--dosignal", help="", action="store_true", default=False)
    parser.add_argument("-l", "--logOn", help="", action="store_true", default=False)
    parser.add_argument("-i", "--inputPath", help="Path to the input directory.",default="/eos/atlas/atlascerngroupdisk/phys-higp/higgs-pairs/Run3/yybb/")
    parser.add_argument("-o", "--outputPath", help="Path to the output directory.",default="./outputs/")
    parser.add_argument("-UB", "--UNBLIND", help="",action="store_true",default=False)
    parser.add_argument("--shapeComparison", help="Run shape comparison plots", action="store_true", default=False)
    parser.add_argument("--rebin", help="Rebin shape comparison histograms by factor 2 (x2 fewer bins)", action="store_true", default=False)
    parser.add_argument("--fitRatio", help="Fit pol1 to ratio plots in shape comparison; restricts x range to 100-160 GeV (myy) / 100-240 GeV (mjj)", action="store_true", default=False)
    parser.add_argument("--errorFit", help="When used with --fitRatio, draw error bars on ratio bins and show slope+/-error in legend", action="store_true", default=False)
    parser.add_argument("--btag", help="Require >=n b-tagged jets at the chosen WP (see --btag_wp)", type=int, default=None)
    parser.add_argument("--btag_exact", help="Require exactly n b-tagged jets at the chosen WP (==n)", type=int, default=None)
    parser.add_argument("--btag_wp", help="b-tagging working point efficiency in %% (65, 70, 77, 85, or 90). Default is 85.", type=int, choices=[65, 70, 77, 85, 90], default=85)
    parser.add_argument("--debug_btag_wp", help="Print jet truth-label IDs for the first N events passing >=2 b-jets at --btag_wp (default 65%%) to verify the WP selection is b-rich. Exits after printing.", type=int, metavar="N", default=None)
    parser.add_argument("--unweighted", help="Fill histograms with raw event counts (no weight_total_NOSYS or btagSF applied to MC)", action="store_true", default=False)

    options = parser.parse_args()

    if options.btag_exact is not None:
        btag_value = options.btag_exact
        btag_is_exact = True
    elif options.btag is not None:
        btag_value = options.btag
        btag_is_exact = False
    else:
        btag_value = None
        btag_is_exact = False

    inDir = options.inputPath
    outDir = options.outputPath
    if not os.path.exists(outDir):
        os.makedirs(outDir)
        print("The output directory did not exist, I have just created one: ", outDir)

    # filter out shape-only flags before passing to main1D
    shape_only_keys = {"shapeComparison", "rebin", "fitRatio", "errorFit", "btag", "btag_exact", "btag_wp"}
    option_dict = {k: v for k, v in vars(options).items() if (v is not None) and (k not in shape_only_keys)}
    option_dict["btag"] = btag_value
    option_dict["btag_exact"] = btag_is_exact
    option_dict["btag_wp"] = options.btag_wp

    if options.debug_btag_wp is not None:
        debug_btag_wp(inputPath=options.inputPath, btag_wp=options.btag_wp, n_events=options.debug_btag_wp)
    elif options.shapeComparison:
        mainShapeComparison(inputPath=options.inputPath, outputPath=options.outputPath, dosignal=options.dosignal,
                           rebin=options.rebin, fitRatio=options.fitRatio, errorFit=options.errorFit,
                           btag=btag_value, btag_exact=btag_is_exact, btag_wp=options.btag_wp)
    else:
        main1D(**option_dict)
