''' 
  A python directory summarising the plotting properties
  of each histogram produced for the final plots

  L. Santi, 2025 <l.santi@cern.ch>
'''


import ROOT as r 


def SampleDict():
    dict = {
        'ggFHHbbyy':
        {
            'histoname': 'HH',
            'color': (242, 56, 90),
            'legend description': 'HH (SM)'
        },
        'VBFHHbbyy':
        {
            'histoname': 'HH',
            'color': (242, 56, 90),
            'legend description': 'HH (SM)'
        },
        'ggFHyy':
        {
            'histoname': 'Hyy',
            'color': (253, 197, 54),
            'legend description': 'Single H'
        },
        'VBFHyy':
        {
            'histoname': 'Hyy',
            'color': (253, 197, 54),
            'legend description': 'Single H'
        },
        'W+Hyy':
        {
            'histoname': 'Hyy',
            'color': (253, 197, 54),
            'legend description': 'Single H'
        },
        'W-Hyy':
        {
            'histoname': 'Hyy',
            'color': (253, 197, 54),
            'legend description': 'Single H'
        },
        'qqZHyy':
        {
            'histoname': 'Hyy',
            'color': (253, 197, 54),
            'legend description': 'Single H'
        },
        'ggZHyy':
        {
            'histoname': 'Hyy',
            'color': (253, 197, 54),
            'legend description': 'Single H'
        },
        'ttHyy':
        {
            'histoname': 'Hyy',
            'color': (253, 197, 54),
            'legend description': 'Single H'
        },
        'tWHyy':
        {
            'histoname': 'Hyy',
            'color': (253, 197, 54),
            'legend description': 'Single H'
        },
        'tHjb':
        {
            'histoname': 'Hyy',
            'color': (253, 197, 54),
            'legend description': 'Single H'
        },
        'bbHyy':
        {
            'histoname': 'Hyy',
            'color': (253, 197, 54),
            'legend description': 'Single H'
        },
        'ttyy_allhad':
        {
            'histoname': 'ttyy', 
            'color': (53, 56, 67),
            'legend description': '#it{tt#gamma#gamma}',
        },
        'ttyy_nonallhad':
        {
            'histoname': 'ttyy',
            'color': (53, 56, 67),
            'legend description': '#it{tt#gamma#gamma}',
        },
        'yy+jets':
        {
            'histoname': 'yy+jets',
            'color': (117, 214, 216),
            'legend description': '#it{#gamma#gamma+others}',
        },
        'yy+jetsbb':
        {
            'histoname': 'yy+jetsbb',
            'color': (117, 214, 216),
            'legend description': '#it{#gamma#gamma+b#bar{b}}',
            'extracut': '(bbyy_Jet1_truthLabel_NOSYS==5 && bbyy_Jet2_truthLabel_NOSYS==5)'
        },
        'yy+jetsbj':
        {
            'histoname': 'yy+jetsbj',
            'color': (194, 126, 224),
            'legend description': '#it{#gamma#gamma+bj}',
            'extracut': '((bbyy_Jet1_truthLabel_NOSYS == 5 && bbyy_Jet2_truthLabel_NOSYS != 5) || (bbyy_Jet1_truthLabel_NOSYS != 5 && bbyy_Jet2_truthLabel_NOSYS == 5))'
        },
        'yy+jetsjj':
        {
            'histoname': 'yy+jetsjj',
            'color': (93, 175, 188),
            'legend description': '#it{#gamma#gamma+jj}',
            'extracut': '(bbyy_Jet1_truthLabel_NOSYS != 5 && bbyy_Jet2_truthLabel_NOSYS != 5)'
        },

# jet flavor breakdown; bbyy_Jet1/2_truthLabel_NOSYS: b=5, c=4, light/gluon=0
# jets sorted by PCBT score (highest first)
'jetsbb':
{
    'histoname': 'jetsbb',
    'color': (0, 0, 0),
    'legend description': 'bb',
    'extracut': '(bbyy_Jet1_truthLabel_NOSYS==5 && bbyy_Jet2_truthLabel_NOSYS==5)'
},


'jetsbc':
{
    'histoname': 'jetsbc',
    'color': (230, 159, 0),
    'legend description': 'bc',
    'extracut': '((bbyy_Jet1_truthLabel_NOSYS==5 && bbyy_Jet2_truthLabel_NOSYS==4) || (bbyy_Jet1_truthLabel_NOSYS==4 && bbyy_Jet2_truthLabel_NOSYS==5))'
},


'jetscc':
{
    'histoname': 'jetscc',
    'color': (0, 114, 178),
    'legend description': 'cc',
    'extracut': '(bbyy_Jet1_truthLabel_NOSYS==4 && bbyy_Jet2_truthLabel_NOSYS==4)'
},


'jetsbl':
{
    'histoname': 'jetsbl',
    'color': (0, 158, 115),
    'legend description': 'bl',
    'extracut': '((bbyy_Jet1_truthLabel_NOSYS==5 && bbyy_Jet2_truthLabel_NOSYS!=5 && bbyy_Jet2_truthLabel_NOSYS!=4) || (bbyy_Jet2_truthLabel_NOSYS==5 && bbyy_Jet1_truthLabel_NOSYS!=5 && bbyy_Jet1_truthLabel_NOSYS!=4))'
},


'jetscl':
{
    'histoname': 'jetscl',
    'color': (204, 121, 167),
    'legend description': 'cl',
    'extracut': '((bbyy_Jet1_truthLabel_NOSYS==4 && bbyy_Jet2_truthLabel_NOSYS!=5 && bbyy_Jet2_truthLabel_NOSYS!=4) || (bbyy_Jet2_truthLabel_NOSYS==4 && bbyy_Jet1_truthLabel_NOSYS!=5 && bbyy_Jet1_truthLabel_NOSYS!=4))'
},


'jetsll':
{
    'histoname': 'jetsll',
    'color': (136, 136, 136),
    'legend description': 'll',
    'extracut': '(bbyy_Jet1_truthLabel_NOSYS!=5 && bbyy_Jet1_truthLabel_NOSYS!=4 && bbyy_Jet2_truthLabel_NOSYS!=5 && bbyy_Jet2_truthLabel_NOSYS!=4)'
},

    }
    return dict
