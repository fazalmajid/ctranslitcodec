#ifndef CTRANSLITCODEC_H

typedef struct {
  unsigned int unichar;
  short pos;
  short len; /* length of UTF-8 encoded replacement, in bytes */
} node;

/* 100K */
#define CTLC_BUFSIZE 131072

#define CTRANSLITCODEC_H 1
#endif
