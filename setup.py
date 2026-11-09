from setuptools import setup, find_packages

setup(
    name="resume_screener_skill_gap",
    version="1.0.0",
    author="Khushi Yadav",
    author_email="ky19tech@gmail.com",
    description="AI-powered ATS Resume Screener, Skill-Gap Analyzer, and Personalized Learning Roadmap Generator for Engineering Students",
    long_description=open("README.md", encoding="utf-8").read() if open("README.md", encoding="utf-8") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/khushiyadav35/resume-screener-skill-gap-analyzer",
    packages=find_packages(where="."),
    package_dir={"": "."},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Education",
    ],
    python_requires=">=3.10",
    install_requires=[
        "streamlit>=1.35.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "pypdf>=4.0.0",
        "python-docx>=1.1.0",
        "plotly>=5.18.0",
    ],
)
