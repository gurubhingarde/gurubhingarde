package com.gurubhingarde.adblocker

/** Minimal DNS / IPv4 / UDP packet helpers. */
object Dns {
    const val TYPE_A = 1
    const val TYPE_AAAA = 28

    class Query(val name: String, val type: Int, val questionEnd: Int)

    private fun u8(b: ByteArray, i: Int) = b[i].toInt() and 0xFF
    private fun u16(b: ByteArray, i: Int) = (u8(b, i) shl 8) or u8(b, i + 1)

    /** Parses the first question of a DNS query. Returns null if malformed or not a query. */
    fun parseQuery(d: ByteArray): Query? {
        if (d.size < 17) return null
        if (u16(d, 2) and 0x8000 != 0) return null // already a response
        if (u16(d, 4) < 1) return null
        var p = 12
        val sb = StringBuilder()
        while (true) {
            if (p >= d.size) return null
            val l = u8(d, p)
            if (l == 0) { p++; break }
            if (l and 0xC0 != 0 || p + 1 + l > d.size) return null
            if (sb.isNotEmpty()) sb.append('.')
            for (i in 1..l) sb.append(u8(d, p + i).toChar().lowercaseChar())
            p += 1 + l
        }
        if (p + 4 > d.size) return null
        return Query(sb.toString(), u16(d, p), p + 4)
    }

    /** Builds a reply that resolves the name to 0.0.0.0 / :: (empty answer for other types). */
    fun blockedResponse(d: ByteArray, q: Query): ByteArray {
        val hasAnswer = q.type == TYPE_A || q.type == TYPE_AAAA
        val rdLen = if (q.type == TYPE_A) 4 else 16
        val out = ByteArray(q.questionEnd + if (hasAnswer) 12 + rdLen else 0)
        System.arraycopy(d, 0, out, 0, q.questionEnd)
        out[2] = (0x80 or (d[2].toInt() and 0x01)).toByte() // QR=1, keep RD
        out[3] = 0x80.toByte()                              // RA=1, RCODE=0
        out[6] = 0; out[7] = if (hasAnswer) 1 else 0        // ANCOUNT
        out[8] = 0; out[9] = 0; out[10] = 0; out[11] = 0    // NSCOUNT, ARCOUNT
        if (hasAnswer) {
            var p = q.questionEnd
            out[p++] = 0xC0.toByte(); out[p++] = 0x0C           // name pointer to question
            out[p++] = 0; out[p++] = q.type.toByte()            // TYPE
            out[p++] = 0; out[p++] = 1                          // CLASS IN
            out[p++] = 0; out[p++] = 0; out[p++] = 0; out[p++] = 60 // TTL
            out[p++] = 0; out[p] = rdLen.toByte()               // RDLENGTH (RDATA stays zero)
        }
        return out
    }

    /** Wraps [payload] in an IPv4+UDP packet that answers the request packet [req]. */
    fun buildUdpReply(req: ByteArray, ihl: Int, payload: ByteArray): ByteArray {
        val total = 20 + 8 + payload.size
        val o = ByteArray(total)
        o[0] = 0x45
        o[2] = (total shr 8).toByte(); o[3] = total.toByte()
        o[6] = 0x40                         // don't fragment
        o[8] = 64                           // TTL
        o[9] = 17                           // UDP
        System.arraycopy(req, 16, o, 12, 4) // src = original dst
        System.arraycopy(req, 12, o, 16, 4) // dst = original src
        val ck = checksum(o, 20)
        o[10] = (ck shr 8).toByte(); o[11] = ck.toByte()
        System.arraycopy(req, ihl + 2, o, 20, 2) // src port = original dst port
        System.arraycopy(req, ihl, o, 22, 2)     // dst port = original src port
        val udpLen = 8 + payload.size
        o[24] = (udpLen shr 8).toByte(); o[25] = udpLen.toByte()
        System.arraycopy(payload, 0, o, 28, payload.size) // UDP checksum 0 = none (valid for IPv4)
        return o
    }

    private fun checksum(b: ByteArray, len: Int): Int {
        var sum = 0
        var i = 0
        while (i < len) { sum += u16(b, i); i += 2 }
        while (sum shr 16 != 0) sum = (sum and 0xFFFF) + (sum shr 16)
        return sum.inv() and 0xFFFF
    }
}
