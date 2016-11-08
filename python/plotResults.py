import numpy as np
import os.path
import json, re, argparse, sys
import matplotlib as mpl
import matplotlib.pyplot as plt
from js.utils.plot.colors import colorScheme

mpl.rc('font',size=30) 
mpl.rc('lines',linewidth=3.)
figSize = (14, 5.5)
figSize = (14, 10)
figSize = (12, 8)
figSize = (20, 8)
c1 = colorScheme("labelMap")["turquoise"]
c2 = colorScheme("labelMap")["orange"]
c3 = colorScheme("labelMap")["red"]

parser = argparse.ArgumentParser(description = 'plot results from results.json files generated by randomRenderAndCompare.py')
parser.add_argument('-i','--input',
    default="/data/vision/fisher/expres1/jstraub/optRotTransCVPR2017/", help='path to results folder')
#    default="/media/jstraub/research/dpOptTrans/", help='path to results folder')
#    default="/home/jstraub/CloudStation/research/dpOptTrans/", help='path to results folder')
#    default="../optRotTrans/", help='path to results folder')
cmdArgs = parser.parse_args()

name = "[a-z_0-9]+_[0-9]+_results.json"

results = []
for root, dirs, files in os.walk(cmdArgs.input):
  for f in files:
    if re.search(name, f):    
      results.append(os.path.join(root,f))
  break # don recurse into subfolders

version = "1.1" # tons of results without FFT
version = "1.11" # some with FFT
version = "1.2" # aborted because of some uncought issues
version = "1.21" # working on tons of FFT here; changed lambdaT to 1.0 from 0.3
version = "1.31" # working on BBEGI
version = "1.32" # working on returning Ks for the MMs used by BB
version = "1.33" # working on returning dt
version = "1.4" # Large scale eval. of all algos and BB with lambda S3 60, 70, 80 and LambdaR3 1.
# ^^ all above here are in subfolder on expres1!
version = "1.5" # Parameter sweep of BB
version = "1.51" # Parameter sweep of BB
version = "2.0" # after bug fixing (fabs bug)
version = "2.1" # more targeted eval
version = "2.3" # more targeted eval
version = "2.5" # more targeted eval
version = "2.8" # 
version = "2.6" # monster final eval for CVPR 2016
version = "2.91" # GoICP with trim=0.2 
version = "2.92" # GoICP with trim=0.2 and timeout at 10min
version = "2.93"
version = "3.0"

errors = {"err_a":{}, "err_t":{}, "dt":{}, "Ks":{}, "overlap":[], "dangle":[],
  "dtranslation":[]}
errTypes = ["err_a", "err_t", "dt", "Ks"]
counter = 0
numRejected = dict()
for result in results:
  r = json.load(open(result))
  if r['version'] == version:
    print result
    errors["overlap"].append(r['GT']['overlap'])
#    dang = 2.*np.arccos(r['GT']['q'][0]) *180/np.pi
#    errors["dangle"].append(dang)
#    errors["dtranslation"].append(np.sqrt((np.array(r['GT']['t'])**2).sum()))
    errors["dangle"].append(r['GT']['dangle'])
    errors["dtranslation"].append(r['GT']['dtranslation'])
    # enforce that all values of one scene be non nan
    isnotnan = True
    for algKey, val in r.iteritems():
      if not algKey in ["GT", "version"]:
        for i,typ in enumerate(errTypes):
          if not typ in val:
            continue
          isnotnan = isnotnan and (not np.isnan(val[typ]).any())
          if np.isnan(val[typ]).any():
            if algKey in numRejected:
              numRejected[algKey] += 1
            else:
              numRejected[algKey] = 1
    if not isnotnan:
      continue
    # collect the values
    for algKey, val in r.iteritems():
      if not algKey in ["GT", "version"]:
        for typ in errTypes:
          if not typ in val:
            continue
          if algKey in errors[typ]:
            errors[typ][algKey].append(val[typ])
          else:
            errors[typ][algKey] = [val[typ]]
    counter += 1 
#    if counter > 100:
#      break
totalRejected = 0
for key,val in numRejected.iteritems():
  totalRejected += val
print "Found {} valid and {} invalid result files. Found the following breakdown of invalid files:".format(counter, totalRejected)
for key,val in numRejected.iteritems():
  print "  {}: \t{}\t{}%".format(key, val, 100.*val/float(totalRejected+counter))

if counter == 0:
  print "No results found for version "+version
  sys.exit(0)

