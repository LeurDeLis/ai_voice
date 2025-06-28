# 使用环境

> Python 3.8
>
> ffmpeg
>
> 阿里云百炼大模型

## 安装Python依赖库

```bash
pip install -r requirements.txt
```

## ffmpeg 安装

`ffmpeg` 下载地址：https://www.gyan.dev/ffmpeg/builds/#release-builds

<img src="media/image-20250628182036124.png" alt="image-20250628182036124" style="zoom: 67%;" />

安装步骤：

![image-20250628182519188](media/image-20250628182519188.png)

# API_KEY获取

注册阿里云账号：https://bailian.console.aliyun.com/#/home

创建API_KEY：

<img src="media/image-20250628184525269.png" alt="image-20250628184525269" style="zoom:67%;" />

<img src="media/image-20250628184533079.png" alt="image-20250628184533079" style="zoom: 33%;" />

配置API_KEY到系统环境变量里面, 右键开始菜单打开`CMD`

<img src="media/image-20250628185034408.png" alt="image-20250628185034408" style="zoom:67%;" />

<img src="media/image-20250628185051176.png" alt="image-20250628185051176" style="zoom:67%;" />

```bash
setx DASHSCOPE_API_KEY "sk-232xxxxxxxxxxxxxxxsdf"
```

![image-20250628185204682](media/image-20250628185204682.png)

查看环境变量是否生效（关闭当前终端再重新打开一个）

```bash
echo %DASHSCOPE_API_KEY%
```

<img src="media/image-20250628185248690.png" alt="image-20250628185248690" style="zoom:67%;" />

# 运行测试

可以使用Python打开项目运行根目录下的`main.py`文件，如图:

<img src="media/image-20250628184005373.png" alt="image-20250628184005373" style="zoom:67%;" />

或者在终端窗口运行下面的命令：

```
python3 main.py
```

## 运行效果

<img src="media/image-20250628185719453.png" alt="image-20250628185719453" style="zoom: 67%;" />

![image-20250628185735004](media/image-20250628185735004.png)