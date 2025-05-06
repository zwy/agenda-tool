<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# windows电脑如何安装python、pip

在Windows电脑上安装Python和pip的步骤如下：

## 1. 安装Python

1. 访问Python官网（https://www.python.org/downloads/），下载适合Windows的最新版本安装包（通常是`.exe`文件）[^3][^4][^5]。
2. 运行下载的安装程序时，**务必勾选“Add Python to PATH”**（将Python添加到系统环境变量），这样安装后可以在命令行直接使用`python`命令[^3][^5]。
3. 选择“Install Now”或“Customize installation”，确保pip选项已被选中（默认会安装pip）[^3][^5]。
4. 安装完成后，打开命令提示符（CMD），输入以下命令验证Python是否安装成功：

```bash
python --version
```

如果显示Python版本号，表示安装成功[^3][^5]。

## 2. 验证pip是否安装

Python安装程序通常会自动安装pip。你可以在命令提示符输入：

```bash
pip --version
```

如果显示pip版本，说明pip已安装[^2][^3][^5]。

## 3. 如果pip未安装，手动安装pip

如果pip未安装或命令无效，可以手动安装：

1. 下载`get-pip.py`脚本文件，安全下载地址可参考官方或可信来源[^1][^5]。
2. 打开命令提示符，进入`get-pip.py`所在目录，运行：

```bash
python get-pip.py
```

这会安装或升级pip，同时安装setuptools和wheel[^1][^5]。
3. 安装完成后，再次运行`pip --version`确认安装成功。

## 4. 配置环境变量（如果安装后命令无效）

有时Python和pip安装成功，但命令提示符无法识别`python`或`pip`命令，可能是环境变量未正确配置。可以手动添加：

1. 找到Python安装目录，例如：

```
C:\Users\用户名\AppData\Local\Programs\Python\Python3xx\
```

2. 找到Scripts目录，例如：

```
C:\Users\用户名\AppData\Local\Programs\Python\Python3xx\Scripts\
```

3. 右键“此电脑”→“属性”→“高级系统设置”→“环境变量”，在“用户变量”或“系统变量”中找到`Path`，点击“编辑”，添加上述两个路径[^3][^5][^6][^8]。
4. 保存后，重新打开命令提示符，输入`python --version`和`pip --version`验证。

## 5. pip的基本使用

安装成功后，可以用pip安装Python包，例如：

```bash
pip install 包名
```

升级pip：

```bash
python -m pip install -U pip
```

卸载包：

```bash
pip uninstall 包名
```

查看已安装包：

```bash
pip list
```

以上就是Windows电脑安装Python和pip的完整流程[^1][^2][^3][^4][^5][^6]。安装时建议直接使用Python官网的安装程序，确保pip自动安装并正确配置环境变量。

<div style="text-align: center">⁂</div>

[^1]: https://blog.csdn.net/acktomas/article/details/117926803

[^2]: https://blog.csdn.net/u012693479/article/details/126367014

[^3]: https://docs.aws.amazon.com/zh_cn/elasticbeanstalk/latest/dg/eb-cli3-install-windows.html

[^4]: https://www.cnblogs.com/chenxiaomeng/p/12638131.html

[^5]: https://www.wbolt.com/how-to-install-pip-in-windows.html

[^6]: https://developer.aliyun.com/article/644881

[^7]: https://www.paddlepaddle.org.cn/documentation/docs/zh/install/pip/windows-pip.html

[^8]: https://doc.aidaxue.com/python-install/python-pip-PATH.html

[^9]: https://learn.microsoft.com/zh-cn/windows/python/faqs

