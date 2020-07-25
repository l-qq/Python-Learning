# 简单数据分析练习

## 搭建环境

``` powershell
scoop install anaconda3  # 安装发行包
```

接下来均是以命令行模式进行介绍，Windows 用户请打开 “Anaconda Prompt” 或 “Anaconda Powershell Prompt”

``` powershell
# 显示已创建环境
conda info --envs
conda info -e
conda env list
conda create --name data_analysis python=3  # 创建一个名为data_analysis的环境，环境中安装版本为3的python
conda activate data_analysis  # 进入该环境
conda list  # 获取当前环境中已安装的包信息
conda install matplotlib numpy pandas # 在当前环境中安装包
conda remove matplotlib  # 卸载当前环境中的包
conda update --all  # 更新所有包
conda update <package_name>  # 更新指定包
conda deactivate  # 退出环境
conda remove --name data_analysis --all  # 删除名为data_analysis的环境
```

> [Anaconda介绍、安装及使用教程](https://zhuanlan.zhihu.com/p/32925500)
