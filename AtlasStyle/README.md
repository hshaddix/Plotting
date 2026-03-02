# ATLAS Root style

The atlasrootstyle repository contains ROOT macro recommendations intended to help the ATLAS physicists who are producing presentations, notes and papers to establish a uniform style for figures. More information is available [on the Pub Com Plot Style twiki](https://twiki.cern.ch/twiki/bin/view/AtlasProtected/PubComPlotStyle).

## ATLAS Style Setup

To setup this file on the command line:

```bash
# Set up ATLASsetup
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source $ATLAS_LOCAL_ROOT_BASE/user/atlasLocalSetup.sh
# Set up this style package
lsetup astyle
```

## Python usage

The setup via lsetup will provide you access to the python modules immediately, e.g.:

```python
import AtlasStyle
```

will work within python.

### C++ usage

The setup via lsetup will provide you with access to the header files immediately, e.g.:

```cpp
#include "AtlasStyle.C"
```

### ROOT login setup

You can add `rootlogon.C` to your working directory to load the ATLAS style automatically
when you start ROOT.

Alternatively, you can add the contents of `dot.rootrc` to the `.rootrc` file in your
home directory to have the ATLAS style automatically loaded when you launch ROOT from
any location. More details on this are given below.

## Package contents

This package contains the following files:

- `AtlasStyle.C`: it contains the actual style definition. You can call it
  from any macro after setup by including or importing it in your macro
  and then invoking the style function with:

```cpp
SetAtlasStyle();
```

- `AtlasStyle.py`: example of python wrapper for `AtlasStyle.C`, in case
  you prefer to use pyROOT.

- `rootlogon.C`: automatically loads the ATLAS style. Put in your
  working directory together with `StyleAtlas.C`, and you'll get the
  ATLAS style loaded by default any time you launch ROOT in that
  directory.

- `dot.rootrc`: this is an example of the `.rootrc` file you could put in
  you home directory to get the ATLAS style loaded any time you launch
  ROOT from any location, without having to copy the style file
  around. It contains the following lines:

```bash
  Unix.*.Root.DynamicPath:    .:$(ROOTSYS)/lib:$(HOME)/RootUtils/lib:
```

  This one tells ROOT where to look for libraries. It points to the
  current directory (`.`), the standard ROOT library location
  (`$(ROOTSYS)/lib`), and a custom location (`$(HOME)/RootUtils/lib`) that
  you should change to fit your needs.

```bash
  Unix.*.Root.MacroPath:      .:$(HOME)/RootUtils:
```

  This one tells root where to look for macros. It points to the
  current directory (`.`) and to a custom location (`$(HOME)/RootUtils`)
  that you should change to fit your needs.

  `$(HOME)/RootUtils` (or whatever is the name of your custom macro
  repository) is where you should put both your `rootlogon.C` and
  `StyleAtlas.C` files in order to get the ATLAS style loaded by
  default without copying them around. You can also use the cvmfs area
  directly, from `/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/astyle`,
  without setting up `astyle` first.

- `AtlasUtils.C` and `AtlasLabels.C`: useful utility packages, containing several function
  definitions, like the one to generate the ATLAS label. You can load
  them by including the following lines near the top of your macro:

```cpp
  #include "AtlasUtils.C"
  #include "AtlasLabels.C"
```

  The files follow the same rules as AtlasStyle above for include/import.

- `AtlasUtils.py`: example of python wrapper for `AtlasUtils.C`, in case
  you prefer to use pyROOT.

- `AtlasLabels.py`: example of python wrapper for `AtlasLabels.C`, in case
  you prefer to use pyROOT.

- `AtlasExample.C` and `nlofiles.root` will produce an example plot. Just copy
  them in the directory with all the other style and utility files,
  and execute the macro. Enter root and do:

```cpp
  .x AtlasExample.C
```

  If you setup your `.rootrc` file and your custom macro repository, in
  order to produce the example plots (`AtlasExample.eps`,
  `AtlasExample.png`, `AtlasExample.pdf`) you will just need `AtlasExample.C` and
  `nlofiles.root`.

## Updates

For any updates, place a tarball on lxplus and email <atlas-adc-tier3sw-install@cern.ch>.
