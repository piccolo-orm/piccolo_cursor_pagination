import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="piccolo_cursor_pagination",
    version="0.1.0",
    author="sinisaos",
    author_email="sinisaos@gmail.com",
    description="Cursor pagination for Piccolo ORM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/piccolo-orm/piccolo_cursor_pagination",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    package_dir={"": "piccolo_cursor_pagination"},
    install_requires=["fastapi", "piccolo"],
    packages=setuptools.find_packages(where="piccolo_cursor_pagination"),
    python_requires=">=3.7",
)
