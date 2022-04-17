import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="piccolo_cursor_pagination",
    version="0.2.2",
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
    packages=["piccolo_cursor_pagination"],
    package_data={
        "piccolo_cursor_pagination": ["py.typed"],
    },
    install_requires=["fastapi", "piccolo"],
    python_requires=">=3.7",
)