def PlotErrHist(x, y, delta):
  if x.size < 1:
    return
  ids = np.floor((x)/delta).astype(np.int)
  means = np.zeros(ids.max()+1)
  stds = np.zeros(ids.max()+1)
  data = []
  for i in range(ids.min(), ids.max()+1):
    if (ids==i).any():
      means[i] = np.mean(y[ids==i])
      stds[i] = np.std(y[ids==i])
      data.append(y[ids==i])
  plt.errorbar(np.arange(ids.max()+1)*delta,means,yerr=stds)

def PlotErrBoxPlot(x, y, delta, ax, showXTicks):
  if x.size < 1:
    return
  ids = np.floor((x)/delta).astype(np.int)
  data = []
  for i in range(ids.min(), ids.max()+1):
    if (ids==i).any():
      data.append(y[ids==i])
  bp = plt.boxplot(data)
#  plt.plot(x,y,'.', color=c1, alpha=0.3)
  # set xticks
  if showXTicks:
    ticks = np.floor((np.arange(ids.min(), ids.max()+1)+0.5)*delta).astype(np.int)
    if np.unique(ticks).size < ticks.size:
      ticks = np.floor((np.arange(ids.min(), ids.max()+1)+0.5)*delta*10.)/10.
    xtickNames = plt.setp(ax, xticklabels=ticks)
    plt.setp(xtickNames, rotation=45)
  else:
    plt.setp(ax.get_xticklabels(), visible=False) 
  for box in bp["boxes"]:
    box.set(color=c1)
    #box.set(facecolor=c1)
  for whisker in bp["whiskers"]:
    whisker.set(color=c1)
  for cap in bp["caps"]:
    cap.set(color=c1)
  for median in bp["medians"]:
    median.set(color=c2)
  for flier in bp["fliers"]:
    flier.set(color=c3, marker=".", alpha=0.15) #,s=6)

def TableErr(x, y, delta):
  if x.size < 1:
    return
  ids = np.floor((x)/delta).astype(np.int)
  data = []
  for i in range(ids.min(), ids.max()+1):
    if (ids==i).any():
      data.append(y[ids==i])
  ticks = np.floor((np.arange(ids.min(), ids.max()+2))*delta).astype(np.int)
  for i,d in enumerate(data):
    dSort = np.sort(d)
    median = dSort[dSort.size/2]
    if dSort.size % 2 == 0:
      median = 0.5*(dSort[dSort.size/2-1]+dSort[dSort.size/2])
    perc75 = dSort[int(np.floor(dSort.size*0.75))]
    perc90 = dSort[int(np.floor(dSort.size*0.9))]
    print "[{} {}]\t #: {}\t 50%: {:.2f}\t 75%: {:.2f}\t 90%: {:.2f}".format(
        ticks[i],ticks[i+1],dSort.size,median,perc75,perc90)

def PlotScatter(x, y, delta, ax, showXTicks):
  if x.size < 1:
    return
  plt.plot(x,y,'.', color=c1, alpha=0.3)
  # set xticks
  if not showXTicks:
    plt.setp(ax.get_xticklabels(), visible=False) 

def PlotErrDensity(x, y, deltax, ymax, deltay, ax, showXTicks):
  if x.size < 1:
    return
  idsx = np.floor((x)/deltax*0.5).astype(np.int)
#  idsy = np.floor((y)/deltay).astype(np.int)
#  density = np.zeros((int(np.floor(ymax/deltay))+1,
#    int(np.floor(x.max()/deltax*0.5))+1))
#  print density.shape
#  for i in range(idsx.min(), idsx.max()+1):
#    if (idsx==i).any():
#      for j in idsy[idsx==i]:
#        density[j, i] += 1.
#  density /= density.sum()
#  print density
#  plt.imshow(density, interpolation="nearest")

  from matplotlib.colors import LogNorm

  bins = ( int(np.floor(x.max()/deltax*0.5))+1), (int(np.floor(ymax/deltay))+1)
  plt.hist2d(x,y, bins=bins, range=[[x.min(),x.max()],[0.,ymax]],
      norm=LogNorm())
  # set xticks
#  if showXTicks:
#    ticks = np.floor((np.arange(idsx.min(), idsx.max()+1)+0.5)*deltax).astype(np.int)
#    if np.unique(ticks).size < ticks.size:
#      ticks = np.floor((np.arange(idsx.min(), idsx.max()+1)+0.5)*deltax*10.)/10.
#    xtickNames = plt.setp(ax, xticklabels=ticks)
#    plt.setp(xtickNames, rotation=45)
#  else:
#    plt.setp(ax.get_xticklabels(), visible=False) 

