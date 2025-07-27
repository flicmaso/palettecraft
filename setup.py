from setuptools import setup, find_packages


setup(
    name="palettecraft",
    version="0.1.0",
    description="Extract and generate color palettes from images using k‑means and basic color theory.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Mason's AI Assistant",
    packages=find_packages(),
    install_requires=[
        "pillow>=8.0.0",
        "numpy>=1.20.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.4.0",
        "click>=8.0.0",
        "flask>=2.0.0",
    ],
    entry_points={
        "console_scripts": ["palettecraft=palettecraft.cli:main"],
    },
    python_requires=">=3.8",
    license="MIT",
)