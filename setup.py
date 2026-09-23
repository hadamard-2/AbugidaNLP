from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="abugida",
    version="0.4.0",
    packages=find_packages(),
    package_data={
        "abugida": ["SERA_table.json"],
    },
    install_requires=[],
    python_requires=">=3.10",
    description="NLP tools and resources for Ethiopian languages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["nlp", "ethiopian languages", "ethiopic", "abugida", "ge'ez"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    project_urls={
        "Source": "https://github.com/hadamard-2/abugidanlp",
    },
)
