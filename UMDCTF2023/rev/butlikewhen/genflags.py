from english_words import get_english_words_set
import random

web2lowerset = list(get_english_words_set(['web2'], lower=True))

for k in range(0, 9999):
    print("\"UMDCTF{%s}\"," % "_".join(random.sample(web2lowerset, k = 5)).replace("-", "").replace("'", "").replace(" ", ""))