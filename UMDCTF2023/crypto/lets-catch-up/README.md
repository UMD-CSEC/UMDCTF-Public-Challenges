# Let's catch up!

I should probably catch up with my buddy Alice on some important matters. It feels like ages since we last caught up. Only problem is, I seem to have misplaced my encryption key.

## Writeup

The only input required is a key (the flag).

File `a.js` is obfuscated using custom but purposefully imperfect transformations.

A helpful comment has been left at the top of the file:
```js
// hopefully this new obfuscation should
// prevent other hackers from finding
// my changes to this secret library
```

and untouched constants such as `0xc66363a5` should tell you it's likely a [JavaScript AES library](https://github.com/ricmoo/aes-js).

Another useful hint resides in a script tag inside `index.html`: 

`some garbage key, do i even need this?`

The key in question is not useful because inside the library we are overriding the encryption round keys after the [key schedule](https://en.wikipedia.org/wiki/AES_key_schedule) step.

The hardcoded encryption round keys are:

```js
[[1431127107, 1413905273, 880369457, 1601003876], [1700754287, 1835360110, 1702322027, 863581565], [-488916096, -1231175431, -2098946104, -578158932], [-1527199490, -912418928, -1393899269, -1617691258], [1016069979, -1978515550, 150380650, -713072954], [-1490382774, 1857488858, -1034039519, 1573794471], [-1280531689, 968793269, 826817759, -466132455], [-827311458, -1610138300, 1650127461, 1066713282], [-1726577054, -1599595817, -1847581176, 1977041937], [1404969244, -205972392, -1847333315, -1367920897], [2082967686, -594572719, 1299164249, 951642184], [1423096398, -1486117354, 914901035, -1728092460], [1242880192, -1768205679, -604700984, -481552768], [1174142339, -493855851, -736619586, 1290237290], [-1635132695, 135432312, -739871056, 816472112]]
```

and to invert this back into the normal encryption key, the following code is used:

```js
const Ke = [[1431127107, 1413905273, 880369457, 1601003876], [1700754287, 1835360110, 1702322027, 863581565], [-488916096, -1231175431, -2098946104, -578158932], [-1527199490, -912418928, -1393899269, -1617691258], [1016069979, -1978515550, 150380650, -713072954], [-1490382774, 1857488858, -1034039519, 1573794471], [-1280531689, 968793269, 826817759, -466132455], [-827311458, -1610138300, 1650127461, 1066713282], [-1726577054, -1599595817, -1847581176, 1977041937], [1404969244, -205972392, -1847333315, -1367920897], [2082967686, -594572719, 1299164249, 951642184], [1423096398, -1486117354, 914901035, -1728092460], [1242880192, -1768205679, -604700984, -481552768], [1174142339, -493855851, -736619586, 1290237290], [-1635132695, 135432312, -739871056, 816472112]];

const AES_BLOCK_SIZE = 4;

const BYTE0 = (num) => (((num) >> 24) & 0xFF);
const BYTE1 = (num) => (((num) >> 16) & 0xFF);
const BYTE2 = (num) => (((num) >> 8) & 0xFF);
const BYTE3 = (num)  => ((num) & 0xFF);

let key = [];

for (let i = 0; i < 8; i++) {
    const round_key = Ke[Math.floor(i / AES_BLOCK_SIZE)][Math.floor(i % AES_BLOCK_SIZE)];
    key.push([BYTE0(round_key), BYTE1(round_key),BYTE2(round_key),BYTE3(round_key)]);
}

console.log(key.flat().map(c => String.fromCharCode(c)).join(''));
```

revealing the flag `UMDCTF{y4y_1_made_some_new_k3y5}`

## Flag
`UMDCTF{y4y_1_made_some_new_k3y5}`
