``connect`` - Peer Connection Request
=====================================

A connect channel is only created from a router that has received and
validated a `peer <peer.md.rst>`__ request. The original ``BODY`` of the
peer open is attached as the ``BODY`` of the ``"type":"connect"``
unreliable channel open packet. The original sender is included as
``"peer":"uvabrvfqacyvgcu8kbrrmk9apjbvgvn2wjechqr3vf9c1zm3hv7g"`` so
that the recipient can track multiple handshakes from the same source.

The recipient should parse the attached ``BODY`` as a packet and process
it as `handshake <../e3x/handshake.md.rst>`__, either encrypted or
unencrypted (if the sender doesn't have the recipient's keys yet). At
least one of the handshakes should be a `key <../e3x/cs/#packet>`__ to
guarantee the recipient can respond. If any of them are invalid the
requests should be ignored and the channel will timeout silently.

When accepted, a `peer path <path.md.rst>`__ should be implicitly added
to the sender's hashname via the incoming router. When the processing of
the attached packet results in a response handshake, it should then be
delivered via a subsequent peer request via the same router.

Automatic Bridging
------------------

When the incoming connect request has a ``BODY`` that is a validated
handshake, the current network path it was received on should also be
added as a network path to hashname of the handshake, since the router
is providing automatic bridging for encrypted channel packets.
