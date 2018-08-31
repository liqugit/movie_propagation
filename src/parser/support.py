"""
File: support.py
Author: Joao Moreira
Creation Date: Feb 7, 2017

Description:
Contains all common functions necessary for figure creation.
"""
import os
import inspect
import json
from itertools import islice

import numpy as np
import pandas as pd
import seaborn as sns

##############################################################################
#######
#######                     GLOBAL VARIABLES
#######
##############################################################################
CREDITS = ['acting_all', 'acting_credited', 'casting', 'cinematography', 'directing', 'producing', 'writing']
GENRES = ['Action', 'Adventure', 'Biography', 'Comedy', 'Crime', 'Drama', 'Documentary', 'Family', 'Fantasy',
          'Film-Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport',
          'Thriller', 'War', 'Western', 'Short',
          # 'Animation', 'Reality-TV', 'Game-Show', 'Talk-Show', 'Adult'
          ]

#          movies,   actors: all,  casting, producers,  directors,  actors: romance, action,
PALETTE = [ 'goldenrod',  #number movies
            '#7570b3',  #actors, all -- purple
            '#66a61e',  #writers -- green
            '#666666',  #directors -- grey
            '#d95f02',  #producers -- orange
            '#a6761d',  #casting -- gold
            '#e7298a',  #cinematography -- pink
            '#e6ab02',  #movies, romance -- yellow
            '#1b9e77',  #movies, action  -- chartreuse
            ]
ROLES = ['cast_all', 'cast_credited', 'casting_directors', 'cinematographers', 'directors',
         'producers', 'screenwriters']

##############################################################################
#######
#######                     IMPORTING DATA
#######
##############################################################################

def load_dataset(dataset):
    """
    Loads a json dataset as a pandas DataFrame.
    """
    valid = {'afi_movies', 'movies', 'career', 'producers'}
    if dataset not in valid:
        raise ValueError("`dataset` must be one of: {}".format(", ".join(valid)))

    raw_dir = os.path.abspath(
        os.path.join('/home/projects/movie-network/', 'data', 'raw_data')
    )
    return pd.read_json(os.path.join(raw_dir, dataset + ".json"))


def get_movies_df(role_key):
    """
    Takes role_key as role in movie and excluded_genres as list of genres to exclude from analysis

    Returns a pandas DataFrame with all movies, and actors gender information.
    """
    movies_df = load_dataset("movies")

    print('Loaded IMDb movies {}'.format(role_key))
    return movies_df.dropna(subset=[role_key])


def get_afi_movies_df():
    """
    Returns a pandas DataFrame with all US, English language AFI movies
    """
    movies_df = load_dataset("afi_movies")
    print('\nLoaded AFI movies')
    return movies_df.dropna(subset=['year'])


def get_movie_budgets_df():
    """
    Takes role_key as role in movie

    Returns a pandas DataFrame with the year, director info, and budget of all
    movies with a single director.
    """     
    movies_df = load_dataset("movies")
    return movies_df.dropna(subset=["adjusted_budget"])


def get_genre_movies_df(genre, role_key):
    """
    Takes tv_flag is whether we want tv movies or non-tv movies
    Takes genre

    Returns a pandas DataFrame with all movies with the given genre,
    and actors gender information.
    """
    movies_df = load_dataset("movies")
    valid_movies_df = movies_df.dropna(subset=[role_key])
    return valid_movies_df[valid_movies_df.genres.apply(lambda x: genre in x)]


def get_movies_staff_df(role):
    """
    Takes in the role of the staff (director, producers, cinematographers, writers)

    Returns a pandas DataFrame with the year and role roster of all movies
    for which we have role information.
    """
    movies_df = load_dataset("movies")
    return movies_df.dropna(subset=[role])


def get_staff_df(role):
    """
    Takes in the role of the staff (director, producers, cinematographers, writers)

    Returns a pandas DataFrame with all directors for which we have gender
    information.
    """

    if role == 'director':
        dirs_df = load_dataset(role + "s")
    else:
        dirs_df = load_dataset(role)

    # Removing staff on undetermined gender
    return dirs_df[dirs_df.gender.apply(lambda x: x in {"male", "female"})]


def get_single_dir_movies_df():
    """
    Returns all movies with a single director that also have producer
    information.
    """
    movies_df = load_dataset("movies")

    valid_movies_df = movies_df.dropna(subset=["director"])

    # Removing movies with more than a single director and
    #  directors on undetermined gender
    return valid_movies_df[valid_movies_df.director.apply(
        lambda x: len(x) == 1 and x[0]["gender"] in {"male", "female"}
    )]


