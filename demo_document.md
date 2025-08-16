# Python 编程基础教程

## 第一章：Python 简介

Python 是一种高级编程语言，由 Guido van Rossum 于 1989 年发明。它以其简洁的语法和强大的功能而闻名。

### 1.1 Python 的特点

- **简洁易读**：Python 的语法接近自然语言
- **跨平台**：可在 Windows、macOS、Linux 等系统运行
- **丰富的库**：拥有大量第三方库和框架
- **面向对象**：支持面向对象编程范式

### 1.2 Python 的应用领域

1. **Web 开发**：Django、Flask 等框架
2. **数据科学**：NumPy、Pandas、Matplotlib
3. **人工智能**：TensorFlow、PyTorch、scikit-learn
4. **自动化脚本**：系统管理、测试自动化

## 第二章：环境搭建

### 2.1 安装 Python

访问 [python.org](https://python.org) 下载最新版本的 Python。

#### Windows 安装步骤：
1. 下载 Python 安装包
2. 运行安装程序
3. 勾选"Add Python to PATH"
4. 点击"Install Now"

#### macOS 安装步骤：
1. 使用 Homebrew：`brew install python`
2. 或下载官方安装包

### 2.2 验证安装

打开命令行，输入：
```bash
python --version
```

应该显示 Python 版本信息。

### 2.3 选择开发环境

推荐的 Python 开发环境：
- **PyCharm**：功能强大的 IDE
- **VS Code**：轻量级编辑器
- **Jupyter Notebook**：交互式开发环境

## 第三章：基础语法

### 3.1 变量和数据类型

Python 中的基本数据类型：

```python
# 整数
age = 25

# 浮点数
height = 1.75

# 字符串
name = "张三"

# 布尔值
is_student = True

# 列表
fruits = ["苹果", "香蕉", "橙子"]

# 字典
person = {
    "name": "李四",
    "age": 30,
    "city": "北京"
}
```

### 3.2 控制结构

#### 条件语句
```python
score = 85

if score >= 90:
    print("优秀")
elif score >= 80:
    print("良好")
elif score >= 60:
    print("及格")
else:
    print("不及格")
```

#### 循环语句
```python
# for 循环
for i in range(5):
    print(f"第 {i+1} 次循环")

# while 循环
count = 0
while count < 3:
    print(f"计数：{count}")
    count += 1
```

### 3.3 函数定义

```python
def greet(name, age=18):
    """
    问候函数
    
    Args:
        name (str): 姓名
        age (int): 年龄，默认为18
    
    Returns:
        str: 问候语
    """
    return f"你好，{name}！你今年{age}岁。"

# 调用函数
message = greet("小明", 20)
print(message)
```

## 第四章：面向对象编程

### 4.1 类的定义

```python
class Student:
    def __init__(self, name, student_id):
        self.name = name
        self.student_id = student_id
        self.courses = []
    
    def add_course(self, course):
        self.courses.append(course)
        print(f"{self.name} 已选课：{course}")
    
    def get_info(self):
        return f"学生：{self.name}，学号：{self.student_id}"

# 创建对象
student1 = Student("王五", "2023001")
student1.add_course("Python 编程")
print(student1.get_info())
```

### 4.2 继承

```python
class GraduateStudent(Student):
    def __init__(self, name, student_id, advisor):
        super().__init__(name, student_id)
        self.advisor = advisor
    
    def get_info(self):
        base_info = super().get_info()
        return f"{base_info}，导师：{self.advisor}"

# 使用继承
grad_student = GraduateStudent("赵六", "2023002", "张教授")
print(grad_student.get_info())
```

## 第五章：常用库介绍

### 5.1 标准库

Python 内置了许多有用的模块：

```python
import datetime
import os
import json

# 日期时间
now = datetime.datetime.now()
print(f"当前时间：{now}")

# 文件操作
current_dir = os.getcwd()
print(f"当前目录：{current_dir}")

# JSON 处理
data = {"name": "Python", "version": "3.9"}
json_str = json.dumps(data, ensure_ascii=False)
print(f"JSON 字符串：{json_str}")
```

### 5.2 第三方库

#### requests - HTTP 请求
```python
import requests

response = requests.get("https://api.github.com/users/python")
if response.status_code == 200:
    user_data = response.json()
    print(f"用户名：{user_data['login']}")
```

#### pandas - 数据处理
```python
import pandas as pd

# 创建数据框
data = {
    "姓名": ["张三", "李四", "王五"],
    "年龄": [25, 30, 35],
    "城市": ["北京", "上海", "广州"]
}

df = pd.DataFrame(data)
print(df)
```

## 第六章：项目实践

### 6.1 简单计算器

```python
class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        if b != 0:
            return a / b
        else:
            return "错误：除数不能为零"

# 使用计算器
calc = Calculator()
print(f"10 + 5 = {calc.add(10, 5)}")
print(f"10 - 5 = {calc.subtract(10, 5)}")
print(f"10 * 5 = {calc.multiply(10, 5)}")
print(f"10 / 5 = {calc.divide(10, 5)}")
```

### 6.2 文件处理程序

```python
def process_text_file(filename):
    """
    处理文本文件，统计行数和字符数
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            line_count = len(lines)
            char_count = sum(len(line) for line in lines)
            
            return {
                "文件名": filename,
                "行数": line_count,
                "字符数": char_count
            }
    except FileNotFoundError:
        return {"错误": "文件未找到"}
    except Exception as e:
        return {"错误": str(e)}

# 使用示例
result = process_text_file("example.txt")
print(result)
```

## 总结

本教程介绍了 Python 编程的基础知识，包括：

1. **语言特点**：简洁、易读、功能强大
2. **环境搭建**：安装和配置开发环境
3. **基础语法**：变量、控制结构、函数
4. **面向对象**：类、继承、封装
5. **常用库**：标准库和第三方库
6. **项目实践**：实际编程示例

继续学习 Python，建议：
- 多练习编程题目
- 参与开源项目
- 学习专业领域的库和框架
- 关注 Python 社区动态

Python 是一门优秀的编程语言，掌握它将为你的编程之路打下坚实的基础！
