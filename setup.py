from setuptools import setup, find_packages

setup(
    name="py-screen-grab",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "mss>=6.1.0",
        "numpy>=1.19.0",
        "opencv-python>=4.5.0"
    ],
    entry_points={
        "console_scripts": [
            "py-screen-grab=py_screen_grab.cli:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple screen recording tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/py-screen-grab",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 