def PlottingDict():
    dict = {
        'bbyy_myy_NOSYS': { # Name of histogram as defined the PlottingList.py
            'x-axis title': '#it{m}_{#gamma#gamma} [GeV]',
            'units' : 'GeV',
            'x-min' : 105,
            'x-max' : 160,
            'nBins' : 11,
            'toGeV' : True
        },
        "bbyy_Jet1_eta_NOSYS": {
            'x-axis title': '#eta_{Jet1}',
            'units' : '',
            'x-min' : -4,
            'x-max' : 4,
            'nBins' : 25,
            'toGeV' : False
        },
        "bbyy_Jet2_eta_NOSYS": {
            'x-axis title': '#eta_{Jet2}',
            'units' : '',
            'x-min' : -4,
            'x-max' : 4,
            'nBins' : 25,
            'toGeV' : False
        },
        "bbyy_Jet3_eta_NOSYS": {
            'x-axis title': '#eta_{Jet3}',
            'units' : '',
            'x-min' : -4,
            'x-max' : 4,
            'nBins' : 25,
            'toGeV' : False
        },
        "bbyy_Jet4_eta_NOSYS": {
            'x-axis title': '#eta_{Jet4}',
            'units' : '',
            'x-min' : -4,
            'x-max' : 4,
            'nBins' : 25,
            'toGeV' : False
        },
        'bbyy_mbb_NOSYS': { 
            'x-axis title': '#it{m_{bb}} [GeV]',
            'units' : 'GeV',
            'x-min' : 0,
            'x-max' : 300,
            'nBins' : 30,
            'toGeV' : True
        }
    
,
'recojet_mjj_NOSYS': {
    'x-axis title': '#it{m_{jj}} [GeV]',
    'units' : 'GeV',
    'x-min' : 0,
    'x-max' : 500,
    'nBins' : 25,
    'toGeV' : True,
    'variable': '(TMath::Sqrt(2*bbyy_Jet1_pt_NOSYS*bbyy_Jet2_pt_NOSYS*(TMath::CosH(bbyy_Jet1_eta_NOSYS-bbyy_Jet2_eta_NOSYS)-TMath::Cos(bbyy_Jet1_phi_NOSYS-bbyy_Jet2_phi_NOSYS))))'
},
'deltaR_yy': {
    'x-axis title': '#Delta#it{R}_{#gamma#gamma}',
    'units' : '',
    'x-min' : 0,
    'x-max' : 5,
    'nBins' : 30,
    'toGeV' : False,
    'variable': '(TMath::Sqrt(pow(bbyy_Photon1_eta_NOSYS-bbyy_Photon2_eta_NOSYS,2)+pow(TMath::Min(TMath::Abs(bbyy_Photon1_phi_NOSYS-bbyy_Photon2_phi_NOSYS),2*TMath::Pi()-TMath::Abs(bbyy_Photon1_phi_NOSYS-bbyy_Photon2_phi_NOSYS)),2)))'
},
'deltaR_jj': {
    'x-axis title': '#Delta#it{R}_{jj}',
    'units' : '',
    'x-min' : 0,
    'x-max' : 5,
    'nBins' : 30,
    'toGeV' : False,
    'variable': '(TMath::Sqrt(pow(recojet_antikt4PFlow_eta_NOSYS[0]-recojet_antikt4PFlow_eta_NOSYS[1],2)+pow(TMath::Min(TMath::Abs(recojet_antikt4PFlow_phi_NOSYS[0]-recojet_antikt4PFlow_phi_NOSYS[1]),2*TMath::Pi()-TMath::Abs(recojet_antikt4PFlow_phi_NOSYS[0]-recojet_antikt4PFlow_phi_NOSYS[1])),2)))'
},
'bbyy_mbbyy_NOSYS': {
    'x-axis title': '#it{m_{yyjj}} [GeV]',
    'units' : 'GeV',
    'x-min' : 200,
    'x-max' : 1000,
    'nBins' : 15,
    'toGeV' : True
}
}
    return dict

