from setuptools import setup, find_packages

setup(
    name="imagen-desktop",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyQt6>=6.0.0",
        "replicate>=0.22.0",
        "SQLAlchemy>=2.0.0",
        "alembic>=1.13.0",
        "Pillow>=10.0.0",
        "requests>=2.31.0"
    ],
    entry_points={
        "console_scripts": [
            "imagen-desktop=imagen_desktop.main:main",
        ],
    },
    author="Ben Davies",
    description="Desktop client for Replicate's image generation models",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Desktop Environment",
    ],
    python_requires=">=3.8",
)