def WriteErrStats(x, y, delta):
  if x.size < 1:
    return
  ids = np.floor((x)/delta).astype(np.int)
  data = []
  for i in range(ids.min(), ids.max()+1):
    if (ids==i).any():
      data.append(y[ids==i])
  ticks = np.floor((np.arange(ids.min(), ids.max()+1)+0.5)*delta).astype(np.int)
  if np.unique(ticks).size < ticks.size:
    ticks = np.floor((np.arange(ids.min(), ids.max()+1)+0.5)*delta*10.)/10.
  for i,d in enumerate(data):
    mean = np.mean(d)
    std = np.std(d)
    dSorted = np.sort(d)
    median = d[d.size/2]
    ninetyP = d[int(np.floor(d.size*0.1))]
    tenP = d[int(np.floor(d.size*0.9))]
    print "{}: |.| {}\t{} +- {}\t median={}\t10% {}\t90% {}".format(ticks[i], d.size, mean, std,
        median, ninetyP, tenP)

errDesc = {"err_a":"$\Delta \\theta$ [deg]", 
    "err_t": "$\|\|\Delta t\|\|_2$ [m]", "dt":"dt [s]",
    "Ks1":"Ks", "Ks2":"Ks", "Ks3":"Ks", "Ks4":"Ks"}
errTypeMax = {"err_a": 360., "err_t": 10., "dt": 120.,
    "Ks1":30, "Ks2":30, "Ks3":30, "Ks4":30}
yMetricLabel={"overlap":"overlap [%]", "dangle":" $\Delta\\theta_{GT}$ [deg]",
  "dtranslation":"$\|\|\Delta t_{GT}\|\|_2$ [m]"}
yMetricResolution={"overlap":9, "dangle":8, "dtranslation":0.4}
yMetricResolution={"overlap":15, "dangle":12, "dtranslation":0.4}
#yMetricResolution={"overlap":15, "dangle":12, "dtranslation":0.4}

evalKs = False
if evalKs:
  errTypes = ["Ks1","Ks2","Ks3","Ks4", "err_a", "err_t"]
  algTypes = ["BB", "BBEGI"]
  # eval of number of clusters
  for yMetric in ["overlap", "dangle", "dtranslation"]:
    fig = plt.figure(figsize = figSize, dpi = 80, facecolor="w",
        edgecolor="k")
    axs = []
    for i,algType in enumerate(algTypes):
      for j,errType in enumerate(errTypes):
        if j == 0:
          axs.append(plt.subplot(len(errTypes),len(algTypes),
            i+len(algTypes)*j+1))
        else:
          axs.append(plt.subplot(len(errTypes),len(algTypes),
              i+len(algTypes)*j+1, sharex=axs[-1] ))
        plt.ylim([0, errTypeMax[errType]])
        axs[-1].yaxis.grid(True, linestyle='-', which='major',
            color='lightgrey', alpha=0.5, linewidth=2)
        axs[-1].set_axisbelow(True) # hide grey lines behind plot
        if errType in ["Ks1", "Ks2", "Ks3", "Ks4"]:
          kId = int(errType[2])-1
          errs = [Ks[kId] for Ks in errors["Ks"][algType]]
  #        print algType, " num errors ", len(errs), "num nans ", np.isnan(np.array(errs)).sum()
  #        errs = np.array(errs)
  #        errs = errs[np.logical_not(np.isnan(errs))]
  #        ids = np.where(errs < errTypeMax[errType])
  #        plt.plot(np.array(errors[yMetric])[ids], errs[ids],'.')
        else:
          errs = errors[errType][algType]
#        print algType, " num errors ", len(errs), "num nans ", np.isnan(np.array(errs)).sum()
        errs = np.array(errs)
        errs = errs[np.logical_not(np.isnan(errs))]
        ids = np.where(errs < errTypeMax[errType])
        PlotErrBoxPlot(np.array(errors[yMetric])[ids], errs[ids],
            yMetricResolution[yMetric], axs[-1], j==len(errTypes)-1)
        if j == 0:
          plt.title(algType)
        if j == len(errTypes)-1:
          plt.xlabel(yMetricLabel[yMetric])
        if i == 0:
          plt.ylabel(errDesc[errType])
        if i>0:
          plt.setp(axs[-1].get_yticklabels(), visible=False)
        if i==0 and j==1:
          axs[-1].set_yticks(axs[-1].get_yticks()[:-1])
  #    plt.ylim([0, errTypeMax[errType]])
    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=0.1)
    plt.show()

