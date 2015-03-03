TCP Transport
=============

See `chunking <../lob/chunking.md.rst>`__ for how to encode one or more
packets on a standard TCP socket. All packets must be
`cloaked <../e3x/cloaking.md.rst>`__.

Local port binding is dynamic (bind to ``0``) unless given a specific
port. Implementations should support mapping the dynamic port via
NAT-PMP and UPnP when possible.

Multipath TCP
-------------

Research is ongoing on how `Multipath
TCP <http://en.wikipedia.org/wiki/Multipath_TCP>`__ can be used to
optimize a normal TCP path.

Timeout
-------

A new keepalive handshake may be automatically triggered when no packets
have been sent for 5 minutes as an extra validation that the TCP socket
is still connected.

Discovery
---------

By default a TCP transport cannot support general discovery for local
networks.

When given a specific IP and port to discover, the transport should
ensure that the IP is on a local subnet and may then send the
announcement packet(s) directly to that IP and port. If the connection
fails it may be retried once every 10 seconds, but if it succeeds and
doesn't respond then no further announcements should be sent as long as
it remains connected.

Path JSON
---------

Example `path <../channels/path.md.rst>`__ JSON for IPv4:

.. code:: json

    {
        "ip": "192.168.0.55",
        "port": 42424,
        "type": "tcp4"
    }

Example `path <../channels/path.md.rst>`__ JSON for IPv6:

.. code:: json

    {
        "ip": "fe80::bae8:56ff:fe43:3de4",
        "port": 42424,
        "type": "tcp6"
    }

