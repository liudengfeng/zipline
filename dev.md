# 测试及修订记录

- `zipline\_protocol.pyx`
  - 多asset、多字段时，使用MultiIndex DataFrame

## 代码

- `zipline\gens\sim_engine.pyx`
  - pd.to_datetime 弃用`box`参数
- `zipline\gens\sim_engine.pyx`
  - `MinuteSimulationClock`考虑午休时间
  - 增加测试`tests\data\test_minute_bar_internal.py`

## 测试

在目标环境下运行
```python
python -m pytest -vv <test_file.py>
```

- `tests\test_clock.py`

## 数据

- 同花顺股票概念 大类提取应该存在问题 ✅
- 以概念生效日期作为 asof_date

## 备注

- 尽量小范围改动代码
- 禁止全文复制，容易遗漏已经改动部分