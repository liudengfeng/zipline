"""
TEST数据包
"""

import time

import pandas as pd
from cnswd.utils import HotDataCache, make_logger

from . import core as bundles
from .adjusts import NON_ADJUSTED_COLUMN_FACTOR
from .utils import _exchanges
from .wy_data import (fetch_single_equity, fetch_single_quity_adjustments,
                      gen_asset_metadata)
from .wy_minute_data import fetch_single_minutely_equity

TODAY = pd.Timestamp('today').normalize()
log = make_logger('wydb', collection='zipline')


OHLCV_COLS = ['open', 'high', 'low', 'close', 'volume']
# 截取测试股票、指数代码 + 新股 + 中途停牌
TEST_SIDS = [1, 2, 333, 2335, 2024, 600645,
             300001, 300882, 300313, 1000002, 1000001]
# TEST_SIDS = [2]
TEST_CODES = [str(x).zfill(6) for x in TEST_SIDS]


def _to_sid(x):
    """符号转换为sid"""
    return int(x)


def _update_splits(splits, asset_id, origin_data, start, end):
    if origin_data.empty:
        # 如为空表，直接返回，不进行任何处理
        return
    ratio = origin_data['s_ratio'] + origin_data['z_ratio']
    # 调整适应于zipline算法
    df = pd.DataFrame({
        'ratio': 1 / (1 + ratio),
        'effective_date': pd.to_datetime(origin_data['ex_date']),
        'sid': asset_id
    })
    cond = (start <= df['effective_date']) & (df['effective_date'] <= end)
    df = df.loc[cond, :]
    if not df.empty:
        # 此时将时间转换UTC时区
        df['effective_date'] = pd.to_datetime(df['effective_date'], utc=True)
        splits.append(df)


def _update_dividends(dividends, asset_id, origin_data, start, end):
    if origin_data.empty:
        return
    # date -> datetime64[ns]
    df = pd.DataFrame({
        'record_date': pd.NaT,
        # pd.to_datetime(origin_data['record_date']),
        'ex_date':
        pd.to_datetime(origin_data['ex_date']),
        'declared_date': pd.NaT,
        # pd.to_datetime(origin_data['declared_date']),
        'pay_date': pd.NaT,
        # pd.to_datetime(origin_data['pay_date']),
        'amount':
        origin_data['amount'],
        'sid':
        asset_id
    })
    cond = (start <= df['ex_date']) & (df['ex_date'] <= end)
    df = df.loc[cond, :]
    if not df.empty:
        # 此时将时间转换UTC时区
        df['ex_date'] = pd.to_datetime(df['ex_date'], utc=True)
        dividends.append(df)


def gen_symbol_data(symbol_map, sessions, splits, dividends, d_index, m_index, is_minutely):
    if not is_minutely:
        cols = OHLCV_COLS + list(NON_ADJUSTED_COLUMN_FACTOR.keys())
    else:
        cols = OHLCV_COLS
    start, end = sessions[0], sessions[-1]
    # 查询时须将时区转换为None
    start, end = start.tz_localize(None), end.tz_localize(None)
    m_index_local = m_index.tz_convert('Asia/Shanghai').tz_localize(None)
    for _, symbol in symbol_map.iteritems():
        asset_id = _to_sid(symbol)
        if not is_minutely:
            raw_data = fetch_single_equity(
                symbol,
                start=start,
                end=end,
            )
            if not raw_data.empty:

                # 以日期、符号为索引
                raw_data.set_index(['date', 'symbol'], inplace=True)
                raw_data = raw_data.loc[:, cols]

                # 时区调整，以0.0填充na
                # 转换为以日期为索引的表(与sessions保持一致)
                asset_data = raw_data.xs(symbol, level=1).reindex(
                    sessions.tz_localize(None)
                ).fillna(0.0).tz_localize('Asia/Shanghai').tz_convert('utc')
            else:
                asset_data = pd.DataFrame(
                    data=0.0, index=d_index, columns=cols)
        else:
            # 处理分钟级别数据
            asset_data = fetch_single_minutely_equity(
                symbol,
                start=start,
                end=end,
            )
            asset_data = asset_data.reindex(m_index_local, method='ffill')
            asset_data = asset_data.tz_localize(
                'Asia/Shanghai').tz_convert('utc')

        # 顺带处理分红派息
        # 获取原始调整数据
        raw_adjustment = fetch_single_quity_adjustments(symbol,
                                                        start=start,
                                                        end=end)
        # 当非空时才执行
        if not raw_adjustment.empty:
            # 剔除未来事件
            raw_adjustment = raw_adjustment[raw_adjustment.ex_date <= TODAY]
            # 更新送转
            # 送转比率大于0才有意义
            ratio = raw_adjustment.s_ratio + raw_adjustment.z_ratio
            raw_splits = raw_adjustment.loc[ratio > 0.0, :]
            _update_splits(splits, asset_id, raw_splits, start, end)

            # 更新股利
            raw_dividends = raw_adjustment.loc[raw_adjustment.amount > 0.0, :]
            _update_dividends(dividends, asset_id, raw_dividends, start, end)
        yield asset_id, asset_data

