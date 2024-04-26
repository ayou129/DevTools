from setuptools import setup, find_packages

setup(
    name='DevTools',  # 项目名称
    version='1.0.0',  # 项目版本
    author='liguoxin',  # 作者
    # long_description=open('README.md').read(),  # 项目详细描述，可以从 README.md 中读取
    # long_description_content_type='text/markdown',  # 描述内容类型
    # url='https://your-project-url',  # 项目网址
    # packages=find_packages(),  # 包和模块
    install_requires=[
        'PySide6',  # 项目所需依赖项
        'importlib',
        'pickle5',
        'chardet',
        'htmlentitydefs',
        'msvcrt',
        'org',
        'multiprocessing',
        'platformdirs',
        'jnius',
        'java',
        'numpy',
        # 添加其他依赖项，例如 'numpy', 'pandas' 等
    ],
    entry_points={
        'console_scripts': [
            'build=DevTools.main:MyWindow',  # 可执行文件入口点
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.9',
        # 添加其他分类，如 'Development Status :: 4 - Beta' 等
    ],
)
