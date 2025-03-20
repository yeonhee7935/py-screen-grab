from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py-screen-grab",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple screen recording tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/py-screen-grab",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video :: Capture",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "mss>=6.1.0",
        "numpy>=1.19.0",
        "opencv-python>=4.5.0",
    ],
    entry_points={
        "console_scripts": [
            "py-screen-grab=py_screen_grab.cli:main",
        ],
    },
) 