# 开始日期必须是交易日


@bundles.register(
    'dtest',
    calendar_name='XSHG',
    start_session=pd.Timestamp('2010-01-04', tz='UTC'),
    # end_session=pd.Timestamp('today', tz='UTC').round('D'),
    minutes_per_day=240)
def cndaily_bundle(environ, asset_db_writer, minute_bar_writer,
                   daily_bar_writer, adjustment_writer, calendar,
                   start_session, end_session, cache, show_progress,
                   output_dir):
    """Build a zipline data bundle from the cnstock dataset.
    """
    t = time.time()
    log.info('读取股票元数据......')
    # metadata = gen_asset_metadata(False)

    # 截取测试代码
    hc = HotDataCache(gen_asset_metadata, hour=9, minute=30, only_in=False)
    metadata = hc.data
    # 资产元数据写法要求添加`sid`列
    metadata['sid'] = metadata.symbol.map(_to_sid)
    cond = metadata['sid'].isin(TEST_SIDS)
    metadata = metadata[cond]
    symbol_map = metadata.symbol
    sessions = calendar.sessions_in_range(start_session, end_session)

    d_fmt = r"%Y-%m-%d"
    start_str = sessions[0].strftime(d_fmt)
    end_str = sessions[-1].strftime(d_fmt)
    # UTC 时区 index
    d_index = calendar.sessions_in_range(start_str, end_str)
    m_index = calendar.minutes_for_sessions_in_range(start_str, end_str)

    log.info('日线数据集（股票数量：{}）'.format(len(symbol_map)))

    # 写入股票元数据
    if show_progress:
        log.info('写入资产元数据')
    asset_db_writer.write(metadata, exchanges=_exchanges())

    splits = []
    dividends = []
    daily_bar_writer.write(
        gen_symbol_data(symbol_map,
                        sessions,
                        splits,
                        dividends,
                        d_index=d_index,
                        m_index=m_index,
                        is_minutely=False),
        show_progress=show_progress,
        has_additional_cols=True,
    )

    adjustment_writer.write(
        splits=None if len(splits) == 0 else pd.concat(splits,
                                                       ignore_index=True),
        dividends=None
        if len(dividends) == 0 else pd.concat(dividends, ignore_index=True),
    )

    log.info(f'完成用时：{time.time() - t:.2f}秒')


@bundles.register(
    'mtest',
    calendar_name='XSHG',
    # 必须与正式环境一致
    start_session=pd.Timestamp('2020-06-29', tz='UTC'),
    # end_session=pd.Timestamp('today', tz='UTC').round('D'),
    minutes_per_day=240)
def cnminutely_bundle(environ, asset_db_writer, minute_bar_writer,
                      daily_bar_writer, adjustment_writer, calendar,
                      start_session, end_session, cache, show_progress,
                      output_dir):
    """Build a zipline data bundle from the cnstock dataset.
    """
    t = time.time()
    log.info('读取股票元数据......')

    # 无股指分时数据，以日线代替分钟级别数据
    hc = HotDataCache(gen_asset_metadata, hour=9, minute=30, only_in=False)
    metadata = hc.data
    metadata['sid'] = metadata.symbol.map(_to_sid)
    cond = metadata['sid'].isin(TEST_SIDS)
    metadata = metadata[cond]

    symbol_map = metadata.symbol

    sessions = calendar.sessions_in_range(start_session, end_session)
    d_fmt = r"%Y-%m-%d"
    start_str = sessions[0].strftime(d_fmt)
    end_str = sessions[-1].strftime(d_fmt)
    d_index = calendar.sessions_in_range(start_str, end_str)
    m_index = calendar.minutes_for_sessions_in_range(start_str, end_str)

    log.info('分钟级别数据集（股票数量：{}）'.format(len(symbol_map)))

    # 写入股票元数据
    if show_progress:
        log.info('写入资产元数据')
    asset_db_writer.write(metadata, exchanges=_exchanges())

    splits = []
    dividends = []
    daily_bar_writer.write(
        gen_symbol_data(symbol_map,
                        sessions,
                        splits,
                        dividends,
                        d_index=d_index,
                        m_index=m_index,
                        is_minutely=False),
        show_progress=show_progress,
        has_additional_cols=True,
    )

    adjustment_writer.write(
        splits=None if len(splits) == 0 else pd.concat(splits,
                                                       ignore_index=True),
        dividends=None
        if len(dividends) == 0 else pd.concat(dividends, ignore_index=True),
    )

    minute_bar_writer.write(
        gen_symbol_data(symbol_map,
                        sessions,
                        splits,
                        dividends,
                        d_index=d_index,
                        m_index=m_index,
                        is_minutely=True),
        show_progress=show_progress,
    )

    log.info(f'完成用时：{time.time() - t:.2f}秒')
