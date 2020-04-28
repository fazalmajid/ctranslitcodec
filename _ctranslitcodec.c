#include <stdlib.h>
#include <string.h>
#include "Python.h"

#include "_ctranslitcodec.h"

#include "ctable.c"

static const node *lookup(unsigned int c, const node *table, const int tlen) {
  int i;

  i = 0;
  while(i < tlen && table[i].unichar) {
    if (table[i].unichar == c) {
      return &table[i];
    }
    if (c < table[i].unichar) {
      i = 2 * i + 1;
    } else {
      i = 2 * i + 2;
    }
  }
  return NULL;
}

static PyObject *translit(PyObject *args, const node *table, const int tlen) {
  Py_UCS4 c;
  char *cout, buf[CTLC_BUFSIZE], *spill, *cmax, utf8buf[5];
  const char *exp;
  int len, kind;
  size_t spill_len;
  Py_ssize_t in_len, i;
  PyObject *in, *out;
  void *data;
  
  if (!PyArg_ParseTuple(args, "U", &in)) {
    return NULL;
  }
  if (PyUnicode_READY(in) != 0) return NULL;
  in_len = PyUnicode_GET_LENGTH(in);
  kind = PyUnicode_KIND(in);
  data = PyUnicode_DATA(in);
  /* XXX should normalize to NFKC for consistency with translitcodec */
  cout = buf;
  spill = NULL;
  spill_len = CTLC_BUFSIZE;
  cmax = buf + CTLC_BUFSIZE - 1;
  utf8buf[4] = '\0';

  for(i=0; i<in_len; i++) {
    c = PyUnicode_READ(kind, data, i);
    /* ASCII printable and non-BMP characters are invariant */
    if ((c >= 32 && c < 127) || c > 65535) {
      len = -1; /* means c needs to be UTF-encoded to determine len */
    } else {
      const node *dec = lookup(c, table, tlen);
      if (!dec) {
        len = -1;
      } else {
        len = dec->len;
        exp = ctlc_strings[dec->pos];
      }
    }
    if (len == -1) {
      /* character is left invariant, but needs to be encoded from
         UCS-4 to UTF-8
         Sadly Python3's internal unicode_encode_utf8 is static and thus not
         accessible from an extension like ourselves
      */
      exp = utf8buf;
      if (c <= 0x7f) {
        utf8buf[0] = c & 0x7f;
        len = 1;
      } else if (c <= 0x7ff) {
        utf8buf[0] = 0xc0 | ((c & 0x7c0) >> 6);
        utf8buf[1] = 0x80 | (c & 0x3f);
        len = 2;
      } else if (c <= 0xffff) {
        utf8buf[0] = 0xe0 | ((c & 0xf000) >> 12);
        utf8buf[1] = 0x80 | ((c & 0xfc0) >> 6);
        utf8buf[2] = 0x80 | (c & 0x3f);
        len = 3;
      } else {
        utf8buf[0] = 0xf0 | ((c & 0x1c0000) >> 18);
        utf8buf[1] = 0x80 | ((c & 0x3f000) >> 12);
        utf8buf[2] = 0x80 | ((c & 0xfc0) >> 6);
        utf8buf[3] = 0x80 | (c & 0x3f);
        len = 4;
      }
      #if 0
      /* XXX */
      if (len > 1) {
        int i;
        printf("UTF-8 0x%x\n", (unsigned int) c);
        for (i=0; i<len; i++) {
          printf("%d/%d %u %x\n", i, len, ((unsigned char *) utf8buf)[i], ((unsigned char *) utf8buf)[i]);
        }
      }
      /* /XXX */
      #endif
    }
    while (cout + len > cmax) {
      int copy = (spill == NULL);
      ssize_t offset = copy ? cout - buf : cout - spill;
      spill_len += CTLC_BUFSIZE;
      spill = realloc(spill, spill_len);
      if (spill == NULL) {
        PyErr_NoMemory();
        return NULL;
      }
      cmax = spill + spill_len - 1;
      if (copy) {
        memcpy(spill, buf, (cout - buf));
      }
      cout = spill + offset;
    }
    memcpy(cout, exp, len);
    cout += len;
  }
  spill = spill ? spill : buf;
  *cout = '\0';

#if 0
  /* XXX */
  {
    int i;
    for (i=0; spill[i]!=0; i++) {
      printf("SPILL %d %c %u 0x%x\n", i, spill[i], ((unsigned char *) spill)[i], ((unsigned char *) spill)[i]);
    }
  }
  /* /XXX */
#endif
  out = Py_BuildValue("s", spill);
  if (spill != buf) {
    free(spill);
  }
  return out;
}

char *testvec[] = {
  "sopo la pougne",
  "£1.95"
};

static PyObject *ctlc_short_encode(PyObject *self, PyObject *args) {
  return translit(args, ctlc_short_table, ctlc_short_tlen);
}

static PyObject *ctlc_long_encode(PyObject *self, PyObject *args) {
  return translit(args, ctlc_long_table, ctlc_long_tlen);
}

static PyObject *ctlc_single_encode(PyObject *self, PyObject *args) {
  return translit(args, ctlc_single_table, ctlc_single_tlen);
}

static char ctlc_short_doc[] =
  "Transliterate to 8 bit using as few letters as possible.\n"
  "For example, \u00e4 LATIN SMALL LETTER A WITH DIAERESIS 'ä' will\n"
  "be replaced with 'a'\n";

static char ctlc_long_doc[] =
  "Transliterate to 8 bit using as many letters as needed.\n"
  "For example, \u00e4 LATIN SMALL LETTER A WITH DIAERESIS 'ä' will\n"
  "be replaced with 'ae'\n";

static char ctlc_single_doc[] =
  "Transliterate to 8 bit using only single letter replacements.\n"
  "For example, \u2639 WHITE FROWNING FACE '☹' will be passed\n"
  "through unchanged.\n";

/* List of functions defined in the module */

static PyMethodDef ctlc_methods[] = {
  {"short_encode", ctlc_short_encode, METH_VARARGS, ctlc_short_doc},
  {"long_encode", ctlc_long_encode, METH_VARARGS, ctlc_long_doc},
  {"single_encode", ctlc_single_encode, METH_VARARGS, ctlc_single_doc},
  {NULL,	  NULL}	/* sentinel */
};


/* Initialization function for the module */

static char ctlc_doc[] =
  "Fast C Unicode to 8-bit charset transliteration codec,\n"
  "inspired by the translitcodec module by Jason Kirtland.\n\n"
  "This package contains codecs for transliterating ISO 10646 texts into\n"
  "best-effort representations using smaller coded character sets (ASCII,\n"
  "ISO 8859, etc.).\n\n"
  "The translation tables used by the codecs are from the 'transtab'\n"
  "collection by Prof. Markus Kuhn, augmented by Fazal Majid.\n\n\n"
  ":copyright: the translitcodec authors and developers, see AUTHORS.\n"
  ":license: MIT, see LICENSE for more details.\n";

static struct PyModuleDef ctlc_module = {
  PyModuleDef_HEAD_INIT,
  "_ctranslitcodec",
  ctlc_doc,
  -1,
  ctlc_methods
};

PyMODINIT_FUNC PyInit__ctranslitcodec(void) {
  return PyModule_Create(&ctlc_module);
}