def get_single_dir_all_actor_movies_df():
    """
    Returns all movies with a single director, and actors gender
    information.
    """
    movies_df = load_dataset("movies")

    valid_movies_df = movies_df.dropna(
        subset=["director", "all_actors", "gender_percent"]
    )

    # Removing movies with more than a single director and
    #  directors on undetermined gender
    return valid_movies_df[valid_movies_df.director.apply(
        lambda x: len(x) == 1 and x[0]["gender"] in {"male", "female"}
    )]


def get_single_dir_all_prod_movies_df():
    """
    Returns all movies with a single director, producer info, and actors gender
    information.
    """
    movies_df = load_dataset("movies")

    valid_movies_df = movies_df.dropna(
        subset=["gender_percent", "producer", "director"]
    )

    # Removing movies with more than a single director and
    #  directors on undetermined gender
    return valid_movies_df[valid_movies_df.director.apply(
        lambda x: len(x) == 1 and x[0]["gender"] in {"male", "female"}
    )]


def get_movies_producers_df():
    """
    Returns a pandas DataFrame with the year and producer roster of all movies
    for which we have producer information.
    """
    movies_df = load_dataset("movies")
    return movies_df.dropna(subset=["producer"])


def get_directors_df():
    """
    Returns a pandas DataFrame with all directors for which we have gender
    information.
    """
    dirs_df = load_dataset("directors")

    # Removing directors on undetermined gender
    return dirs_df[dirs_df.gender.apply(lambda x: x in {"male", "female"})]


def get_producers_df():
    """
    Returns a pandas DataFrame with all producers, including their gender,
    mongo id, first and last movie years (as any producers role and several
    specific producer role)
    """
    prods_df = load_dataset("producers")

    # Removing producers on undetermined gender
    return prods_df[prods_df.gender.apply(lambda x: x in {"male", "female"})]



##############################################################################
#######
#######                     EXPORTING UTILITIES
#######
##############################################################################

def savefig(figure):
    """
    Saves a figure with the proper name and properties in the appropriate
    directory.
    """
    # This always returns the path to whichever file this function is being
    # called from.
    frame = inspect.stack()[1]
    caller_filepath = frame[1]
    figure_name = os.path.splitext(os.path.basename(caller_filepath))[0]

    extension = ".pdf"
    figure_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), os.pardir, figure_name + extension
    ))

    figure.savefig(figure_path, dpi=300, bbox_inches="tight")


def save_stats(stats, *other_stats):
    """
    Saves a json with all the given figure/table(s) stats with the proper name
    in the appropriate directory.
    """
    # This always returns the path to whichever file this function is being
    # called from.
    frame = inspect.stack()[1]
    caller_filepath = frame[1]
    filename = os.path.splitext(os.path.basename(caller_filepath))[0]

    stats_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), os.pardir, "stats_json"
    ))
    # The stats directory is not in the repo so we need to create it first.
    if not os.path.exists(stats_dir):
        os.makedirs(stats_dir)

    all_stats = dict(stats)
    for other in other_stats:
        all_stats.update(other)

    extension = ".json"
    stats_path = os.path.join(stats_dir, filename + extension)
    with open(stats_path, "w") as fobj:
        json.dump(all_stats, fobj)


def to_tex_scientific(numb, sig_digits=2):
    """
    Convert a number to classical scientific notation:
    2.5e+6 -> 2.5 x 10^6

    Outputs number as a string of math tex code (e.g., 2.5 \times 10^{6}), meant
    to be used inside a pre-defined math environment.

    numb: Number to convert
    sig_digits: Number of significant digits to use in the mantissa.
    """
    # If the number is too small python does not convert it to scientific
    # notation
    if abs(numb) <= 1e5:
        return str(numb)
    fmt = "{{:.{}g}}".format(sig_digits)

    numb_str = fmt.format(numb)
    mantissa, exp = numb_str.split("e")

    return r"{} \times 10^{{{}}}".format(mantissa, int(exp))



##############################################################################
#######
#######                     STATISTICS UTILITIES
#######
##############################################################################

def window(seq, n=3):
    """
    Returns a sliding window (of width n) over data from the iterable:
       s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...
    From: https://docs.python.org/3.6/library/itertools.html#itertools-recipes
    """
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def get_decade(year):
    """
    Returns the decade when the movie was released.
    If year >= 2000, decade is 100, 110, 120, etc...
    """
    return int(pd.np.floor((year - 1900)/10)*10)


def sem(data):
    """
    Calculates the standard error of the mean for the given dataset.
    """
    return pd.np.std(data)/pd.np.sqrt(len(data))