def SignalDict():
    dict = {
        'HH': {
            'legend description': 'HH (SM)',
            'color': (227, 73, 102),
            'multiplier': 50
        },
        #'ZH': {
        #    'legend description': 'ZH(b#bar{b}#gamma#gamma)',
        #    'color': (20, 100, 150),
        #    'multiplier': 20
        #}
    }
    return dict

def SelectionDict():
    dict = {
        'Run2_preselection': {
            'legend upper': 'Run 2 pre-selection',
            'legend lower': '',
            'sfs': { "yy+jetsbb": 1.7906, "yy+jetsbj": 1.7906, "yy+jetsjj": 1.7906,
                     "jetsbb": 1.7906, "jetsbc": 1.7906, "jetscc": 1.7906, "jetsbl": 1.7906, "jetscl": 1.7906, "jetsll": 1.7906}
        },
        'Run2_preselection_HM': {
            'legend upper': 'Run 2 pre-selection',
            'legend lower': 'm_{HH}>350 GeV',
            'sfs': { "yy+jetsbb": 1.7906, "yy+jetsbj": 1.7906, "yy+jetsjj": 1.7906,
                     "jetsbb": 1.7906, "jetsbc": 1.7906, "jetscc": 1.7906, "jetsbl": 1.7906, "jetscl": 1.7906, "jetsll": 1.7906},
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS <= 3)']
        },
        'Run2_preselection_LM': {
            'legend upper': 'Run 2 pre-selection',
            'legend lower': 'm_{HH}<350 GeV',
            'sfs': { "yy+jetsbb": 1.7906, "yy+jetsbj": 1.7906, "yy+jetsjj": 1.7906,
                     "jetsbb": 1.7906, "jetsbc": 1.7906, "jetscc": 1.7906, "jetsbl": 1.7906, "jetscl": 1.7906, "jetsll": 1.7906},
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS >= 1000)']
        },
        'Run2_HM0': {
            'legend upper': 'Run 2 HM 0',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==0)'],
            'sfs': { "yy+jetsbb": 1.7906, "yy+jetsbj": 1.7906, "yy+jetsjj": 1.7906,
                     "jetsbb": 1.7906, "jetsbc": 1.7906, "jetscc": 1.7906, "jetsbl": 1.7906, "jetscl": 1.7906, "jetsll": 1.7906}
        },
        'Run2_HM1': {
            'legend upper': 'Run 2 HM 1',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==1)'],
            'sfs': { "yy+jetsbb": 1.7906, "yy+jetsbj": 1.7906, "yy+jetsjj": 1.7906,
                     "jetsbb": 1.7906, "jetsbc": 1.7906, "jetscc": 1.7906, "jetsbl": 1.7906, "jetscl": 1.7906, "jetsll": 1.7906}
        },
        'Run2_HM2': {
            'legend upper': 'Run 2 HM 2',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==2)'],
            'sfs': { "yy+jetsbb": 1.7906, "yy+jetsbj": 1.7906, "yy+jetsjj": 1.7906,
                     "jetsbb": 1.7906, "jetsbc": 1.7906, "jetscc": 1.7906, "jetsbl": 1.7906, "jetscl": 1.7906, "jetsll": 1.7906}
        },
        'Run2_HM3': {
            'legend upper': 'Run 2 HM 3',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==3)'],
            'sfs': { "yy+jetsbb": 1.7906, "yy+jetsbj": 1.7906, "yy+jetsjj": 1.7906,
                     "jetsbb": 1.7906, "jetsbc": 1.7906, "jetscc": 1.7906, "jetsbl": 1.7906, "jetscl": 1.7906, "jetsll": 1.7906}
        },
        'Run2_LM0': {
            'legend upper': 'Run 2 LM 0',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==1000)'],
            'sfs': { "yy+jetsbb": 1.7906, "yy+jetsbj": 1.7906, "yy+jetsjj": 1.7906,
                     "jetsbb": 1.7906, "jetsbc": 1.7906, "jetscc": 1.7906, "jetsbl": 1.7906, "jetscl": 1.7906, "jetsll": 1.7906}
        },
        'Run2_LM1': {
            'legend upper': 'Run 2 LM 1',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==1001)'],
            'sfs': { "yy+jetsbb": 1.7906, "yy+jetsbj": 1.7906, "yy+jetsjj": 1.7906,
                     "jetsbb": 1.7906, "jetsbc": 1.7906, "jetscc": 1.7906, "jetsbl": 1.7906, "jetscl": 1.7906, "jetsll": 1.7906}
        },
        'Run2_LM2': {
            'legend upper': 'Run 2 LM 2',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==1002)'],
            'sfs': { "yy+jetsbb": 1.7906, "yy+jetsbj": 1.7906, "yy+jetsjj": 1.7906,
                     "jetsbb": 1.7906, "jetsbc": 1.7906, "jetscc": 1.7906, "jetsbl": 1.7906, "jetscl": 1.7906, "jetsll": 1.7906}
        },
        'Run2_LM3': {
            'legend upper': 'Run 2 LM 3',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==1003)'],
            'sfs': { "yy+jetsbb": 1.7906, "yy+jetsbj": 1.7906, "yy+jetsjj": 1.7906,
                     "jetsbb": 1.7906, "jetsbc": 1.7906, "jetscc": 1.7906, "jetsbl": 1.7906, "jetscl": 1.7906, "jetsll": 1.7906}
        },
        'Run2_LM4': {
            'legend upper': 'Run 2 LM 4',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==1004)'],
            'sfs': { "yy+jetsbb": 1.7906, "yy+jetsbj": 1.7906, "yy+jetsjj": 1.7906,
                     "jetsbb": 1.7906, "jetsbc": 1.7906, "jetscc": 1.7906, "jetsbl": 1.7906, "jetscl": 1.7906, "jetsll": 1.7906}
        },


        'Run3_preselection': {
            'legend upper': 'Run 3 pre-selection',
            'legend lower': '',
            'sfs': { "yy+jetsbb": 1.4681, "yy+jetsbj": 1.4681, "yy+jetsjj": 1.4681,
                     "jetsbb": 1.4681, "jetsbc": 1.4681, "jetscc": 1.4681, "jetsbl": 1.4681, "jetscl": 1.4681, "jetsll": 1.4681}
        },
        'Run3_preselection_HM': {
            'legend upper': 'Run 3 pre-selection',
            'legend lower': 'm_{HH}>350 GeV',
            'sfs': { "yy+jetsbb": 1.4681, "yy+jetsbj": 1.4681, "yy+jetsjj": 1.4681,
                     "jetsbb": 1.4681, "jetsbc": 1.4681, "jetscc": 1.4681, "jetsbl": 1.4681, "jetscl": 1.4681, "jetsll": 1.4681},
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS <= 3)']
        },
        'Run3_preselection_LM': {
            'legend upper': 'Run 3 pre-selection',
            'legend lower': 'm_{HH}<350 GeV',
            'sfs': { "yy+jetsbb": 1.4681, "yy+jetsbj": 1.4681, "yy+jetsjj": 1.4681,
                     "jetsbb": 1.4681, "jetsbc": 1.4681, "jetscc": 1.4681, "jetsbl": 1.4681, "jetscl": 1.4681, "jetsll": 1.4681},
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS >= 1000)']
        },
        'Run3_HM0': {
            'legend upper': 'Run 3 HM 0',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==0)'],
            'sfs': { "yy+jetsbb": 1.4681, "yy+jetsbj": 1.4681, "yy+jetsjj": 1.4681,
                     "jetsbb": 1.4681, "jetsbc": 1.4681, "jetscc": 1.4681, "jetsbl": 1.4681, "jetscl": 1.4681, "jetsll": 1.4681}
        },
        'Run3_HM1': {
            'legend upper': 'Run 3 HM 1',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==1)'],
            'sfs': { "yy+jetsbb": 1.4681, "yy+jetsbj": 1.4681, "yy+jetsjj": 1.4681,
                     "jetsbb": 1.4681, "jetsbc": 1.4681, "jetscc": 1.4681, "jetsbl": 1.4681, "jetscl": 1.4681, "jetsll": 1.4681}
        },
        'Run3_HM2': {
            'legend upper': 'Run 3 HM 2',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==2)'],
            'sfs': { "yy+jetsbb": 1.4681, "yy+jetsbj": 1.4681, "yy+jetsjj": 1.4681,
                     "jetsbb": 1.4681, "jetsbc": 1.4681, "jetscc": 1.4681, "jetsbl": 1.4681, "jetscl": 1.4681, "jetsll": 1.4681}
        },
        'Run3_HM3': {
            'legend upper': 'Run 3 HM 3',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==3)'],
            'sfs': { "yy+jetsbb": 1.4681, "yy+jetsbj": 1.4681, "yy+jetsjj": 1.4681,
                     "jetsbb": 1.4681, "jetsbc": 1.4681, "jetscc": 1.4681, "jetsbl": 1.4681, "jetscl": 1.4681, "jetsll": 1.4681}
        },
        'Run3_LM0': {
            'legend upper': 'Run 3 LM 0',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==1000)'],
            'sfs': { "yy+jetsbb": 1.4681, "yy+jetsbj": 1.4681, "yy+jetsjj": 1.4681,
                     "jetsbb": 1.4681, "jetsbc": 1.4681, "jetscc": 1.4681, "jetsbl": 1.4681, "jetscl": 1.4681, "jetsll": 1.4681}
        },
        'Run3_LM1': {
            'legend upper': 'Run 3 LM 1',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==1001)'],
            'sfs': { "yy+jetsbb": 1.4681, "yy+jetsbj": 1.4681, "yy+jetsjj": 1.4681,
                     "jetsbb": 1.4681, "jetsbc": 1.4681, "jetscc": 1.4681, "jetsbl": 1.4681, "jetscl": 1.4681, "jetsll": 1.4681}
        },
        'Run3_LM2': {
            'legend upper': 'Run 3 LM 2',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==1002)'],
            'sfs': { "yy+jetsbb": 1.4681, "yy+jetsbj": 1.4681, "yy+jetsjj": 1.4681,
                     "jetsbb": 1.4681, "jetsbc": 1.4681, "jetscc": 1.4681, "jetsbl": 1.4681, "jetscl": 1.4681, "jetsll": 1.4681}
        },
        'Run3_LM3': {
            'legend upper': 'Run 3 LM 3',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==1003)'],
            'sfs': { "yy+jetsbb": 1.4681, "yy+jetsbj": 1.4681, "yy+jetsjj": 1.4681,
                     "jetsbb": 1.4681, "jetsbc": 1.4681, "jetscc": 1.4681, "jetsbl": 1.4681, "jetscl": 1.4681, "jetsll": 1.4681}
        },
        'Run3_LM4': {
            'legend upper': 'Run 3 LM 4',
            'legend lower': '',
            'cuts': ['(bbyy_KF_corr_with2024_bdtSel_category_NOSYS ==1004)'],
            'sfs': { "yy+jetsbb": 1.4681, "yy+jetsbj": 1.4681, "yy+jetsjj": 1.4681,
                     "jetsbb": 1.4681, "jetsbc": 1.4681, "jetscc": 1.4681, "jetsbl": 1.4681, "jetscl": 1.4681, "jetsll": 1.4681}
        },

        'Run2_preselection_sidebands': {
            'legend upper': 'Run 2 pre-selection',
            'legend lower': 'sidebands',
            'sfs': { "yy+jetsbb": 1., "yy+jetsbj": 1., "yy+jetsjj": 1.,
                     "jetsbb": 1., "jetsbc": 1., "jetscc": 1., "jetsbl": 1., "jetscl": 1., "jetsll": 1.},
            'cuts': ['(bbyy_myy_NOSYS < 120e3 || bbyy_myy_NOSYS > 130e3)']
        },
        'Run3_preselection_sidebands': {
            'legend upper': 'Run 3 pre-selection',
            'legend lower': 'sidebands',
            'sfs': { "yy+jetsbb": 1., "yy+jetsbj": 1., "yy+jetsjj": 1.,
                     "jetsbb": 1., "jetsbc": 1., "jetscc": 1., "jetsbl": 1., "jetscl": 1., "jetsll": 1.},
            'cuts': ['(bbyy_myy_NOSYS < 120e3 || bbyy_myy_NOSYS > 130e3)']

        }
    }

    return dict

