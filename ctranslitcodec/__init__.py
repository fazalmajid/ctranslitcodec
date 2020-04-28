# -*- coding: utf-8 -*-
"""Fast C Unicode to 8-bit charset transliteration codec,
inspired by the translitcodec module by Jason Kirtland.

This package contains codecs for transliterating ISO 10646 texts into
best-effort representations using smaller coded character sets (ASCII,
ISO 8859, etc.).

The translation tables used by the codecs are from the 'transtab'
collection by Prof. Markus Kuhn, augmented by Fazal Majid.

:copyright: the translitcodec authors and developers, see AUTHORS.
:license: MIT, see LICENSE for more details.
"""
import codecs
import sys
import unicodedata
import _ctranslitcodec

__version_info__ = (0, 1, 0)
__version__ = ".".join(str(_) for _ in __version_info__)

assert sys.version_info[0] >= 3


def long_encode(input, errors="strict"):
    """Transliterate to 8 bit using as many letters as needed.

    For example, \u00e4 LATIN SMALL LETTER A WITH DIAERESIS ``ä`` will
    be replaced with ``ae``.

    """
    if not isinstance(input, str):
        input = str(input, sys.getdefaultencoding(), errors)
    length = len(input)
    input = unicodedata.normalize("NFKC", input)
    return _ctranslitcodec.long_encode(input), length


def short_encode(input, errors="strict"):
    """Transliterate to 8 bit using as few letters as possible.

    For example, \u00e4 LATIN SMALL LETTER A WITH DIAERESIS ``ä`` will
    be replaced with ``a``.

    """
    if not isinstance(input, str):
        input = str(input, sys.getdefaultencoding(), errors)
    length = len(input)
    input = unicodedata.normalize("NFKC", input)
    return _ctranslitcodec.short_encode(input), length


def single_encode(input, errors="strict"):
    """Transliterate to 8 bit using only single letter replacements.

    For example, \u2639 WHITE FROWNING FACE ``☹`` will be passed
    through unchanged.

    """
    if not isinstance(input, str):
        input = str(input, sys.getdefaultencoding(), errors)
    length = len(input)
    input = unicodedata.normalize("NFKC", input)
    return _ctranslitcodec.single_encode(input), length


def no_decode(input, errors="strict"):
    raise TypeError("transliterating codec does not support decode.")


def _double_encoding_factory(encoder, byte_encoder, byte_encoding):
    """Send the transliterated output to another codec."""

    def dbl_encode(input, errors="strict"):
        uni, length = encoder(input, errors)
        return byte_encoder(uni, errors)[0], length

    dbl_encode.__name__ = "%s_%s" % (encoder.__name__, byte_encoding)
    return dbl_encode


def trans_search(encoding):
    """Lookup transliterating codecs."""
    if encoding == "transliterate":
        return codecs.CodecInfo(long_encode, no_decode)

    # translit/long/utf8
    # translit/one
    # translit/short/ascii

    if encoding.startswith("translit/"):
        parts = encoding.split("/")
        if parts[1] == "long":
            encoder = long_encode
        elif parts[1] == "short":
            encoder = short_encode
        elif parts[1] == "one":
            encoder = single_encode
        else:
            return None

        if len(parts) == 2:
            pass
        elif len(parts) == 3:
            byte_enc = parts[2]
            byte_encoder = codecs.lookup(byte_enc).encode
            encoder = _double_encoding_factory(encoder, byte_encoder, byte_enc)
        else:
            return None
        return codecs.CodecInfo(encoder, no_decode)
    return None


codecs.register(trans_search)