def roll_mean_sem_movies(key, df, date_range, w_width, count = False):
    """
    Calculate the rolling mean and stderr for the given movies df.

    Params:
        role       : String with type of role in movie
        df         : Dataframe with 'year' as one of the keys
        date_range : List/array of unique, sorted datetime year values
                     to roll over.
        w_width    : Integer specifying rolling window width.

    Returns (Series with mean, Series with sem)
    """
    series_mean = {}
    series_sem = {}

    print(df.keys(), len(df))
    if count:
        new_column = np.array([len(df.iloc[i][key]) if len(df.iloc[i][key]) > 0 else np.nan for i in range(len(df))])
        df = df.assign(counter=new_column)
        pkey = 'counter'
    else:
        pkey = key

    df.sort_values(by="year", inplace=True)

    for w in window(date_range, w_width):
        rolling_df = df[(df.year >= w[0]) & (df.year <= w[-1])]
        mean = rolling_df[pkey].mean()

        if pd.isnull(mean):
            continue
        series_mean[w[-1]] = mean
        series_sem[w[-1]] = sem(rolling_df[pkey])

    return (pd.Series(series_mean), pd.Series(series_sem))



def find_largest_consec_region(s_bool, threshold=2):
    """
    Finds the start and end indices of largest consecutive region
    of values from the given boolean Series that are True. Ignores any short
    peaks of `threshold` (default 2) or less values.

    Inspired by: http://stackoverflow.com/a/24433632
    """
    indices = s_bool.index

    regions = pd.DataFrame()

    # First row of consecutive region is a True preceded by a False in tags
    regions["start"] = indices[s_bool & ~s_bool.shift(1).fillna(False)]

    # Last row of consecutive region is a False preceded by a True
    regions["end"] = indices[s_bool & ~s_bool.shift(-1).fillna(False)]

    # How long is each region
    regions["span"] = regions.end - regions.start + 1

    # index of the region with the longest span
    max_idx = regions.span.argmax()
    start_max = regions.start.iloc[max_idx]
    end_max = regions.end.iloc[max_idx]

    # How many years between gaps
    regions["gap"] = regions.start - regions.end.shift(1)

    # Are there any non-spurious gaps separated by `threshold` values or less
    # right after the largest gap?
    small_gaps = (regions.end > end_max)
    small_gaps &= (regions.gap <= threshold)
    small_gaps &= (regions.span > 1)

    # If so, the largest such gap is now the region's end
    if small_gaps.sum() > 0:
        end_max = regions.end[small_gaps].iloc[-1]

    return (start_max, end_max)



##############################################################################
#######
#######                     GENDER CALCULATIONS
#######
##############################################################################

def convert_gender(gender):
    """
    Converts gender to a numerical scale:
    0 - male
    1 - female
    2 - undetermined
    """
    if gender == "male":
        return 0
    elif gender == "female":
        return 1
    else:
        return 2


def calc_staff_gender_percent(role):
    """
    Takes role as dataframe with information on specific staff role (director, producer, etc)

    Calculates the gender percent of a movie's role crew.
    The percent only includes staff for which we know the gender.
    """
    females = sum(1 for p in role if p["gender"] == "female")
    males = sum(1 for p in role if p["gender"] == "male")
    try:
        return 100*females/(males + females)
    except ZeroDivisionError:
        return pd.np.nan


def get_staff_gender_df(movies_df, role):
    """
    Returns a pandas DataFrame with the yearly mean and standard error of the
    role gender fraction for all movies with role information.
    """
    key = role + "_gender_p"

    movies_df[key] = movies_df[role].apply(calc_staff_gender_percent)

    key = movies_df.groupby("year")[key].agg(
        {"mean": "mean", "sem": sem}
    )

    return key


def get_directors_gender_df(directors_df):
    """
    Calculates the percent of movies directed by females over time from the
    input director data.
    """
    gender_raw = []
    for _, d in directors_df.iterrows():
        for m in d["movies_list"]:
            gender_raw.append({
                "year": m["year"],
                "dir_gender": d["gender"],
                "movie": m["movie_id"],
                "dir_id": d["_id"],
            })
    gender_df = pd.DataFrame(gender_raw)

    # Group by year and pivot on gender, i.e.,
    # count occurrences of each gender per year
    gender_pivot = pd.pivot_table(
        gender_df, index='year', columns='dir_gender', aggfunc=len
    )
    # The pivot repeats information in column groups.
    # Any of `dir_id`,`movie` groups will have the same info (these
    # are the columns from `gender_raw` that are not used in created the pivot)
    gender_pivot = gender_pivot["dir_id"]

    # Convert absolute numbers to percent
    return (gender_pivot.female/gender_pivot.sum(axis=1)).dropna()*100


