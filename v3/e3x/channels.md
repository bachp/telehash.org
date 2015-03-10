# Channels - Streaming Content Transport

All streaming data sent between two endpoints in an exchange must be part of a `channel` packet. Every channel has an integer id included as the `c` parameter in the JSON. See [Channel IDs](#ids) for details on how they are selected/handled.

A channel may have only one outgoing initial packet, only one response to it, or it may be long-lived with many packets exchanged using the same "c" identifier (depending on the type of channel).  Channels are by default unreliable, they have no retransmit or ordering guarantees, and an `end` always signals the last *content* packet being sent (acknowledgements/retransmits may still occur after).  When required, an app can also create a [reliable](reliable.md) channel that does provide ordering and retransmission functionality.

## Packet Size Default

Channel packets should always be a maximum of 1400 bytes or less each, which allows enough space for added variable encryption, token, and transport overhead to fit within 1500 bytes total (one ethernet frame).  Larger data should use reliable channels to sequence and reassemble pieces of this size, and transports with a fixed lower MTU than 1400 should use [chunked encoding](../chunking.md) by default.

A channel library should provide a `quota` method per packet for the app to determine how many bytes are available within the 1400 limit, and app-specific channel logic can use this to break larger data into packets.  In special cases (such as with a local high bandwidth transport) when the transport MTU is known, the app or custom channel logic may ignore this and send larger/smaller packets.

## Packet Encryption

All channel packets are encrypted using a stream cipher as determined by the [Cipher Set](cs/README.md) in use for the exchange.  The encrypted (OUTER) packets must have a `HEAD` of length 0 and the encrypted contents as the binary `BODY`.

Once decrypted they result in an INNER packet that must always contain valid JSON (have a `HEAD` of 7 or greater).

## Decrypted Packets


Base parameters on channel packets:

* `"type":"value"` - A channel always opens with a `type` in the first outgoing packet to distinguish to the recipient what the name/category of the channel it is. This value must only be set on the first packet (called the *open packet*), not on any subsequent ones or any responses.
* `"end":true` - Upon sending any content packet with an `end` of true, the sender must not send any more content packets (reliability acks/resends may still be happening though). An `end` may be sent by either side and is required to be sent by *both* to cleanly close a channel, otherwise the channel will eventually close with a timeout.
* `"err":"message"` - As soon as any packet on a channel is received with an `err` it is immediately closed and no more packets can be sent or received at all, any/all buffered content in either direction must be dropped. Any `err` packets must contain no channel content other than additional error details. Any internal channel inactivity timeout is the same as receiving an `"err":"timeout"`.
* `"seq":1` - A positive integer sequence number that is only used for and defined by [reliable](reliable.md) channels and must be sent in the first open packet along with the `type`, it is an error to send/receive this without using reliability on both sides.

An example unreliable channel start packet JSON for a built-in channel:

```json
{
	"c":1,
	"type":"path",
	"paths":[...]
}
```

An example initial reliable channel open request:

```json
{
	"c":2,
	"seq":1,
	"type":"hello",
	"hello":{"custom":"values"}
}
```

<a name="states"></a>
### Channel States

A channel may only be in one of the following states:

* `OPENING` - the initial channel open packet containing the `type` has been sent or received, but not confirmed or responded to yet and will time out in this state
* `OPEN` - the channel open packets have been both sent and received and it will not timeout unless the exchange does or reliability fails
* `ENDED` - a packet containing an `"end":true` has been received and no further content will be delivered for this channel, it will be timed out

These are the states that e3x manages, if an application requires additional states (such as when one party ended but the other hasn't) it must track them itself.  Any channel having received or sent an `err` is immediately removed after processing that packet and no more state is tracked, so e3x has no error state.  

Any channel in the `ENDED` state and has also sent an `end` is no longer available for any sending/receiving, but internal state will be tracked until the channel timeout for any necessary reliability retransmits/acknowledgements.

<a name="ids"></a>
### Channel IDs

A Channel ID is a *positive* integer (uint32_t) from 1 to 4,294,967,295 and is determined by the sender and then used by both sides to send/receive packets on that channel.  In order to prevent two endpoints from picking the same `c` value they choose them based on their [order](order.md): the `ODD` endpoint uses odd numbers starting with 1, and the `EVEN` endpoint uses even numbers starting with 2. 0 is never a valid ID.

When a new channel is created, the ID must be higher than the last one the initiator used, they must always increment. Upon receiving a new channel request, the recipient must validate that it is higher than the last active channel (note: switches must still allow for two new channel requests to arrive out of order).

When a new exchange is established, it errors any `OPEN` channels and sets the minimum required incoming channel IDs back to 1.

If the maximum ID is reached the exchange must be regenerated, resetting it back to 1.

<a name="timeouts"></a>
### Timeouts

Every channel is responsible for it's own timeout and may have a different value than others.  A timeout occurs whenever the channel is in `OPENING` or `ENDED` state or when any packet has not been ack'd for reliable channels.

Any channel that is in `OPEN` state will not trigger a timeout individually since the exchange as a whole will timeout if the connection is lost based on the network transports in use.  Those timeouts independently occur at a higher level for the overall exchange when the handshake process fails and do not use any channel timeout values.
