import setuptools

setuptools.setup(
    name="code-dumper",
    version="0.1.0",
    author="Pranav Nutalapati",
    author_email="pranavnutalapati@gmail.com",
    description="A dependency analyzer and tree-shaker to dump a specific class/function.",
    url="https://github.com/preyneyv/code-dumper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
