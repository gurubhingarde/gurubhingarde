package com.gurubhingarde.adblocker

import android.content.Intent
import android.net.VpnService
import android.os.ParcelFileDescriptor
import java.io.FileInputStream
import java.io.FileOutputStream
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.net.InetSocketAddress
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicInteger

/**
 * Local VPN that captures only DNS traffic. Queries for ad domains get a dead-end answer
 * (0.0.0.0), everything else is forwarded to a real DNS server. All other traffic bypasses the VPN.
 */
class AdBlockVpnService : VpnService() {

    companion object {
        const val ACTION_STOP = "com.gurubhingarde.adblocker.STOP"
        private const val VIRTUAL_DNS = "10.111.222.2"
        private const val UPSTREAM_DNS = "1.1.1.1"

        @Volatile var running = false
        val blocked = AtomicInteger()
        val allowed = AtomicInteger()
    }

    private var tun: ParcelFileDescriptor? = null
    private var reader: Thread? = null
    private var pool: ExecutorService? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) {
            stop()
            return START_NOT_STICKY
        }
        if (!running) start()
        return START_STICKY
    }

    private fun start() {
        Blocklist.load(this)
        val fd = Builder()
            .setSession("AdBlocker")
            .addAddress("10.111.222.1", 32)
            .addDnsServer(VIRTUAL_DNS)
            .addRoute(VIRTUAL_DNS, 32) // only DNS goes through us
            .setBlocking(true)
            .establish() ?: return
        tun = fd
        blocked.set(0); allowed.set(0)
        running = true
        pool = Executors.newFixedThreadPool(8)
        reader = Thread({ readLoop(fd) }, "adblock-reader").also { it.start() }
    }

    private fun readLoop(fd: ParcelFileDescriptor) {
        val input = FileInputStream(fd.fileDescriptor)
        val output = FileOutputStream(fd.fileDescriptor)
        val buf = ByteArray(32767)
        val dnsIp = InetAddress.getByName(VIRTUAL_DNS).address
        try {
            while (running) {
                val n = input.read(buf)
                if (n <= 0) continue
                if (n < 28 || (buf[0].toInt() shr 4) != 4) continue          // IPv4 only
                val ihl = (buf[0].toInt() and 0x0F) * 4
                if (buf[9].toInt() != 17 || n < ihl + 8) continue             // UDP only
                if (!(0..3).all { buf[16 + it] == dnsIp[it] }) continue       // to our DNS
                val dport = ((buf[ihl + 2].toInt() and 0xFF) shl 8) or (buf[ihl + 3].toInt() and 0xFF)
                if (dport != 53) continue
                val packet = buf.copyOf(n)
                val payload = buf.copyOfRange(ihl + 8, n)
                pool?.execute { handleQuery(packet, ihl, payload, output) }
            }
        } catch (_: Exception) {
            // tun closed
        } finally {
            stop()
        }
    }

    private fun handleQuery(packet: ByteArray, ihl: Int, query: ByteArray, out: FileOutputStream) {
        val q = Dns.parseQuery(query)
        val answer: ByteArray? = if (q != null && Blocklist.isBlocked(q.name)) {
            blocked.incrementAndGet()
            Dns.blockedResponse(query, q)
        } else {
            allowed.incrementAndGet()
            forward(query)
        }
        if (answer == null) return
        val reply = Dns.buildUdpReply(packet, ihl, answer)
        try {
            synchronized(out) { out.write(reply) }
        } catch (_: Exception) {
        }
    }

    private fun forward(query: ByteArray): ByteArray? = try {
        DatagramSocket().use { s ->
            protect(s) // keep this socket outside the VPN to avoid a loop
            s.soTimeout = 4000
            s.send(DatagramPacket(query, query.size, InetSocketAddress(UPSTREAM_DNS, 53)))
            val resp = ByteArray(4096)
            val p = DatagramPacket(resp, resp.size)
            s.receive(p)
            resp.copyOf(p.length)
        }
    } catch (_: Exception) {
        null
    }

    private fun stop() {
        running = false
        try { tun?.close() } catch (_: Exception) {}
        tun = null
        pool?.shutdownNow()
        pool = null
        stopSelf()
    }

    override fun onRevoke() = stop()

    override fun onDestroy() {
        stop()
        super.onDestroy()
    }
}