evalBB = False
if evalBB:
  # eval of BB s different parameters
#  paramEvalLambdaS3 = [30., 45.,60., 75., 90.,105.]
#  paramEvalLambdaR3 = [0.3, 0.5, 0.75, 1.5]
#  paramEvalLambdaS3 = [20., 30., 45.,60., 75., 90.]
#  paramEvalLambdaR3 = [0.3, 0.5, 0.75, 1.0]
#  paramEvalLambdaS3 = [40., 45., 52., 60., 75.] #, 90.]
#  paramEvalLambdaR3 = [0.5, 0.75, 1.0]
  paramEvalLambdaS3 = [45., 60., 80] #, 90.]
  paramEvalLambdaR3 = [0.5, 0.75, 1.0]

  algTypes = ["BB"]
  for lambdaS3 in paramEvalLambdaS3:
    for lambdaR3 in paramEvalLambdaR3:
      key = "BB_{}_{}".format(lambdaS3, lambdaR3)
      algTypes.append(key)
  errTypes = ["err_a"] #, "err_t", "dt"]

  for yMetric in ["overlap", "dangle", "dtranslation"]:
    for i,algType in enumerate(algTypes):
      for j,errType in enumerate(errTypes):
        errs = errors[errType][algType]
        errs = np.array(errs)
        errs = errs[np.logical_not(np.isnan(errs))]
        ids = np.where(errs < errTypeMax[errType])
        print " - {} - {} - {}".format(yMetric, algType, errType)
        WriteErrStats(np.array(errors[yMetric])[ids], errs[ids],
            yMetricResolution[yMetric])

  algTypes = ["BB"]
  for lambdaR3 in paramEvalLambdaR3:
    key = "BB_{}_{}".format(45.0, lambdaR3)
    algTypes.append(key)

  algTypes = ["BB"]
  for lambdaS3 in paramEvalLambdaS3:
    key = "BB_{}_{}".format(lambdaS3, 0.75)
    algTypes.append(key)

  errTypes = ["err_a", "err_t", "dt"]
else:
  # eval of all algos against eachother
  errTypes = ["err_a", "err_t"] #, "dt"]
  algTypes = ["BB", "BB+ICP", "BBEGI", "BBEGI+ICP", "FFT", "FFT+ICP", "ICP", "MM", "MM+ICP"]
  algTypes = ["BB", "BB+ICP", "BBEGI", "BB_45.0_0.5",
      "FFT", "FFT+ICP", "ICP", "MM", "MM+ICP"]
  algTypes = ["BB_45.0_0.5", "BB", "BB+ICP",
      "FFT", "FFT+ICP", "ICP", "MM", "MM+ICP"]
  algTypes = ["BB","BB_45.0_0.5", "FFT",  "MM", "ICP"]
  algTypes = ["BB_45.0_0.5"]
  algTypes = ["GoICP"]
  algTypes = ["BB", "FFT",  "GoICP", "ICP"]
  algTypes = ["BB", "Map", "FFT",  "GoICP", "ICP"]


if not "DISPLAY" in os.environ:
  sys.exit(0)

algDesc = {"BB_45.0_0.5":"BB45", "MM":"MoM"}
errTypeResolution = {"err_a": 5., "err_t": 0.2, "dt": 3.}

print algTypes
print errTypes
for yMetric in ["overlap", "dangle", "dtranslation"]:
  fig = plt.figure(figsize = figSize, dpi = 80, facecolor="w",
      edgecolor="k")
  axs = []
  print yMetric
  for i,algType in enumerate(algTypes):
    print algType
    for j,errType in enumerate(errTypes):
      if j == 0:
        axs.append(plt.subplot(len(errTypes),len(algTypes),
          i+len(algTypes)*j+1))
      else:
        axs.append(plt.subplot(len(errTypes),len(algTypes),
            i+len(algTypes)*j+1, sharex=axs[-1] ))
      plt.ylim([0, errTypeMax[errType]])
      axs[-1].yaxis.grid(True, linestyle='-', which='major',
          color='lightgrey', alpha=0.5, linewidth=2)
      axs[-1].set_axisbelow(True) # hide grey lines behind plot
      errs = errors[errType][algType]
      errs = np.array(errs)
      errs = errs[np.logical_not(np.isnan(errs))]
      ids = np.where(errs < errTypeMax[errType])
