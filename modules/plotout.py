import matplotlib.pyplot as plt

def plotout(scenario, yvar='assets', xvar='age', xlim='auto', ylim='auto', legend_below=False):
    # plot function for list of max_taxable scenarios for given marr, roi, and inflation
    # dollars converted to M$
    d2m = 1/1E6
    marr = []
    roi = []
    inflation = []
    for i in range(0,len(scenario)):
        df = scenario[i].df
        marr = scenario[i].marr
        roi = scenario[i].roi
        inflation = scenario[i].inflation
        #label=str(i)+'. limit: $'+str(round(df.max_taxable[0]*d2m,3))+'M; PVestate='+str(round(df.PVestate[len(df.PVestate)-1]*d2m,3))
        label=scenario[i].name+'; limit: $'+str(round(scenario[i].max_taxable*d2m,3)) \
              + 'M; MARR='+str(marr) + '; ROI='+str(roi) + '; inflation='+str(inflation) \
              + '; assets='+str(round(df.assets.iloc[-1]*d2m,3))
        if 'rate' in yvar: 
            plt.plot(df[xvar], df[yvar], label=label)
        else:
            # yvar is likely dollars so convert to million dollars
            plt.plot(df[xvar], df[yvar]*d2m, label=label)
    plt.xlabel(xvar)
    plt.ylabel(yvar)
    marr = scenario[i].marr
    roi = scenario[i].roi
    inflation = scenario[i].inflation
    if xlim != 'auto':
        plt.xlim(xlim)
    if ylim != 'auto':
        plt.ylim(ylim)
    #plt.title(yvar+': MARR='+str(marr)+'; ROI='+str(roi)+'; Inflation='+str(inflation))
    if legend_below:
        plt.legend(bbox_to_anchor=(1, 0), loc="upper right", fontsize=8)
        plt.tight_layout(rect=[0, 0, 0.75, 1])
    else:
        plt.legend
        plt.legend(fontsize=8) # Displays the labels for each line
    plt.grid(True)
    plt.show()
