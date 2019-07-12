def read_data(fname):
    from pathlib import Path
    from numpy import float64 as float

    if Path(fname).exists():
        with open(fname) as f:
            inputs = list(f)
        keys = [f.strip().partition(';')[0].split('=')[0].strip()
                for f in inputs]
        values = [f.strip().partition(';')[0].split('=')[1].strip()
                  for f in inputs]
        for i in range(len(values)):
            try:
                values[i] = float(values[i])
            except ValueError:
                continue

        config = dict(zip(keys, values))
    else:
        raise FileNotFoundError(f'info file was not found: {fname}')

    return config


def make_canvas(width, height, nx=1, ny=1):
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    import matplotlib.gridspec as gridspec

    latexify(width, height)
    fig = Figure(figsize=(width, height), frameon=True)
    canvas = FigureCanvas(fig)
    gs = gridspec.GridSpec(nx, ny,
                           left=0.15, right=0.95, bottom=0.15, top=0.95,
                           wspace=None, hspace=None,
                           width_ratios=None, height_ratios=None)
    return fig, gs, canvas


def latexify(fig_width=None, fig_height=None, columns=1):
    import matplotlib.pyplot as plt
    import matplotlib
    from math import sqrt
    SPINE_COLOR = 'gray'


    """Set up matplotlib's RC params for LaTeX plotting.
    Call this before plotting a figure.

    Parameters
    ----------
    fig_width : float, optional, inches
    fig_height : float,  optional, inches
    columns : {1, 2}
    """

    # code adapted from http://www.scipy.org/Cookbook/Matplotlib/LaTeX_Examples

    # Width and max height in inches for IEEE journals taken from
    # computer.org/cms/Computer.org/Journal%20templates/transactions_art_guide.pdf

    assert(columns in [1,2])

    if fig_width is None:
        fig_width = 3.39 if columns==1 else 6.9 # width in inches

    if fig_height is None:
        golden_mean = (sqrt(5)-1.0)/2.0    # Aesthetic ratio
        fig_height = fig_width*golden_mean # height in inches

    MAX_HEIGHT_INCHES = 8.0
    if fig_height > MAX_HEIGHT_INCHES:
        print("WARNING: fig_height too large:" + fig_height + 
              "so will reduce to" + MAX_HEIGHT_INCHES + "inches.")
        fig_height = MAX_HEIGHT_INCHES

    params = {'backend': 'ps',
              'text.latex.preamble': ['\\usepackage{gensymb}', '\\usepackage{mathtools}'],
              'axes.labelsize': 11, # fontsize for x and y labels (was 10)
              'axes.titlesize': 11,
              'font.size': 11,
              'xtick.labelsize': 11,
              'ytick.labelsize': 11,
              'text.usetex': True,
              'figure.figsize': [fig_width,fig_height],
              'font.family': 'serif'
    }

    matplotlib.rcParams.update(params)


def animation(func, frames, clip_name):
    import time as dt
    import subprocess
    import multiprocessing
    from pathlib import Path
    import os

    print('Plotting in parallel ...')
    starttime = dt.time()
    pool = multiprocessing.Pool()
    pool.map(func, frames)
    pool.close()
    print(f'Plotting finished after {dt.time() - starttime:.1f} seconds')

    print('Making animation from the plots ...')
    if not Path('images').exists():
        Path('images').mkdir()

    output_loc = Path('images', 'frame_%03d.png')

    p = subprocess.Popen(['ffmpeg',
                          '-framerate',
                          '15',
                          '-hide_banner',
                          '-loglevel', 'panic',
                          '-y',
                          '-i', output_loc,
                          f'{clip_name}.mp4'])
    p.communicate()
    for f in list(Path('images').glob('*.png')):
        os.remove(f)
    print('Completed successfully')