#      PlotErrDensity(np.array(errors[yMetric])[ids], errs[ids],
#          yMetricResolution[yMetric], errTypeMax[errType],
#          errTypeResolution[errType], axs[-1], j==len(errTypes)-1)
      print errType
      TableErr(np.array(errors[yMetric])[ids], errs[ids],
          yMetricResolution[yMetric])
      PlotErrBoxPlot(np.array(errors[yMetric])[ids], errs[ids],
          yMetricResolution[yMetric], axs[-1], j==len(errTypes)-1)
#      PlotScatter(np.array(errors[yMetric])[ids], errs[ids],
#          yMetricResolution[yMetric], axs[-1], j==len(errTypes)-1)
      if j == 0 and yMetric=="overlap":
        if algType in algDesc:
          plt.title(algDesc[algType])
        else:
          plt.title(algType)
      if j == len(errTypes)-1:
        plt.xlabel(yMetricLabel[yMetric])
      if i == 0:
        plt.ylabel(errDesc[errType])
      if i>0:
        plt.setp(axs[-1].get_yticklabels(), visible=False)
      if i==0 and j==1:
        axs[-1].set_yticks(axs[-1].get_yticks()[:-1])
  plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=0.1)
  plt.savefig("deviation_"+yMetric+"_N_{}_".format(counter)+"_".join(algTypes)+"_results.png", figure=fig)
  plt.show()

import sys
sys.exit(0)

for errType in errTypes:
  print errType
  fig = plt.figure()
  # overlap
  plt.subplot(3,2,1)
  for algType, errs in errors[errType].iteritems():
    ids = np.where(np.array(errs) < errTypeMax[errType])
    plt.plot(np.array(errors["overlap"])[ids], np.array(errs)[ids], '.', label=algType)
    print "  ", algType, errs
  plt.legend()
  plt.xlabel("overlap [%]")
  plt.ylabel(errDesc[errType])
  plt.ylim([0, errTypeMax[errType]])
  plt.subplot(3,2,2)
  for algType, errs in errors[errType].iteritems():
    ids = np.where(np.array(errs) < errTypeMax[errType])
    PlotErrHist(np.array(errors["overlap"])[ids], np.array(errs)[ids],
        5.)
  plt.legend()
  plt.xlabel("overlap [%]")
  plt.ylabel(errDesc[errType])
  plt.ylim([0, errTypeMax[errType]])
  # dangle
  plt.subplot(3,2,3)
  for algType, errs in errors[errType].iteritems():
    ids = np.where(np.array(errs) < errTypeMax[errType])
    plt.plot(np.array(errors["dangle"])[ids], np.array(errs)[ids], '.', label=algType)
  plt.legend()
  plt.xlabel("delta angle [deg]")
  plt.ylabel(errDesc[errType])
  plt.ylim([0, errTypeMax[errType]])
  plt.subplot(3,2,4)
  for algType, errs in errors[errType].iteritems():
    ids = np.where(np.array(errs) < errTypeMax[errType])
    PlotErrHist(np.array(errors["dangle"])[ids], np.array(errs)[ids], 10.)
  plt.legend()
  plt.xlabel("delta angle [deg]")
  plt.ylabel(errDesc[errType])
  plt.ylim([0, errTypeMax[errType]])
  # dtranslation
  plt.subplot(3,2,5)
  for algType, errs in errors[errType].iteritems():
    ids = np.where(np.array(errs) < errTypeMax[errType])
    plt.plot(np.array(errors["dtranslation"])[ids], np.array(errs)[ids], '.', label=algType)
  plt.legend()
  plt.xlabel("delta translation [m]")
  plt.ylabel(errDesc[errType])
  plt.ylim([0, errTypeMax[errType]])
  plt.subplot(3,2,6)
  for algType, errs in errors[errType].iteritems():
    ids = np.where(np.array(errs) < errTypeMax[errType])
    PlotErrHist(np.array(errors["dtranslation"])[ids],
        np.array(errs)[ids], 0.5)
  plt.legend()
  plt.xlabel("delta translation [m]")
  plt.ylabel(errDesc[errType])
  plt.ylim([0, errTypeMax[errType]])
plt.show()
