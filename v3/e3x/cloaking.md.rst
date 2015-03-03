Cloaking - Network Obfuscation
==============================

In situations where the network may be performing any packet filtering
or inspection it is important to add as much random noise as possible to
all bytes sent across an untrusted/unencrypted transport. Cloaking is a
simple and efficient technique that can be used on any transport and is
the default for all unencrypted ones by default (such as TCP and UDP).

The cloaking technique simply requires an extra processing step that
adds a random number of 8 byte nonces to every packet and randomizes
100% of the bytes on the wire. It makes large-scale pattern
identification techniques significantly more difficult, but is not a
guarantee that individual packets cannot be targetted. Future designs
will continually increase this difficulty.

Per-Packet
----------

Due to all encrypted packets beginning with single zero byte (0x00) when
sent on the wire (since they have no JSON encoded), cloaking uses a
first byte that is any non-zero value (0x01 to 0xff).

Cloaking is performed using the `ChaCha20
cipher <http://cr.yp.to/chacha.html>`__ and choosing a random nonce of 8
bytes that does not begin with 0x00. The key is a fixed well-known 32
byte value of
``d7f0e555546241b2a944ecd6d0de66856ac50b0baba76a6f5a4782956ca9459a``
(shown as hex encoded), which is the SHA-256 of the string ``telehash``.

The resulting cloaked packet is the concatenation of the 8-byte nonce
and the ChaCha20 ciphertext output. Once decloaked, the ciphertext
should be processed as another packet, which may be a raw encrypted
packet (0x00) or may be another cloaked one. A random number of multiple
cloakings should always be used to obfuscate the original packet's size.

Accept both
-----------

All implementations must support receiving both cloaked and uncloaked
packets, and the default for any un-encrypted transport should always be
cloaking enabled. The initial sender determines when to send un-cloaked
packets on any transport, but when receiving a cloaked packet any sender
should always respond with cloaked packets as that may be the only way
to ensure they are transmitted.
