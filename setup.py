from setuptools import setup, find_packages

setup(
    name="hackathon_project",
    version="0.1.0",
    author="Dhruv Sharma",
    author_email="dhruvsharma983@gmail.com",
    description="A project created for a hackathon.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here, e.g., 'requests', 'numpy'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)