package com.gurubhingarde.adblocker

import android.content.Context
import java.io.File
import java.net.HttpURLConnection
import java.net.URL

/** Set of ad/tracker domains. A domain is blocked if it or any parent domain is listed. */
object Blocklist {
    private const val EXTRA_FILE = "extra_hosts.txt"
    private const val UPDATE_URL = "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
    private val IGNORED = setOf(
        "localhost", "localhost.localdomain", "local", "broadcasthost",
        "ip6-localhost", "ip6-loopback", "0.0.0.0"
    )

    @Volatile private var domains: Set<String> = emptySet()

    val size: Int get() = domains.size

    fun load(ctx: Context) {
        val set = HashSet<String>(100_000)
        ctx.assets.open("blocklist.txt").bufferedReader().useLines { parse(it, set) }
        val extra = File(ctx.filesDir, EXTRA_FILE)
        if (extra.exists()) extra.bufferedReader().useLines { parse(it, set) }
        domains = set
    }

    /** Downloads a large community hosts list. Call off the main thread. */
    fun update(ctx: Context) {
        val conn = URL(UPDATE_URL).openConnection() as HttpURLConnection
        conn.connectTimeout = 10_000
        conn.readTimeout = 20_000
        try {
            val tmp = File(ctx.filesDir, "$EXTRA_FILE.tmp")
            conn.inputStream.use { input -> tmp.outputStream().use { input.copyTo(it) } }
            if (!tmp.renameTo(File(ctx.filesDir, EXTRA_FILE))) {
                tmp.copyTo(File(ctx.filesDir, EXTRA_FILE), overwrite = true)
                tmp.delete()
            }
        } finally {
            conn.disconnect()
        }
        load(ctx)
    }

    fun isBlocked(name: String): Boolean {
        val set = domains
        var d = name
        while (true) {
            if (d in set) return true
            val i = d.indexOf('.')
            if (i < 0) return false
            d = d.substring(i + 1)
        }
    }

    private fun parse(lines: Sequence<String>, out: MutableSet<String>) {
        for (raw in lines) {
            val line = raw.substringBefore('#').trim()
            if (line.isEmpty()) continue
            val t = line.split(Regex("\\s+"))
            val d = (if (t.size >= 2) t[1] else t[0]).lowercase()
            if (d in IGNORED || !d.contains('.')) continue
            out.add(d)
        }
    }
}
