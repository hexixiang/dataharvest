# DataHarvest

DataHarvest 是一个专为构建大型语言模型数据集而设计的工具集。它提供了一系列的数据获取、清洗和处理的pipeline，旨在为中文大模型提供高质量的训练数据。

## 特性

- **数据获取**: 从多种来源自动获取数据，包括网站、API、文档等。
- **数据清洗**: 清洗和预处理数据，去除噪声、重复和无关内容。
- **数据转换**: 将数据转换为适合训练的格式，如文本、序列等。
- **自定义pipeline**: 灵活的pipeline配置，允许用户根据需要定制数据处理流程。

## 安装

1. 克隆仓库：

    ```bash
    git clone https://github.com/yourusername/dataharvest.git
    ```

2. 安装依赖：

    ```bash
    pip install -r requirements.txt
    ```

## 使用方法

### 数据获取

```python
from dataharvest import data_fetcher

# 获取数据
data = data_fetcher.fetch_data(source='web', url='https://example.com')

# 保存数据
data.to_csv('data.csv')
```

### 数据清洗

```python
from dataharvest import data_cleaner

# 加载数据
data = data_cleaner.load_data('data.csv')

# 清洗数据
clean_data = data_cleaner.clean(data)

# 保存清洗后的数据
clean_data.to_csv('clean_data.csv')
```

### 构建pipeline

```python
from dataharvest import Pipeline

# 初始化pipeline
pipeline = Pipeline([
    ('fetch', data_fetcher.fetch_data),
    ('clean', data_cleaner.clean),
    ('transform', lambda x: x)  # 添加其他转换函数
])

# 执行pipeline
processed_data = pipeline.execute(source='web', url='https://example.com')

# 保存处理后的数据
processed_data.to_csv('processed_data.csv')
```

## 贡献

如果您有任何建议或希望为项目做出贡献，请随时提出 issue 或发送 pull request。我们欢迎任何形式的贡献！

## 许可证

本项目采用 MIT 许可证。详细信息请参阅 [LICENSE](LICENSE) 文件。

---

希望 DataHarvest 能够帮助您构建高质量的中文语言模型数据集！如果您有任何问题或建议，请随时联系我们。