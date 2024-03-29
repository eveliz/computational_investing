import datetime as dt
import math
import numpy as np
import pandas as pd

# QSTK Imports
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu

def get_values_list(s_file_path):
    df_values_list = pd.read_csv(s_file_path, sep=',', header=None)
    df_values_list.columns = ["year", "month", "day", "total"]
    return df_values_list


def get_values(df_values_list):
    np_values_list = df_values_list.values
    l_values = []
    for value in np_values_list:
        dt_date = dt.datetime(value[0], value[1], value[2], hour=16)
        total = float(value[3])
        l_values.append([dt_date, total])
    np_values = np.array(l_values)
    df_values = pd.DataFrame(np_values[:, 1], index=np_values[:, 0], columns=["val"])
    return df_values


def get_data(ldt_timestamps, ls_symbols):
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    dataobj = da.DataAccess('Yahoo')
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    return d_data

def get_prices(ldt_timestamps, ls_symbols, s_key="close"):
    d_data = get_data(ldt_timestamps, ls_symbols)
    return d_data[s_key]


def get_performance_indicators(df_data):
    na_data = df_data.values
    df_result = pd.DataFrame(index=["avg_daily_ret", "std_daily_ret", "sharpe_ratio", "total_ret"], \
                             columns=df_data.columns)

    # Calculating the daily return
    # It gets a copy of na_data becouse tsu.returnize0 does not return
    # anything, the function changes the argument.
    na_daily_ret = na_data.copy()
    tsu.returnize0(na_daily_ret)

    na_cum_ret = na_data / na_data[0, :]
    
    for col in range(na_data.shape[1]):
        df_result.ix["avg_daily_ret", col] = np.mean(na_daily_ret[:, col])
        df_result.ix["std_daily_ret", col] = np.std(na_daily_ret[:, col])
        df_result.ix["sharpe_ratio", col] = math.sqrt(252) * df_result.ix["avg_daily_ret", col] / df_result.ix["std_daily_ret", col]
        df_result.ix["total_ret", col] = na_cum_ret[-1 , col]
        
    print df_result


if __name__ == '__main__':
    print "start analyze.py"
    print
    s_file_path = "q2_values.csv"
    ls_symbols = ["$SPX"]
    df_values_list = get_values_list(s_file_path)
    df_values = get_values(df_values_list)
    df_prices = get_prices(list(df_values.index), ls_symbols)
    df_data = df_values.join(df_prices)
    get_performance_indicators(df_data)
    print
    print "end analize.py"