def get_active_gender_percent(elements_df, left, right):
    """
    Calculates the gender percent of active elements (actors, producers, or
    directors) in each year y. Elements are considered active in year y if
    `left` <= y <= `right`.

    Gender percent is relative to females:
        100% means all female;
        0% means all male.
    """
    y_min = int(elements_df[left].min())
    y_max = int(elements_df[right].max())

    active_dir = {"male": {}, "female": {}}
    for gender, gender_active in active_dir.items():
        gender_df = elements_df.loc[elements_df.gender == gender]
        for year in range(y_min, y_max+1):
            gender_active[year] = sum(
                (gender_df[left] <= year) & (gender_df[right] >= year)
            )

    active_df = pd.DataFrame(active_dir)

    return 100*active_df.female/(active_df.male+active_df.female)



##############################################################################
#######
#######                     PLOTTING
#######
##############################################################################

def place_commas(n):
    """Takes integer and returns string from printing with commas separating factors of 1000
    """
    tmp = str(n)
    n_digits = len(tmp)

    line = ''
    for i in range(n_digits):
        if not (i) % 3 and i != 0:
            line = tmp[-i - 1] + ',' + line
        else:
            line = tmp[-i - 1] + line

    return line


def set_style(sns):
    """
    Sets the plots style.

    Params:
    sns : seaborn module
    """
    # White background with outward ticks
    sns.set_context("poster")
    sns.set_style("ticks")

    # Try to use regular fonts for equations
    sns.mpl.rc('text', usetex=False)
    sns.mpl.rc('text.latex', unicode=False)
    sns.mpl.rc('mathtext', default='regular')


def half_frame(sub, xaxis_label, yaxis_label, font_size = 15, padding = -0.02):
    """Formats frame, axes, and ticks for matplotlib made graphic with half frame."""

    # Format graph frame and tick marks
    sub.yaxis.set_ticks_position('left')
    sub.xaxis.set_ticks_position('bottom')
    sub.tick_params(axis = 'both', which = 'major', length = 7, width = 2, direction = 'out', pad = 10,
                    labelsize = font_size)
    sub.tick_params(axis = 'both', which = 'minor', length = 5, width = 2, direction = 'out', labelsize = 10)
    for axis in ['bottom','left']:
        sub.spines[axis].set_linewidth(2)
        sub.spines[axis].set_position(("axes", padding))
    for axis in ['top','right']:
        sub.spines[axis].set_visible(False)

    # Format axes
    sub.set_xlabel(xaxis_label, fontsize = 1.6 * font_size)
    sub.set_ylabel(yaxis_label, fontsize = 1.6 * font_size)


def bottom_frame(sub, xaxis_label, font_size = 15, padding = -0.02):
    """Formats frame, axes, and ticks for matplotlib made graphic with half frame."""

    # Format graph frame and tick marks
    sub.yaxis.set_ticks_position('none')
    sub.yaxis.set_ticklabels([])
    sub.xaxis.set_ticks_position('bottom')
    sub.tick_params(axis = 'x', which = 'major', length = 7, width = 2, direction = 'out', pad = 10,
                    labelsize = font_size)
    sub.tick_params(axis = 'x', which = 'minor', length = 5, width = 2, direction = 'out', labelsize = 10)
    for axis in ['bottom']:
        sub.spines[axis].set_linewidth(2)
        sub.spines[axis].set_position(("axes", padding))
    for axis in ['top','right', 'left']:
        sub.spines[axis].set_visible(False)

    # Format axes
    sub.set_xlabel(xaxis_label, fontsize = 1.6 * font_size)


def plot_total_year_movies(axes, all_movies, y_min, y_max, y_scale_max, my_font_size, genre, ax_labels):
    """
    Plots the total number of movies per year over time.
    """
    half_frame(axes, '', '', font_size = my_font_size)
    year_range1 = (all_movies.year >= y_min) & (all_movies.year <= y_max)
    N_movies = len(all_movies[year_range1])
    print('Number of movies in IMDb database is {}'.format(N_movies))

    # We bin movies every k years
    k = 1
    x_years = np.linspace(y_min, y_max, 101)
    hist = [0] * int((y_max - y_min + 1)/k)
    for year in all_movies[year_range1].year:
        i = year - y_min
        hist[i] += 1

    axes.bar(x_years, hist,
             width = 0.8,
             align = 'center',
             color = PALETTE[0],
            )

    axes.set_xlabel(ax_labels[0])
    axes.set_xlim(y_min-1, y_max+1)
    axes.set_xticks(np.arange(1910, 2011, 10))

    axes.set_ylabel(ax_labels[1])
    # May have to adjust parameters for y_ticks
    axes.set_yticks(np.arange(0, y_scale_max+1, y_scale_max/4))

    sns.despine(ax=axes, trim=True)

    if genre:
        line = genre + '\n{} movies'.format(place_commas(N_movies))
        axes.text(1960, 0.8 * y_scale_max, line,
                  horizontalalignment = "center",
                  verticalalignment = "center",
                  size = 1.5 * my_font_size,
                  bbox = {"facecolor": "white", "edgecolor": "white"}
                  )
