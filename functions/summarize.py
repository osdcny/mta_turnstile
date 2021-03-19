import numpy as np
import pandas as pd


def generate_usage_stats(_df, level='station', window=12, first_period='2020-01-01', last_period='2021-02-01',
                         add_city_total=True, comparison_type='base_year'):
    """
    Generate usage summary statistics from the turnstile usage dataframe
    ----------
    _df: the input dataframe
    level: at what level is data aggregated. choices are 'station', 'neighborhood', 'pUMA', 'borough'
    window: the number of periods to look back. 12 is YoY, 1 is MoM.
    first_period: first period included in the summary dataset
    last_period: last period included in the summary dataset
    add_city_total: whether to add a NYC subtotal

    Returns
    -------
    a single summary dataset (pandas dataframe)
    """

    _pivot_table = pd.pivot_table(_df, values=['entries_diff', 'exits_diff'], index=[level, 'period'],
                                  aggfunc=np.sum)

    if add_city_total:
        _pivot_table = _pivot_table.reset_index()
        _nyc_pivot_table = pd.pivot_table(_df, values=['entries_diff', 'exits_diff'], index=['period'],
                                          aggfunc=np.sum).reset_index()
        _nyc_pivot_table.insert(0, level, 'New York City')

        _pivot_table = _pivot_table.append(_nyc_pivot_table)
        _pivot_table.set_index([level, 'period'], inplace=True)
        
    if comparison_type == 'yoy':

        _summary = _pivot_table.groupby([level]).transform(lambda x: x.pct_change(window) + 1).dropna()
        # _summary = _summary.reset_index()
        # _summary = _summary[_summary['period'] >= first_period]
        _summary = _summary[(_summary.index.get_level_values('period') >= first_period) &
                            (_summary.index.get_level_values('period') <= last_period)].reset_index()
        
        return _summary
    
    elif comparison_type == 'base_year':
        
        for unit in list(_pivot_table.index.get_level_values(level).unique()):
            for period in list(_pivot_table.index.get_level_values('period').unique()):
                base_period = period.replace(year=2019)
                current_period = period
                try:
                    _pivot_table.loc[(unit, period), "entries_usage_pct"] = _pivot_table.loc[(unit, current_period), "entries_diff"] / _pivot_table.loc[(unit, base_period), "entries_diff"]
                    _pivot_table.loc[(unit, period), "exits_usage_pct"] = _pivot_table.loc[(unit, current_period), "exits_diff"] / _pivot_table.loc[(unit, base_period), "exits_diff"]
                except:
                    _pivot_table.loc[(unit, period), "entries_usage_pct"] = np.nan
                    _pivot_table.loc[(unit, period), "exits_usage_pct"] = np.nan
                    
        _pivot_table = _pivot_table[(_pivot_table.index.get_level_values('period') >= first_period) & (_pivot_table.index.get_level_values('period') <= last_period)]
        
        return _pivot_table
                
    


def generate_nominal_stats(_df, level='station', window=12, first_period='2020-01-01', last_period='2021-01-01',
                         add_city_total=True):
    """
    Generate usage summary statistics from the turnstile usage dataframe
    ----------
    _df: the input dataframe
    level: at what level is data aggregated. choices are 'station', 'neighborhood', 'pUMA', 'borough'
    window: the number of periods to look back. 12 is YoY, 1 is MoM.
    first_period: first period included in the summary dataset
    last_period: last period included in the summary dataset
    add_city_total: whether to add a NYC subtotal

    Returns
    -------
    a single summary dataset (pandas dataframe)
    """

    _pivot_table = pd.pivot_table(_df, values=['entries_diff', 'exits_diff'], index=[level, 'period'],
                                  aggfunc=np.sum)

    if add_city_total:
        _pivot_table = _pivot_table.reset_index()
        _nyc_pivot_table = pd.pivot_table(_df, values=['entries_diff', 'exits_diff'], index=['period'],
                                          aggfunc=np.sum).reset_index()
        _nyc_pivot_table.insert(0, level, 'New York City')

        _pivot_table = _pivot_table.append(_nyc_pivot_table)
        _pivot_table.set_index([level, 'period'], inplace=True)

    return _pivot_table

if __name__ == '__main__':
    help(generate_usage_stats)


