#!/usr/local/bin/python3
import sys, os, unicodedata, timeit
sys.path.append(os.getcwd() + '/lib/python3.8/site-packages')
import ctranslitcodec, translitcodec, _ctranslitcodec

x = '£ ☹ wøóf méåw ﷲ etsi vereor judices ne turpe sit pro fortissimo viro incipientem timere minimeque deceat'

a = open('long.txt').read()
print(a)
assert '\u2639' in a
print(translitcodec.long_encode(a))
print(ctranslitcodec.long_encode(unicodedata.normalize('NFKC', a)))
assert ctranslitcodec.long_encode(unicodedata.normalize('NFKC', a))[0] \
  == translitcodec.long_encode(a)[0]
# validate UTF-8 encoding
for i in range(1, 0x10FFFF):
  try:
    c = chr(i)
    c.encode('utf-8')
  except:
    continue
  if len(unicodedata.normalize('NFKC', c)) != 1: continue
  if c in a: continue
  if unicodedata.normalize('NFKC', c) in a: continue
  try:
    assert ctranslitcodec.long_encode(c) == \
      (unicodedata.normalize('NFKC', c), 1)
    assert _ctranslitcodec.long_encode(c) == c
  except:
    print('FAILED AT', i, c)
    print(ctranslitcodec.long_encode(c), '!=', unicodedata.normalize('NFKC', c))
    raise

print('LONG')
y = translitcodec.long_encode(x)
print(x)
print(y)
print(ctranslitcodec.long_encode(x))
assert ctranslitcodec.long_encode(x) == y
assert ctranslitcodec.long_encode(x * 10000)[0] == y[0] * 10000
print()

print('SHORT')
y = translitcodec.short_encode(x)
print(x)
print(y)
print(ctranslitcodec.short_encode(x))
assert ctranslitcodec.short_encode(x) == y
assert ctranslitcodec.short_encode(x * 10000)[0] == y[0] * 10000
print()

print('SINGLE')
y = translitcodec.single_encode(x)
print(x)
print(y)
print(ctranslitcodec.single_encode(x))
assert ctranslitcodec.single_encode(x) == y
assert ctranslitcodec.single_encode(x * 10000)[0] == y[0] * 10000
print()

print('BENCHMARK translitcodec')
print(timeit.timeit('translitcodec.long_encode(x)', globals=globals()))
print()

print('BENCHMARK ctranslitcodec')
print(timeit.timeit('ctranslitcodec.long_encode(x)', globals=globals()))
