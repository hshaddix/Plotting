# bbyy_PlottingTool

```
setupATLAS
lsetup "views LCG_106 x86_64-el9-gcc13-opt"
mkdir outputs
python3 makePlot.py
```
create a '''./outputs''' directory before starting

mkdir outputs

## How to Use it

python3 makePlot.py --options

In PlottingList.py:

- [ ] Specify Variables via histosToPlot (you can define your own)
- [ ] Specify the Selection you want to use via selectionToPlot
- [ ] Select the list of sample to run on via samplesToStack
- [ ] Some maps are defined here

In histoDict.py:

- [ ] PlottingDict: define a plotting dictionary between Variable name and histogram properties: x-axis title, units, x-range, nbins "variable" (root-like variable can be specified here; i.e. (bbyy_Diphoton_myy_NOSYS-125e3)**2 )
- [ ] SelectionDict: map between the selection chosen and the cut list applied (on top of preselection)
- [ ] SampleDict TODO
- [ ] SignalDict TODO

Flags are implemented to run different options:

- [ ] -m / --mcOnly to run on montecarlo only
- [ ] -r / --include_ratio add a ratio panel: if combined with --mcOnly provides the binned significance otherwise the Data/MC ratio
- [ ] -l / --logOn activate the log on y axis
- [ ] -s / --doSignal overlay signal line with a multiplier factor
- [ ] -i / --inputPath
- [ ] -o / --outputPath
- [ ] -UB / --UNBLIND!!!

Added functionality  
- [ ] --btag N to require greater than or equal to N b jets per event
- [ ] --btag_wp N to require a WP efficiency of N (65, 70, 77, 85, 90)
- [ ] --shapeComparison to allow for normalization and by area to compare shapes, not rates
- [ ] --fitRatio to overlay ratio of jet flavor to bb, and applies first order polynomial fit to most plotted variables
- [ ] --errorfit when used with --fitRatio, adds error bars on bins and error margins on the slope parameter from the polynomial fit

## Example Usage
 
Run the standard stack plot, requiring at least 2 b-jets at the 77% WP:
```
python3 makePlot.py --btag 2 --btag_wp 77
```
 
Run shape comparison plots across jet flavors with ratio-to-bb overlays and fit lines:
```
python3 makePlot.py --shapeComparison --fitRatio --errorFit --btag 2 --btag_wp 77
```
 
