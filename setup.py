import codecs
from distutils.core import setup
from distutils.extension import Extension
import sys


lines = codecs.open("README", "r", "utf-8").readlines()[3:]
# lines.extend(codecs.open("CHANGES", "r", "utf-8").readlines()[1:])
desc = u"".join(lines).lstrip()
if sys.version_info < (3, 0):
    raise Exception("Unsupported on Python 2.x")
    desc = desc.encode("utf-8")

setup(
    name="ctranslitcodec",
    version="0.1",
    description="Fast C Unicode to 8-bit charset transliteration codec",
    long_description=desc,
    author="Fazal Majid",
    author_email="python@sentfrom.com",
    url="https://github.com/fazalmajid/ctranslitcodec/",
    packages=["ctranslitcodec"],
    keywords=["Unicode"],
    license="MIT License",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
    ext_modules=[
        Extension("_ctranslitcodec", ["_ctranslitcodec.c"], extra_compile_args=["-O3"])
    ],
)
