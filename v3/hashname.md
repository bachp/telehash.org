# Hashnames

A `hashname` is a unique fingerprint to represent the union of one or more public keys of different formats ([Cipher Sets](e3x/cs/README.md)), providing consistent verifiable endpoint addresses utilizing multiple PKI systems. This enables a compatibility layer for adding or enhancing PKI in any application so that it can still represent itself securely to both existing and new endpoints.

In many ways, a `hashname` can be viewed as a portable secure [MAC address](http://en.wikipedia.org/wiki/MAC_address), it is a globally unique identifier for a network endpoint that is also self-generated and cryptographically verifiable.

The value of a `hashname` is always a [base 32](http://tools.ietf.org/html/rfc4648) encoded string that is 52 characters long, lower cased with [no padding](http://tools.ietf.org/html/rfc4648#section-3.2).  When decoded it is always a 32 byte binary value, the result of a [SHA-256](http://en.wikipedia.org/wiki/SHA-2) hash digest.  An example hashname is `kw3akwcypoedvfdquuppofpujbu7rplhj3vjvmvbkvf7z3do7kkq`.

Base32 encoding was chosen to maximize compatibilty and consistency, such that it is usable in any URI component, DNS labels, is case insensitive and alphanumeric only.

## Implementations

* [javascript](https://github.com/telehash/hashname) (node and browserify)
* [c](https://github.com/telehash/telehash-c/blob/master/src/lib/hashname.c)
* [c#](https://github.com/telehash/telehash.net/blob/master/Telehash.Net/Hashname.cs)
* [go](https://github.com/telehash/gogotelehash/tree/master/hashname)

## Hashname Generation

A hashname is calculated by combining one or more Cipher Set Keys ([CSK](e3x/cs/README.md)) through multiple rounds of [SHA-256](http://en.wikipedia.org/wiki/SHA-2) hashing.

The generation has three distinct steps, all of them operating on binary/byte inputs and outputs:

1. Every `CSK` is identified by a single unique `CSID` and sorted by it from low to high
2. Each `CSK` is hashed into `intermediate` digest values
3. Roll-up hashing of the `CSIDs` and intermediate values generates the final 32-byte digest

Any hashname generation software does not need to know or understand the Cipher Sets or support the algorithms defined there, it only has to do the consistent hashing of any given set of `CSID` and `CSK` pair inputs.

The `intermediate` digest values may be used and exchanged directly instead of the original `CSK` to minimize the amount of data required to calculate and verify a hashname.

### Final Rollup

To calculate the `hashname` the `intermediate` digests are sequentially hashed in ascending order by their `CSID`. Each one contributes two values: the single byte `CSID` value and the 32 byte `intermediate` digest value. The calculated hash is rolled up, wherein each resulting 32 byte binary output is concatenated with the next binary value as the input. An example calculation would look like (in pseudo-code):

```js
hash = sha256(0x1a)
hash = sha256(hash + 0x21b65ba5a9567fed892569f00090b3c17fd66a5c32d7b355940088605fa7f350)
hash = sha256(hash + 0x3a)
hash = sha256(hash + 0x97d83d1af8919874a449769145b7b3cb46359b2c12169ee53e683477bec47101)
final = hash
```

Here is a working example in node.js to do the calculation, results in `27ywx5e5ylzxfzxrhptowvwntqrd3jhksyxrfkzi6jfn64d3lwxa`

```js
var crypto = require("crypto");
var base32 = require("rfc-3548-b32"); // https://github.com/sehrope/node-rfc-3548-b32
var keys = {
  "3a":"eg3fxjnjkz763cjfnhyabeftyf75m2s4gll3gvmuacegax5h6nia",
  "1a": "an7lbl5e6vk4ql6nblznjicn5rmf3lmzlm"
};
var rollup = new Buffer(0);
Object.keys(keys).sort().forEach(function(id){
  rollup = crypto.createHash("sha256").update(Buffer.concat([rollup,new Buffer(id,"hex")])).digest();
  var intermediate = crypto.createHash("sha256").update(new Buffer(base32.decode(keys[id]),"binary")).digest();
  rollup = crypto.createHash("sha256").update(Buffer.concat([rollup,intermediate])).digest();
});
var hashname = base32.encode(rollup).toLowerCase().split("=").join(""); // normalize to lower case and remove padding
console.log(hashname); // prints 27ywx5e5ylzxfzxrhptowvwntqrd3jhksyxrfkzi6jfn64d3lwxa
```


