"""Optional chart generation: python3 -m pip install matplotlib."""
import csv
from pathlib import Path

def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    with open('results/summary.csv') as f:
        rows=list(csv.DictReader(f))
    fig,axes=plt.subplots(1,2,figsize=(11,4.5))
    for ax,metric,label in zip(axes,['elapsed_ms','assignments_tried'],['Runtime (ms)','Assignments attempted']):
        for j,method in enumerate(['baseline','optimized']):
            selected=[next(r for r in rows if r['scenario']=='original' and r['method']==method and r['difficulty']==d) for d in ['easy','medium','hard']]
            x=[i+(j-.5)*.35 for i in range(3)]
            ax.bar(x,[float(r[metric+'_mean']) for r in selected],width=.35,
                yerr=[float(r[metric+'_std']) for r in selected],capsize=3,label=method)
        ax.set_xticks(range(3),['4 digits/domain','7 digits/domain','10 digits/domain'])
        ax.set_ylabel(label)
        ax.set_title('Original satisfiable puzzles')
        ax.legend()
    fig.suptitle('CSP comparison: 100 seeds, 5 repetitions per instance\nBars: mean; error bars: sample SD across per-instance means')
    fig.tight_layout()
    Path('results').mkdir(exist_ok=True)
    fig.savefig('results/comparison.png',dpi=180)

if __name__=='__main__': main()
