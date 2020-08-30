#
# Copyright 2015 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

########################################################################
#                   修改后的模拟引擎只适用于A股
########################################################################

cimport numpy as np
import numpy as np
import pandas as pd
cimport cython
from cpython cimport bool

cdef np.int64_t _nanos_in_minute = 60000000000
NANOS_IN_MINUTE = _nanos_in_minute

cpdef enum:
    BAR = 0
    SESSION_START = 1
    SESSION_END = 2
    MINUTE_END = 3
    BEFORE_TRADING_START_BAR = 4

cdef class MinuteSimulationClock:
    cdef bool minute_emission
    cdef np.int64_t[:] market_opens_nanos, market_closes_nanos, bts_nanos, \
        sessions_nanos, am_end_nanos, pm_start_nanos
    cdef dict minutes_by_session

    def __init__(self,
                 sessions,
                 market_opens,
                 market_closes,
                 before_trading_start_minutes,
                 minute_emission=False):
        self.minute_emission = minute_emission

        self.market_opens_nanos = market_opens.values.astype(np.int64)
        # 🆗 传入时间为utc，Asia/Shanghai am_end 11:30 -> 3:30 pm_start 13:01 -> 5:01
        self.am_end_nanos = market_opens.index.map(lambda x:x.replace(hour=3,minute=30)).values.astype(np.int64)
        self.pm_start_nanos = market_opens.index.map(lambda x:x.replace(hour=5,minute=1)).values.astype(np.int64)
        self.market_closes_nanos = market_closes.values.astype(np.int64)
        self.sessions_nanos = sessions.values.astype(np.int64)
        self.bts_nanos = before_trading_start_minutes.values.astype(np.int64)

        self.minutes_by_session = self.calc_minutes_by_session()

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef dict calc_minutes_by_session(self):
        cdef dict minutes_by_session
        cdef int session_idx
        cdef np.int64_t session_nano
        cdef np.ndarray[np.int64_t, ndim=1] minutes_nanos, am_minutes_nanos, pm_minutes_nanos

        minutes_by_session = {}
        for session_idx, session_nano in enumerate(self.sessions_nanos):
            # 🆗 固定上午结束、下午开始时间，且忽略延迟开盘及提早收盘
            am_minutes_nanos = np.arange(
                self.market_opens_nanos[session_idx],
                self.am_end_nanos[session_idx] + _nanos_in_minute,
                _nanos_in_minute
            )
            pm_minutes_nanos = np.arange(
                self.pm_start_nanos[session_idx],
                self.market_closes_nanos[session_idx] + _nanos_in_minute,
                _nanos_in_minute
            )
            minutes_nanos = np.append(am_minutes_nanos, pm_minutes_nanos)
            minutes_by_session[session_nano] = pd.to_datetime(
                minutes_nanos, utc=True
            ).sort_values()
        return minutes_by_session

    def __iter__(self):
        minute_emission = self.minute_emission

        for idx, session_nano in enumerate(self.sessions_nanos):
            print("SESSION_START", pd.Timestamp(session_nano, tz='UTC'))
            yield pd.Timestamp(session_nano, tz='UTC'), SESSION_START

            bts_minute = pd.Timestamp(self.bts_nanos[idx], tz='UTC')
            regular_minutes = self.minutes_by_session[session_nano]

            print("bts_minute", bts_minute)
            print("常规分钟", regular_minutes)

            if bts_minute > regular_minutes[-1]:
                print('before_trading_start is after the last close')
                print("================================")
                # before_trading_start is after the last close,
                # so don't emit it
                for minute, evt in self._get_minutes_for_list(
                    regular_minutes,
                    minute_emission
                ):
                    print(minute, repr(evt))
                    yield minute, evt
            else:
                print("bts_minute <= regular_minutes[-1]")
                print(bts_minute, regular_minutes[-1])
                print("================================")
                # we have to search a new every session, because there is no
                # guarantee that any two session start on the same minute
                bts_idx = regular_minutes.searchsorted(bts_minute)

                # emit all the minutes before bts_minute
                for minute, evt in self._get_minutes_for_list(
                    regular_minutes[0:bts_idx],
                    minute_emission
                ):
                    print(minute, repr(evt))
                    yield minute, evt
                print("BEFORE_TRADING_START_BAR", bts_minute)
                yield bts_minute, BEFORE_TRADING_START_BAR

                # emit all the minutes after bts_minute
                for minute, evt in self._get_minutes_for_list(
                    regular_minutes[bts_idx:],
                    minute_emission
                ):
                    print(minute, repr(evt))
                    yield minute, evt
            print("SESSION_END", regular_minutes[-1])
            yield regular_minutes[-1], SESSION_END

    def _get_minutes_for_list(self, minutes, minute_emission):
        for minute in minutes:
            print("BAR", minute)
            yield minute, BAR
            if minute_emission:
                print("MINUTE_END", minute)
                yield minute, MINUTE_END