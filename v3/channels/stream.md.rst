``stream`` - Reliable Data Streams
==================================

One of the most common needs between any two endpoints is creating
streams of data. The ``"type":"stream"`` reliable channel is a request
from one endpoint to open a stream to another.

The stream open request may contain a single additional packet attached
as the ``BODY`` that is the options for this stream request, these
options should contain anything the recipient app needs to determine
what the stream is for and to create it.

.. code:: json

    {
      "c":1,
      "type":"stream"
    }
    BODY: ...

Once accepted (and once the open packet is acknowledged), the stream may
immediately begin sending data in either direction. All streamed data is
attached as the binary ``BODY`` to every packet. The ``JSON`` may
contain one of the following options:

-  ``"chunk":true`` - when set, the attached BODY should be buffered
   along with any other chunks in order, until a packet is received
   without a chunk at which time they are all processed
-  ``"enc":"..."`` - what encoding is the attached data, current options
   are: ``binary`` (default), ``json``, and ```lob`` <../lob/>`__. This
   applies to any buffered chunks as well at the time it's processed
   (``enc`` is not valid to be set when ``chunk`` is true).

Any channel ``end`` or ``err`` is processed normally and has the same
implications for a stream.
