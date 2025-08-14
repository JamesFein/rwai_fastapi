import requests
import json
import os

# 调用API
response = requests.get("http://localhost:8000/api/v1/outline/file/0001/000001")
data = response.json()

# 创建文件名
filename = "outline_" + data["course_id"] + "_" + data["course_material_id"] + ".md"
filepath = "D:/rwai_fastapi/try_fetch/" + filename

# 保存文件内容
with open(filepath, "w", encoding="utf-8") as f:
    f.write(data["file_content"])

print("文件已保存到:", filepath)
print("文件大小:", data["file_size"], "字节")
print("材料名称:", data["material_name"])
print("API响应状态:", data["success"])

