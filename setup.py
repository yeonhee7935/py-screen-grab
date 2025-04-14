import sys
from setuptools import setup, find_packages

try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError as e:
    print(e)
    pass

__version__ = "1.4.0"
    
setup(
    name="py-screen-grab", 
    version=__version__,
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    install_requires=[
        "mss>=6.1.0",
        "numpy>=1.19.0",
        "opencv-python>=4.5.0",
        "rx>=3.2.0"
    ],
    entry_points={
        "console_scripts": [
            "screengrab=py_screen_grab.cli:main",
        ],
    },
    author="twid_yuni",
    author_email="jyhee7935@naver.com",
    description="A simple screen recording tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yeonhee7935/py-screen-grab",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        'Operating System :: POSIX :: Linux', 
    ],
    python_requires=">=3.6",
    test_suite="tests",
    tests_require=[
        "pytest>=6.0.0",
        "pytest-cov>=2.10.0",
    ],
) 