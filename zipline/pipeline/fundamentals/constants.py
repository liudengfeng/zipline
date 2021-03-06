"""

部门编码

"""

SUPER_SECTOR_NAMES = {
    1: '周期',  # 'Cyclical'),
    2: '防御',  # 'Defensive'),
    3: '敏感',  # 'Sensitive'),
}

SECTOR_NAMES = {
    101: '基本材料',  # 'BASIC_MATERIALS'),
    102: '主要消费',  # 'CONSUMER_CYCLICAL'),
    103: '金融服务',  # 'FINANCIAL_SERVICES'),
    104: '房地产',    # 'REAL_ESTATE'),
    205: '可选消费',  # 'CONSUMER_DEFENSIVE'),
    206: '医疗保健',  # 'HEALTHCARE'),
    207: '公用事业',  # 'UTILITIES'),
    308: '通讯服务',  # 'COMMUNICATION_SERVICES'),
    309: '能源',      # 'ENERGY'),
    310: '工业领域',  # 'INDUSTRIALS'),
    311: '工程技术',  # 'TECHNOLOGY'),
}

# 国证一级行业分类转换为`SECTOR`编码
CN_TO_SECTOR = {
    'Z01': 309,
    'Z02': 101,
    'Z03': 310,
    'Z04': 205,
    'Z05': 102,
    'Z06': 206,
    'Z07': 103,
    'Z08': 311,
    'Z09': 308,
    'Z10': 207,
    'Z11': 104,
}

# 申万编码转换映射表
SW_SECTOR_MAPS = {
    801010: 'S11',  # 农林牧渔
    801020: 'S21',  # 采掘
    801030: 'S22',  # 化工
    801040: 'S23',  # 钢铁
    801050: 'S24',  # 有色金属
    801080: 'S27',  # 电子
    801110: 'S33',  # 家用电器
    801120: 'S34',  # 食品饮料
    801130: 'S35',  # 纺织服装
    801140: 'S36',  # 轻工制造
    801150: 'S37',  # 医药生物
    801160: 'S41',  # 公用事业
    801170: 'S42',  # 交通运输
    801180: 'S43',  # 房地产
    801200: 'S45',  # 商业贸易
    801210: 'S46',  # 休闲服务
    801230: 'S51',  # 综合
    801710: 'S61',  # 建筑材料
    801720: 'S62',  # 建筑装饰
    801730: 'S63',  # 电气设备
    801740: 'S65',  # 国防军工
    801750: 'S71',  # 计算机
    801760: 'S72',  # 传媒
    801770: 'S73',  # 通信
    801780: 'S48',  # 银行
    801790: 'S49',  # 非银金融
    801880: 'S28',  # 汽车
    801890: 'S64',  # 机械设备
}

SW_SECTOR_NAMES = {
    801010: '农林牧渔',  # 'AGRICULTURE'
    801020: '采掘',  # MINING
    801030: '化工',  # CHEMICALS
    801040: '钢铁',  # STEEL
    801050: '有色金属',  # METALS
    801080: '电子',  # ELECTRONICS
    801110: '家用电器',  # APPLIANCES
    801120: '食品饮料',  # FOOD
    801130: '纺织服装',  # TEXTILES
    801140: '轻工制造',  # LIGHT_MANUFACTURING
    801150: '医药生物',  # PHARMACEUTICALS
    801160: '公用事业',  # UTILITIES
    801170: '交通运输',  # TRANSPORTATION
    801180: '房地产',  # REAL_ESTATE
    801200: '商业贸易',  # COMMERCE
    801210: '休闲服务',  # SERVICES
    801230: '综合',  # CONGLOMERATE
    801710: '建筑材料',  # BUILDING_MATERIALS
    801720: '建筑装饰',  # BUILDING_DECORATIONS
    801730: '电气设备',  # ELECTRICALS
    801740: '国防军工',  # DEFENSE_MILITARY
    801750: '计算机',  # IT
    801760: '传媒',  # MEDIA
    801770: '通信',  # COMMUNICATION_SERVICES
    801780: '银行',  # BANKS
    801790: '非银金融',  # NONBANK_FINANCIALS
    801880: '汽车',  # AUTO
    801890: '机械设备',  # MACHINERY
}
