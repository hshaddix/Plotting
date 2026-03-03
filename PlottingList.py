signalName = ["HH"] # ["HH", "ZH"]

# VARIABLE (either branch name or custom expression)
histosToPlot = [
    "bbyy_myy_NOSYS",
    #"bbyy_Jet1_eta_NOSYS",
    #"bbyy_Jet2_eta_NOSYS",
    #"bbyy_Jet3_eta_NOSYS",
    #"bbyy_Jet4_eta_NOSYS",
    "bbyy_mbb_NOSYS",
    "recojet_mjj_NOSYS",
    "deltaR_yy",
    "deltaR_jj",
    "bbyy_mbbyy_NOSYS",
    #"HH_mbb_myy_discriminant"
    #"ZH_mbb_myy_discriminant",
    #"bbyy_mbbyy_star_NOSYS",
    #"bbyy_HbbCandidate_Jet1_pt_NOSYS",
    #"bbyy_HbbCandidate_Jet2_pt_NOSYS",
]

# SELECTION
selectionToPlot = [
    "Run2_preselection",
    #"Run2_preselection_HM",
    #"Run2_preselection_LM",
    #"Run2_HM0",
    #"Run2_LM0",
    #"Run3_HM0",
    #"Run3_LM0",
    #"Run2_HM1",
    #"Run2_HM2",
    #"Run2_HM3",
    #"Run2_LM1",
    #"Run2_LM2",
    #"Run2_LM3",
    #"Run2_LM4",
    "Run3_preselection",
    #"Run3_preselection_HM",
    #"Run3_preselection_LM",
    #"Run3_HM1",
    #"Run3_HM2",
    #"Run3_HM3",
    #"Run3_LM1",
    #"Run3_LM2",
    #"Run3_LM3",
    #"Run3_LM4",

    #"Run2_preselection_sidebands",
    #"Run3_preselection_sidebands",
]

# SAMPLES
samplesToStack = [
    #yy+jets
    "yy+jetsjj",
    "yy+jetsbj",
    "yy+jetsbb",
    #"ttyy_allhad",
    #"ttyy_nonallhad",
    #single higgs
    "ggFHyy",
    "VBFHyy",
    "W+Hyy",
    "W-Hyy",
    "ttHyy",
    "tWHyy",
    "tHjb",
    "bbHyy",
    #ZH
    "qqZHyy",
    "ggZHyy",
    #HH
    "ggFHHbbyy",
    "VBFHHbbyy",
]


# jet flavor breakdown (bb, bc, bl, cc, cl, ll) for shape comparisons
jetsSamplesToStack = [
    "jetsbb",
    "jetsbc",
    "jetscc",
    "jetsbl",
    "jetscl",
    "jetsll",
]
# SAMPLES map to dataset name in common folder
sample_map = {
    "data": "data_0_data15_data.root",
    # HH
    "ggFHHbbyy": "ggFHHbbyy_kl1_6",
    "VBFHHbbyy": "VBFHHbbyy_l1cvv1cv1_5",
    
    # H
    "ggFHyy": "ggFHyy",
    "VBFHyy": "VBFHyy",
    "W+Hyy": "WpHyy",
    "W-Hyy": "WmHyy",
    "qqZHyy": "qqZHyy",
    "ggZHyy": "ggFHyy",
    "bbHyy": "bbHyy",
    "ttHyy": "ttHyy",
    "tWHyy": "tWHyy",
    "tHjb": "tHjb",
    # continuous
    "ttyy_allhad": "ttyy_allhad",
    "ttyy_nonallhad": "ttyy_nonallhad",
    "yy+jets": "yyjets",
    "yy+jetsbb": "yyjets",
    "yy+jetsbj": "yyjets",
    "yy+jetsjj": "yyjets",
    }

for s in ["jetsbb","jetsbc","jetscc","jetsbl","jetscl","jetsll"]:
    sample_map[s] = sample_map["yy+jets"]


